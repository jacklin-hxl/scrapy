import abc

class BaseService(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def login(self):
        pass

    @abc.abstractmethod
    def check_cookie(self,cookie_dict):
        pass