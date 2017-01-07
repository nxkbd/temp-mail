import string
import random
import requests

from hashlib import md5
from urllib.parse import urlunparse


CONST_API_SETTINGS = {
    'api_url_scheme': 'https',
    'api_domain': 'api.temp-mail',
    'top_level_domains': ['org', 'ru']
}


class TempMail:
    def __init__(self, login=None, domain=None, api_top_level_domain='org'):
        self.api_top_level_domain = api_top_level_domain
        if self.api_top_level_domain.lower() not in CONST_API_SETTINGS['top_level_domains']:
            raise ValueError

        self.login = login
        self.domain = domain

    @property
    def available_domains(self):
        path = 'domains'
        if not hasattr(self, '_available_domains'):
            domains = self.__request(path)
            setattr(self, '_available_domains', domains)
        return self._available_domains

    @property
    def email_address(self):
        self.login = self.__random_login() if not self.login else self.login
        self.domain = random.choice(self.available_domains) if not self.domain else self.domain

        if not self.domain.startswith('@'):
            self.domain = '@' + self.domain

        if self.domain not in self.available_domains:
            raise ValueError('Domain not found in available domains')

        email = ''.join((self.login, self.domain))
        setattr(self, '_email_address', email)
        return self._email_address

    @staticmethod
    def __random_login(min_len=6, max_len=20, digits=True):
        chars = string.ascii_letters + string.digits if digits else string.ascii_letters
        return ''.join([random.choice(chars) for i in range(random.randint(min_len, max_len))])

    @staticmethod
    def __md5_hash(string):
        _h = md5(string.encode('utf-8'))
        return _h.hexdigest()

    def __request(self, path):
        response_format = 'format/json'
        api_netloc = '.'.join((CONST_API_SETTINGS['api_domain'], self.api_top_level_domain))
        path = '/'.join(('request', path, response_format))
        url = urlunparse((CONST_API_SETTINGS['api_url_scheme'], api_netloc, path, '', '', ''))
        return requests.get(url).json()

    def get_mailbox(self):
        path = 'mail/id'
        path = '/'.join((path, self.__md5_hash(self.email_address)))
        return self.__request(path)

    def delete_message(self, msg_id):
        msg_id = msg_id.strip()
        if len(msg_id) != 32:
            raise ValueError
        path = 'delete/id'
        path = '/'.join((path, msg_id))
        return self.__request(path)
