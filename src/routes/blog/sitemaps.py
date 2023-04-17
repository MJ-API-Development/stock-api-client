from datetime import datetime

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
