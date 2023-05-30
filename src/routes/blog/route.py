import os
import random
import re
import unicodedata

import markdown
import requests
import requests_cache
from flask import render_template, request, send_from_directory, Blueprint, url_for, Response

from src.config import config_instance
from src.logger import init_logger
from src.main import github_blog
from src.routes.authentication.routes import user_details
from src.routes.blog.github import submit_sitemap_to_google_search_console
from src.routes.blog.sitemaps import create_financial_news_sitemap
from src.routes.blog.tickers import (get_meme_tickers, get_meme_tickers_brazil, get_meme_tickers_canada,
                                     get_meme_tickers_us)

github_blog_route = Blueprint('blog', __name__)
blog_logger = init_logger('blog_logger')

# ONE HOUR Timeout
CACHE_TIMEOUT = 60 * 60 * 3

blog_requests_session = requests_cache.CachedSession(cache_name='blog_requests_cache', expire_after=CACHE_TIMEOUT)
stories_slug_uid_pair = dict()


def format_to_html(text: str) -> str:
    """takes text and convert the text html formatting it with paragraphs"""
    return ["".join(f'<p class="text-body">{paragraph}</p>') for paragraph in text.split(". ")][0]


@github_blog_route.route('/blog', methods={"GET"})
@user_details
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


# noinspection DuplicatedCode
@github_blog_route.route('/blog/top-stories', methods=['GET', 'POST'])
@user_details
def load_top_stories(user_data: dict):
    """
    **load_top_stories**
    Using our financial news API to display a list of top stories
    """

    DEFAULT_IMAGE_URL = url_for('static', filename='images/placeholder.png')
    meme_tickers = [symbol for symbol in get_meme_tickers().keys()]
    # If the form has been submitted, get the selected ticker symbol
    selected_ticker = request.args.get('ticker', False)

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
            _slug = slugify(story.get('title'))
            new_story = {
                'uuid': uuid,
                'slug': _slug,
                'title': story.get('title', '').title(),
                'publisher': story.get('publisher', '').title(),
                'datetime_published': story.get('datetime_published'),
                'link': story.get('link', ''),
                'related_tickers': story.get('tickers', []),
                'sentiment': story.get('sentiment', {}),
                'thumbnail_url': good_image_url,
            }
            created_stories.append(new_story)
            uuids.add(uuid)
            stories_slug_uid_pair[_slug] = uuid
    # created_stories.sort(key=lambda _story: _story['datetime_published'])

    context = dict(stories=created_stories,
                   tickers=get_meme_tickers_us(),
                   selected_ticker=selected_ticker, user_data=user_data)

    return render_template('blog/top_stories.html', **context)


# noinspection DuplicatedCode
@github_blog_route.route('/blog/financial-news/tweets/<path:uuid>', methods=['GET'])
@user_details
def get_article_by_uuid(user_data: dict, uuid: str):
    response = get_story_with_uuid(uuid=uuid)
    payload = response.get('payload', {})
    default_image_url = url_for('static', filename='images/placeholder.png')
    good_image_url = select_resolution(payload.get('thumbnail', [])) or default_image_url

    new_story = {
        'uuid': uuid,
        'title': payload.get('title', '').title(),
        'publisher': payload.get('publisher', '').title(),
        'datetime_published': payload.get('datetime_published'),
        'link': payload.get('link', ''),
        'related_tickers': payload.get('tickers', []),
        'sentiment': payload.get('sentiment', {}),
        'thumbnail_url': good_image_url,
    }
    html_body = None
    # will retrieve body_text and test if the text exist
    if body_text := payload.get('sentiment', {}).get('article'):
        html_body = format_to_html(text=body_text)
    context = dict(story=new_story, html_body=html_body, user_data=user_data)
    # noinspection PyUnresolvedReferences
    return render_template("/blog/article.html", **context)


# noinspection DuplicatedCode
@github_blog_route.route('/blog/financial-news/<path:country>', methods=['GET', 'POST'])
@user_details
def financial_news(user_data: dict, country: str):
    """
    Using our financial news API to display a list of top stories
    """
    default_image_url = url_for('static', filename='images/placeholder.png')

    _introduction = """
<div class="card">
<div class="card-header">
        <h2 class="card-title">Introducing our Financial News API</h2>
</div>
 <div class="card-body">
        <p class="text text-body"><strong>Your go-to source for the latest news on the top stocks from around the world.</strong></p> 

        <p class="text text-body">Whether you're interested in <strong>US Stocks News, Canadian Stock News, Brazil or beyond,</strong> we've got you covered.</p> 

        <p class="text text-body">With our extensive coverage of the most popular stocks in each country,</p> 
        you can stay up-to-date on the latest market trends and make informed investment decisions. 

        <p class="text text-body"><strong>Our API delivers Breaking News,</strong> <strong>in-depth analysis,</strong> and <strong>real-time market data,</strong> 
        so you never miss a beat. 
        <p>Keep reading for the latest top stock news from our API.</p>
        
        <p><strong><a href="https://eod-stock-api.site/plan-descriptions/basic"> If you want to <strong>Integrate our Financial News API</strong> into your website or blog please subscribe to obtain your API Key and get started</a></strong></p>
    </div>
    </div>         
"""

    if country.casefold() == "us":
        country_tickers = get_meme_tickers_us()
    elif country.casefold() == "canada":
        country_tickers = get_meme_tickers_canada()
    elif country.casefold() == "brazil":
        country_tickers = get_meme_tickers_brazil()
    else:
        country_tickers = get_meme_tickers()

    meme_tickers = [symbol for symbol in country_tickers.keys()]

    # If the form has been submitted, get the selected ticker symbol
    selected_ticker = request.args.get('ticker', False)

    # Use a set to avoid duplicate stories
    created_stories = []
    uuids = set()

    selected_ticker = selected_ticker or random.choice(meme_tickers)

    for story in get_financial_news_by_ticker(stock_code=selected_ticker):
        # Use dict.get() method with a default value to avoid errors if a key is missing
        # Use a named constant for default image url to improve code readability and usability
        good_image_url = select_resolution(story.get('thumbnail', [])) or default_image_url
        # Use a uuid to identify each story and avoid duplicates
        uuid = story.get('uuid')
        if uuid not in uuids:
            _slug = slugify(story.get('title'))
            new_story = {
                'uuid': uuid,
                'slug': _slug,
                'title': story.get('title', '').title(),
                'publisher': story.get('publisher', '').title(),
                'datetime_published': story.get('datetime_published'),
                'link': story.get('link', ''),
                'related_tickers': story.get('tickers', []),
                'sentiment': story.get('sentiment', {}),
                'thumbnail_url': good_image_url,
            }

            created_stories.append(new_story)
            uuids.add(uuid)
            stories_slug_uid_pair[_slug] = uuid

    # created_stories.sort(key=lambda _story: _story['datetime_published'])

    context = dict(stories=created_stories,
                   tickers=country_tickers,
                   _introduction=_introduction,
                   country=country,
                   selected_ticker=selected_ticker, user_data=user_data)

    return render_template('blog/top_stories.html', **context)


# noinspection DuplicatedCode
@github_blog_route.route('/blog/financial-news/article/<path:slug>', methods=['GET'])
@user_details
def financial_news_article(user_data: dict, slug: str):
    """
    **financial_news_article**

    :param user_data:
    :param slug:
    :return:
    """
    try:
        uuid = stories_slug_uid_pair[slug]
    except KeyError:
        # noinspection PyUnresolvedReferences
        return render_template('/blog/404.html')

    response = get_story_with_uuid(uuid=uuid)
    payload = response.get('payload', {})
    default_image_url = url_for('static', filename='images/placeholder.png')
    good_image_url = select_resolution(payload.get('thumbnail', [])) or default_image_url

    new_story = {
        'uuid': uuid,
        'title': payload.get('title', '').title(),
        'publisher': payload.get('publisher', '').title(),
        'datetime_published': payload.get('datetime_published'),
        'link': payload.get('link', ''),
        'related_tickers': payload.get('tickers', []),
        'sentiment': payload.get('sentiment', {}),
        'thumbnail_url': good_image_url,
    }
    html_body = None
    # will retrieve body_text and test if the text exist
    if body_text := payload.get('sentiment', {}).get('article'):
        html_body = format_to_html(text=body_text)
    context = dict(story=new_story, html_body=html_body, user_data=user_data)
    # noinspection PyUnresolvedReferences
    return render_template("/blog/article.html", **context)


def create_blog_url():
    """

    **create_blog_url**
        will create an internal blog URL
    :return:
    """
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _path = request.path
    if _path.endswith(".html"):
        _path = _path.replace(".html", ".md")
    _url = f"{scheme}{request.host}{_path}"
    return _url


# noinspection PyUnusedLocal
@github_blog_route.route('/blog/<path:blog_path>', methods=["GET"])
@user_details
def blog_post(user_data: str, blog_path: str):
    # convert the blog URL to the corresponding GitHub URL
    _url: str = create_blog_url()

    # get the content of the blog post and assign to content then test if its None
    if content := github_blog.get_blog_file(url=_url) is None:
        return render_template('blog/404.html', message=_url), 404
    # convert the markdown content into html
    html_content: str = markdown.markdown(content)

    # render the content as HTML and return it
    context = dict(user_data=user_data, document=html_content)
    return render_template('blog/blog_post.html', **context)


# route to serve static files (e.g., images) from the blog
@github_blog_route.route('/blog/static/<path:file_path>')
def blog_static(file_path: str):
    """static files will only be images """
    # get the content of the file from GitHub
    content: str = github_blog.get_blog_file(file_path)
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


@github_blog_route.route('/blog/financial-news/<path:country>/sitemap.xml', methods=['GET'])
def financial_news_sitemap(country: str):
    """
    Creates a sitemap for financial news articles.
    :return: a string representing the sitemap XML.
    """
    # get the list of all the tickers
    sitemap_content = create_financial_news_sitemap(country)
    return Response(sitemap_content, mimetype='application/xml')


@github_blog_route.route('/blog/financial-news/sitemap.xml', methods=['GET'])
def financial_news_meme_sitemap():
    """
    Creates a sitemap for financial news articles.
    :return: a string representing the sitemap XML.
    """
    # get the list of all the tickers
    sitemap_content = create_financial_news_sitemap("meme")
    return Response(sitemap_content, mimetype='application/xml')


@github_blog_route.route('/_admin/blog/update-blog', methods=['GET'])
def check_commits():
    github_blog.check_for_updates()


@github_blog_route.route('/_admin/blog/submit-sitemap', methods=['GET'])
def submit_sitemap():
    blog_sitemap_url = 'https://eod-stock-api.site/blog/sitemap.xml'
    home_sitemap_url = 'https://eod-stock-api.site/sitemap.xml'
    financial_news_us_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/us/sitemap.xml'
    financial_news_canada_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/canada/sitemap.xml'
    financial_news_meme_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/meme/sitemap.xml'
    financial_news_brazil_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/brazil/sitemap.xml'

    _ = submit_sitemap_to_google_search_console(blog_sitemap_url)
    _ = submit_sitemap_to_google_search_console(home_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_us_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_brazil_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_canada_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_meme_sitemap_url)

    return github_blog.sitemap()


@github_blog_route.route('/blog/sidebar', methods=['GET'])
def create_sidebar():
    sidebar = github_blog.create_sidebar_menu()
    for key, value in sidebar.items():
        print(f"{key} {value}")
    return 'OK', 200


def get_financial_news_by_ticker(stock_code: str) -> list[dict[str, str]]:
    """
       ** get_financial_news_by_ticker**
        : param stock_code (str): ticker symbol for the company you want to fetch the news for
    """
    url = f'https://gateway.eod-stock-api.site/api/v1/news/articles-by-ticker/{stock_code}'
    headers = {'Content-Type': 'application/json'}
    params = {'api_key': config_instance().EOD_STOCK_API_KEY}

    with requests_cache.CachedSession(cache_name='blog_requests_cache', expire_after=CACHE_TIMEOUT) as session:
        try:
            blog_logger.info(f"Get financial searching related articles for symbol : {stock_code}")
            response = session.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            return []
        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.HTTPError:
            return []

    if response.headers['Content-Type'] != 'application/json':
        return []

    response_data: dict[str, str | dict] = response.json()

    if response_data and not response_data.get('status', False):
        return []

    return response_data.get('payload', [])


def get_story_with_uuid(uuid: str) -> dict[str, str | dict[str, str | int]]:
    """
    **get_story_with_uuid**
        get story with a particular uuid
    :param uuid:
    :return:
    """
    url: str = f'https://gateway.eod-stock-api.site/api/v1/news/article/{uuid}'
    headers: dict[str, str] = {'Content-Type': 'application/json'}
    params: dict[str, str] = {'api_key': config_instance().EOD_STOCK_API_KEY}

    with requests_cache.CachedSession(cache_name='blog_requests_cache', expire_after=CACHE_TIMEOUT) as session:
        try:
            blog_logger.info(f"get financial searching article with uuid : {uuid}")
            response: requests.Response = session.get(url, headers=headers, params=params)
            blog_logger.info("response : {}".format(response.json()))
            response.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return {}
        except requests.exceptions.HTTPError:
            return {}

    if response.headers['Content-Type'] != 'application/json':
        return {}

    response_data: dict[str, str | dict[str, str | int]] = response.json()
    return response_data


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


def slugify(title: str) -> str:
    """create a slug from title"""
    slug = title.lower()
    # Remove non-alphanumeric characters and replace them with dashes
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading and trailing dashes
    slug = slug.strip('-')
    # Normalize the slug to remove any diacritical marks or special characters
    return unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore').decode('utf-8')
