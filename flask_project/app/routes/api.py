from flask import Blueprint, request, jsonify
from ..models import db, Company, Certificate, Brand, ProductCategory, Product, News, ContactMessage, NewsletterSubscriber, Banner

api_bp = Blueprint("api", __name__)

# ---------- Helper ----------
def get_or_404(model, object_id):
    obj = model.query.get(object_id)
    if not obj:
        return jsonify({"error": f"{model.__name__} with id {object_id} not found"}), 404
    return obj


# ---------- COMPANY ----------
@api_bp.route("/companies", methods=["GET"], endpoint="companies_list")
def get_companies():
    companies = Company.query.all()
    return jsonify([{"id": c.id, "name": c.name, "email": c.email, "phone": c.phone} for c in companies])


@api_bp.route("/companies/<int:company_id>", methods=["GET"], endpoint="companies_get")
def get_company(company_id):
    c = get_or_404(Company, company_id)
    if isinstance(c, tuple):
        return c
    return jsonify({
        "id": c.id, "name": c.name, "mission": c.mission, "vision": c.vision,
        "phone": c.phone, "email": c.email, "address": c.address, "map_coordinates": c.map_coordinates
    })


@api_bp.route("/companies", methods=["POST"], endpoint="companies_create")
def create_company():
    data = request.json
    company = Company(**data)
    db.session.add(company)
    db.session.commit()
    return jsonify({"id": company.id}), 201


@api_bp.route("/companies/<int:company_id>", methods=["PUT"], endpoint="companies_update")
def update_company(company_id):
    c = get_or_404(Company, company_id)
    if isinstance(c, tuple):
        return c
    data = request.json
    for key, value in data.items():
        setattr(c, key, value)
    db.session.commit()
    return jsonify({"message": "Updated"})


@api_bp.route("/companies/<int:company_id>", methods=["DELETE"], endpoint="companies_delete")
def delete_company(company_id):
    c = get_or_404(Company, company_id)
    if isinstance(c, tuple):
        return c
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Deleted"})


# ---------- GENERIC CRUD ----------
def register_crud(model, endpoint, fields):
    """Автоматически создаёт CRUD для модели"""

    # LIST
    @api_bp.route(f"/{endpoint}", methods=["GET"], endpoint=f"{endpoint}_list")
    def list_items(model=model, fields=fields):
        items = model.query.all()
        return jsonify([{f: getattr(item, f) for f in fields} for item in items])

    # GET by id
    @api_bp.route(f"/{endpoint}/<int:item_id>", methods=["GET"], endpoint=f"{endpoint}_get")
    def get_item(item_id, model=model, fields=fields):
        item = get_or_404(model, item_id)
        if isinstance(item, tuple):
            return item
        return jsonify({f: getattr(item, f) for f in fields})

    # CREATE
    @api_bp.route(f"/{endpoint}", methods=["POST"], endpoint=f"{endpoint}_create")
    def create_item(model=model):
        data = request.json
        item = model(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify({"id": item.id}), 201

    # UPDATE
    @api_bp.route(f"/{endpoint}/<int:item_id>", methods=["PUT"], endpoint=f"{endpoint}_update")
    def update_item(item_id, model=model):
        item = get_or_404(model, item_id)
        if isinstance(item, tuple):
            return item
        data = request.json
        for key, value in data.items():
            setattr(item, key, value)
        db.session.commit()
        return jsonify({"message": "Updated"})

    # DELETE
    @api_bp.route(f"/{endpoint}/<int:item_id>", methods=["DELETE"], endpoint=f"{endpoint}_delete")
    def delete_item(item_id, model=model):
        item = get_or_404(model, item_id)
        if isinstance(item, tuple):
            return item
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Deleted"})


# ---------- REGISTER MODELS ----------
register_crud(Certificate, "certificates", ["id", "name", "description", "company_id"])
register_crud(Brand, "brands", ["id", "name", "slug", "company_id"])
register_crud(ProductCategory, "categories", ["id", "name", "slug", "parent_category_id"])
register_crud(Product, "products", ["id", "name", "slug", "category_id", "brand_id"])
register_crud(News, "news", ["id", "title", "slug", "publication_date", "company_id"])
register_crud(Banner, "banners", ["id", "title", "description", "link"])


# ---------- CONTACT MESSAGE (only POST) ----------
@api_bp.route("/contact_messages", methods=["POST"], endpoint="contact_messages_create")
def create_contact_message():
    data = request.json
    msg = ContactMessage(**data)
    db.session.add(msg)
    db.session.commit()
    return jsonify({"id": msg.id}), 201


# ---------- NEWSLETTER SUBSCRIBER (only POST) ----------
@api_bp.route("/newsletter_subscribers", methods=["POST"], endpoint="newsletter_subscribers_create")
def create_newsletter_subscriber():
    data = request.json
    sub = NewsletterSubscriber(**data)
    db.session.add(sub)
    db.session.commit()
    return jsonify({"id": sub.id}), 201
