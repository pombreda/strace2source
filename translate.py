import re
import sys

__author__ = 'Jungsik Choi'

class Syscall:
    def __init__(self, _line, _tid, _time, _name, _args, _return_value):
        self.line = _line
        self.tid = _tid
        self.time = _time
        self.name = _name
        self.args = _args
        self.return_value = _return_value

def main():
    unfinished_syscall_dic = {}
    interested_syscalls = ['open', 'read', 'pread', 'write', 'pwrite', 'close', 'lseek']
    strace_file_path = raw_input("a strace file path : ")
    #data_files_path = "/mnt/tmpfs"

    # open and read a strace file
    try:
        strace_file = open(strace_file_path, 'r')
    except IOError:
        print "[Exception] I can't open this file : " + strace_file_path
        sys.exit()

    lines = strace_file.readlines()

    for line in lines:
        strace_line = line
        # get TID info
        try:
            match = re.match(r'^\d+', line)
            tid = match.group()
            line = re.sub(r'^\d+', '', line)
            line = line.strip()
        except:
            print "[Exception] I can't find this call TID : " + strace_line
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
            print "[Exception] I can't find this call TIME : " + strace_line
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
            print "[Exception] I can't find this call name : " + strace_line
            continue

        # We observe only our interests
        if name not in interested_syscalls:
            continue

        # get args
        try:
            match = re.match(r'^\(.*\)\s*=', line)
            args = match.group()
            args = args.rstrip('=').strip()
            args = args.strip('()')
            args_list = args.split(',')
            line = re.sub(r'^\(.*\)\s*=', '', line)
        except:
            print "[Exception] I can't find this call's args : " + strace_line
            continue

        # get return value
        try:
            return_value = line.strip()
        except:
            print "[Exception] return value : " + strace_line

        call = Syscall(strace_line, tid, time, name, args_list, return_value)
        print call.name

if __name__ == '__main__':
    main()