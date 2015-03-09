__author__ = 'Jungsik Choi'

class Syscall:
    def __init__(self, _line, _tid, _time, _name, _args, _return_value):
        self.line = _line
        self.tid = _tid
        self.time = _time
        self.name = _name
        self.args = _args
        self.return_value = _return_value
