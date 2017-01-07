import string
import random
import requests

from hashlib import md5
from urllib.parse import urlunparse


CONST_API_SETTINGS = {
    'url_scheme': 'https',
    'domain': 'api.temp-mail',
    'top_level_domains': ['org', 'ru']
}


class TempMail:
    def __init__(self, login=None, domain=None):
        self.login = login
        self.domain = domain

    def __repr__(self):
        return self.email

    @property
    def domain(self):
        return self._domain
    @domain.setter
    def domain(self, domain):
        if domain:
            domain = domain.strip()
            if not domain.startswith('@'):
                domain = ''.join(('@', domain))
            if domain not in sum(self.available_domains.values(), []):
                raise ValueError('Domain not found in available domains')
        else:
            domain = random.choice(sum(self.available_domains.values(), []))

        for api_tld, domains in self.available_domains.items():
            if domain in domains:
                self.api_top_level_domain = api_tld
        self._domain = domain

    @property
    def login(self):
        return self._login
    @login.setter
    def login(self, login):
        self._login = self.random_login() if not login else login.strip()

    @property
    def email(self):
        email = ''.join((self.login, self.domain))
        setattr(self, '_email', email)
        return self._email

    @property
    def available_domains(self):
        path = 'domains'
        if not hasattr(self, '_available_domains'):
            domains = {}
            for val in CONST_API_SETTINGS['top_level_domains']:
                self.api_top_level_domain = val
                domains[val] = self.__request(path)
            setattr(self, '_available_domains', domains)
        return self._available_domains

    @staticmethod
    def random_login(min_len=6, max_len=20, digits=True):
        chars = string.ascii_letters + string.digits if digits else string.ascii_letters
        return ''.join([random.choice(chars) for i in range(random.randint(min_len, max_len))])

    @staticmethod
    def __md5_hash(string):
        _h = md5(string.encode('utf-8'))
        return _h.hexdigest()

    def __request(self, path):
        response_format = 'format/json'
        api_netloc = '.'.join((CONST_API_SETTINGS['domain'], self.api_top_level_domain))
        path = '/'.join(('request', path, response_format))
        url = urlunparse((CONST_API_SETTINGS['url_scheme'], api_netloc, path, '', '', ''))
        return requests.get(url).json()

    def get_mailbox(self):
        path = 'mail/id'
        path = '/'.join((path, self.__md5_hash(self.email)))
        return self.__request(path)

    def delete_message(self, msg_id):
        msg_id = msg_id.strip()
        if len(msg_id) != 32:
            raise ValueError
        path = 'delete/id'
        path = '/'.join((path, msg_id))
        return self.__request(path)
