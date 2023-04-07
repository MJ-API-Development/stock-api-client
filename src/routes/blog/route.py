import itertools
import os
from pprint import pprint

import markdown
import requests
from flask import render_template, request, send_from_directory, Blueprint

from src.config import config_instance
from src.main import github_blog
from src.routes.blog.github import submit_sitemap_to_google_search_console

github_blog_route = Blueprint('blog', __name__)


@github_blog_route.route('/blog', methods={"GET"})
def blog():
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
    return render_template('blog/blog_post.html', document=html_content)


@github_blog_route.route('/blog/top-stories', methods=['GET'])
def load_top_stories():
    """
        using our financial news API
        display a list of top stories
    :return:
    """
    tickers = ['MSFT']

    _top_stories = [get_financial_news_by_ticker(stock_code=ticker) for ticker in tickers]
    top_stories = itertools.chain(*_top_stories)
    created_stories = []
    for story in top_stories:
        good_image_url: str = select_resolution(story.get('thumbnail', []))
        new_story = {
            'title': story.get('title').title(),
            'publisher': story.get('publisher').title(),
            'datetime_published': story.get('datetime_published'),
            'link': story.get('link'),
            'related_tickers': story.get('related_tickers', []),
            'thumbnail_url': good_image_url,
        }
        created_stories.append(new_story)

    # sort stories by date published in ascending order
    created_stories = sorted(created_stories, key=lambda k: k['datetime_published'])

    return render_template('blog/top_stories.html', stories=created_stories)


@github_blog_route.route('/blog/<path:blog_path>', methods=["GET"])
def blog_post(blog_path: str):
    # convert the blog URL to the corresponding GitHub URL
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _url = f"{scheme}{request.host}{request.path}"
    # get the content of the blog post
    content = github_blog.get_blog_file(url=_url)
    if content is None:
        return render_template('blog/404.html', message=_url), 404
    html_content = markdown.markdown(content)
    # process the content to replace any links to images and other resources with links to the static directory
    # content = process_content(content)

    # render the content as HTML and return it
    return render_template('blog/blog_post.html', document=html_content)


# route to serve static files (e.g., images) from the blog
@github_blog_route.route('/blog/static/<path:file_path>')
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
    response = submit_sitemap_to_google_search_console(sitemap_url)
    return github_blog.sitemap()


@github_blog_route.route('/blog/sidebar', methods=['GET'])
def create_sidebar():
    sidebar = github_blog.create_sidebar_menu()
    for key, value in sidebar.items():
        print(f"{key} {value}")
    return 'OK', 200


def get_financial_news_by_ticker(stock_code: str) -> list[dict[str, str]]:
    """

    : param stock_code (str): ticker symbol for the company you want to fetch the news for
    """

    url = f'https://gateway.eod-stock-api.site/api/v1/news/articles-by-ticker/{stock_code}'
    headers = {
        'Content-Type': 'application/json'
    }

    params = {'api_key': config_instance().EOD_STOCK_API_KEY}
    response = requests.get(url, headers=headers, params=params)

    if response.headers['Content-Type'] != 'application/json':
        raise Exception

    response_data: dict[str, str | dict] = response.json()

    if not response_data['status']:
        raise Exception(response_data['message'])

    return response_data['payload']


def select_resolution(thumbnals: list[dict[str, int | str]]) -> str:
    # Access the resolutions of the thumbnail image
    thumbnail_resolutions = thumbnals['resolutions']

    # Sort the resolutions by height in descending order
    sorted_resolutions = sorted(thumbnail_resolutions, key=lambda x: x['height'], reverse=True)

    # Select the resolution with the highest height (which is the first element after sorting)
    highest_resolution = sorted_resolutions[0]

    # Access the URL of the image with the highest resolution
    highest_resolution_url = highest_resolution['url']
    return highest_resolution_url
