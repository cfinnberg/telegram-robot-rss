import sqlite3
from util.filehandler import FileHandler
from util.datehandler import DateHandler as dh
import json


class DatabaseHandler(object):

    def __init__(self, database_path):

        self.database_path = database_path
        self.filehandler = FileHandler(relative_root_path="..")

        if not self.filehandler.file_exists(self.database_path):
            sql_command = self.filehandler.load_file("resources/setup.sql")

            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.executescript(sql_command)
            conn.commit()
            conn.close()

    def add_user(self, telegram_id, username, firstname, lastname, language_code, is_bot, is_active):
        """Adds a user to sqlite database

        Args:
            param1 (int): The telegram_id of a user.
            param2 (str): The username of a user.
            param3 (str): The firstname of a user.
            param4 (str): The lastname of a user.
            param5 (str): The language_code of a user.
            param6 (str): The is_bot flag of a user.
        """

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("INSERT OR IGNORE INTO user VALUES (?,?,?,?,?,?,?)",
                       (telegram_id, username, firstname, lastname, language_code, is_bot, is_active))

        conn.commit()
        conn.close()

    def remove_user(self, telegram_id):
        """Removes a user to sqlite database

        Args:
            param1 (int): The telegram_id of a user.
        """

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user WHERE telegram_id=?", (telegram_id,))

        conn.commit()
        conn.close()

    def update_user(self, telegram_id, **kwargs):
        """Updates a user to sqlite database

        Args:
            param1 (int): The telegram_id of a user.
            param2 (kwargs): The attributes to be updated of a user.
        """

        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        sql_command = "UPDATE user SET "
        for key in kwargs:
            sql_command += f"{key} ='{kwargs[key]}', "
        sql_command = sql_command[:-2] + f" WHERE telegram_id={telegram_id}"

        cursor.execute(sql_command)

        conn.commit()
        conn.close()

    def get_user(self, telegram_id):
        """Returns a user by its id

        Args:
            param1 (int): The telegram_id of a user.

        Returns:
            list: The return value. A list containing all attributes of a user.
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()

        conn.commit()
        conn.close()

        return result

    def add_url(self, url, items):
        """Add URL to database

        Args:
            url (string): URL to add
            items (dict): A dictionary containing the items from the given feed.
                          Dictionary in the form: { 'Item_hash': {'active': True/False, 'last_date': Str}, ...}
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("INSERT OR IGNORE INTO web (url, last_updated, items) VALUES (?,?,?)",
                       (url, dh.get_datetime_now(), json.dumps(items)))

        conn.commit()
        conn.close()

    def remove_url(self, url):
        """Remove URL to database

        Args:
            url (string): URL to be removed
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        sql_command = "DELETE FROM web_user WHERE url=?;"
        cursor.execute(sql_command, (url,))

        sql_command = "DELETE FROM web WHERE web.url NOT IN (SELECT web_user.url from web_user)"
        cursor.execute(sql_command)

        conn.commit()
        conn.close()

    def get_all_urls(self):
        """Return all URLs

        Args:
            None

        Returns:
            list: A list containing every URL
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        sql_command = "SELECT url FROM web;"

        cursor.execute(sql_command)
        result = cursor.fetchall()

        conn.commit()
        conn.close()

        return result

    def get_url_items(self, url):
        """Return saved items from a feed identified by URL

        Args:
            url (string): URL of the feed

        Returns:
            Dict: A dictionary containing the saved items from the given feed or empty dict if empty.
                  Dictionary in the form: { 'Item1_hash': {'active': True/False, 'last_date': Str}, ...}
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT items FROM web WHERE url=?;", (url,))
        result = cursor.fetchone()

        conn.commit()
        conn.close()

        if result:
            return json.loads(result[0])
        else:
            return dict()

    def update_url_items(self,url,items):
        """Update the saved items from a feed identified by URL

        Args:
            url (string): URL of the feed
            items (dict): A dictionary containing the saved items from the given feed or empty dict if empty.
                          Dictionary in the form: { 'Item1_hash': {'active': True/False, 'last_date': Str}, ...}

        Returns:
            None
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE web SET items=? WHERE url=?;", (json.dumps(items), url))

        conn.commit()
        conn.close()        

    def add_user_bookmark(self, telegram_id, url, alias):
        """Add a user bookmark

        Args:
            telegram_id (int): Telegram ID of the user
            url (string): URL of the feed to add (URL must be already saved in web -table)
            alias (string): Name/Alias of the feed for this user

        Returns:
            None
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        #self.add_url(url)  # add if not exists
        cursor.execute("INSERT OR IGNORE INTO web_user VALUES (?,?,?)",
                       (url, telegram_id, alias))

        conn.commit()
        conn.close()

    def remove_user_bookmark(self, telegram_id, url):
        """Remove a user bookmark. Remove also from the URL table if there is no more bookmarks with this URL

        Args:
            telegram_id (int): Telegram ID of the user
            url (string): URL of the bookmark to be removed from this user

        Returns:
            None
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM web_user WHERE telegram_id=? AND url = ?", (telegram_id, url))
        cursor.execute(
            "DELETE FROM web WHERE web.url NOT IN (SELECT web_user.url from web_user)")

        conn.commit()
        conn.close()

    def update_user_bookmark(self, telegram_id, url, alias):
        """Update a user bookmark.

        Args:
            telegram_id (int): Telegram ID of the user
            url (string): URL of the bookmark to be updated from this user
            alias (string): New name/alias of the feed for this user

        Returns:
            None
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute("UPDATE web_user SET alias='?' WHERE telegram_id=? AND url=?", (alias, telegram_id, url))

        conn.commit()
        conn.close()

    def get_user_bookmark(self, telegram_id, alias):
        """Get a user bookmark from the alias

        Args:
            telegram_id (int): Telegram ID of the user
            alias (string): Name/alias of the feed to get for this user

        Returns:
            URL (String): URL of the feed identified with alias for this user
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT url FROM web_user WHERE telegram_id =? AND alias =?;", (telegram_id, alias))

        result = cursor.fetchone()

        conn.commit()
        conn.close()

        return result

    def get_urls_for_user(self, telegram_id):
        """Get a user's URLs

        Args:
            telegram_id (int): Telegram ID of the user

        Returns:
            List: List of [url, alias] of this user.
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT url, alias FROM web_user WHERE telegram_id =?;", (telegram_id,))

        result = cursor.fetchall()

        conn.commit()
        conn.close()

        return result

    def get_users_for_url(self, url):
        """Get users and user's data for a given URL

        Args:
            URL (String): URL to search for

        Returns:
            List: 
        """        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()

        sql_command = "SELECT user.*, web_user.alias FROM user, web_user WHERE web_user.telegram_id = user.telegram_id " + \
                      "AND web_user.url =? AND user.is_active = 1;"

        cursor.execute(sql_command, (url,))
        result = cursor.fetchall()

        conn.commit()
        conn.close()

        return result
