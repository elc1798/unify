"""
Sharing memory between concurrent gunicorn workers is too much of a hassle, so
it's easier to just store shared data inside a database.

This is a helper class to make shared data access more abstract.
"""

import sqlite3
import os

this_path = os.path.realpath(__file__)
this_dir = os.path.dirname(this_path)

CONFIG = {
    "PROJECT_DB_NAME" : this_dir + os.path.sep + "shared_data.db",
    "TABLES" : {
        "messages" : {
            "contents" : "TEXT"
        },
        "sessions" : {
            "key" : "TEXT"
        }
    }
}

class Connection:
    """
    Class to simplify executing SQL queries
    """

    def __init__(self, db_name):
        """
        Sets up the SQLite3 connection and cursor variable
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def execute(self, *args):
        """
        Executes an SQLite3 command and returns the return value, if any
        """
        self.cursor.execute(*args)
        self.conn.commit()
        return self.cursor.fetchall()

    def __del__(self):
        """
        Destroys the internal variables of this class
        """
        # print "CALLING DELETE ON CONNECTION"
        self.conn.close()
        del self.cursor
        del self.conn

class DatabaseVerifier:

    def __init__(self, db_name):
        self.conn = Connection(db_name)
        self.execute = self.conn.execute

    def are_tables_set_up(self):
        """
        Returns True if for all keys in CONFIG["TABLES"] the following conditions
        are satisfied:
            If an entry in CONFIG["TABLES"] is True, it must exist in the database
            If an entry in CONFIG["TABLES"] is False, it must not exist in the
            database
        False otherwise
        """

        retval = True

        for table in CONFIG["TABLES"]:
            if type(CONFIG["TABLES"]) == dict:
                retval = retval and ( len(self.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,)
                )) == 1 )
            else:
                print("ERROR: CONFIG[TABLES] contains invalid value")
                return False

        return retval

    def set_up_tables(self):
        """
        Creates database tables based on entries in CONFIG["TABLES"]

        Returns True if tables are successfully created, False otherwise
        """

        for table in CONFIG["TABLES"]:
            try:
                print "Creating table", table, "..."
                create = "CREATE TABLE %s " % (table,)
                table_setup = []
                for tkey in CONFIG["TABLES"][table]:
                    table_setup.append("%s %s" % (tkey, CONFIG["TABLES"][table][tkey]))

                query = "%s ( %s );" % (create, ", ".join(table_setup))
                self.execute(query)
            except:
                raise
                return False

        return True

    def drop_tables(self):
        """
        Drops all database tables based on entries in CONFIG["TABLES"]

        Returns True if table was successfully deleted, False otherwise
        """

        for table in CONFIG["TABLES"]:
            try:
                query = "DROP TABLE IF EXISTS %s;" % (table,)
                self.execute(query)
            except:
                raise
                return False

    def __del__(self):
        # print "CALLING DELETE ON DatabaseVerifier"
        self.execute = None
        del self.execute

class UnifyDB:

    def __init__(self):
        self.conn = DatabaseVerifier(CONFIG["PROJECT_DB_NAME"])
        if not self.conn.are_tables_set_up():
            print "Tables are not set up!"
            self.conn.drop_tables()
            self.conn.set_up_tables()
        self.execute = self.conn.execute

    def add_message(self, message):
        self.execute("INSERT INTO messages VALUES ( ? );", (message,))

    def delete_messages(self):
        self.execute("DELETE FROM messages;")

    def get_messages(self):
        retval = self.execute("SELECT * FROM messages;")
        self.delete_messages()
        return map(lambda l: str(l[0]), retval) if retval is not None else None

    def add_user_auth(self, name):
        self.execute("INSERT INTO sessions VALUES ( ? );", (name,))

    def revoke_user_auth(self, name):
        self.execute("DELETE FROM sessions WHERE key=?;", (name,))

    def check_user_auth(self, name):
        return len(self.execute("SELECT * FROM sessions WHERE key=?;", (name,))) > 0

    def get_authed_users(self):
        retval = self.execute("SELECT * FROM sessions;")
        return map(lambda l: str(l[0]), retval) if retval is not None else None

    def __del__(self):
        # print "CALLING DELETE ON UNIFYDB"
        self.execute = None
        del self.execute

if __name__ == "__main__":
    test = UnifyDB()
    test.add_message("test 1")
    test.add_message("test 2")
    print test.get_messages()
    test.add_message("test 3")
    test.add_message("test 4")
    print test.get_messages()
    test.add_user_auth("ethan")
    print test.get_authed_users()
    print test.check_user_auth("ethan")
    test.revoke_user_auth("ethan")
    print test.check_user_auth("ethan")

