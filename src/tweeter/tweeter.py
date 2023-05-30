import tweepy

from src.config import config_instance
from src.logger import init_logger
from src.utils import camel_to_snake


class CronNewsTwitter:
    """
        will create a cron job from this cron we will access tweets
        from the datastore and send the news as tweets to Twitter
    """
    _twitter_rate_15_min_limit: int = 900

    def __init__(self, exit_on_rate_limit: bool = False):
        self._exit_on_rate_limit = exit_on_rate_limit
        self._tweets_limit = 50
        self._news_limit = 100
        self._task_limit = 150
        self._logger = init_logger(camel_to_snake(self.__class__.__name__))
        self._tweeter_api = self._create_api()
        self.timeout = 1 * 60

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    @staticmethod
    def _get_twitter_user_agent() -> str:
        """
            Find a proper user agent for scrapping twitter and supply here
        :return:
        """
        return f"EOD-STOCK-MARKET-API:version 1.0.0.1"

    def _create_api(self):
        settings = config_instance().TWITTER_SETTINGS
        auth = self.get_authenticated_session(settings)
        # TODO - very important supply cache
        _user_agent = self._get_twitter_user_agent()
        api_args = dict(auth=auth, retry_count=3, retry_delay=60, wait_on_rate_limit=True, user_agent=_user_agent)
        try:
            api = tweepy.API(**api_args)

            if api.verify_credentials():
                return api
        except tweepy.errors.Unauthorized as e:
            self._logger.error(e)

    @staticmethod
    def get_authenticated_session(settings) -> any:
        consumer_key = settings.TWITTER_API_KEY
        consumer_secret = settings.TWITTER_API_SECRET
        access_token = settings.TWITTER_ACCESS_TOKEN
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth

    async def create_tweet(self, tweet: dict[str, str]):
        """
            main method run this from cron
        :return:
        """
        image_link = tweet.get()
        status = tweet.get('tweet')
        media_ids = {}
        if image_link:
            # ensure that one media_id is reused if image already uploaded
            if image_link not in media_ids:
                response = self._tweeter_api.media_upload(image_link)
                media_ids[image_link] = response.media_id
            await self._tweeter_api.update_status(status, media_ids=[media_ids[image_link]])
        else:
            await self._tweeter_api.update_status(status)

