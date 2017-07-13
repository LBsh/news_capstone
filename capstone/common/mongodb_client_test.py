import mongodb_client as client

def test_basic():
    db = client.get_db('test')
    db.test.drop()
    assert db.test.count() == 0
    db.test1.insert({'test3': 1})
    assert db.test1.count() == 1
    db.testtest.insert({'ttttt': 2})
    # db.test.drop()
    # assert db.test.count() == 0
    print 'test_basic passed.'

if __name__ == "__main__":
    test_basic()