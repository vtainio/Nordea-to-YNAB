import sqlite3

DATABASE_NAME = 'nordea_to_ynab.db'


def prepare_tables(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS category (category_id text primary key not null, name text)')
    cursor.execute('CREATE TABLE IF NOT EXISTS payment (name text primary key not null, category_id text, FOREIGN KEY(category_id) REFERENCES category(category_id))')


def get_db_connection():
    conn = get_sqlite_connection()
    c = conn.cursor()
    prepare_tables(c)
    return conn, c


def get_sqlite_connection():
    return sqlite3.connect(DATABASE_NAME)


def store_categories(categories):
    conn, c = get_db_connection()

    for category in categories:
        c.execute("INSERT OR REPLACE INTO category VALUES (?, ?)", (category.id, category.name))

    conn.commit()
    conn.close()


def get_subcategory_for_transaction(transaction):
    conn, c = get_db_connection()

    existing_category_id = c.execute("SELECT category_id FROM payment WHERE name=?", transaction.target)
    if not existing_category_id:
        category_id = get_subcategory_from_user(transaction.target)

    conn.commit()
    conn.close()

def get_subcategory_from_user(cursor, target):
    categories = cursor.execute("SELECT * FROM category")
    print categories

