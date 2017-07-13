import news_api_client as client

def test_basic():
    news = client.getNewsFromSources()
    for new in news:
        if new['source'] == 'bbc-news':
            print new
    # print news
    assert len(news) > 0

    news = client.getNewsFromSources(sources = ['bloomberg'])
    # print news
    assert len(news) > 0

    print "test_basic passed."

if __name__ == "__main__":
    test_basic()