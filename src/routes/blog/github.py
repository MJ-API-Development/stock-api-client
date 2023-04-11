from datetime import date
from urllib.parse import urlparse

import requests
from flask import render_template, Response
from github import Github

from src.cache import cached
from src.config import config_instance
from src.logger import init_logger


def submit_sitemap_to_google_search_console(sitemap_url):
    """
    Submit the sitemap to Google Search Console
    """
    api_endpoint = f"https://www.google.com/ping?sitemap={sitemap_url}"
    # Define the request headers
    headers = {
        'Content-Type': 'application/xml',
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows)',
    }
    params = {'key': config_instance().SEARCH_CONSOLE_API_KEY}
    response = requests.get(api_endpoint, headers=headers, params=params)

    return response


class GithubBlog:
    """
    A class representing a blog hosted on GitHub.
    """

    def __init__(self, github_token, blog_repo, ignore_files=None, github_url=None, blog_url=None):
        """
            Initialize a GithubBlog object.

            Parameters:
            - github_token (str): A personal access token for accessing the GitHub API.
            - blog_repo (str): The name of the GitHub repository containing the blog.
            - ignore_files (list of str, optional): A list of filenames to ignore when fetching blog files.
            - github_url (str, optional): The base URL for the raw GitHub content.
            - blog_url (str, optional): The base URL for the published blog.
        """
        self.token = github_token
        self.github = Github(self.token)
        self.repo = self.github.get_repo(blog_repo)
        self.ignore_files = ignore_files or ['readme.md', '.gitignore', 'license']
        self.github_url = github_url or 'https://raw.githubusercontent.com/MJ-API-Development/eod-api-blog/main/'
        self.blog_url = blog_url or 'https://eod-stock-api.site/blog/'
        self.last_commit_time = None
        self.blog_files = {}
        self._logger = init_logger('github_blog')

    def check_for_updates(self):
        """
        Check if there has been a commit since the last time this method was called.
        """
        latest_commit_time = self.repo.updated_at
        if self.last_commit_time is None or latest_commit_time > self.last_commit_time:
            self.last_commit_time = latest_commit_time
            # Do something if there has been an update
            self.update_blog()
            sitemap_url = f"{self.blog_url}sitemap.xml"
            submit_sitemap_to_google_search_console(sitemap_url)
        else:
            # Do something if there has not been an update
            pass

    @cached
    def fetch_all_blog_files(self):
        """
        Fetch the blog files from the GitHub repository.
        """
        contents = self.repo.get_contents('')
        while contents:
            file_content = contents.pop(0)
            if file_content.type == 'dir':
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                if file_content.name.lower() not in self.ignore_files:
                    self.blog_files[file_content.name] = file_content

    def update_blog(self):
        """
            **blog_pages**
        :return:
        """
        self.blog_files = {}
        blog_files = self.blog_directories()
        # update the self.blog_files dictionary with the new files
        for _key, value in list(blog_files.items()):
            if _key not in [key for key, _ in self.blog_files.items()]:
                self.blog_files[_key] = value

    @cached
    def blog_directories(self, directory=""):
        """
        Recursively searches for blog files in a given directory and its subdirectories,
        and returns a dictionary of file names and URLs.
        """
        blog_files = {}

        # Get the contents of the given directory using the GitHub API
        contents = self.repo.get_contents(directory)

        for content_file in contents:
            if content_file.type == "dir" and not content_file.name.lower().startswith(".idea"):
                # If the content file is a directory, recursively call this method to get its files
                subdir_files = self.blog_directories(content_file.path)
                # Add the subdirectory files to the parent directory's dictionary
                blog_files[content_file.name] = subdir_files
            elif content_file.type == "file":
                # If the content file is a file, check if it's a blog file and add it to the dictionary
                file_name = content_file.name
                file_url = content_file.download_url
                if self._is_blog_file(file_name) and file_url not in blog_files:
                    blog_files[file_url] = file_name

        return blog_files

    def _is_blog_file(self, file_name):
        """
        Checks if a given file name is a valid blog file by checking its extension
        and ensuring it's not in the ignore_files list.
        """
        if not file_name.casefold().endswith(".md"):
            return False
        if file_name.casefold() in self.ignore_files:
            return False
        return True

    @cached
    def sitemap(self):
        """
        **sitemap**
             Generate a sitemap.xml file for the blog
        """
        folders = []
        single_files = []
        for key, value in self.blog_files.items():
            if isinstance(value, dict):
                folders.append({f"{self.swap_to_blog_url(key)}": f"{value}"})
                for _key, _value in value.items():
                    folders.append({f"{self.swap_to_blog_url(_key)}": f"{_value}"})
            else:
                single_files.append({f"{self.swap_to_blog_url(key)}": f"{value}"})

        folders.extend(single_files)
        sitemap = [{key[:-3] + '.html' if key.endswith('.md') else key: value} for folder_dict in folders for key, value
                   in folder_dict.items()]

        sitemap_content = render_template('blog/sitemap.xml', pages=sitemap, root_url=self.blog_url,
                                          formatted_date=date.today().isoformat())

        return Response(sitemap_content, mimetype='application/xml')

    @cached
    def get_blog_file(self, url: str) -> str | None:
        """
            Returns the content of the blog file corresponding to the given URL
        """
        self._logger.info("original url is {}".format(url))
        url = f"{self.swap_to_github_url(url)}"
        _found_url = self._locate_url(_url=url, blog_urls=self.blog_files)
        if _found_url is not None:
            file_name = self.blog_files[_found_url]
            content_file = self.repo.get_contents(file_name)
            return content_file.decoded_content.decode('utf-8')
        else:
            for dir_name, files in self.blog_files.items():
                _found_url = self._locate_url(_url=url, blog_urls=files)

                if _found_url is not None:
                    file_name = files[_found_url]
                    content_file = self.repo.get_contents(dir_name + "/" + file_name)
                    return content_file.decoded_content.decode("utf-8")
            return None

    @staticmethod
    def _locate_url(_url: str, blog_urls: dict[str, str]) -> str | None:
        if not isinstance(blog_urls, dict):
            return
        if not _url.endswith("/") and not _url.endswith(".md"):
            _url += "/"
        _url = _url.casefold()

        for blog_url, value in blog_urls.items():
            if blog_url and blog_url.casefold().startswith(_url):
                suffix = urlparse(blog_url).path[-3:].lower()
                if (suffix == ".md") or (suffix[-1] == "/"):
                    return blog_url
        return

    def swap_to_blog_url(self, url: str) -> str:
        """
        Given a GitHub URL, returns the corresponding URL for the blog.
        """
        if url.startswith(self.github_url):
            return url.replace(self.github_url, self.blog_url).split("?")[0]
        return f"{self.blog_url}{url.split('?')[0]}"

    def swap_to_github_url(self, url: str) -> str:
        """
        Given a blog URL, returns the corresponding URL for GitHub.
        """
        github_url = None
        if url.casefold().startswith(self.blog_url.casefold()):
            github_url = url.replace(self.blog_url, self.github_url)
        return github_url

    def remove_github_url(self, filename: str) -> str:
        return filename.replace(self.github_url, "")

    def create_blog_link(self, directory: str, filename: str) -> str:
        """
        Create a link for a blog post.

        Parameters:
        - directory (str): The name of the directory where the file is located.
        - filename (str): The name of the file.

        Returns:
        - str: The link to the blog post.
        """

        blog_url = 'https://eod-stock-api.site/blog/'
        if directory:
            return f'{blog_url}{directory}/{filename}'
        else:
            _filename = self.remove_github_url(filename)
            return f'{blog_url}{filename}'

    def create_menu(self, links: list[dict]):
        menu = {}

        def remove_blog_link(_self, _link: str) -> str:
            """

            :param _link:
            :param _self:
            :return:
            """
            return _link.replace(_self.blog_url, "")

        for link in links:
            name = remove_blog_link(self, link)

            if name.endswith('.md'):
                # this is a file link
                filename = name
                directory = None
            else:
                parts = name.split("/")
                # this is a directory link
                if len(parts) == 2:
                    filename = parts[1]
                    directory = parts[0]
                else:
                    filename = None
                    directory = parts[0]

            # add the directory to the menu if it doesn't exist yet
            if directory and directory not in menu:
                menu[directory] = {}

            # add the file to the menu
            if directory and filename:
                menu[directory][filename] = link
            else:
                menu[filename] = link

        return menu

    def create_sidebar_menu(self):
        folders = []
        single_files = []
        for key, value in self.blog_files.items():
            if isinstance(value, dict):
                folders.append({f"{self.swap_to_blog_url(key)}": f"{value}"})
                for _key, _value in value.items():
                    folders.append({f"{self.swap_to_blog_url(_key)}": f"{_value}"})
            else:
                single_files.append({f"{self.swap_to_blog_url(key)}": f"{value}"})

        folders.extend(single_files)

        links = []
        for files in folders:
            if isinstance(files, dict):
                for url, name in files.items():
                    links.append(url)
            else:
                links.append(files)

        return self.create_menu(links=links)
