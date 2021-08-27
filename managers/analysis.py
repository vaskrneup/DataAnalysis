import pandas as pd

from data_analyzer.mixins import PercentagePriceChangeMixin
from utils.logger import Logger


class AnalysisManager(PercentagePriceChangeMixin):
    # [{"class": CLASS, "data_identifier": str}]
    EXTRACTOR_CLASSES: list[dict] = []

    def __init__(self):
        self.logger = Logger()

        self.data = {}
        self.runtime_data = {}
        self.test_functions = []

        self.load_data()

    @staticmethod
    def get_successful_message(message):
        return {
            "successful": True,
            "message": message
        }

    @staticmethod
    def get_unsuccessful_message(message):
        return {
            "successful": False,
            "message": message
        }

    def load_data(self):
        for extractor in self.EXTRACTOR_CLASSES:
            self.data[extractor["data_identifier"]] = pd.read_csv(
                extractor["class"].get_data_file_path(extractor["class"])
            )

    def __call__(self, *validation_functions, **kwargs):
        self.runtime_data = kwargs

        if validation_functions:
            self.test_functions = [f"validate_{validation_function}" for validation_function in validation_functions]
        else:
            self.test_functions = [method for method in dir(self) if method.startswith("validate_")]

        for method in self.test_functions:
            self.logger.info(f"Testing '{method.replace('validate_', '')}'")

            method_pointer = getattr(self, method, None)

            if method_pointer is None:
                self.logger.info(f"Test '{method.replace('validate_', '')}' not found, Skipping for now.")
            else:
                test_successful = method_pointer()

                if test_successful["successful"]:
                    self.logger.success(test_successful["message"])
                else:
                    self.logger.error(test_successful["message"])
