
from github import Github
from src.config import config_instance


class GithubBlog:
    """

    """
    def __init__(self):
        self.github = Github(config_instance().GITHUB_SETTINGS.GITHUB_BLOG_TOKEN)
        self.repo = self.github.get_repo(config_instance().GITHUB_SETTINGS.BLOG_REPO)

    async def blog_pages(self):
        """
            **blog_pages**
        :return:
        """
        root_contents = self.repo.get_contents("")

        # iterate through the contents of the root directory
        for content_file in root_contents:
            # print the name of each file or directory in the root directory
            print(content_file.name)

            # if the file is a directory, print the names of its contents
            if content_file.type == "dir":
                sub_contents = self.repo.get_contents(content_file.path)
                for sub_file in sub_contents:
                    print("  ", sub_file.name)


