"""
数据校验工具
"""
from flask import current_app


class UserValidator:
    """用户数据校验"""

    @classmethod
    def validate_register(cls, data: dict) -> tuple:
        """
        校验注册数据
        :return: (is_valid, error_message)
        """
        if not data:
            return False, '请求体不能为空'

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username:
            return False, '用户名不能为空'

        if not password:
            return False, '密码不能为空'

        min_len = current_app.config['MIN_USERNAME_LENGTH']
        max_len = current_app.config['MAX_USERNAME_LENGTH']
        if len(username) < min_len or len(username) > max_len:
            return False, f'用户名长度应在{min_len}-{max_len}个字符之间'

        min_pwd_len = current_app.config['MIN_PASSWORD_LENGTH']
        if len(password) < min_pwd_len:
            return False, f'密码至少{min_pwd_len}个字符'

        # 手机号格式（可选字段）
        phone = data.get('phone', '')
        if phone and (not phone.isdigit() or len(phone) != 11):
            return False, '手机号格式不正确'

        return True, None

    @classmethod
    def validate_login(cls, data: dict) -> tuple:
        """校验登录数据"""
        if not data:
            return False, '请求体不能为空'

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return False, '用户名和密码不能为空'

        return True, None