import requests
import yaml
import os
from json import loads

NEWS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config/news.yaml')

with open(NEWS_CONFIG_FILE, 'r') as newsCfg:
    news_config = yaml.load(newsCfg)

def buildUrl(end_point = news_config['news_api_endpoint'], api_name = news_config['articles_api']):
    return end_point + api_name

def getNewsFromSources(sources, sortBy = news_config['sort_by']):
    articles = []
    for source in sources:
        payload = {'apiKey': news_config['news_api_key'],
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