from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, LoginManager
from flask import redirect, url_for
from .models import (
    db, Product, ProductCategory, Brand, News, Banner, 
    ContactMessage, NewsletterSubscriber, AdminUser, 
    Company, Certificate
)

# login_manager
login_manager = LoginManager()

# Убираем проверку роли, доступ будет открыт всем вошедшим
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))

# Кастомный дашборд
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

def create_admin(app):
    admin = Admin(
        app,
        name="Админка",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView()
    )
    admin.add_view(SecureModelView(Company, db.session))
    admin.add_view(SecureModelView(Product, db.session))
    admin.add_view(SecureModelView(ProductCategory, db.session))
    admin.add_view(SecureModelView(Brand, db.session))
    admin.add_view(SecureModelView(News, db.session))
    admin.add_view(SecureModelView(Certificate, db.session))
    admin.add_view(SecureModelView(Banner, db.session))
    admin.add_view(SecureModelView(ContactMessage, db.session))
    admin.add_view(SecureModelView(NewsletterSubscriber, db.session))
    admin.add_view(SecureModelView(AdminUser, db.session))
    return admin