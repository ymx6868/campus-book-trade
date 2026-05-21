"""
JWT认证工具
"""
from functools import wraps
from datetime import datetime, timedelta

import jwt
from flask import request, jsonify, current_app

from ..models.user import User


def generate_token(user_id: int) -> str:
    """
    生成JWT Token
    
    :param user_id: 用户ID
    :return: JWT token字符串
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(
            hours=current_app.config['JWT_EXPIRATION_HOURS']
        ),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def login_required(f):
    """
    登录验证装饰器
    使用方式：在路由函数上加 @login_required
    被装饰的函数第一个参数会自动收到 current_user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': '缺少认证Token，请先登录'}), 401

        # 支持 "Bearer <token>" 格式
        if token.startswith('Bearer '):
            token = token[7:]

        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user = User.query.get(payload['user_id'])
            if current_user is None:
                return jsonify({'error': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token无效'}), 401

        return f(current_user, *args, **kwargs)

    return decorated_function