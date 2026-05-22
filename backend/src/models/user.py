from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# 用户模型
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=True)
    books = db.relationship('Book', backref='seller', lazy=True)


# 图书模型
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='on_sale')  # on_sale/sold/off_shelf
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# 订单模型
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/paid/completed/cancelled
    remark = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    buyer = db.relationship('User', foreign_keys=[buyer_id])
    book = db.relationship('Book', foreign_keys=[book_id])