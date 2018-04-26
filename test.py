from util.database import DatabaseHandler
from util.feedhandler import FeedHandler
from util.datehandler import DateHandler
from cityhash import CityHash64

db = DatabaseHandler("resources/datastore.db")

arg_url = 'http://yle.fi/uutiset/rss/paauutiset.rss'

feed=FeedHandler.is_parsable(url=arg_url)

items = {}
for item in feed:
    hash=CityHash64(item['summary']+item['title']+item['link'])
    if (hash in items):
        print(item['link'],item['summary'],items[hash])
    items[hash] = {'active': True, 'last_date': DateHandler.get_datetime_now(), 'link': item['link']}
#self.db.add_url(url=arg_url, items=items)

url_items = db.get_url_items(url=arg_url)
for item in url_items:
        url_items[item]['active'] = False

new_items = []
for item in feed:
    hash=CityHash64(item['summary']+item['title']+item['link'])
    if not(str(hash) in url_items):
        new_items.append(item)
    url_items[hash] = {'active': True, 'last_date': DateHandler.get_datetime_now()}

for item,value in url_items.copy().items():
    if not value['active']:
        url_items.pop(item)

