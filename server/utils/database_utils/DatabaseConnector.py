from utils.common.general_utils import open_file
import psycopg2

"""
This class is for estabilishing the connection to the database.
"""
class DatabaseConnector:
    
    """
    Create the object
    """
    def __init__(self):
       pass
       
    """
    Function for establishing the connection object to the database.
    """
    def _establish_conn(self):
        list = open_file('/root/recipeWebsite/database/databaseUtils/database_access.txt')
        dbname = list[0]
        user = list[1]
        password = list[2]
        connStr = ("dbname = " + dbname +  "user=" + user + " password=" + password)
        conn= psycopg2.connect(connStr)
        self.conn = conn
        
    """
    Function used to get the cursor to the database. The cursor is used
    to apply SQL commands onto the database directly
    """
    def connect(self):
        self._establish_conn()
        cur = self.conn.cursor()
        cur.execute('SET search_path to public')
        self.cur = cur
        
    """
    Function used to check if there still is a connection, and if there is,
    it closes it.
    """
    def close_connection(self):
        if self.conn:
            self.conn.close()
            
    """
    Function used to commit changes if they have been made
    """
    def commit_changes(self):
        self.conn.commit()