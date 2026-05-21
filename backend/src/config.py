"""
应用配置
"""
import os


class Config:
    """生产/开发配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///campus_book.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT配置
    JWT_EXPIRATION_HOURS = 24

    # 用户配置
    MIN_PASSWORD_LENGTH = 6
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50


class TestConfig(Config):
    """测试配置（内存数据库）"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True