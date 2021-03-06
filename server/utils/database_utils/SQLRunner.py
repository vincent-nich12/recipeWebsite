
"""
This class is used to run SQL statements
and return their results
"""
class SQLRunner:

    """
    Create the object
    """
    def __init__(self, db_conn):
        self.db_conn = db_conn
        
    """
    Run a list of SQL statements and return the result, it automatically commits 
    the changes (if its not a SELECT command) and returns the result as a list of rows.
    """
    def run_scripts(self, sql_strings: list, values: list):
        all_rows = []
        for x in range(len(sql_strings)):
            all_rows.append(self.run_script(sql_strings[x],values[x]))
        return all_rows
        
    """
    Function run in run_scripts to run a single SQL statement.
    """
    def run_script(self, sql_string: str, values: list):
        self.db_conn.cur.execute(sql_string,values)
        rows = None
        if not ("SELECT" in sql_string):
            self.db_conn.commit_changes()
        else:
            rows = self.db_conn.cur.fetchall()
        return rows
