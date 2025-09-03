import os
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import ImageUploadField
from flask import redirect, url_for
from wtforms import FileField, TextAreaField
from .models import (
    db, Product, ProductCategory, Brand, News, Banner,
    ContactMessage, NewsletterSubscriber, AdminUser,
    Company, Certificate
)

# --- Доступ для авторизованных ---
class SecureModelView(ModelView):
    def is_accessible(self):
        from flask_login import current_user
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))

# --- Дашборд ---
class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        stats = {
            "companies": Company.query.count(),
            "products": Product.query.count(),
            "categories": ProductCategory.query.count(),
            "brands": Brand.query.count(),
            "news": News.query.count(),
            "certificates": Certificate.query.count(),
            "subscribers": NewsletterSubscriber.query.count(),
            "users": AdminUser.query.count(),
        }
        return self.render("admin/dashboard.html", stats=stats)

    def is_visible(self):
        return False

# --- Множественный аплоад ---
class MultiImageUploadField(FileField):
    def process_formdata(self, valuelist):
        self.data = []
        upload_folder = os.path.join("app", "static", "uploads", "products")
        os.makedirs(upload_folder, exist_ok=True)

        for f in valuelist:
            if f.filename:
                file_path = os.path.join(upload_folder, f.filename)
                f.save(file_path)
                self.data.append(os.path.join("static", "uploads", "products", f.filename))

    def _value(self):
        return self.data if self.data else []

# --- Используем кастомный шаблон для CKEditor ---
EDIT_TEMPLATE = "admin/edit.html"

# --- Product Admin ---
class ProductAdmin(SecureModelView):
    form_overrides = {"description": TextAreaField}
    form_template = EDIT_TEMPLATE
    form_extra_fields = {
        "image": ImageUploadField(
            "Главное изображение",
            base_path=os.path.join("app", "static", "uploads", "products"),
            relative_path="products/",
            url_relative_path="static/uploads/products/"
        ),
        "additional_images": MultiImageUploadField("Дополнительные изображения")
    }

    def on_model_change(self, form, model, is_created):
        if form.additional_images.data:
            model.additional_images = form.additional_images.data

# --- Brand Admin ---
class BrandAdmin(SecureModelView):
    form_overrides = {"description": TextAreaField}
    form_template = EDIT_TEMPLATE
    form_extra_fields = {
        "logo_image": ImageUploadField(
            "Логотип",
            base_path=os.path.join("app", "static", "uploads", "brands"),
            relative_path="brands/",
            url_relative_path="static/uploads/brands/"
        )
    }

# --- News Admin ---
class NewsAdmin(SecureModelView):
    form_overrides = {"body_text": TextAreaField}
    form_template = EDIT_TEMPLATE
    form_extra_fields = {
        "image": ImageUploadField(
            "Изображение новости",
            base_path=os.path.join("app", "static", "uploads", "news"),
            relative_path="news/",
            url_relative_path="static/uploads/news/"
        )
    }

# --- Certificate Admin ---
class CertificateAdmin(SecureModelView):
    form_overrides = {"description": TextAreaField}
    form_template = EDIT_TEMPLATE
    form_extra_fields = {
        "image": ImageUploadField(
            "Изображение сертификата",
            base_path=os.path.join("app", "static", "uploads", "certificates"),
            relative_path="certificates/",
            url_relative_path="static/uploads/certificates/"
        )
    }

# --- Banner Admin ---
class BannerAdmin(SecureModelView):
    form_overrides = {
        "title": TextAreaField,
        "description": TextAreaField
    }
    form_template = EDIT_TEMPLATE
    form_extra_fields = {
        "image": ImageUploadField(
            "Изображение баннера",
            base_path=os.path.join("app", "static", "uploads", "banners"),
            relative_path="banners/",
            url_relative_path="static/uploads/banners/"
        )
    }

# --- Company Admin ---
class CompanyAdmin(SecureModelView):
    form_overrides = {
        "mission": TextAreaField,
        "vision": TextAreaField,
        "address": TextAreaField
    }
    form_template = EDIT_TEMPLATE

# --- Инициализация админки ---
def create_admin(app):
    admin = Admin(
        app,
        name="Админка",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView()
    )
    admin.add_view(CompanyAdmin(Company, db.session))
    admin.add_view(ProductAdmin(Product, db.session))
    admin.add_view(SecureModelView(ProductCategory, db.session))
    admin.add_view(BrandAdmin(Brand, db.session))
    admin.add_view(NewsAdmin(News, db.session))
    admin.add_view(CertificateAdmin(Certificate, db.session))
    admin.add_view(BannerAdmin(Banner, db.session))
    admin.add_view(SecureModelView(ContactMessage, db.session))
    admin.add_view(SecureModelView(NewsletterSubscriber, db.session))
    admin.add_view(SecureModelView(AdminUser, db.session))
    return admin
