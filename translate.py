import re
import sys

from syscall import *
from file import *

__author__ = 'Jungsik Choi'

class Translate:
    def __init__(self):
        self.logfile = open('strace2source.log', 'w')
        self.manager = Manager(self)

    def __del__(self):
        self.logfile.close()
        del self.manager

    def log(self, _message):
        message = str(_message) + '\n'
        self.logfile.write(message)

    def file_open (self, fd, filename, permission):
        pass

    def open_syscall(self, syscall):
        self.log('\n[open] ')
        fd = int(syscall.return_value)
        path = syscall.args_list[0].strip('"')
        oflag = syscall.args_list[1].strip()
        self.log('original=' + syscall.line)
        self.log('analysis=(fd)' + str(fd) + ', (path)' + path + ', (oflag)' + oflag + '.')
        new_file = File(fd, path, oflag)
        self.manager.add_file(syscall, new_file)

    def read_syscall(self, syscall):
        self.log('\n[read] ')
        self.log(syscall.args_list)

    def pread_syscall(self, syscall):
        self.log('\n[pread] ')
        self.log(syscall.args_list)
        self.log(syscall.return_value)

    def write_syscall(self, syscall):
        self.log('\n[write] ')
        self.log(syscall.args_list)
        self.log(syscall.return_value)

    def pwrite_syscall(self, syscall):
        self.log('\n[pwrite] ')
        self.log(syscall.args_list)
        self.log(syscall.return_value)

    def lseek_syscall(self, syscall):
        self.log('\n[lseek] ')
        self.log(syscall.args_list)
        self.log(syscall.return_value)

    def close_syscall(self, syscall):
        self.log('\n[close] ')
        self.log(syscall.args_list)
        self.log(syscall.return_value)

        if syscall.return_value == '0':
            try:
                compile = re.compile(r'(?P<fd>\d+)(?P<path>\<.+\>)')
                match = compile.match(syscall.args_list[0])
                fd = match.group('fd')
                path = match.group('path')
                path = path.strip('<>')
                self.log('fd=' + fd)
                self.log('path=' + path)
            except:
                self.log("[Exception] I can't find the fd/path in this syscall : " + syscall.line)
                return

        else:
            self.log('[Exception] This close is failed : ' + syscall.line)

    def clone_syscall(self, syscall):
        self.log('\n[close] ')
        self.log(syscall.args_list)
        self.log(syscall.return_value)

    # The end of Translate class

def main():
    translate = Translate()
    unfinished_syscall_dic = {}
    interested_syscalls = ['open', 'read', 'pread', 'write', 'pwrite', 'lseek', 'close', 'clone']

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

        strace_line = line.strip()

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

        elif syscall.name == 'read':
            translate.read_syscall(syscall)

        elif syscall.name == 'pread':
            translate.pread_syscall(syscall)

        elif syscall.name == 'write':
            translate.write_syscall(syscall)

        elif syscall.name == 'pwrite':
            translate.pwrite_syscall(syscall)

        elif syscall.name == 'lseek':
            translate.lseek_syscall(syscall)

        elif syscall.name == 'close':
            translate.close_syscall(syscall)

        elif syscall.name == 'clone':
            translate.clone_syscall(syscall)

        else:
            translate.log("[Exception] unexpected syscall : " + strace_line)

        # the end of for loop

    del translate
    print 'Translation is done!!'
    # the end of main() function

if __name__ == '__main__':
    main()