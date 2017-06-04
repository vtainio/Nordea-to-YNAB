class NordeaTransaction(object):
    def __init__(self, row):
        self.date = row[2]
        self.amount = row[3][1:]
        self.target = row[4]
