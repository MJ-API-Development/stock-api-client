from datetime import datetime

import requests

from src.config import config_instance
from src.routes.blog.tickers import get_meme_tickers, get_meme_tickers_us, get_meme_tickers_canada, \
    get_meme_tickers_brazil


def create_financial_news_sitemap(country: str = None) -> str:
    """
    :param country:
    :return:
    """
    if country == "meme":
        meme_tickers = get_meme_tickers()
        tickers = [symbol for symbol, name in meme_tickers.items()]
        urls = [f"https://eod-stock-api.site/blog/financial-news/meme?ticker={ticker}" for ticker in tickers]
    elif country.casefold() == 'us':
        meme_tickers = get_meme_tickers_us()
        tickers = [symbol for symbol, name in meme_tickers.items()]
        urls = [f"https://eod-stock-api.site/blog/financial-news/us?ticker={ticker}" for ticker in tickers]
    elif country.casefold() == "canada":
        meme_tickers = get_meme_tickers_canada()
        tickers = [symbol for symbol, name in meme_tickers.items()]
        urls = [f"https://eod-stock-api.site/blog/financial-news/canada?ticker={ticker}" for ticker in tickers]

    elif country.casefold() == "brazil":
        meme_tickers = get_meme_tickers_brazil()
        tickers = [symbol for symbol, name in meme_tickers.items()]
        urls = [f"https://eod-stock-api.site/blog/financial-news/brazil?ticker={ticker}" for ticker in tickers]
    else:
        meme_tickers = get_meme_tickers()
        tickers = [symbol for symbol, name in meme_tickers.items()]
        urls = [f"https://eod-stock-api.site/blog/financial-news/meme?ticker={ticker}" for ticker in tickers]

    names = [name for symbol, name in meme_tickers.items()]

    # create the sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url, name in zip(urls, names):
        sitemap += f'<url>\n'
        sitemap += f'  <loc>{url}</loc>\n'
        sitemap += f'  <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap += f'  <changefreq>hourly</changefreq>\n'
        sitemap += f'</url>\n'
    sitemap += '</urlset>'

    return sitemap


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
