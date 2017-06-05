# Nordea-to-YNAB

This is a simple command line utility for sending transactions exported from [Nordea](https://www.nordea.fi/) (tested with the Finnish version) and sending them directly to [YNAB](https://www.youneedabudget.com/).

### Setting up

Install dependencies with

`pip install -r requirements.txt`

Your YNAB username and password are read from environment variables so you need to export two variables called

`YNAB_USERNAME` and `YNAB_PASSWORD`.

After that you can create a directory called `transactions` and place your exports there.

Then you simply need to call `python run.py --file <your_file_name>` to send the transactions to YNAB.

### Legal

View [LICENSE](https://github.com/Wisheri/Nordea-to-YNAB/blob/master/LICENSE) for detailed information.
