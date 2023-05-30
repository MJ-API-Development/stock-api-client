from flask import Blueprint, jsonify, request

from src.logger import init_logger
from src.routes.blog.route import stories_slug_uid_pair, get_story_with_uuid
from src.tweeter.tweeter import send_to_tweeter

tweet_route = Blueprint('tweet', __name__)
tweet_logger = init_logger('tweet_logger')
# ONE HOUR Timeout
CACHE_TIMEOUT = 60 * 60 * 3


@tweet_route.route('/_admin/redis/active-articles-list', methods=['GET'])
def get_active_articles():
    """
        **get_active_articles**

    :return:
    """
    articles = [get_story_with_uuid(uuid).get('payload', {}) for slug, uuid in stories_slug_uid_pair.items()]
    _payload = dict(status=True, payload=articles, message='successfully retrieved active articles')
    return jsonify(_payload)


@tweet_route.route('/_admin/send-tweet', methods=['POST'])
def send_tweet():
    """
        **send_tweet**
    :return:
    """
    payload: dict[str, str] = request.json()
    response = send_to_tweeter(tweet=payload)
    if response.status == [200, 201]:
        _payload = dict(status=True, payload={}, message="successfully sent tweet")
    _payload = dict(status=False, payload={}, message="Error sending tweet")
    return jsonify(_payload)

