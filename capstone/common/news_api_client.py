import requests
from json import loads

NEWS_API_KEY = "908dea5d81f349c2a0f4eca79c5efc87"
NEWS_API_ENDPOINT = "https://newsapi.org/v1/"
ARTICLES_API = "articles"

DEFAULT_SOURCES = ['cnn', 'bbc-news']
SORT_BY_TOP = 'top'

def buildUrl(end_point = NEWS_API_ENDPOINT, api_name = ARTICLES_API):
    return end_point + api_name

def getNewsFromSources(sources = [DEFAULT_SOURCES], sortBy = SORT_BY_TOP):
    articles = []
    for source in sources:
        payload = {'apiKey': NEWS_API_KEY,
                   'source': source,
                   'sortBy': sortBy}
        response = requests.get(buildUrl(), params = payload)
        res_json = loads(response.content)

        # Extract news from response
        if (res_json is not None and
            res_json['status'] == "ok" and
            res_json['source'] is not None):
            # Populate news source in each article
            for news in res_json['articles']:
                news['source'] = res_json['source']

            # Add all articles from response using 'extend'
            articles.extend(res_json['articles'])

    return articles