from flask import Blueprint, render_template, send_from_directory

from src.cache import cached
from src.databases.models.schemas.subscriptions import PlanModels
from src.routes.authentication.routes import user_details
from src.routes.subscriptions.plan import get_all_plans

home_route = Blueprint('home', __name__)


def select_plan_by_name(plans_models: list[PlanModels], plan_name: str) -> str:
    """**select_plan_by_name** selects plan by name"""
    selected_plan = [plan for plan in plans_models if plan.plan_name.casefold() == plan_name.casefold()]
    return selected_plan[0] if any(selected_plan) else ""


@cached
def get_plan_models_dicts() -> dict[str, dict[str, str | float]]:
    """
        **get_plan_models_dicts**
        returns dicts for plan models
    :return:
    """
    _plans_models: dict[str, str | dict[str, str]] = get_all_plans()
    plans_models: list[PlanModels] = [PlanModels.parse_obj(plan_dict) for plan_dict in _plans_models.get('payload', {})]
    basic_plan: PlanModels = select_plan_by_name(plans_models=plans_models, plan_name="BASIC")
    enterprise_plan: PlanModels = select_plan_by_name(plans_models=plans_models, plan_name="ENTERPRISE")
    business_plan: PlanModels = select_plan_by_name(plans_models=plans_models, plan_name="BUSINESS")
    professional_plan: PlanModels = select_plan_by_name(plans_models=plans_models, plan_name="PROFESSIONAL")
    plans_models_dict: PlanModels = dict(basic_plan=basic_plan.dict(), enterprise_plan=enterprise_plan.dict(),
                                         business_plan=business_plan.dict(), professional_plan=professional_plan.dict())
    return plans_models_dict


@home_route.route('/')
@user_details
def home(user_data: dict[str, str]):
    plans_models_dict = get_plan_models_dicts()
    context: dict[str, str] = dict(user_data=user_data, total_exchanges=75, BASE_URL="https://eod-stock-api.site",
                                   plans=plans_models_dict)

    return render_template('index.html', **context)


@home_route.route('/status')
@user_details
def status(user_data: dict[str, str]):
    context: dict[str, str] = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('dashboard/status.html', **context)


@home_route.route('/pricing')
@user_details
def pricing(user_data: dict[str, str]):
    context: dict[str, str] = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('index.html', **context)


@home_route.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')


@home_route.route('/Robots.txt')
def _robots():
    return send_from_directory('static', 'robots.txt')


@home_route.route('/terms')
@user_details
def terms_of_use(user_data: dict[str, str]):
    context: dict[str, str] = dict(user_data=user_data, BASE_URL="eod-stock-api.site")
    return render_template('terms.html', **context)


@home_route.route('/privacy')
@user_details
def privacy_policy(user_data: dict[str, str]):
    context = dict(user_data=user_data)
    return render_template('privacy.html', **context)
