"""
认证相关路由：注册、登录、获取个人信息
"""
from flask import Blueprint, request, jsonify

from ..models.user import db, User
from ..utils.auth import generate_token, login_required
from ..utils.validators import UserValidator

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    POST /api/auth/register
    Body: {"username": "xxx", "password": "xxx", "phone": "xxx"}
    """
    data = request.get_json()

    # 数据校验
    is_valid, error_msg = UserValidator.validate_register(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    username = data['username'].strip()
    password = data['password']
    phone = data.get('phone', '').strip()

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已被占用'}), 409

    # 创建用户
    user = User(username=username, phone=phone if phone else None)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '注册失败，请稍后重试'}), 500

    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    POST /api/auth/login
    Body: {"username": "xxx", "password": "xxx"}
    Return: {"token": "xxx", "user": {...}}
    """
    data = request.get_json()

    # 数据校验
    is_valid, error_msg = UserValidator.validate_login(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    username = data['username'].strip()
    password = data['password']

    user = User.query.filter_by(username=username).first()

    # 用户不存在或密码错误（统一提示，避免信息泄露）
    if user is None or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401

    # 生成Token
    token = generate_token(user.id)

    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile(current_user):
    """
    获取当前用户信息
    GET /api/auth/profile
    Headers: Authorization: Bearer <token>
    """
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile(current_user):
    """
    更新当前用户信息（目前只支持改手机号）
    PUT /api/auth/profile
    Body: {"phone": "xxx"}
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    if 'phone' in data:
        phone = data['phone'].strip()
        if phone and (not phone.isdigit() or len(phone) != 11):
            return jsonify({'error': '手机号格式不正确'}), 400
        current_user.phone = phone if phone else None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': '更新失败'}), 500

    return jsonify({
        'message': '更新成功',
        'user': current_user.to_dict()
    }), 200