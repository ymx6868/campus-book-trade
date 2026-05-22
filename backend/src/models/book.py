"""
书籍数据模型
"""
from datetime import datetime
from enum import Enum as PyEnum

from .user import db


class BookStatus(PyEnum):
    """书籍状态枚举"""
    ON_SALE = "on_sale"      # 在售
    SOLD = "sold"            # 已售
    OFF_SHELF = "off_shelf"  # 下架


class BookCondition(PyEnum):
    """书籍成色枚举"""
    NEW = "new"               # 全新
    LIKE_NEW = "like_new"     # 九成新
    GOOD = "good"             # 八成新
    FAIR = "fair"             # 七成新
    POOR = "poor"             # 较旧


class Book(db.Model):
    """书籍表"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    author = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    condition = db.Column(db.Enum(BookCondition), default=BookCondition.GOOD, nullable=False)
    status = db.Column(db.Enum(BookStatus), default=BookStatus.ON_SALE, nullable=False)
    
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    # 关联卖家用户
    seller = db.relationship('User', backref='books', foreign_keys=[seller_id])

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'price': float(self.price),
            'condition': self.condition.value,
            'status': self.status.value,
            'seller_id': self.seller_id,
            'seller_name': self.seller.username if self.seller else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Book {self.title}>'