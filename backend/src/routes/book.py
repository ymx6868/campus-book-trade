"""
书籍相关路由：发布、查询、修改、下架
"""
from flask import Blueprint, request, jsonify

from ..models.user import db
from ..models.book import Book, BookStatus, BookCondition
from ..utils.auth import login_required
from ..utils.validators import BookValidator

book_bp = Blueprint('book', __name__, url_prefix='/api/books')


@book_bp.route('', methods=['GET'])
def get_books():
    """
    获取书籍列表（公开接口，支持搜索、筛选、分页）
    GET /api/books?keyword=xxx&condition=good&page=1&per_page=20
    """
    # 基础查询：只显示未删除、在售的书
    query = Book.query.filter_by(is_deleted=False)

    # 按状态筛选（默认只看在售）
    status = request.args.get('status', 'on_sale')
    if status != 'all':
        try:
            query = query.filter_by(status=BookStatus(status))
        except ValueError:
            pass

    # 按成色筛选
    condition = request.args.get('condition')
    if condition:
        try:
            query = query.filter_by(condition=BookCondition(condition))
        except ValueError:
            pass

    # 关键词搜索（书名/作者）
    keyword = request.args.get('keyword', '').strip()
    if keyword:
        query = query.filter(
            db.or_(
                Book.title.like(f'%{keyword}%'),
                Book.author.like(f'%{keyword}%')
            )
        )

    # 排序（默认按创建时间倒序）
    query = query.order_by(Book.created_at.desc())

    # 分页
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(max(per_page, 1), 100)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'books': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """获取单本书籍详情（公开接口）"""
    book = Book.query.get(book_id)

    if not book or book.is_deleted:
        return jsonify({'error': '书籍不存在'}), 404

    return jsonify({'book': book.to_dict()}), 200


@book_bp.route('', methods=['POST'])
@login_required
def create_book(current_user):
    """
    发布书籍（需登录）
    POST /api/books
    Body: {"title": "xxx", "price": 19.9, "condition": "good", ...}
    """
    data = request.get_json()

    # 数据校验
    is_valid, error_msg = BookValidator.validate_create(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    book = Book(
        title=data['title'].strip(),
        author=data.get('author', '').strip() or None,
        description=data.get('description', '').strip() or None,
        price=float(data['price']),
        condition=BookCondition(data.get('condition', 'good')),
        seller_id=current_user.id
    )

    try:
        db.session.add(book)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': '发布失败，请稍后重试'}), 500

    return jsonify({
        'message': '发布成功',
        'book': book.to_dict()
    }), 201


@book_bp.route('/<int:book_id>', methods=['PUT'])
@login_required
def update_book(current_user, book_id):
    """修改书籍（仅卖家可改）"""
    book = Book.query.get(book_id)

    if not book or book.is_deleted:
        return jsonify({'error': '书籍不存在'}), 404

    if book.seller_id != current_user.id:
        return jsonify({'error': '无权修改此书籍'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': '请求体不能为空'}), 400

    is_valid, error_msg = BookValidator.validate_update(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    if 'title' in data:
        book.title = data['title'].strip()
    if 'author' in data:
        book.author = data['author'].strip() or None
    if 'description' in data:
        book.description = data['description'].strip() or None
    if 'price' in data:
        book.price = float(data['price'])
    if 'condition' in data:
        book.condition = BookCondition(data['condition'])
    if 'status' in data:
        book.status = BookStatus(data['status'])

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': '修改失败'}), 500

    return jsonify({
        'message': '修改成功',
        'book': book.to_dict()
    }), 200


@book_bp.route('/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(current_user, book_id):
    """下架书籍（软删除，仅卖家可操作）"""
    book = Book.query.get(book_id)

    if not book or book.is_deleted:
        return jsonify({'error': '书籍不存在'}), 404

    if book.seller_id != current_user.id:
        return jsonify({'error': '无权下架此书籍'}), 403

    book.is_deleted = True

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': '下架失败'}), 500

    return jsonify({'message': '下架成功'}), 200


@book_bp.route('/my', methods=['GET'])
@login_required
def get_my_books(current_user):
    """获取我发布的书籍列表"""
    books = Book.query.filter_by(
        seller_id=current_user.id,
        is_deleted=False
    ).order_by(Book.created_at.desc()).all()

    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': len(books)
    }), 200