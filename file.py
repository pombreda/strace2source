__author__ = 'Jungsik Choi'

class File:
    def __init__(self, _fd, _path, _oflag):
        self.fd = _fd
        self.path = _path
        self.oflag = _oflag
        self.offset = 0
        self.access_history = []

class Manager:
    def __init__(self, translate):
        self.opened_files_dic = {}
        self.traslate = translate

    def add_file(self, syscall, new_file):
        key = str(syscall.tid) + str(new_file.fd)

        if key not in self.opened_files_dic:
            self.opened_files_dic[key] = new_file
        else:
            self.traslate.log('[Exception] There is a redundant key in opened_files_dic')

    def sub_file(self, syscall):
        pass


