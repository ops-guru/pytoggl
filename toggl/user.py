from .base import ObjectList, Object

__all__ = ['UserList', 'User']


class UserList(ObjectList):
    get_instance_cls = lambda self: User
    url = 'users'
    url2 = 'users'

    def __getitem__(self, object_id):

        if object_id not in self._instance_cache:
            if not hasattr(self, '_datalist'):
                self.refresh(self)
            for item in self._datalist:
                if item['id'] == object_id:
                    self._instance_cache[object_id] = \
                        self.get_instance_cls()(self.api, **item)
                    break
        if object_id not in self._instance_cache:
            raise IndexError("%s with id %d doesn't exist" %
                (self.get_instance_cls().__name__, object_id))

        return self._instance_cache[object_id]


class User(Object):

    @property
    def name(self):
        return self.fullname

    def get_instance_url(self):
        return 'signups'

    def get_instance_data(self, data):
        return {"user":data}

