import argparse
import os
import sys
from src.main import run

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
