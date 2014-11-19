from abc import ABCMeta, abstractmethod
import csv
import logging
from datetime import datetime


class BaseHandler(metaclass=ABCMeta):

    @abstractmethod
    def on_up(self, result):
        pass

    @abstractmethod
    def on_down(self, result):
        pass


class StdOutHandler(BaseHandler):

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


class LogHandler(BaseHandler):

    def __init__(self, logger=None):
        self.logger = logger or logging

    def on_up(self, result):
        return self.logger.info('{} was up at {}'.format(result.uri, result.time))

    def on_down(self, result):
        return self.logger.warning('{} was down at {}'.format(result.uri, result.time))


class DeltaHandler(BaseHandler):

    def __init__(self, time_delta, logger=None):
        self.d = time_delta
        self._alert_times = {}
        self.logger = logger

    def _should_alert_error_for(self, uri):
        last_alert = self._alert_times.get(uri)
        return last_alert is None or (datetime.now() - last_alert) >= self.d

    def alert(self, result):
        self._alert_times[result.uri] = datetime.now()
        return self

    def on_down(self, result):
        """
        When a service is down the subscriber will be alerted.
        We only alert once every d delta so that the subscriber
        will not be annoyed and has time to respond.

        """

        if self.logger is not None:
            self.logger.warn('{} was down'.format(result.uri))

        if self._should_alert_error_for(result.uri):
            self.alert(result)

        return self

    def on_up(self, result):
        raise NotImplementedError('This handler only takes care of down alerts.')


class EmailHandler(DeltaHandler):

    def __init__(self, email_address, time_delta, subscriber, logger=None):
        super().__init__(time_delta, logger=logger)
        self.email_address = email_address
        self.c = subscriber

    def format_subject(self, result):
        raise NotImplementedError('Need to format the subject')

    def format_body(self, result):
        raise NotImplementedError('Need to format the body')

    def alert(self, result):
        super().alert(result)

        if self.logger is not None:
            self.logger.info('Sending email alert.')

        # generate what will be sent to the subscriber
        subject = self.format_subject(result)
        content = self.format_body(result)

        # send the email alerting that the website is down
        return self.c.send(self.email_address, subject, content)

    def on_up(self, result):
        """
        We don't care when the website is up so we don't do anything.
        """
        if self.logger is not None:
            self.logger.info('{} is up'.format(result.uri))

        return self


class DefaultEmailHandler(EmailHandler):
    EMAIL_SUBJECT = '{} is down'

    EMAIL_BODY_TEMPLATE = 'URL:    {}\n' \
                          'Status: {}\n' \
                          'Reason: {}'

    def format_subject(self, result):
        return self.EMAIL_SUBJECT.format(result.uri)

    def format_body(self, result):
        return self.EMAIL_BODY_TEMPLATE.format(result.uri, result.response.status_code, result.response.content)
