import requests
from bs4 import BeautifulSoup


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
