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
            if not user:
                return jsonify(error="Unauthorized"), 401
            return f(user, *args, **kwargs)
        return decorated

    # ==================== 用户认证路由 ====================
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """注册接口"""
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip() or None

        if not username or not password:
            return jsonify(error="用户名和密码不能为空"), 400
        if len(password) < 6:
            return jsonify(error="密码至少需要6位"), 400
        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(error="手机号格式不正确"), 400

        if User.query.filter_by(username=username).first():
            return jsonify(error="用户名已被占用"), 400
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify(error="手机号已被注册"), 400

        user = User(username=username, phone=phone)
        user.password_hash = password  # 实际中应使用哈希，此处简化

        db.session.add(user)
        db.session.commit()

        return jsonify(message="注册成功"), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """登录接口"""
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if not user or user.password_hash != password:
            return jsonify(error="用户名或密码错误"), 401

        # 生成 Token
        token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify(token=token), 200

    @app.route('/api/auth/profile', methods=['GET'])
    @token_required
    def get_profile(user):
        """获取个人信息"""
        return jsonify(
            user={
                "id": user.id,
                "username": user.username,
                "phone": user.phone
            }
        ), 200

    @app.route('/api/auth/profile', methods=['PUT'])
    @token_required
    def update_profile(user):
        """修改个人信息"""
        data = request.get_json()
        phone = data.get('phone', '').strip() or None

        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify(error="手机号格式不正确"), 400

        if phone and phone != user.phone:
            if User.query.filter_by(phone=phone).first():
                return jsonify(error="该手机号已被其它账号绑定"), 400

        user.phone = phone
        db.session.commit()

        return jsonify(message="更新成功"), 200

    # ==================== 书籍管理路由 ====================
    @app.route('/api/books', methods=['GET'])
    def get_books():
        """获取书籍列表（只展示未删除、且上架在售的书籍）"""
        keyword = request.args.get('keyword', '')
        
        # 核心修改点：主页只查在售的书，过滤掉下架(off_shelf)或删除(is_deleted)的书
        query = Book.query.filter_by(is_deleted=False, status='on_sale')
        
        if keyword:
            query = query.filter(Book.title.contains(keyword))
            
        books = query.order_by(Book.created_at.desc()).all()

        return jsonify(
            total=len(books),
            books=[{
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "description": b.description,
                "price": b.price,
                "condition": b.condition,
                "status": b.status,
                "seller_id": b.seller_id,
                "seller_name": b.seller.username if b.seller else "热心校友",
                "created_at": b.created_at.isoformat()
            } for b in books]
        ), 200

    @app.route('/api/books/<int:id>', methods=['GET'])
    def get_book(id):
        """获取单本书籍详情"""
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不存在或已下架"), 404

        return jsonify(
            book={
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
                "price": book.price,
                "condition": book.condition,
                "status": book.status,
                "seller_id": book.seller_id,
                "seller_name": book.seller.username if book.seller else "热心校友",
                "created_at": book.created_at.isoformat()
            }
        ), 200

    @app.route('/api/books', methods=['POST'])
    @token_required
    def create_book(user):
        """发布置闲书籍"""
        data = request.get_json()
        title = data.get('title', '').strip()
        author = data.get('author', '').strip() or None
        description = data.get('description', '').strip() or None
        price = data.get('price')
        condition = data.get('condition', 'good')

        if not title:
            return jsonify(error="书名不能为空"), 400
        try:
            price_f = float(price)
            if price_f <= 0:
                return jsonify(error="价格必须大于0"), 400
        except:
            return jsonify(error="并非合法的价格数字"), 400

        book = Book(
            title=title, author=author, description=description,
            price=price_f, condition=condition, seller_id=user.id,
            status='on_sale'
        )
        db.session.add(book)
        db.session.commit()

        return jsonify(message="发布成功", book_id=book.id), 201

    @app.route('/api/books/<int:id>', methods=['PUT'])
    @token_required
    def update_book(user, id):
        """修改书籍信息"""
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不存在"), 404
        if book.seller_id != user.id:
            return jsonify(error="无权修改此书籍"), 403

        data = request.get_json()
        book.title = data.get('title', book.title).strip()
        book.author = data.get('author', book.author).strip()
        book.description = data.get('description', book.description).strip()
        if 'price' in data:
            book.price = float(data['price'])
        if 'condition' in data:
            book.condition = data['condition']

        db.session.commit()
        return jsonify(message="更新成功"), 200

    @app.route('/api/books/<int:id>', methods=['DELETE'])
    @token_required
    def delete_book(user, id):
        """下架商品接口修复"""
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不存在"), 404

        # 校验：只有管理员或者卖家本人能下架
        if book.seller_id != user.id:
            return jsonify(error="无权下架此书籍"), 403

        book.is_deleted = True
        book.status = 'off_shelf'  # 标记为已下架状态
        db.session.commit()

        return jsonify(message="下架成功"), 200

    # ==================== 订单交易路由 ====================
    @app.route('/api/orders', methods=['POST'])
    @token_required
    def create_order(user):
        """创建交易订单"""
        data = request.get_json()
        book_id = data.get('book_id')

        book = Book.query.filter_by(id=book_id, is_deleted=False).first()
        if not book:
            return jsonify(error="书籍不可售"), 404
        if book.status != 'on_sale':
            return jsonify(error="该书非在售状态，无法购买"), 400
        if book.seller_id == user.id:
            return jsonify(error="不能购买自己发布的书籍"), 400

        order = Order(
            buyer_id=user.id,
            book_id=book.id,
            amount=book.price,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()

        return jsonify(message="下单成功", order_id=order.id), 201

    @app.route('/api/orders', methods=['GET'])
    @token_required
    def get_orders(user):
        """获取我的订单中心"""
        role = request.args.get('role', 'buyer')

        if role == 'seller':
            orders = Order.query.join(Book).filter(Book.seller_id == user.id).order_by(Order.created_at.desc()).all()
        else:
            orders = Order.query.filter_by(buyer_id=user.id).order_by(Order.created_at.desc()).all()

        return jsonify(
            total=len(orders),
            orders=[{
                "id": order.id,
                "amount": order.amount,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "book": {
                    "id": order.book.id,
                    "title": order.book.title
                } if order.book else None
            } for order in orders]
        ), 200

    @app.route('/api/orders/<int:id>/status', methods=['PATCH'])
    @token_required
    def update_order_status(user, id):
        """更新订单状态接口修复（解除 pending 到 completed 的强校验限制）"""
        order = Order.query.get(id)
        if not order:
            return jsonify(error="订单不存在"), 404

        if order.buyer_id != user.id and order.book.seller_id != user.id:
            return jsonify(error="无权操作此订单"), 403

        data = request.get_json()
        status = data.get('status')
        if status not in ['paid', 'completed', 'cancelled']:
            return jsonify(error="非法状态格式"), 400

        # 核心修改点：如果是完成交易交付（completed），无需卡死状态
        if status == 'completed':
            order.status = 'completed'
            order.completed_at = datetime.utcnow()
            # 级联更新：当线下交付完成后，自动把图书状态更新为“已售出”(sold)
            if order.book:
                order.book.status = 'sold'
        else:
            order.status = status
            if status == 'paid':
                order.paid_at = datetime.utcnow()

        db.session.commit()

        return jsonify(
            message="订单状态更新成功",
            order={"id": order.id, "status": order.status}
        ), 200

    # ==================== 留言区咨询路由 ====================
    @app.route('/api/books/<int:book_id>/comments', methods=['POST'])
    @token_required
    def create_comment(user, book_id):
        """发表留言咨询"""
        data = request.get_json()
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')

        if not content:
            return jsonify(error="留言内容不能为空"), 400

        comment = Comment(
            content=content, book_id=book_id,
            user_id=user.id, parent_id=parent_id
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify(message="留言成功", comment_id=comment.id), 201

    @app.route('/api/books/<int:book_id>/comments', methods=['GET'])
    def get_comments(book_id):
        """获取书本留言列表"""
        comments = Comment.query.filter_by(
            book_id=book_id, is_deleted=False
        ).order_by(Comment.created_at.asc()).all()

        return jsonify(
            total=len(comments),
            comments=[{
                "id": c.id,
                "content": c.content,
                "user_id": c.user_id,
                "user_name": c.user.username if c.user else "热心校友",
                "parent_id": c.parent_id,
                "created_at": c.created_at.isoformat()
            } for c in comments]
        ), 200

    @app.route('/api/comments/<int:id>', methods=['DELETE'])
    @token_required
    def delete_comment(user, id):
        """删除留言"""
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
                "created_at": c.created_at.isoformat()
            } for c in comments]
        ), 200

    return app