import os

from src.main import process_file

FINNISH_FIXTURE = "%s/fixtures/finnish.txt" % os.path.dirname(os.path.realpath(__file__))


# One of the fields is positive and the application doesn't currently take it into account, therefore the
# expected length of processed transactions is 2.
def test_finnish_version():
    transactions = process_file(FINNISH_FIXTURE)
    assert len(transactions) == 2
