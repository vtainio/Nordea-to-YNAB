import sqlite3
from tabulate import tabulate

DATABASE_NAME = 'nordea_to_ynab.db'


def prepare_tables(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS category (category_id text primary key not null, name text)')
    cursor.execute('CREATE TABLE IF NOT EXISTS payment (name text primary key not null, category_id text, FOREIGN KEY(category_id) REFERENCES category(category_id))')


def get_db_connection():
    conn = get_sqlite_connection()
    conn.text_factory = str
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

    c.execute("SELECT category_id FROM payment WHERE name=:name", {"name": transaction.target})
    category_id = c.fetchone()

    if not category_id:
        category_id = get_subcategory_from_user(c, transaction.target)
        c.execute("INSERT INTO payment VALUES (?, ?)", (transaction.target, category_id))
    else:
        category_id = category_id[0]  # Get the value from a single element tuple

    conn.commit()
    conn.close()

    return category_id


def get_subcategory_from_user(cursor, target):
    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()
    options = []
    categories_by_name = {}

    for index, category in enumerate(categories):
        category_id, name = category
        categories_by_name[name] = category_id
        options.append([index, name])

    id = prompt_user_for_id(target, options)
    return categories_by_name[options[id][1]]


def prompt_user_for_id(target, options):
    print "No category found for %s. Please select one from below:\n\n" % target
    print tabulate(options, headers=["ID, Name"])
    while True:
        selection = raw_input("Enter the ID of your selection: ")
        if selection.isdigit() and int(selection) >= 0 and int(selection) < len(options):
            break
    return int(selection)
