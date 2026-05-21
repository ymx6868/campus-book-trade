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
        class BookValidator:
    """书籍数据校验"""

    VALID_CONDITIONS = {'new', 'like_new', 'good', 'fair', 'poor'}
    VALID_STATUSES = {'on_sale', 'sold', 'off_shelf'}

    MAX_TITLE_LENGTH = 100
    MAX_AUTHOR_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 2000

    @classmethod
    def validate_create(cls, data: dict) -> tuple:
        """校验创建书籍数据"""
        if not data:
            return False, '请求体不能为空'

        # 书名校验
        title = data.get('title', '').strip()
        if not title:
            return False, '书名不能为空'
        if len(title) > cls.MAX_TITLE_LENGTH:
            return False, f'书名不能超过{cls.MAX_TITLE_LENGTH}个字符'

        # 价格校验
        price = data.get('price')
        if price is None:
            return False, '价格不能为空'
        try:
            price = float(price)
            if price <= 0:
                return False, '价格必须大于0'
            if price > 99999:
                return False, '价格不能超过99999'
        except (ValueError, TypeError):
            return False, '价格格式不正确'

        # 作者校验（可选）
        author = data.get('author', '')
        if author and len(author) > cls.MAX_AUTHOR_LENGTH:
            return False, f'作者名不能超过{cls.MAX_AUTHOR_LENGTH}个字符'

        # 描述校验（可选）
        description = data.get('description', '')
        if description and len(description) > cls.MAX_DESCRIPTION_LENGTH:
            return False, f'描述不能超过{cls.MAX_DESCRIPTION_LENGTH}个字符'

        # 成色校验
        condition = data.get('condition', 'good')
        if condition not in cls.VALID_CONDITIONS:
            return False, f'成色无效，可选：{", ".join(cls.VALID_CONDITIONS)}'

        return True, None

    @classmethod
    def validate_update(cls, data: dict) -> tuple:
        """校验更新书籍数据"""
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return False, '书名不能为空'
            if len(title) > cls.MAX_TITLE_LENGTH:
                return False, f'书名不能超过{cls.MAX_TITLE_LENGTH}个字符'

        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return False, '价格必须大于0'
            except (ValueError, TypeError):
                return False, '价格格式不正确'

        if 'condition' in data and data['condition'] not in cls.VALID_CONDITIONS:
            return False, '成色无效'

        if 'status' in data and data['status'] not in cls.VALID_STATUSES:
            return False, '状态无效'

        return True, None