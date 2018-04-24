import feedparser
import re
from urllib.parse import urlparse


class FeedHandler(object):

    @staticmethod
    def parse_feed(url, entries=0):
        """
        Parses the given url, returns a list containing all available entries
        """

        if 1 <= entries <= 10:
            feed = feedparser.parse(url)
            return feed.entries[:entries]
        else:
            feed = feedparser.parse(url)
            return feed.entries[:4]

    @staticmethod
    def is_parsable(url):
        """
        Checks wether the given url provides a news feed. Return True if news are available, else False
        """

        parsed_url = urlparse(url)
        if (parsed_url.scheme != "http" and parsed_url.scheme != "https") or not parsed_url.netloc or not parsed_url.path:
            return False

        feed = feedparser.parse(url)

        if feed['bozo']:
            if type(feed['bozo_exception']) == 'urllib.error.URLError':         # No connection to site
                return False
            # Check JSON Feed
            return False    # For now just not supported, so return False

        return True
