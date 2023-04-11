import os
import random
import time

import markdown
import requests
from flask import render_template, request, send_from_directory, Blueprint, url_for
from src.cache import cached
from src.config import config_instance
from src.logger import init_logger
from src.main import github_blog
from src.routes.authentication.routes import user_details
from src.routes.blog.github import submit_sitemap_to_google_search_console

github_blog_route = Blueprint('blog', __name__)
blog_logger = init_logger('blog_logger')

storyType = dict[str, float | list[dict[str, str]]]

stories: dict[str, storyType] = {}

# ONE HOUR Timeout
CACHE_TIMEOUT = 60 * 60


def add_to_stories(_ticker: str, _stories: list[dict[str, str]]) -> list[dict[str, str]]:
    global stories
    stories[_ticker] = {'articles': _stories, 'timestamp': time.monotonic()}


def get_from_stories(_ticker: str) -> list[dict[str, str]]:
    global stories
    story_dict: storyType = stories.get(_ticker, {})
    now = time.monotonic()
    if now - story_dict.get('timestamp', 0) < CACHE_TIMEOUT:
        return story_dict.get('articles', [])
    return []


def return_any_stories() -> tuple[str, list[dict[str, str]]]:
    global stories
    for ticker, story_dict in stories.items():
        return ticker, story_dict.get('articles', [])
    return None, []


@github_blog_route.route('/blog', methods={"GET"})
@user_details
@cached
def blog(user_data: dict[str, str]):
    # convert the blog URL to the corresponding GitHub URL
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _url = f"{scheme}{request.host}{request.path}/index.md"
    # get the content of the blog post
    content = github_blog.get_blog_file(url=_url)
    if content is None:
        return render_template('blog/404.html', message=_url), 404
    html_content = markdown.markdown(content)
    # process the content to replace any links to images and other resources with links to the static directory
    # content = process_content(content)
    # render the content as HTML and return it
    context = dict(user_data=user_data, document=html_content)
    return render_template('blog/blog_post.html', **context)


@github_blog_route.route('/blog/top-stories', methods=['GET', 'POST'])
@user_details
def load_top_stories(user_data: dict):
    """
    Using our financial news API to display a list of top stories
    """

    DEFAULT_IMAGE_URL = url_for('static', filename='images/placeholder.png')

    meme_tickers = ['AAPL', 'AMZN', 'GOOGL', 'TSLA', 'FB', 'NVDA', 'NFLX', 'MSFT',
                    'JPM', 'V', 'BAC', 'WMT', 'JNJ', 'PG', 'KO', 'PEP', 'CSCO',
                    'INTC', 'ORCL', 'AMD']

    # If the form has been submitted, get the selected ticker symbol

    selected_ticker = request.args.get('ticker', False)
    if not selected_ticker:
        blog_logger.info('No ticker selected')
        ticker, created_stories = return_any_stories()
        if ticker and created_stories:
            blog_logger.info(f'Found Random Story with ticker : {ticker}')
            context = dict(stories=created_stories,
                           tickers=meme_tickers.remove(ticker),
                           selected_ticker=selected_ticker, user_data=user_data)

            return render_template('blog/top_stories.html', **context)
        blog_logger.info('Did not find any random story')

    if selected_ticker:
        blog_logger.info(f'Ticker Was Selected : {selected_ticker}')
        created_stories: list[dict[str, str]] = get_from_stories(_ticker=selected_ticker)
        if created_stories:
            blog_logger.info(f'Found some old articles within the cache timeout : {selected_ticker}')
            context = dict(stories=created_stories,
                           tickers=meme_tickers.remove(selected_ticker),
                           selected_ticker=selected_ticker, user_data=user_data)

            return render_template('blog/top_stories.html', **context)

    # Use a set to avoid duplicate stories
    created_stories = []
    uuids = set()

    selected_ticker = selected_ticker or random.choice(meme_tickers)

    for story in get_financial_news_by_ticker(stock_code=selected_ticker):
        # Use dict.get() method with a default value to avoid errors if a key is missing
        # Use a named constant for default image url to improve code readability and usability
        good_image_url = select_resolution(story.get('thumbnail', [])) or DEFAULT_IMAGE_URL
        # Use a uuid to identify each story and avoid duplicates
        uuid = story.get('uuid')
        if uuid not in uuids:
            new_story = {
                'uuid': uuid,
                'title': story.get('title', '').title(),
                'publisher': story.get('publisher', '').title(),
                'datetime_published': story.get('datetime_published'),
                'link': story.get('link', ''),
                'related_tickers': story.get('related_tickers', []),
                'thumbnail_url': good_image_url,
            }
            created_stories.append(new_story)
            uuids.add(uuid)

    created_stories.sort(key=lambda _story: _story['datetime_published'])

    context = dict(stories=created_stories,
                   tickers=meme_tickers,
                   selected_ticker=selected_ticker, user_data=user_data)

    add_to_stories(_ticker=selected_ticker, _stories=created_stories)

    return render_template('blog/top_stories.html', **context)


# noinspection PyUnusedLocal
@github_blog_route.route('/blog/<path:blog_path>', methods=["GET"])
@user_details
@cached
def blog_post(user_data: str, blog_path: str):
    # convert the blog URL to the corresponding GitHub URL
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _path = request.path
    if _path.endswith(".html"):
        _path = _path.replace(".html", ".md")

    _url = f"{scheme}{request.host}{_path}"

    # get the content of the blog post
    content = github_blog.get_blog_file(url=_url)
    if content is None:
        return render_template('blog/404.html', message=_url), 404
    html_content = markdown.markdown(content)
    # process the content to replace any links to images and other resources with links to the static directory
    # content = process_content(content)

    # render the content as HTML and return it
    context = dict(user_data=user_data, document=html_content)
    return render_template('blog/blog_post.html', **context)


# route to serve static files (e.g., images) from the blog
@github_blog_route.route('/blog/static/<path:file_path>')
@cached
def blog_static(file_path):
    """static files will only be images """
    # get the content of the file from GitHub
    content = github_blog.get_blog_file(file_path)
    # return the file content with appropriate headers
    return send_from_directory(os.path.dirname(file_path), content, as_attachment=False)


@github_blog_route.route('/blog/sitemap.xml', methods=['GET'])
def sitemap():
    """
        Route to serve the sitemap.xml file for the blog
    """
    github_blog.update_blog()
    sitemap_content = github_blog.sitemap()
    return sitemap_content


@github_blog_route.route('/_admin/blog/update-blog', methods=['GET'])
def check_commits():
    github_blog.check_for_updates()


@github_blog_route.route('/_admin/blog/submit-sitemap', methods=['GET'])
def submit_sitemap():
    sitemap_url = 'https://eod-stock-api.site/blog/sitemap.xml'
    _ = submit_sitemap_to_google_search_console(sitemap_url)
    return github_blog.sitemap()


@github_blog_route.route('/blog/sidebar', methods=['GET'])
def create_sidebar():
    sidebar = github_blog.create_sidebar_menu()
    for key, value in sidebar.items():
        print(f"{key} {value}")
    return 'OK', 200


@cached
def get_financial_news_by_ticker(stock_code: str) -> list[dict[str, str]]:
    """
       ** get_financial_news_by_ticker**
        : param stock_code (str): ticker symbol for the company you want to fetch the news for
    """
    url = f'https://gateway.eod-stock-api.site/api/v1/news/articles-by-ticker/{stock_code}'
    headers = {'Content-Type': 'application/json'}
    params = {'api_key': config_instance().EOD_STOCK_API_KEY}

    with requests.Session() as session:
        try:
            blog_logger.info(f"get financial searching related articles for symbol : {stock_code}")
            response = session.get(url, headers=headers, params=params)
            blog_logger.info(f"get financial news found : {response.text}")
        except requests.exceptions.ConnectionError:
            return []
        except requests.exceptions.Timeout:
            return []

    if response.headers['Content-Type'] != 'application/json':
        return []

    response_data: dict[str, str | dict] = response.json()

    if response_data and not response_data.get('status', False):
        return []

    return response_data.get('payload', [])


@cached
def select_resolution(thumbnails: list[dict[str, int | str]]) -> str:
    # Access the resolutions of the thumbnail image
    thumbnail_resolutions = thumbnails['resolutions']

    # Sort the resolutions by height in descending order
    sorted_resolutions = sorted(thumbnail_resolutions, key=lambda x: x['height'], reverse=True)

    # Select the resolution with the highest height (which is the first element after sorting)
    if sorted_resolutions:
        highest_resolution = sorted_resolutions[0]

        # Access the URL of the image with the highest resolution
        highest_resolution_url = highest_resolution['url']
        return highest_resolution_url
    return None
