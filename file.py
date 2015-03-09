__author__ = 'Jungsik Choi'

class File:
    def __init__(self, _fd, _path, _permission):
        self.fd = _fd
        self.path = _path
        self.permission = _permission
        self.offset = 0
        print 'create a file object'