import os
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import markdown
import requests
import requests_cache
from flask import render_template, request, send_from_directory, Blueprint, url_for, Response
from src.cache import cached
from src.config import config_instance
from src.logger import init_logger
from src.main import github_blog
from src.routes.authentication.routes import user_details
from src.routes.blog.github import submit_sitemap_to_google_search_console

github_blog_route = Blueprint('blog', __name__)
blog_logger = init_logger('blog_logger')

storyType = dict[str, float | list[dict[str, str]]]

stories: dict[str, storyType] = {}

# ONE HOUR Timeout
CACHE_TIMEOUT = 60 * 60 * 3

blog_requests_session = requests_cache.CachedSession(cache_name='blog_requests_cache', expire_after=CACHE_TIMEOUT)


def get_meme_tickers() -> dict[str, str]:
    """
    Returns a dictionary of ticker symbols and company names for Mexican stocks.
    :return: A dictionary of ticker symbols and company names for Mexican stocks.
    """
    url = "https://finance.yahoo.com/most-active?count=100&offset=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    tickers = {}

    for row in soup.find_all("tbody")[0].find_all("tr"):
        cells = row.find_all("td")
        symbol = cells[0].text.strip()
        name = cells[1].text.strip()
        tickers[symbol] = name

    return tickers


def get_meme_tickers_us() -> dict[str, str]:
    """
    :return:
    """
    return {
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "AMZN": "Amazon.com, Inc.",
        "GOOGL": "Alphabet Inc.",
        "FB": "Meta Platforms, Inc.",
        "NVDA": "NVIDIA Corporation",
        "NFLX": "Netflix, Inc.",
        "TSLA": "Tesla, Inc.",
        "JPM": "JPMorgan Chase & Co.",
        "V": "Visa Inc.",
        "BAC": "Bank of America Corporation",
        "WMT": "Walmart Inc.",
        "JNJ": "Johnson & Johnson",
        "PG": "Procter & Gamble Co.",
        "KO": "The Coca-Cola Company",
        "PEP": "PepsiCo, Inc.",
        "CSCO": "Cisco Systems, Inc.",
        "INTC": "Intel Corporation",
        "ORCL": "Oracle Corporation",
        "AMD": "Advanced Micro Devices, Inc.",
        "PYPL": "PayPal Holdings, Inc.",
        "CRM": "Salesforce.com, Inc.",
        "ATVI": "Activision Blizzard, Inc.",
        "EA": "Electronic Arts Inc.",
        "TTD": "The Trade Desk, Inc.",
        "ZG": "Zillow Group, Inc.",
        "MTCH": "Match Group, Inc.",
        "YELP": "Yelp Inc.",
        "BABA": "Alibaba Group Holding Limited",
        "NKE": "Nike, Inc.",
        "DIS": "The Walt Disney Company",
        "IBM": "International Business Machines Corporation",
        "UNH": "UnitedHealth Group Incorporated",
        "HD": "The Home Depot, Inc.",
        "MMM": "3M Company",
        "GS": "The Goldman Sachs Group, Inc.",
        "AXP": "American Express Company",
        "VZ": "Verizon Communications Inc.",
        "C": "Citigroup Inc.",
        "GE": "General Electric Company",
        "PFE": "Pfizer Inc.",
        "WFC": "Wells Fargo & Company",
        "CVX": "Chevron Corporation",
        "XOM": "Exxon Mobil Corporation",
        "BP": "BP p.l.c.",
        "T": "AT&T Inc.",
        "GM": "General Motors Company",
        "F": "Ford Motor Company"
    }


def get_meme_tickers_canada():
    """
    :return:
    """
    canadian_stocks = {
        'SHOP': 'Shopify Inc.',
        'BNS': 'Bank of Nova Scotia',
        'TD': 'Toronto-Dominion Bank',
        'RY': 'Royal Bank of Canada',
        'BMO': 'Bank of Montreal',
        'ENB': 'Enbridge Inc.',
        'TRP': 'TC Energy Corporation',
        'SU': 'Suncor Energy Inc.',
        'CNQ': 'Canadian Natural Resources Limited',
        'MFC': 'Manulife Financial Corporation',
        'RYAAY': 'Ryanair Holdings plc',
        'FTS': 'Fortis Inc.',
        'CP': 'Canadian Pacific Railway Limited',
        'POT': 'Potash Corporation of Saskatchewan Inc.',
        'CVE': 'Cenovus Energy Inc.',
        'BCE': 'BCE Inc.',
        'TRI': 'Thomson Reuters Corporation',
        'CNTR': 'Contrarian Metal Resources Inc.',
        'WEED': 'Canopy Growth Corporation',
        'MRU': 'Metro Inc.',
        'MG': 'Magna International Inc.',
        'QSR': 'Restaurant Brands International Inc.',
        'HSE': 'Husky Energy Inc.',
        'LNR': 'Lorne Resources Inc.',
        'EMA': 'Emera Incorporated',
        'VET': 'Vermilion Energy Inc.',
        'SLF': 'Sun Life Financial Inc.',
        'GIB.A': 'CGI Inc.',
        'CM': 'Canadian Imperial Bank of Commerce',
        'TECK.A': 'Teck Resources Limited',
        'SNC': 'SNC-Lavalin Group Inc.',
        'TRQ': 'Turquoise Hill Resources Ltd.',
        'IPL': 'Inter Pipeline Ltd.',
        'GIL': 'Gildan Activewear Inc.',
        'CNR': 'Canadian National Railway Company',
        'AEM': 'Agnico Eagle Mines Limited',
        'K': 'Kinross Gold Corporation',
        'EMA.A': 'Emera Incorporated',
        'FNV': 'Franco-Nevada Corporation',
        'YRI': 'Yamana Gold Inc.',
        'PXT': 'Parex Resources Inc.',
        'VII': 'Seven Generations Energy Ltd.',
        'AC': 'Air Canada',
        'IMO': 'Imperial Oil Limited',
        'WFT': 'West Fraser Timber Co. Ltd.',
        'CPG': 'Crescent Point Energy Corp.',
        'MEG': 'MEG Energy Corp.',
        'TOU': 'Tourmaline Oil Corp.',
    }

    return canadian_stocks


def get_meme_tickers_brazil() -> dict[str, str]:
    """

    :return:
    """
    brazilian_stocks = {
        'ABEV3': 'Ambev S.A.',
        'BBAS3': 'Banco do Brasil S.A.',
        'BBDC3': 'Banco Bradesco S.A.',
        'BBDC4': 'Banco Bradesco S.A.',
        'BBSE3': 'BB Seguridade Participações S.A.',
        'BEEF3': 'Minerva S.A.',
        'BIDI11': 'Banco Inter S.A.',
        'BPAC11': 'BTG Pactual Group',
        'BRDT3': 'Petrobras Distribuidora S.A.',
        'BRFS3': 'BRF S.A.',
        'BRKM5': 'Braskem S.A.',
        'BRML3': 'BR Malls Participações S.A.',
        'BTOW3': 'B2W Digital Participações S.A.',
        'CCRO3': 'CCR S.A.',
        'CIEL3': 'Cielo S.A.',
        'CMIG4': 'CEMIG - Companhia Energética de Minas Gerais',
        'CPFE3': 'CPFL Energia S.A.',
        'CRFB3': 'Carrefour Brasil Comércio e Participações S.A.',
        'CSAN3': 'Cosan S.A.',
        'CSNA3': 'Companhia Siderúrgica Nacional',
        'CYRE3': 'Cyrela Brazil Realty S.A.',
        'ECOR3': 'Ecorodovias Infraestrutura e Logística S.A.',
        'EGIE3': 'Engie Brasil Energia S.A.',
        'ELET3': 'Centrais Elétricas Brasileiras S.A. - Eletrobras',
        'ELET6': 'Centrais Elétricas Brasileiras S.A. - Eletrobras',
        'EMBR3': 'Embraer S.A.',
        'ENBR3': 'EDP - Energias do Brasil S.A.',
        'ENEV3': 'Eneva S.A.',
        'EQTL3': 'Equatorial Energia S.A.',
        'EZTC3': 'EZTEC Empreendimentos e Participações S.A.',
        'FLRY3': 'Fleury S.A.',
        'GGBR4': 'Gerdau S.A.',
        'GNDI3': 'Grupo NotreDame Intermédica',
        'GOAU4': 'Metalúrgica Gerdau S.A.',
        'HAPV3': 'Hapvida Participações e Investimentos S.A.',
        'HGTX3': 'Cia. Hering S.A.',
        'HYPE3': 'Hypera S.A.',
        'ITSA4': 'Itaúsa - Investimentos Itaú S.A.',
        'ITUB4': 'Itaú Unibanco Holding S.A.',
        'JBSS3': 'JBS S.A.',
        'KLBN11': 'Klabin S.A.',
        'LAME4': 'Lojas Americanas S.A.',
        'LREN3': 'Lojas Renner S.A.',
        'MGLU3': 'Magazine Luiza S.A.',
        'MRFG3': 'Marfrig Global Foods S.A.',
        'MRVE3': 'MRV Engenharia e Participações S.A.',
        'MULT3': 'Multiplan Empreendimentos Imobiliários S.A.'
    }
    return brazilian_stocks


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


@github_blog_route.route('/blog', methods={"GET"})
@user_details
@cached
def blog(user_data: dict[str, str]):
    # convert the blog URL to the corresponding GitHub URL
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _url = f"{scheme}{request.host}{request.path}/index.md"
    # get the content of the blog post
    content = github_blog.get_blog_file(url=_url)
    if content is None:
        return render_template('blog/404.html', message=_url), 404
    html_content = markdown.markdown(content)
    # process the content to replace any links to images and other resources with links to the static directory
    # content = process_content(content)
    # render the content as HTML and return it
    context = dict(user_data=user_data, document=html_content)
    return render_template('blog/blog_post.html', **context)


@github_blog_route.route('/blog/top-stories', methods=['GET', 'POST'])
@user_details
def load_top_stories(user_data: dict):
    """
    Using our financial news API to display a list of top stories
    """

    DEFAULT_IMAGE_URL = url_for('static', filename='images/placeholder.png')

    meme_tickers = [symbol for symbol in get_meme_tickers().keys()]

    # If the form has been submitted, get the selected ticker symbol
    selected_ticker = request.args.get('ticker', False)

    # Use a set to avoid duplicate stories
    created_stories = []
    uuids = set()

    selected_ticker = selected_ticker or random.choice(meme_tickers)

    for story in get_financial_news_by_ticker(stock_code=selected_ticker):
        # Use dict.get() method with a default value to avoid errors if a key is missing
        # Use a named constant for default image url to improve code readability and usability
        good_image_url = select_resolution(story.get('thumbnail', [])) or DEFAULT_IMAGE_URL
        # Use a uuid to identify each story and avoid duplicates
        uuid = story.get('uuid')
        if uuid not in uuids:
            new_story = {
                'uuid': uuid,
                'title': story.get('title', '').title(),
                'publisher': story.get('publisher', '').title(),
                'datetime_published': story.get('datetime_published'),
                'link': story.get('link', ''),
                'related_tickers': story.get('related_tickers', []),
                'thumbnail_url': good_image_url,
            }
            created_stories.append(new_story)
            uuids.add(uuid)

    created_stories.sort(key=lambda _story: _story['datetime_published'])

    context = dict(stories=created_stories,
                   tickers=get_meme_tickers_us(),
                   selected_ticker=selected_ticker, user_data=user_data)

    add_to_stories(_ticker=selected_ticker, _stories=created_stories)

    return render_template('blog/top_stories.html', **context)


# noinspection DuplicatedCode
@github_blog_route.route('/blog/financial-news/<country>', methods=['GET', 'POST'])
@user_details
def financial_news(user_data: dict, country: str):
    """
    Using our financial news API to display a list of top stories
    """
    DEFAULT_IMAGE_URL = url_for('static', filename='images/placeholder.png')
    country_tickers = dict()
    _introduction = """
                        <h2>Introducing our Financial News API</h2> 
                        <p><strong>Your go-to source for the latest news on the top stocks from around the world.</strong></p> 

                        <p>Whether you're interested in <strong>US Stocks News, Canadian Stock News, Brazil or beyond,</strong> we've got you covered.</p> 

                        <p>With our extensive coverage of the most popular stocks in each country,</p> 
                        you can stay up-to-date on the latest market trends and make informed investment decisions. 

                        <p><strong>Our API delivers Breaking News,</strong> <strong>in-depth analysis,</strong> and <strong>real-time market data,</strong> 
                        so you never miss a beat. 
                        <p>Keep reading for the latest top stock news from our API.</p>
                        
                        <p><strong><a href="http://eod-stock-api.local:8081/#subscription_plans"> If you want to Intergrate our Financial News API into your website or blog please subscribe to obtain your API Key and get started</a></strong></p>         
                    """

    if country.casefold() == "us":
        country_tickers = get_meme_tickers_us()
    elif country.casefold() == "canada":
        country_tickers = get_meme_tickers_canada()

    elif country.casefold() == "brazil":
        country_tickers = get_meme_tickers_brazil()
    else:
        country_tickers = get_meme_tickers()

    meme_tickers = [symbol for symbol in country_tickers.keys()]

    # If the form has been submitted, get the selected ticker symbol
    selected_ticker = request.args.get('ticker', False)

    # Use a set to avoid duplicate stories
    created_stories = []
    uuids = set()

    selected_ticker = selected_ticker or random.choice(meme_tickers)

    for story in get_financial_news_by_ticker(stock_code=selected_ticker):
        # Use dict.get() method with a default value to avoid errors if a key is missing
        # Use a named constant for default image url to improve code readability and usability
        good_image_url = select_resolution(story.get('thumbnail', [])) or DEFAULT_IMAGE_URL
        # Use a uuid to identify each story and avoid duplicates
        uuid = story.get('uuid')
        if uuid not in uuids:
            new_story = {
                'uuid': uuid,
                'title': story.get('title', '').title(),
                'publisher': story.get('publisher', '').title(),
                'datetime_published': story.get('datetime_published'),
                'link': story.get('link', ''),
                'related_tickers': story.get('related_tickers', []),
                'thumbnail_url': good_image_url,
            }
            created_stories.append(new_story)
            uuids.add(uuid)

    created_stories.sort(key=lambda _story: _story['datetime_published'])

    context = dict(stories=created_stories,
                   tickers=country_tickers,
                   _introduction=_introduction,
                   selected_ticker=selected_ticker, user_data=user_data)

    add_to_stories(_ticker=selected_ticker,
                   _stories=created_stories)

    return render_template('blog/top_stories.html', **context)


# noinspection PyUnusedLocal
@github_blog_route.route('/blog/<path:blog_path>', methods=["GET"])
@user_details
@cached
def blog_post(user_data: str, blog_path: str):
    # convert the blog URL to the corresponding GitHub URL
    server_url = config_instance().SERVER_NAME
    scheme = "http://" if "local" in server_url else "https://"
    _path = request.path
    if _path.endswith(".html"):
        _path = _path.replace(".html", ".md")

    _url = f"{scheme}{request.host}{_path}"

    # get the content of the blog post
    content = github_blog.get_blog_file(url=_url)
    if content is None:
        return render_template('blog/404.html', message=_url), 404
    html_content = markdown.markdown(content)
    # process the content to replace any links to images and other resources with links to the static directory
    # content = process_content(content)

    # render the content as HTML and return it
    context = dict(user_data=user_data, document=html_content)
    return render_template('blog/blog_post.html', **context)


# route to serve static files (e.g., images) from the blog
@github_blog_route.route('/blog/static/<path:file_path>')
@cached
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


@github_blog_route.route('/blog/financial-news/<country>/sitemap.xml', methods=['GET'])
def financial_news_sitemap(country: str):
    """
    Creates a sitemap for financial news articles.
    :return: a string representing the sitemap XML.
    """
    # get the list of all the tickers
    sitemap_content = create_financial_news_sitemap(country)
    return Response(sitemap_content, mimetype='application/xml')


@github_blog_route.route('/blog/financial-news/sitemap.xml', methods=['GET'])
def financial_news_meme_sitemap():
    """
    Creates a sitemap for financial news articles.
    :return: a string representing the sitemap XML.
    """
    # get the list of all the tickers
    sitemap_content = create_financial_news_sitemap("meme")
    return Response(sitemap_content, mimetype='application/xml')


@github_blog_route.route('/_admin/blog/update-blog', methods=['GET'])
def check_commits():
    github_blog.check_for_updates()


@github_blog_route.route('/_admin/blog/submit-sitemap', methods=['GET'])
def submit_sitemap():
    blog_sitemap_url = 'https://eod-stock-api.site/blog/sitemap.xml'
    home_sitemap_url = 'https://eod-stock-api.site/sitemap.xml'
    financial_news_us_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/us/sitemap.xml'
    financial_news_canada_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/canada/sitemap.xml'
    financial_news_meme_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/meme/sitemap.xml'
    financial_news_brazil_sitemap_url = 'https://eod-stock-api.site/blog/financial-news/brazil/sitemap.xml'

    _ = submit_sitemap_to_google_search_console(blog_sitemap_url)
    _ = submit_sitemap_to_google_search_console(home_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_us_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_brazil_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_canada_sitemap_url)
    _ = submit_sitemap_to_google_search_console(financial_news_meme_sitemap_url)

    return github_blog.sitemap()


@github_blog_route.route('/blog/sidebar', methods=['GET'])
def create_sidebar():
    sidebar = github_blog.create_sidebar_menu()
    for key, value in sidebar.items():
        print(f"{key} {value}")
    return 'OK', 200


@cached
def get_financial_news_by_ticker(stock_code: str) -> list[dict[str, str]]:
    """
       ** get_financial_news_by_ticker**
        : param stock_code (str): ticker symbol for the company you want to fetch the news for
    """
    url = f'https://gateway.eod-stock-api.site/api/v1/news/articles-by-ticker/{stock_code}'
    headers = {'Content-Type': 'application/json'}
    params = {'api_key': config_instance().EOD_STOCK_API_KEY}

    with requests_cache.CachedSession(cache_name='blog_requests_cache', expire_after=CACHE_TIMEOUT) as session:
        try:
            blog_logger.info(f"get financial searching related articles for symbol : {stock_code}")
            response = session.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            return []
        except requests.exceptions.Timeout:
            return []
        except requests.exceptions.HTTPError:
            return []

    if response.headers['Content-Type'] != 'application/json':
        return []

    response_data: dict[str, str | dict] = response.json()

    if response_data and not response_data.get('status', False):
        return []

    return response_data.get('payload', [])


@cached
def select_resolution(thumbnails: list[dict[str, int | str]]) -> str:
    # Access the resolutions of the thumbnail image
    thumbnail_resolutions = thumbnails['resolutions']

    # Sort the resolutions by height in descending order
    sorted_resolutions = sorted(thumbnail_resolutions, key=lambda x: x['height'], reverse=True)

    # Select the resolution with the highest height (which is the first element after sorting)
    if sorted_resolutions:
        highest_resolution = sorted_resolutions[0]

        # Access the URL of the image with the highest resolution
        highest_resolution_url = highest_resolution['url']
        return highest_resolution_url
    return None


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
