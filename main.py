import argparse
import os
import sys
import csv
import datetime

from pynYNAB.Client import clientfromargs
from pynYNAB.schema.budget import Transaction


class NordeaTransaction(object):
    def __init__(self, row):
        self.date = row[2]
        self.amount = row[3][1:]
        self.target = row[4]


def process_file(filepath):
    nordea_transactions = []
    with open(filepath, 'rb') as transactions_file:
        reader = csv.reader(transactions_file, delimiter='\t', quotechar='|')

        for row in reader:
            if len(row) < 4:
                continue
            processed_row = process_row(row)
            if processed_row:
                nordea_transactions.append(processed_row)

        return nordea_transactions


def process_row(row):
    outflow = False
    if row[3][0] == '-': # Check if the transaction is negative.
        outflow = True
    if outflow:
        return NordeaTransaction(row)


def run(args):
    file_path = 'transactions/%s' % args.file
    if not os.path.isfile(file_path):
        print "Error: No such file exists (%s)" % file_path
        sys.exit()

    nordea_transactions = process_file(file_path)
    push_transactions(nordea_transactions, args)


def get_ynab_transaction(nordea_transaction, account_id):
    imported_date = datetime.datetime.now().date()
    splitted_amount = nordea_transaction.amount.split(",")
    return Transaction(
        entities_account_id=account_id,
        amount=float("-%s.%s" % (splitted_amount[0], splitted_amount[1])),
        date=datetime.datetime.strptime(nordea_transaction.date, "%d.%m.%Y"),
        imported_date=imported_date,
        source="Imported"
    )


def push_transactions(nordea_transactions, args):
    client = clientfromargs(args)
    client.sync()

    account = None
    for be_account in client.budget.be_accounts:
        if be_account.account_name == 'Checking':
            account = be_account
            break

    if not account:
        print "Could not find checking account"
        sys.exit()

    for nordea_transaction in nordea_transactions:
        new_transaction = get_ynab_transaction(nordea_transaction, account.id)
        client.add_transaction(new_transaction)

    client.sync()


if __name__ == '__main__':
    # Parse filename.
    parser = argparse.ArgumentParser(description="TODO write description.")
    parser.add_argument('--file', help='Transactions filename')
    args = parser.parse_args()

    username = os.environ['YNAB_USERNAME']
    password = os.environ['YNAB_PASSWORD']

    if not username:
        print "No YNAB username provided"
        sys.exit()

    if not password:
        print "No YNAB password provided"
        sys.exit()

    if not args.file:
        print "Error: No filename provided"
        sys.exit()

    args.email = username
    args.password = password
    args.budgetname = "My Budget"

    run(args)
