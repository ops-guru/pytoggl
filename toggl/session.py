import requests
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
import logging
import json

from .error import Error

log = logging.getLogger(__name__)

class Session(object):

    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (api_token, 'api_token')
        self.session.headers['content-type'] = 'application/json'

    def _exec(self, method, url, *args, **kwargs):
        try:
            log.debug("[req]: %s?%s [data: %s]" % (self.base_url + url,
                urlencode(kwargs.get('params', {})), kwargs.get('data')))
            if method == self.session.post:
                print("_exec", self.base_url + url, args, kwargs)
                response = method(self.base_url + url, data=json.dumps(kwargs))
                print("response", response.status_code, response.text)
            else:
                #print("_exec", self.base_url + url, args, kwargs)
                response = method(self.base_url + url, *args, **kwargs)
                #print("response", response.status_code, response.text)
            log.debug("[resp %d]: %s" % (response.status_code,
                repr(response.text)))
        except Exception as ex:
            log.debug("[err]: %s" % str(ex))
            raise Error(str(ex))

        if (response.status_code // 100) != 2:
            raise Error(response=response)

        try:
            return response.json()
        except Exception as ex:
            log.debug("[err]: error parsing JSON response: " + str(ex))
            raise Error(str(ex))

    def get(self, url, **params):
        return self._exec(self.session.get, url, params=params)

    def post(self, url, data):
        return self._exec(self.session.post, url, **data)

    #def put(self, url, data):
        #return self._exec2(self.session.put, url, data=json.dumps(data))

    def delete(self, url):
        return self._exec(self.session.delete, url)
