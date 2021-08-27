class Logger:
    def __init__(self):
        pass

    def log(self, text):  # NOQA
        print(text)

    def error(self, text):
        self.log(text)

    def success(self, text):
        self.log(text)

    def info(self, text):
        self.log(text)
