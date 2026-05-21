from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from functools import wraps
import re

from .models.user import db, User, Book

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
        books = Book.query.filter(Book.title.contains(keyword), Book.is_deleted==False).all()
        return jsonify(total=len(books), books=[{"id": b.id, "title": b.title} for b in books]), 200

    @app.route('/api/books/<int:id>', methods=['GET'])
    def get_book(id):
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book: return jsonify(error="not found"), 404
        return jsonify(book={"id": book.id, "title": book.title, "price": book.price}), 200

    @app.route('/api/books/<int:id>', methods=['PUT'])
    @token_required
    def update_book(user, id):
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book or book.seller_id != user.id: return jsonify(error="forbidden"), 403
        data = request.json
        book.title = data.get('title', book.title)
        book.price = data.get('price', book.price)
        db.session.commit()
        return jsonify(book={"id": book.id, "title": book.title, "price": book.price}), 200

    @app.route('/api/books/<int:id>', methods=['DELETE'])
    @token_required
    def delete_book(user, id):
        book = Book.query.filter_by(id=id, is_deleted=False).first()
        if not book or book.seller_id != user.id: return jsonify(error="forbidden"), 403
        book.is_deleted = True
        db.session.commit()
        return jsonify(message="deleted"), 200

    return app