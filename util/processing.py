# /bin/bash/python/

from telegram.error import (TelegramError, Unauthorized)
from telegram import ParseMode
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread as RunningThread
from util.datehandler import DateHandler
from util.database import DatabaseHandler
from util.feedhandler import FeedHandler
import datetime
import threading
import traceback
from time import sleep
from cityhash import CityHash64


class BatchProcess(threading.Thread):

    def __init__(self, database, update_interval, bot):
        RunningThread.__init__(self)
        self.db = database
        self.update_interval = float(update_interval)
        self.bot = bot
        self.running = True

    def run(self):
        """
        Starts the BatchThreadPool
        """

        while self.running:
            # Init workload queue, add queue to ThreadPool
            url_queue = self.db.get_all_urls()
            self.parse_parallel(queue=url_queue, threads=4)

            # Sleep for interval
            sleep(self.update_interval)

    def parse_parallel(self, queue, threads):
        time_started = datetime.datetime.now()

        pool = ThreadPool(threads)
        pool.map(self.update_feed, queue)
        pool.close()
        pool.join()

        time_ended = datetime.datetime.now()
        duration = time_ended - time_started
        print("Finished updating! Parsed " + str(len(queue)) +
              " rss feeds in " + str(duration) + " !")

    def update_feed(self, url):
        try:
            feed = FeedHandler.parse_feed(url[0])
        except:
            feed = False
            traceback.print_exc() # ???
        
        if feed:
            print(f'{url[0]}:')
            print(f'Longitud de feed: {len(feed)}')
            url_items = self.db.get_url_items(url=url[0])
            for item in url_items:
                 url_items[item]['active'] = False

            new_items = []
            for item in feed:
                hash=str(CityHash64(item['summary']+item['title']+item['link']))
                if not(hash in url_items):
                    new_items.append(item)
                url_items[hash] = {'active': True, 'last_date': DateHandler.get_datetime_now()}

            for item,value in url_items.copy().items():
                if not value['active']:
                    print(f'Desactivando {item}')
                if not value['active'] and DateHandler.is_older_than_days(value['last_date'],5):
                    print(f'Borrando {item}')
                    url_items.pop(item)

            self.db.update_url_items(url=url[0],items=url_items)

        telegram_users = self.db.get_users_for_url(url=url[0])

        for user in telegram_users:
            if user[6]:  # is_active
                if not feed:
                    message = "Something went wrong when I tried to parse the URL: \n\n " + \
                        url[0] + "\n\nCould you please check that for me? Remove the url from your subscriptions using the /remove command, it seems like it does not work anymore!"
                    self.bot.send_message(chat_id=user[0], text=message, parse_mode=ParseMode.HTML)
                    return

                for post in new_items:
                    self.send_message(post=post, user=user)

    def send_message(self, post, user):

        message = "[" + user[7] + "] <a href='" + post.link + "'>" + post.title + "</a>"
        try:
            self.bot.send_message(chat_id=user[0], text=message, parse_mode=ParseMode.HTML)
        except Unauthorized:
            self.db.update_user(telegram_id=user[0], is_active=0)
        except TelegramError:
            # handle all other telegram related errors
            pass

    def set_running(self, running):
        self.running = running
