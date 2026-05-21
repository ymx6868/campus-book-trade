"""
用户模块单元测试
"""
import pytest

from src.app import create_app
from src.config import TestConfig
from src.models.user import db


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """注册并登录，返回token"""
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    return response.get_json()['token']


# =========================================
# 正常路径测试（驾驶员A编写）
# =========================================

class TestRegister:
    """注册接口测试"""

    def test_register_success(self, client):
        """正常注册"""
        response = client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '123456'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['user']['username'] == 'alice'

    def test_register_with_phone(self, client):
        """带手机号注册"""
        response = client.post('/api/auth/register', json={
            'username': 'bob',
            'password': '123456',
            'phone': '13800138000'
        })
        assert response.status_code == 201
        assert response.get_json()['user']['phone'] == '13800138000'


class TestLogin:
    """登录接口测试"""

    def test_login_success(self, client):
        """正常登录"""
        client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '123456'
        })
        response = client.post('/api/auth/login', json={
            'username': 'alice',
            'password': '123456'
        })
        assert response.status_code == 200
        assert 'token' in response.get_json()


class TestProfile:
    """个人信息测试"""

    def test_get_profile(self, client, auth_token):
        """获取个人信息"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/auth/profile', headers=headers)
        assert response.status_code == 200
        assert response.get_json()['user']['username'] == 'testuser'

    def test_update_profile(self, client, auth_token):
        """更新个人信息"""
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.put('/api/auth/profile',
                              json={'phone': '13900139000'},
                              headers=headers)
        assert response.status_code == 200
        assert response.get_json()['user']['phone'] == '13900139000'


# =========================================
# 异常路径测试（领航员B设计，驾驶员A实现）
# =========================================

class TestRegisterEdgeCases:
    """注册边界测试"""

    def test_empty_username(self, client):
        """空用户名"""
        response = client.post('/api/auth/register', json={
            'username': '',
            'password': '123456'
        })
        assert response.status_code == 400

    def test_short_password(self, client):
        """密码太短（5位）"""
        response = client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '12345'
        })
        assert response.status_code == 400

    def test_min_valid_password(self, client):
        """密码刚好6位（边界值）"""
        response = client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '123456'
        })
        assert response.status_code == 201

    def test_duplicate_username(self, client):
        """重复用户名"""
        client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '123456'
        })
        response = client.post('/api/auth/register', json={
            'username': 'alice',
            'password': 'other123'
        })
        assert response.status_code == 409

    def test_invalid_phone(self, client):
        """手机号格式错误"""
        response = client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '123456',
            'phone': '12345'
        })
        assert response.status_code == 400

    def test_short_username(self, client):
        """用户名太短（2位）"""
        response = client.post('/api/auth/register', json={
            'username': 'ab',
            'password': '123456'
        })
        assert response.status_code == 400


class TestLoginEdgeCases:
    """登录边界测试"""

    def test_wrong_password(self, client):
        """错误密码"""
        client.post('/api/auth/register', json={
            'username': 'alice',
            'password': '123456'
        })
        response = client.post('/api/auth/login', json={
            'username': 'alice',
            'password': 'wrong'
        })
        assert response.status_code == 401
        # 确保不泄露具体错误
        assert '用户名或密码错误' in response.get_json()['error']

    def test_nonexistent_user(self, client):
        """不存在的用户"""
        response = client.post('/api/auth/login', json={
            'username': 'ghost',
            'password': '123456'
        })
        assert response.status_code == 401


class TestAuthorizationEdgeCases:
    """权限验证测试"""

    def test_access_without_token(self, client):
        """无Token访问"""
        response = client.get('/api/auth/profile')
        assert response.status_code == 401

    def test_invalid_token(self, client):
        """无效Token"""
        headers = {'Authorization': 'Bearer invalid.token.here'}
        response = client.get('/api/auth/profile', headers=headers)
        assert response.status_code == 401