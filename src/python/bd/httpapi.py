from __future__ import annotations

from typing import TYPE_CHECKING

from bd.config import APIConfig
import requests
from requests.auth import HTTPBasicAuth
from threading import Thread
import json

if TYPE_CHECKING:
    from typing import Dict

# что-то я подумал сколько тут делать и передумал
# class BombDashAPI:
#     def __init__(self, login, password, url='https://bombdash.net/api/'):
#         self.url = url
#         self.auth = HTTPBasicAuth(login, password)
#         self.baseurl = url
#
#     def _request(self, method_name, **kwargs):
#         response = requests.get(method='POST', url=f'{self.baseurl}{method_name}', auth=self.auth)
#         # if response.status_code == 200:
#         return response.json()
#
#     def account_verify(self, id: str, profiles: Dict[str, Dict]):
#         response = self._request('account.verify', id=id, profiles=profiles)
#         return AccountVerifyResponse(**response)


def _make_request(url, auth, method_name, kwargs) -> Dict:
    response = requests.post(url=f'{url}{method_name}', auth=auth, data=json.dumps(kwargs),
                             headers={'Content-Type': 'Application/JSON'})
    # if response.status_code == 200:
    return response.json()


class Request:
    def __init__(self, baseurl, auth, method):
        self.baseurl = baseurl
        self.auth = auth
        self.method = method

    def __call__(self, in_thread=False, **kwargs) -> Dict:
        print(f'CALL {self.method}')
        if in_thread:
            thread = Thread(target=_make_request,
                            args=(self.method, kwargs,))
            thread.start()
        else:
            return _make_request(self.baseurl, self.auth, self.method, kwargs)

    def __getattr__(self, method) -> Request:
        return Request(
            self.baseurl,
            self.auth,
            (self.method + '.' if self.method else '') + method)


class BombDashAPI:
    """Allows access to API methods.

    To use:
    >>> api = BombDashAPI(login=..., password=...)
    >>> api.player.get(id='pb-IF4RUFYT')
    {...}
    """

    def __init__(self, login, password, url='https://bombdash.net/api/'):
        self.url = url
        self.auth = HTTPBasicAuth(login, password)
        self.baseurl = url

    def __getattr__(self, method) -> Request:
        return Request(
            self.baseurl,
            self.auth,
            method)


sharedapi = BombDashAPI(login=APIConfig.USER, password=APIConfig.PASSWORD)
