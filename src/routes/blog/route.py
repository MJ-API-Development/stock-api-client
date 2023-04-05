
import os
import markdown
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
    _url = f"{scheme}://{request.host}{request.path}/index.md"
    # get the content of the blog post
    content = github_blog.get_blog_file(url=_url)
    if content is None:
        return render_template('blog/404.html', message=_url), 404
    html_content = markdown.markdown(content)
    # process the content to replace any links to images and other resources with links to the static directory
    # content = process_content(content)

    # render the content as HTML and return it
    return render_template('blog/blog_post.html', document=html_content)


@github_blog_route.route('/blog/<path:blog_path>', methods=["GET"])
def blog_post(blog_path: str):
    # convert the blog URL to the corresponding GitHub URL
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _url = f"{scheme}://{request.host}{request.path}"
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
