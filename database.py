import sqlite3

dbName = "orders.db"

def get_connection():
    """
    Create and returns a connection with the SQLite database
    The property 'row_factory' allow to access columns by the name
    """

    connection = sqlite3.connect(dbName)
    connection.row_factory = sqlite3.Row
    return connection

def init_dataBase():
    """
    initialize the data base with the collumn 'orders'
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_in TEXT DEFAULT (datetime('now', 'localtime'))
        )
        '''
    )

    connection.commit()
    connection.close()
    print("Data Base initialized")
