
import os
import markdown
from flask import render_template, request, send_from_directory, Blueprint
from src.main import github_blog

github_blog_route = Blueprint('blog', __name__)


@github_blog_route.route('/blog/<path:blog_path>')
def blog_post(blog_path):
    # convert the blog URL to the corresponding GitHub URL
    github_url = f"{request.scheme}://{request.host}{request.path}"

    # get the content of the blog post
    content = github_blog.get_blog_file(url=github_url)
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
    github_blog.blog_pages()
    sitemap_content = github_blog.sitemap()
    return sitemap_content
