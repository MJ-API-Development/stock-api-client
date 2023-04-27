from flask import Blueprint
from src.main import sitemap

sitemap_bp = Blueprint('sitemap', __name__)


@sitemap.register_generator
def generate_sitemap():
    yield 'home.home', {}
    yield 'contact.contact', {}
    yield 'auth.login', {}
    yield 'plan.plan_by_name', {'plan_name': 'basic'},
    yield 'plan.plan_by_name', {'plan_name': 'professional'},
    yield 'plan.plan_by_name', {'plan_name': 'business'},
    yield 'plan.plan_by_name', {'plan_name': 'enterprise'},
    yield 'docs.redoc', {}
    yield 'docs.openapi_json', {}
    yield 'docs.openapi_html', {}
    yield 'docs.documentations', {'path': 'exchanges'},
    yield 'docs.documentations', {'path': 'fundamentals'},
    yield 'docs.documentations', {'path': 'financial-news'},
    yield 'docs.documentations', {'path': 'eod'},
    yield 'blog.sitemap', {}
    yield 'blog.blog', {}
    yield 'blog.load_top_stories', {}
    yield 'blog.financial_news', {'country': 'meme'},
    yield 'blog.financial_news', {'country': 'us'},
    yield 'blog.financial_news', {'country': 'canada'},
    yield 'blog.financial_news', {'country': 'brazil'}
    yield 'home.status', {}
    yield 'home.terms_of_use', {}
    yield 'home.privacy_policy', {}


@sitemap_bp.route('/sitemap.xml', methods=['GET'])
def sitemap_xml():
    return sitemap.sitemap()
