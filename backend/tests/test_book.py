"""
书籍模块单元测试（适配当前真实后端接口）
"""
import pytest
import jwt
from datetime import datetime

from src.app import create_app
from src.config import TestConfig
from src.models.user import db


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seller_token(client, app):
    """注册卖家并登录，返回 token"""
    # 注册
    client.post('/api/auth/register', json={
        'username': 'seller',
        'password': '123456'
    })
    # 登录
    response = client.post('/api/auth/login', json={
        'username': 'seller',
        'password': '123456'
    })
    return response.get_json()['token']


@pytest.fixture
def buyer_token(client):
    """注册买家并登录，返回 token"""
    client.post('/api/auth/register', json={
        'username': 'buyer',
        'password': '123456'
    })
    response = client.post('/api/auth/login', json={
        'username': 'buyer',
        'password': '123456'
    })
    return response.get_json()['token']


# ============== 正常路径测试 ==============

class TestCreateBook:
    """发布书籍测试"""

    def test_create_success(self, client, seller_token):
        """正常发布"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': 'Python编程',
            'price': 29.9,
            'condition': 'like_new'
        }, headers=headers)
        assert response.status_code == 201
        assert response.get_json()['book']['title'] == 'Python编程'

    def test_create_with_all_fields(self, client, seller_token):
        """完整字段发布"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': '算法导论',
            'author': 'Thomas',
            'description': '经典教材',
            'price': 99.0,
            'condition': 'good'
        }, headers=headers)
        assert response.status_code == 201


class TestGetBooks:
    """查询书籍测试"""

    def test_get_empty_list(self, client):
        """空列表"""
        response = client.get('/api/books')
        assert response.status_code == 200
        assert response.get_json()['total'] == 0

    def test_get_book_detail(self, client, seller_token):
        """查询单本"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        create_resp = client.post('/api/books', json={
            'title': 'Test Book', 'price': 10
        }, headers=headers)
        book_id = create_resp.get_json()['book']['id']

        response = client.get(f'/api/books/{book_id}')
        assert response.status_code == 200
        assert response.get_json()['book']['title'] == 'Test Book'

    def test_search_by_keyword(self, client, seller_token):
        """关键词搜索"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        client.post('/api/books', json={'title': 'Python基础', 'price': 10}, headers=headers)
        client.post('/api/books', json={'title': 'Java编程', 'price': 20}, headers=headers)

        response = client.get('/api/books?keyword=Python')
        data = response.get_json()
        assert data['total'] == 1
        assert 'Python' in data['books'][0]['title']


class TestUpdateBook:
    """修改书籍测试"""

    def test_update_success(self, client, seller_token):
        """正常修改"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        create_resp = client.post('/api/books', json={
            'title': 'Old Title', 'price': 10
        }, headers=headers)
        book_id = create_resp.get_json()['book']['id']

        response = client.put(f'/api/books/{book_id}', json={
            'title': 'New Title', 'price': 15
        }, headers=headers)
        assert response.status_code == 200
        assert response.get_json()['book']['title'] == 'New Title'


class TestDeleteBook:
    """删除书籍测试"""

    def test_delete_success(self, client, seller_token):
        """正常下架"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        create_resp = client.post('/api/books', json={
            'title': 'To Delete', 'price': 10
        }, headers=headers)
        book_id = create_resp.get_json()['book']['id']

        response = client.delete(f'/api/books/{book_id}', headers=headers)
        assert response.status_code == 200

        # 验证已被软删除
        response2 = client.get(f'/api/books/{book_id}')
        assert response2.status_code == 404


# ============== 异常路径测试 ==============

class TestCreateBookEdgeCases:
    """发布书籍边界测试"""

    def test_no_auth(self, client):
        """未登录"""
        response = client.post('/api/books', json={
            'title': 'Test', 'price': 10
        })
        assert response.status_code == 401

    def test_empty_title(self, client, seller_token):
        """空书名"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': '', 'price': 10
        }, headers=headers)
        assert response.status_code == 400

    def test_negative_price(self, client, seller_token):
        """负价格"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': 'Test', 'price': -10
        }, headers=headers)
        assert response.status_code == 400

    def test_zero_price(self, client, seller_token):
        """0价格"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': 'Test', 'price': 0
        }, headers=headers)
        assert response.status_code == 400

    def test_title_max_length(self, client, seller_token):
        """书名100字符（边界）"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': 'a' * 100, 'price': 10
        }, headers=headers)
        assert response.status_code == 201

    def test_title_exceed_max(self, client, seller_token):
        """书名101字符（超出）"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': 'a' * 101, 'price': 10
        }, headers=headers)
        assert response.status_code == 400

    def test_invalid_condition(self, client, seller_token):
        """无效成色"""
        headers = {'Authorization': f'Bearer {seller_token}'}
        response = client.post('/api/books', json={
            'title': 'Test', 'price': 10, 'condition': 'broken'
        }, headers=headers)
        assert response.status_code == 400


class TestUpdateBookPermission:
    """修改权限测试"""

    def test_get_nonexistent(self, client):
        """查询不存在的书"""
        response = client.get('/api/books/99999')
        assert response.status_code == 404

    def test_update_others_book(self, client, seller_token, buyer_token):
        """修改他人书籍"""
        # 卖家发布
        headers_seller = {'Authorization': f'Bearer {seller_token}'}
        create_resp = client.post('/api/books', json={
            'title': 'Seller Book', 'price': 10
        }, headers=headers_seller)
        book_id = create_resp.get_json()['book']['id']

        # 买家尝试修改
        headers_buyer = {'Authorization': f'Bearer {buyer_token}'}
        response = client.put(f'/api/books/{book_id}', json={
            'title': 'Hacked'
        }, headers=headers_buyer)
        assert response.status_code == 403

    def test_delete_others_book(self, client, seller_token, buyer_token):
        """删除他人书籍"""
        headers_seller = {'Authorization': f'Bearer {seller_token}'}
        create_resp = client.post('/api/books', json={
            'title': 'Seller Book', 'price': 10
        }, headers=headers_seller)
        book_id = create_resp.get_json()['book']['id']

        headers_buyer = {'Authorization': f'Bearer {buyer_token}'}
        response = client.delete(f'/api/books/{book_id}', headers=headers_buyer)
        assert response.status_code == 403