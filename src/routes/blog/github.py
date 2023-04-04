
from github import Github
from src.config import config_instance


class GithubBlog:
    """

    """
    def __init__(self):
        self.github = Github(config_instance().GITHUB_SETTINGS.GITHUB_BLOG_TOKEN)
        self.repo = self.github.get_repo(config_instance().GITHUB_SETTINGS.BLOG_REPO)

    def blog_pages(self):
        """
            **blog_pages**
        :return:
        """
        pass



