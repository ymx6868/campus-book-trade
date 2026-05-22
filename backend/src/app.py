from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from functools import wraps
import re

from .models.user import db, User, Book, Order, Comment


def create_app(config=None):
    app = Flask(__name__)

    # 默认配置
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = False

    if config is not None:
        app.config.from_object(config)

    db.init_app(app)
    CORS(app)

    with app.app_context():
        db.create_all()

    # Token 校验装饰器
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.headers.get('Authorization', '')
            if not auth.startswith('Bearer '):
                return jsonify(error="Unauthorized"), 401
            try:
                token = auth.split(' ')[1]
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user = User.query.get(payload['user_id'])
            except:
                return jsonify(error="Unauthorized"), 401
            return f(user, *args, **kwargs)
        return decorated

    # ====================== 用户注册 ======================
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        phone = data.get('phone', None)

        if not username:
            return jsonify(error="用户名不能为空"), 400
        if len(username) < 3:
            return jsonify(error="用户名长度不能小于3位"), 400
        if len(password) < 6:
            return jsonify(error="密码长度不能小于6位"), 400
        if User.query.filter_by(username=username).first():
            return jsonify(error="用户名已存在"), 409
        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(error="手机号格式错误"), 400
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify(error="手机号已存在"), 400

        user = User(
            username=username,
            phone=phone,
            password_hash=password
        )
        db.session.add(user)
        db.session.commit()

        return jsonify(
            message="注册成功",
            user={
                "id": user.id,
                "username": user.username,
                "phone": user.phone
            }
        ), 201

    # ====================== 用户登录 ======================
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.json
        user = User.query.filter_by(username=data.get('username')).first()

        if not user or user.password_hash != data.get('password'):
            return jsonify(error="用户名或密码错误"), 401

        token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'])
        return jsonify(token=token), 200

    # ====================== 获取个人资料 ======================
    @app.route('/api/auth/profile', methods=['GET'])
    @token_required
    def get_profile(user):
        return jsonify(
            user={
                "username": user.username,
                "phone": user.phone
            }
        ), 200

    # ====================== 更新个人资料 ======================
    @app.route('/api/auth/profile', methods=['PUT'])
    @token_required
    def update_profile(user):
        data = request.json
        phone = data.get('phone')

        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(error="手机号格式错误"), 400

        user.phone = phone
        db.session.commit()
        return jsonify(
            user={
                "username": user.username,
                "phone": user.phone
            }
        ), 200

    # ====================== 图书接口 ======================
    @app.route('/api/books', methods=['POST'])
    @token_required
    def create_book(user):
        data = request.json
        title = data.get('title', '').strip()
        price = data.get('price', 0)
        condition = data.get('condition', 'good')

        if not title:
            return jsonify(error="书名不能为空"), 400
        if len(title) > 100:
            return jsonify(error="书名长度不能超过100字符"), 400
        if price <= 0:
            return jsonify(error="价格必须大于0"), 400
        if condition not in ['like_new', 'good', 'normal', 'poor']:
            return jsonify(error="无效的书籍成色"), 400

        book = Book(
            title=title,
            price=price,
            condition=condition,
            seller_id=user.id,
            author=data.get('author', ''),
            description=data.get('description', '')
        )
        db.session.add(book)
        db.session.commit()

        return jsonify(book={
            "id": book.id,
            "title": book.title,
            "price": book.price
        }), 201

    @app.route('/api/books', methods=['GET'])
    def get_books():
        keyword = request.args.get('keyword', '')
        books = Book.query.filter(Book.title.contains(keyword), Book.is_deleted == False).all()
        return jsonify(total=len(books), books=[{
            "id": b.id, "title": b.title, "price": b.price,
            "author": b.author, "condition": b.condition, "status": b.status
        } for b in books]), 200

    @app.route('/api/books/<int:id>', methods=['GET'])
    def get_book(id):
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book:
            return jsonify(error="not found"), 404
        return jsonify(book={
            "id": book.id, "title": book.title, "price": book.price,
            "author": book.author, "description": book.description,
            "condition": book.condition, "status": book.status,
            "seller_id": book.seller_id
        }), 200

    @app.route('/api/books/<int:id>', methods=['PUT'])
    @token_required
    def update_book(user, id):
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book or book.seller_id != user.id:
            return jsonify(error="forbidden"), 403
        data = request.json
        book.title = data.get('title', book.title)
        book.price = data.get('price', book.price)
        db.session.commit()
        return jsonify(book={"id": book.id, "title": book.title, "price": book.price}), 200

    @app.route('/api/books/<int:id>', methods=['DELETE'])
    @token_required
    def delete_book(user, id):
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book or book.seller_id != user.id:
            return jsonify(error="forbidden"), 403
        book.is_deleted = True
        db.session.commit()
        return jsonify(message="deleted"), 200

    # ====================== 订单接口 ======================
    @app.route('/api/orders', methods=['POST'])
    @token_required
    def create_order(user):
        """创建订单（下单）"""
        data = request.json
        book_id = data.get('book_id')
        remark = data.get('remark', '')

        if not book_id:
            return jsonify(error="书籍ID不能为空"), 400

        book = Book.query.filter_by(id=book_id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不存在"), 404

        if book.status != 'on_sale':
            return jsonify(error="该书籍已不可购买"), 400

        if book.seller_id == user.id:
            return jsonify(error="不能购买自己发布的书籍"), 400

        if remark and len(remark) > 500:
            return jsonify(error="备注不能超过500字符"), 400

        order = Order(
            buyer_id=user.id,
            book_id=book_id,
            amount=book.price,
            remark=remark if remark else None
        )
        db.session.add(order)
        db.session.commit()

        return jsonify(
            message="下单成功",
            order={
                "id": order.id,
                "book_id": order.book_id,
                "amount": order.amount,
                "status": order.status,
                "remark": order.remark
            }
        ), 201

    @app.route('/api/orders', methods=['GET'])
    @token_required
    def get_orders(user):
        """获取我的订单列表（role=buyer/seller）"""
        role = request.args.get('role', 'buyer')

        if role == 'seller':
            orders = Order.query.join(Book).filter(Book.seller_id == user.id).all()
        else:
            orders = Order.query.filter_by(buyer_id=user.id).all()

        return jsonify(
            total=len(orders),
            orders=[{
                "id": o.id,
                "book_id": o.book_id,
                "book_title": o.book.title if o.book else None,
                "buyer_id": o.buyer_id,
                "buyer_name": o.buyer.username if o.buyer else None,
                "amount": o.amount,
                "status": o.status,
                "remark": o.remark,
                "created_at": o.created_at.isoformat() if o.created_at else None
            } for o in orders]
        ), 200

    @app.route('/api/orders/<int:id>', methods=['GET'])
    @token_required
    def get_order(user, id):
        """获取订单详情"""
        order = Order.query.get(id)
        if not order:
            return jsonify(error="订单不存在"), 404

        is_buyer = order.buyer_id == user.id
        is_seller = order.book and order.book.seller_id == user.id

        if not (is_buyer or is_seller):
            return jsonify(error="无权查看此订单"), 403

        return jsonify(order={
            "id": order.id,
            "book_id": order.book_id,
            "book_title": order.book.title if order.book else None,
            "buyer_id": order.buyer_id,
            "amount": order.amount,
            "status": order.status,
            "remark": order.remark,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            "completed_at": order.completed_at.isoformat() if order.completed_at else None
        }), 200

    @app.route('/api/orders/<int:id>/status', methods=['PATCH'])
    @token_required
    def update_order_status(user, id):
        """更新订单状态"""
        order = Order.query.get(id)
        if not order:
            return jsonify(error="订单不存在"), 404

        is_buyer = order.buyer_id == user.id
        is_seller = order.book and order.book.seller_id == user.id

        if not (is_buyer or is_seller):
            return jsonify(error="无权操作此订单"), 403

        data = request.json
        new_status = data.get('status')

        if new_status not in ['paid', 'completed', 'cancelled']:
            return jsonify(error="状态无效"), 400

        # 状态流转校验
        valid_transitions = {
            'pending': ['paid', 'cancelled'],
            'paid': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        if new_status not in valid_transitions.get(order.status, []):
            return jsonify(error=f"状态不能从{order.status}变更为{new_status}"), 400

        # 权限细分
        if new_status == 'paid' and not is_buyer:
            return jsonify(error="只有买家可以支付"), 403
        if new_status == 'completed' and not is_buyer:
            return jsonify(error="只有买家可以确认收货"), 403

        old_status = order.status
        order.status = new_status

        if new_status == 'paid':
            order.paid_at = datetime.utcnow()
            if order.book:
                order.book.status = 'sold'
        elif new_status == 'completed':
            order.completed_at = datetime.utcnow()
        elif new_status == 'cancelled':
            if old_status == 'paid' and order.book:
                order.book.status = 'on_sale'

        db.session.commit()

        return jsonify(
            message="状态更新成功",
            order={
                "id": order.id,
                "status": order.status
            }
        ), 200

            # ====================== 留言接口 ======================
    @app.route('/api/books/<int:book_id>/comments', methods=['POST'])
    @token_required
    def create_comment(user, book_id):
        """发表留言"""
        data = request.json
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id', None)

        if not content:
            return jsonify(error="留言内容不能为空"), 400
        if len(content) > 500:
            return jsonify(error="留言内容不能超过500字符"), 400

        # 检查书籍存在
        book = Book.query.filter_by(id=book_id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不存在"), 404

        # 如果是回复，检查父留言存在
        if parent_id:
            parent = Comment.query.filter_by(id=parent_id, is_deleted=False).first()
            if not parent:
                return jsonify(error="回复的留言不存在"), 404

        comment = Comment(
            content=content,
            user_id=user.id,
            book_id=book_id,
            parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify(
            message="留言成功",
            comment={
                "id": comment.id,
                "content": comment.content,
                "user_id": comment.user_id,
                "user_name": user.username,
                "book_id": comment.book_id,
                "parent_id": comment.parent_id,
                "created_at": comment.created_at.isoformat()
            }
        ), 201

    @app.route('/api/books/<int:book_id>/comments', methods=['GET'])
    def get_comments(book_id):
        """获取某本书的所有留言"""
        # 检查书籍存在
        book = Book.query.filter_by(id=book_id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不存在"), 404

        comments = Comment.query.filter_by(
            book_id=book_id, is_deleted=False
        ).order_by(Comment.created_at.desc()).all()

        return jsonify(
            total=len(comments),
            comments=[{
                "id": c.id,
                "content": c.content,
                "user_id": c.user_id,
                "user_name": c.user.username if c.user else None,
                "parent_id": c.parent_id,
                "created_at": c.created_at.isoformat()
            } for c in comments]
        ), 200

    @app.route('/api/comments/<int:id>', methods=['DELETE'])
    @token_required
    def delete_comment(user, id):
        """删除留言（仅作者可删）"""
        comment = Comment.query.filter_by(id=id, is_deleted=False).first()
        if not comment:
            return jsonify(error="留言不存在"), 404

        if comment.user_id != user.id:
            return jsonify(error="无权删除此留言"), 403

        comment.is_deleted = True
        db.session.commit()

        return jsonify(message="删除成功"), 200

    @app.route('/api/comments/my', methods=['GET'])
    @token_required
    def get_my_comments(user):
        """获取我的留言列表"""
        comments = Comment.query.filter_by(
            user_id=user.id, is_deleted=False
        ).order_by(Comment.created_at.desc()).all()

        return jsonify(
            total=len(comments),
            comments=[{
                "id": c.id,
                "content": c.content,
                "book_id": c.book_id,
                "book_title": c.book.title if c.book else None,
                "parent_id": c.parent_id,
                "created_at": c.created_at.isoformat()
            } for c in comments]
        ), 200

    return app