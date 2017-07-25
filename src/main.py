from __future__ import print_function
import os
import sys
import csv
import datetime
from progress.bar import Bar

from pynYNAB.ClientFactory import clientfromargs
from pynYNAB.schema.budget import Transaction, Payee

from src.database import store_categories
from src.database import get_subcategory_for_transaction
from src.models import NordeaTransaction

def process_file(filepath):
    nordea_transactions = []
    with open(filepath, 'r') as transactions_file:
        reader = csv.reader(transactions_file, delimiter='\t', quotechar='|')

        for row in reader:
            if len(row) < 4:
                continue
            processed_row = process_row(row)
            if processed_row:
                nordea_transactions.append(processed_row)

        return nordea_transactions


def process_row(row):
    outflow = row[3][0] == '-'  # Check if the transaction is negative.
    if outflow:
        return NordeaTransaction(row)


def run(args):
    file_path = 'transactions/%s' % args.file
    if not os.path.isfile(file_path):
        print("Error: No such file exists (%s)" % file_path)
        sys.exit()

    nordea_transactions = process_file(file_path)
    push_transactions(nordea_transactions, args)


def get_ynab_transaction(nordea_transaction, account_id, subcategory_id, payee_id):
    imported_date = datetime.datetime.now().date()
    splitted_amount = nordea_transaction.amount.split(",")
    return Transaction(
        entities_account_id=account_id,
        amount=float("-%s.%s" % (splitted_amount[0], splitted_amount[1])),
        date=datetime.datetime.strptime(nordea_transaction.date, "%d.%m.%Y"),
        imported_date=imported_date,
        entities_subcategory_id=subcategory_id,
        entities_payee_id=payee_id,
        source="Imported"
    )


def find_existing_payee(name, payees):
    for payee in payees:
        if payee.name == name:
            return payee
    return None


def create_new_payee(name):
    return Payee(name=name.decode('utf-8'))


def push_transactions(nordea_transactions, args):
    print("******** FETCHING DATA FROM YNAB ********")
    client = clientfromargs(args)
    client.sync()

    with client.session.no_autoflush:
        account = None
        for be_account in client.budget.be_accounts:
            if be_account.account_name == 'Checking':
                account = be_account
                break

        if not account:
            print("Could not find checking account")
            sys.exit()

        store_categories(client.budget.be_subcategories)
        new_transactions = []
        new_payees = []

        for nordea_transaction in nordea_transactions:
            subcategory_id = get_subcategory_for_transaction(nordea_transaction)
            payee = find_existing_payee(nordea_transaction.target, client.budget.be_payees)
            if payee is None:
                for new_payee in new_payees:
                    if new_payee.name == nordea_transaction.target:
                        payee = new_payee
                if payee is None:
                    payee = create_new_payee(nordea_transaction.target)
                    new_payees.append(payee)
            new_transaction = get_ynab_transaction(nordea_transaction, account.id, subcategory_id, payee.id)
            new_transactions.append(new_transaction)

        print("\n\n******** SENDING DATA TO YNAB ********\n\n")
        print("Pushing new payees:\n")

        for new_payee in new_payees:
            client.budget.be_payees.append(new_payee)
        client.push(len(new_payees))

        print("Done...\n")
        print("Syncing...\n")
        client.sync()

        bar = Bar('Sending transactions', max=len(new_transactions))
        for transaction in new_transactions:
            client.add_transaction(transaction)
            bar.next()

        bar.finish()
        client.sync()
        print("******** DONE ********")
