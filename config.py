SOURCES = [
    {
        "name": "Finextra",
        "url": "https://www.finextra.com/rss/headlines.aspx",
        "kind": "rss",
    },
    {
        "name": "UK Finance",
        "url": "https://www.ukfinance.org.uk/news-and-insight",
        "kind": "html",
        "article_path_prefix": "/news-and-insight/",
    },
    {
        "name": "Tech.eu",
        "url": "https://tech.eu/feed/",
        "kind": "rss",
    },
]


OPPORTUNITY_CATEGORIES = {
    "Independent hedging": [
        "hedging",
        "hedge exposure",
        "currency risk",
        "fx risk",
        "fx hedging",
        "interest rate risk",
        "foreign exchange exposure",
        "hedging strategy",
        "risk hedging",
    ],

    "Derivatives structuring / consulting": [
        "derivatives",
        "derivative contracts",
        "structured products",
        "structured derivatives",
        "interest rate swap",
        "currency swap",
        "swaps",
        "options strategy",
        "derivatives structuring",
    ],

    "Illiquid financing solutions": [
        "private credit",
        "illiquid assets",
        "illiquid financing",
        "asset-backed financing",
        "asset-based lending",
        "structured financing",
        "special situations financing",
        "distressed debt",
        "real estate debt",
        "structured credit",
    ],

    "Capital raising": [
        "capital raising",
        "capital raise",
        "raising capital",
        "funding round",
        "fundraising",
        "fundraise",
        "equity financing",
        "debt financing",
        "private placement",
        "bond issuance",
        "series a",
        "series b",
        "series c",
        "raises £",
        "raises $",
        "raises €",
        "raised £",
        "raised $",
        "raised €",
    ],
}


MAX_ARTICLES_PER_SOURCE = 8

REQUEST_DELAY_SECONDS = 0.8