"""
are_you_up.py

Python code to make sure a website is up.

"""
import requests
from datetime import datetime
from time import sleep


class Result(object):
    """

    """

    def __init__(self, response):
        self.response = response
        self.ok = response.status_code == requests.codes.ok
        self.uri = response.url
        self.time = datetime.now()


class BaseChecker(object):
    """

    """

    def __init__(self, uris, sleep_time, handler):
        self.uris = uris
        self.sleep_time = sleep_time
        self.handler = handler

    def run(self, should_run):

        while should_run(self):
            for result in self.check():
                if result.ok:
                    self.handler.on_up(result)
                else:
                    self.handler.on_down(result)

            self.sleep()

    def sleep(self):
        sleep(self.sleep_time)

    def check(self):
        return map(self.handle_uri, self.uris)

    def handle_uri(self, u):
        return Result(requests.get(u))


class Checker(BaseChecker):
    pass
