from abc import ABCMeta, abstractmethod
import csv


class BaseHandler(metaclass=ABCMeta):

    @abstractmethod
    def on_up(self, result):
        pass

    @abstractmethod
    def on_down(self, result):
        pass


class StdoutHandler(BaseHandler):

    def on_up(self, result):
        print('{} is ok...'.format(result.uri))

    def on_down(self, result):
        print('{} is down!'.format(result.uri))


class CsvHandler(BaseHandler):

    def __init__(self, fp, time_format=None, date_format=None):
        self.csv = csv.writer(fp)
        self.csv.writerow(('URI', 'OK?', 'Date', 'Time'))
        self.date_format = date_format or '%w-%d-%Y'
        self.time_format = time_format or '%I:%M%p'

    def _on_something(self, result):
        self.csv.writerow((result.uri,
                           result.ok,
                           result.time.strftime(self.date_format),
                           result.time.strftime(self.time_format)))

    def on_up(self, result):
        return self._on_something(result)

    def on_down(self, result):
        self._on_something(result)
