import re
import sys

__author__ = 'Jungsik Choi'

class Syscall:
    def __init__(self, _line, _tid, _time, _name, _args_list, _return_value):
        self.line = _line
        self.tid = _tid
        self.time = _time
        self.name = _name
        self.args_list = _args_list
        self.return_value = _return_value

class File:
    def __init__(self, _fd, _path, _permission):
        self.fd = _fd
        self.path = _path
        self.permission = _permission
        self.offset = 0
        self.access_history = []

class Translate:
    def __init__(self):
        self.logfile = open('strace2source.log', 'w')

    def __del__(self):
        self.logfile.close()

    def log(self, _message):
        message = str(_message) + '\n'
        self.logfile.write(message)

    def open_syscall(self, syscall):
        self.log('[open] ')
        self.log(syscall.args_list)

    def close_syscall(self, syscall):
        self.log('[close] ')
        self.log(syscall.args_list)

def main():
    translate = Translate()
    unfinished_syscall_dic = {}
    interested_syscalls = ['open', 'read', 'pread', 'write', 'pwrite', 'close', 'lseek']

    strace_file_path = raw_input("strace file path? (default: strace/fileserver.strace) : ")
    if strace_file_path == '':
        strace_file_path = 'strace/fileserver.strace'

    dataset_path = raw_input("dataset path? (default: /mnt/tmpfs) : ")
    if dataset_path == '':
        dataset_path = '/mnt/tmpfs'

    buf = raw_input("Do you translate only syscalls associated with the dataset? (default: yes) : ")
    if buf == '':
        buf = 'yes'

    if buf == 'yes':
        only_dataset = 1
    else:
        only_dataset = 0

    # open and read a strace file
    try:
        strace_file = open(strace_file_path, 'r')
    except IOError:
        translate.log("[Exception] I can't open this file : " + strace_file_path)
        sys.exit()

    lines = strace_file.readlines()

    nr_lines = len(lines)
    count_lines = 0
    completion_rate = 0

    for line in lines:
        # check completion rate
        count_lines = count_lines + 1
        rate =  (float(count_lines) / float(nr_lines)) * 100

        if rate >= completion_rate:
            print str(completion_rate) + '%'
            completion_rate = completion_rate + 10

        strace_line = line

        # get TID info
        try:
            match = re.match(r'^\d+', line)
            tid = match.group()
            line = re.sub(r'^\d+', '', line)
            line = line.strip()
        except:
            translate.log("[Exception] I can't find this call TID : " + strace_line)
            sys.exit()

        # if this syscall is not finished
        if line.endswith('<unfinished ...>'):
            unfinished_syscall_dic[tid] = line
            continue

        # get time info
        try:
            match = re.match(r'^\d{2}:\d{2}:\d{2}.\d{6}', line)
            time = match.group()
            line = re.sub(r'^\d{2}:\d{2}:\d{2}.\d{6}', '', line)
            line = line.strip()
        except:
            translate.log("[Exception] I can't find this call TIME : " + strace_line)
            sys.exit()

        # if this syscall is a resumed syscall
        match = re.match(r'^<\.\.\.\s+\w+\s+resumed>', line)
        if match:
            resumed_line = re.sub(r'^<\.\.\.\s+\w+\s+resumed>', '', line).strip()
            unfinished_line = unfinished_syscall_dic[tid]
            unfinished_line = re.sub(r'^\d{2}:\d{2}:\d{2}.\d{6}\s+', '', unfinished_line)
            unfinished_line = unfinished_line.replace('<unfinished ...>', '').strip()
            del unfinished_syscall_dic[tid]
            line = unfinished_line + resumed_line

        # get a system call name
        try:
            match = re.match(r'^\w+', line)
            name = match.group()
            line = re.sub(r'^\w+', '', line)
        except:
            translate.log("[Exception] I can't find this call name : " + strace_line)
            continue

        # We observe only our interests
        if name not in interested_syscalls:
            continue

        # get args
        try:
            match = re.match(r'^\(.*\)\s*=', line)
            args = match.group()
            args = args.rstrip('=').strip()

            if only_dataset:
                try:
                    ret = args.index(dataset_path)
                except:
                    continue

            args = args.strip('()')
            args_list = args.split(',')
            line = re.sub(r'^\(.*\)\s*=', '', line)
        except:
            translate.log("[Exception] I can't find this call's args : " + strace_line)
            continue

        # get return value
        try:
            return_value = line.strip()
        except:
            translate.log("[Exception] return value : " + strace_line)

        syscall = Syscall(strace_line, tid, time, name, args_list, return_value)

        if syscall.name == 'open':
            translate.open_syscall(syscall)
        elif syscall.name == 'close':
            translate.close_syscall(syscall)
        else:
            translate.log("[Exception] unexpected syscall : " + strace_line)

        # the end of for loop

    del translate
    print 'Translation is done!!'
    # the end of main() function

if __name__ == '__main__':
    main()