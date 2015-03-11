__author__ = 'Jungsik Choi'

class Syscall:
    def __init__(self, _line, _tid, _time, _name, _args_list, _return_value):
        self.line = _line
        self.tid = _tid
        self.time = _time
        self.name = _name
        self.args_list = _args_list
        self.return_value = _return_value

    def get_line(self):
        return self.line

    def get_time(self):
        return self.time

class OpenSyscall(Syscall):
    def __init__(self, _line, _tid, _time):
        Syscall.__init__(self, _line, _tid, _time, 'open')

    def set_fd(self, _fd):
        self.fd = _fd

    def get_fd(self):
        return self.fd

    def set_path(self, _path):
        self.path = _path

    def get_path(self):
        return self.path

    def set_oflag(self, _oflag):
        self.oflag = _oflag

    def get_oflag(self):
        return self.oflag
