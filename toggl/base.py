import iso8601
from datetime import date, datetime

__all__ = ['ObjectList', 'Object', 'cached_property']


class ObjectList(object):

    get_instance_cls = None
    url = None # For __iter__
    url2 = None # For __getitem__

    def __init__(self, api, url=None):
        if url is not None:
            self.url = url
        self.api = api
        self._instance_cache = {}

    def list(self):
        return list(self)

    def __iter__(self):
        if self.url is None:
            raise StopIteration

        if not hasattr(self, '_datalist'):
            self._datalist = self.api.session.get(self.url)

        for data in self._datalist:
            yield self.get_instance_cls()(self.api, **data)

    def refresh(self):
        '''
        Read current list from Toggl
        '''
        self._datalist = self.api.session.get(self.url)

    def get(self, object_id):
        return self[object_id]

    def __getitem__(self, object_id):
        if self.url2 is None:
            raise AttributeError('URL is not set')

        if object_id not in self._instance_cache:
            data = self.api.session.get('%s/%d' % (self.url2, object_id))
            if data and 'data' in data and data['data'] is not None:
                self._instance_cache[object_id] = \
                    self.get_instance_cls()(self.api, **data['data'])
            else:
                raise IndexError("%s with id %d doesn't exist" % \
                    (self.get_instance_cls().__name__, object_id))

        return self._instance_cache[object_id]

    def create(self, **kwargs):
        obj = self.get_instance_cls()(self.api, **kwargs)
        obj.save()
        self._instance_cache[obj.id] = obj
        return obj


class Object(object):

    def __init__(self, api, **kwargs):
        self.api = api
        self.id = None
        self._update_attrs(kwargs)

    def _update_attrs(self, attrs):
        try:
            iteritems = dict.items # Python 3
        except AttributeError:
            iteritems = dict.iteritems # Python 2

        for k, v in iteritems(attrs):
            try:
                v = iso8601.parse_date(v)
                attrs[k] = v
            except iso8601.iso8601.ParseError:
                pass
        self.__dict__.update(attrs)

    def _serialize_attrs(self, attrs):
        data = {}
        for k, v in attrs.items():
            if k in ['api']:
                continue
            if isinstance(v, date): # Date or datetime
                if isinstance(v, datetime):
                    # Send to Toggl
                    v = v.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                else:
                    v = v.strftime('%Y-%m-%d')
            data[k] = v
        return data

    def _serialize_attrs2(self, attrs):
        data = {}
        for k, v in attrs.items():
            if k in ['api']:
                continue
            if isinstance(v, date): # Date or datetime
                if isinstance(v, datetime):
                    # Get from Toggl
                    v = v.strftime('%Y-%m-%dT%H:%M:%S%z')
                    if len(v) == 24 and v[22:] == '00':
                        v = v[:22] + ':' + v[22:]
                else:
                    v = v.strftime('%Y-%m-%d')
            data[k] = v
        return data

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return str(self.name)

    def get_instance_url(self):
        return None

    def get_instance_data(self, data):
        return data

    def to_dict(self, data):
        return data

    def to_serialized_dict(self):
        return self.to_dict(self._serialize_attrs(self.__dict__))

    def delete(self):
        url = self.get_instance_url()
        if not url:
            raise IndexError("%s can't be deleted", self.__class__.__name__)
        self.api.session.delete(url)

    def save(self):
        data = self.to_dict(self._serialize_attrs(self.__dict__))
        data = self.get_instance_data(data)
        url = self.get_instance_url()

        #if self.id:
            #response = self.api.session.put(url, data)
        #else:
            #response = self.api.session.post(url, data)
        response = self.api.session.post(url, data)

        if response and 'data' in response and response['data'] is not None:
            self._update_attrs(response['data'])

        return self


def cached_property(fn):
    cache_name = '_' + fn.__name__ + '_cache'
    def wrapper(self):
        if not hasattr(self, cache_name):
            setattr(self, cache_name, fn(self))
        return getattr(self, cache_name)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return property(wrapper)
