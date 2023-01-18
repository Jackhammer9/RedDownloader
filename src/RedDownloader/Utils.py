import logging

class Logger:

    def __init__(self, verbose=True):
        self.verbose = verbose

    def LogInfo(self, text):
        if self.verbose == True:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
            logging.info(text)
        else:
            logging.basicConfig(format="%(levelname)s: %(message)s")

    def LogError(self, text):
        if self.verbose == True:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.ERROR)
            logging.error(text)
        else:
            logging.basicConfig(format="%(levelname)s: %(message)s")

    def LogWarning(self, text):
        if self.verbose == True:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
            logging.warning(text)
        else:
            logging.basicConfig(format="%(levelname)s: %(message)s")

    def SetVerbose(self, boo):
        self.verbose = boo

    def GetVerbose(self):
        return self.verbose
