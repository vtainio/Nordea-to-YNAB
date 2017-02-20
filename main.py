import argparse
import settings
import os.path
import sys
import csv

class Transaction(object):
    def __init__(self, row):
        self.date = row[2]
        self.amount = row[3][1:]
        self.target = row[4]


def process_file(filepath):
    transactions = []
    with open(filepath, 'rb') as transactions_file:
        reader = csv.reader(transactions_file, delimiter='\t', quotechar='|')

        for row in reader:
            if len(row) < 4:
                continue
            transactions.append(process_row(row))

def process_row(row):
    outflow = False
    if (row[3][0] == '-'): # Check if the transaction is negative.
        outflow = True
    if outflow:
        return Transaction(row)

def run(filename):
    filepath = 'transactions/%s' % filename
    if not os.path.isfile(filepath):
        print "Error: No such file exists (%s)" % filepath
        sys.exit()

    process_file(filepath)

if __name__ == '__main__':
    # Parse filename.
    parser = argparse.ArgumentParser(description="TODO write description.")
    parser.add_argument('--file', help='Transactions filename')
    args = parser.parse_args()

    if not args.file:
        print "Error: No filename provided"
        sys.exit()

    run(args.file)
