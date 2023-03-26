from flask import Blueprint, render_template, redirect, request, jsonify, request
import requests

from src.routes.authentication.routes import get_headers

plan_routes = Blueprint('plan', __name__)


def get_plan_details(plan_id: str) -> dict:
    endpoint = 'https://example.com/plan-details'
    data = {'plan_id': plan_id}
    headers = get_headers(user_data=data)

    # Make a POST request with plan_id in the body as a dict
    response = requests.post(endpoint, headers=headers, json=data)

    # Check if the request was successful and return the response body as a dict
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        # Handle errors
        response.raise_for_status()


@plan_routes.route('/plan-subscription')
def plan_subscription(plan_id: str):
    if not plan_id:
        return redirect('/')

    plan = get_plan_details(plan_id)
    return render_template('dashboard/plan_subscriptions.html', plan=plan)


@plan_routes.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    plan = data['plan']
    # Handle subscription process using PayPal API
    return jsonify({'success': True})
