from datetime import date

import requests
from flask import render_template, Response
from github import Github
from markdown import markdown

from src.config import config_instance


class GithubBlog:
    """

    """

    def __init__(self):
        self.token = config_instance().GITHUB_SETTINGS.GITHUB_BLOG_TOKEN
        self.github = Github(self.token)
        self.repo = self.github.get_repo(config_instance().GITHUB_SETTINGS.BLOG_REPO)
        self.blog_files = {}
        self.ignore_files = ['readme.md', '.gitignore', 'license']
        self.github_url = 'https://raw.githubusercontent.com/MJ-API-Development/eod-api-blog/main/'
        self.blog_url = 'https://eod-stock-api.site/blog/' if config_instance().SERVER_NAME.startswith('eod-stock-api.site') else "http://eod-stock-api.local:8081/blog/"

    def blog_pages(self):
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

    def blog_directories(self, directory=""):
        blog_files = {}
        contents = self.repo.get_contents(directory)
        for content_file in contents:
            if content_file.type == "dir":
                # If the content file is a directory, recursively call this method
                subdir_files = self.blog_directories(content_file.path)
                blog_files[content_file.name] = subdir_files
            else:
                # If the content file is a file, add it to the dictionary of blog files
                file_name = content_file.name
                if file_name.casefold() not in self.ignore_files:
                    file_url = content_file.download_url
                    if file_url not in blog_files:  # Check if the file URL has already been added
                        blog_files[file_url] = file_name

        return blog_files

    def sitemap(self):
        """
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
        sitemap_content = render_template('blog/sitemap.xml', pages=folders, root_url=self.blog_url,
                                          formatted_date=date.today().isoformat())
        return Response(sitemap_content, mimetype='application/xml')

    def get_blog_file(self, url):
        """
            Returns the content of the blog file corresponding to the given URL
        """
        print(url)
        url = f"{self.swap_to_github_url(url)}"
        response = requests.get(url)
        _found_url = self.locate_url(_url=url, blog_urls=self.blog_files)
        if _found_url is not None:
            print("url found")
            file_name = self.blog_files[_found_url]
            content_file = self.repo.get_contents(file_name)
            return content_file.decoded_content.decode('utf-8')
        else:
            print("url not found : {}".format(url))
            for dir_name, files in self.blog_files.items():

                _found_url = self.locate_url(_url=url, blog_urls=files)
                if _found_url is not None:
                    print("found in directories")
                    file_name = files[_found_url]
                    content_file = self.repo.get_contents(dir_name + "/" + file_name)
                    return content_file.decoded_content.decode("utf-8")
            return None
        # print(url)
        # return markdown(response.content.decode('utf-8'))

    @staticmethod
    def locate_url(_url: str, blog_urls: dict[str, str]) -> str:
        for blog_url, value in blog_urls.items():
            print(blog_url)
            if blog_url.startswith(_url):
                return blog_url
        return None

    def swap_to_blog_url(self, url: str) -> str:
        """ given a github url change to blog url"""
        _url = url.replace(self.github_url, self.blog_url) if url.startswith(self.github_url) else f"{self.blog_url}{url}"
        return _url.split("?")[0]

    def swap_to_github_url(self, url: str) -> str:
        if url.startswith(self.blog_url):
            return url.replace(self.blog_url, self.github_url)
        return None
