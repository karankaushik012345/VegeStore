
from flask import Blueprint, request, jsonify
from models import Product, Category, db
from sqlalchemy import func

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["GET"])
def get_products():
    q = request.args.get("q", "")
    category = request.args.get("category", "")
    sort = request.args.get("sort", "featured")
    organic = request.args.get("organic", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    query = Product.query
    if q:
        query = query.filter(
            Product.name.ilike(f"%{q}%") |
            Product.description.ilike(f"%{q}%") |
            Product.tags.ilike(f"%{q}%")
        )
    if category:
        query = query.join(Product.category).filter(Category.name == category)
    if organic == "true":
        query = query.filter(Product.is_organic == True)
    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort == "newest":
        query = query.order_by(Product.id.desc())
    else:
        query = query.order_by(Product.is_featured.desc(), Product.rating.desc())
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    return jsonify({
        "products": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page
    })

@products_bp.route("/<int:pid>", methods=["GET"])
def get_product(pid):
    p = Product.query.get_or_404(pid)
    data = p.to_dict()
    # Related products in same category
    related = Product.query.filter(
        Product.category_id == p.category_id,
        Product.id != p.id
    ).order_by(Product.rating.desc()).limit(6).all()
    data["related"] = [r.to_dict() for r in related]
    # Fake reviews data
    import random
    random.seed(pid)
    reviewers = [
        ("Priya S.", "Bengaluru"), ("Rahul M.", "Mumbai"), ("Anita K.", "Hyderabad"),
        ("Suresh P.", "Delhi"), ("Deepa R.", "Chennai"), ("Arjun V.", "Pune"),
        ("Kavya N.", "Bengaluru"), ("Vikram T.", "Kolkata"), ("Meera J.", "Ahmedabad"),
        ("Rohan B.", "Jaipur"), ("Sunita G.", "Lucknow"), ("Arun S.", "Chandigarh"),
    ]
    comments = [
        "Super fresh! Came well packaged and looked farm-picked.",
        "Excellent quality. Better than what I get from local market.",
        "Very fresh and the taste was amazing. Will order again.",
        "Delivery was on time and vegetables were in perfect condition.",
        "Organic and fresh. My family loved it. Highly recommended.",
        "Good quality but slightly expensive. Worth it for the freshness.",
        "Brilliant! The produce is noticeably fresher than supermarket.",
        "Ordered multiple times. Consistent quality every single time.",
        "The description matched perfectly. Great farm-to-table experience.",
        "My kids actually ate their vegetables today. That says it all!",
    ]
    sample_reviews = []
    for i in range(min(8, p.review_count // 100 + 3)):
        reviewer = reviewers[random.randint(0, len(reviewers)-1)]
        rating = random.choice([4, 4, 4, 5, 5, 5, 5])
        daysago = random.randint(1, 60)
        sample_reviews.append({
            "name": reviewer[0],
            "city": reviewer[1],
            "rating": rating,
            "comment": comments[random.randint(0, len(comments)-1)],
            "days_ago": daysago,
            "verified": True
        })
    data["reviews"] = sample_reviews
    return jsonify(data)

@products_bp.route("/featured", methods=["GET"])
def featured():
    products = Product.query.filter_by(is_featured=True).limit(12).all()
    return jsonify([p.to_dict() for p in products])

@products_bp.route("/categories", methods=["GET"])
def categories():
    cats = Category.query.all()
    result = []
    for c in cats:
        count = Product.query.filter_by(category_id=c.id).count()
        d = c.to_dict()
        d["count"] = count
        result.append(d)
    return jsonify(result)

@products_bp.route("/search/suggestions", methods=["GET"])
def search_suggestions():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    products = Product.query.filter(
        Product.name.ilike(f"%{q}%")
    ).limit(6).all()
    return jsonify([{"id": p.id, "name": p.name, "emoji": p.emoji, "price": p.price, "unit": p.unit} for p in products])
