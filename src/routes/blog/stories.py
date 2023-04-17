import time

storyType = dict[str, float | list[dict[str, str]]]
# ONE HOUR Timeout
CACHE_TIMEOUT = 60 * 60 * 3

stories: dict[str, storyType] = {}


def add_to_stories(_ticker: str, _stories: list[dict[str, str]]) -> list[dict[str, str]]:
    global stories
    stories[_ticker] = {'articles': _stories, 'timestamp': time.monotonic()}


def get_from_stories(_ticker: str) -> list[dict[str, str]]:
    global stories
    story_dict: storyType = stories.get(_ticker, {})
    if not story_dict:
        return []

    now = time.monotonic()
    if now - story_dict.get('timestamp', 0) < CACHE_TIMEOUT:
        return story_dict.get('articles', [])
    return []


def return_any_stories() -> tuple[str, list[dict[str, str]]]:
    global stories
    for ticker, story_dict in stories.items():
        return ticker, story_dict.get('articles', [])
    return None, []
