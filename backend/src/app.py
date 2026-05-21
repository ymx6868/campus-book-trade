"""
Flask应用工厂
"""
from flask import Flask
from flask_cors import CORS

from .config import Config
from .models.user import db
from .routes.auth import auth_bp


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 允许跨域（前端调用需要）

    # 注册蓝图
    app.register_blueprint(auth_bp)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'error': '资源不存在'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': '服务器内部错误'}, 500

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': '请求方法不允许'}, 405

    return app