__author__ = 'Jungsik Choi'

import sys
import os
import subprocess

class File:
    def __init__(self, _fd, _path, _oflag):
        self.fd = _fd
        self.path = _path
        self.oflag = _oflag
        self.cur_offset = 0
        self.max_offset = 0
        self.access_history = []

class Manager:
    def __init__(self, translate):
        self.opened_files_dic = {}
        self.opened_files_list = []
        self.translate = translate
        self.max_nr_fds = 0
        self.total_file_size = 0
        self.total_access_size = 0

    def finish(self):
        total_access_rate = float(self.total_access_size) / float(self.total_file_size) * 100
        self.translate.log('\nTotal File Size = ' + str(self.total_file_size))
        self.translate.log('Total Access Size = ' + str(self.total_access_size))
        self.translate.log('Total Access Rate = ' + str(total_access_rate))

    # Fix me!!
    def make_testfile(self, _path, _size):
        dir = os.path.dirname(_path)
        print dir
        if not os.path.exists(dir):
            os.mkdir(dir)

        file_name = 'of=' + _path
        repeat = _size / 4096 + 1
        count = 'count=' + str(repeat)

        subprocess.check_output(["dd", "if=/dev/zero", file_name, "bs=4k", count])


    def make_key(self, _syscall, _fd):
        return str(_syscall.tid) + str(_fd)

    def add_file(self, syscall, new_file):
        key = str(syscall.tid) + str(new_file.fd)

        if key not in self.opened_files_dic:
            self.opened_files_dic[key] = new_file
            self.translate.log('The number of files in opened_files_dic : ' + str(len(self.opened_files_dic)))
        else:
            self.translate.log('[Exception] There is a redundant key in opened_files_dic')

        if self.opened_files_list.count(key) == 0:
            self.opened_files_list.append(key)
            self.translate.log('The number of fds in opened_files_list : ' + str(len(self.opened_files_list)))
            index = self.opened_files_list.index(key)
            nr_fds = len(self.opened_files_list)

            if nr_fds > self.max_nr_fds:
                self.max_nr_fds = nr_fds

            return index
        else:
            self.translate.log('[Exception] There is a redundant key in opened_files_list')
            return -1

    def analysis_access_history(self, _max_offset, _access_history):
        file_size = _max_offset
        exclusive_access_history = [[0, 0]]

        for access in _access_history:
            is_not_match = 1
            for exclusive_access in exclusive_access_history:
                # access['read', start_offset, end_offset], [1]=start, [2]=end
                # exclusive_access[start_offset, end_offset], [0]=start, [1]=end
                if access[1] < exclusive_access[1] and access[2] > exclusive_access[0]:
                    # case 1
                    if access[1] < exclusive_access[0] and access[2] > exclusive_access[1]:
                        index = exclusive_access_history.index(exclusive_access)
                        exclusive_access_history.pop(index)
                        exclusive_access_history.insert(index, [access[1], access[2]])

                    # case 2
                    elif access[1] < exclusive_access[0] and access[2] < exclusive_access[1]:
                        index = exclusive_access_history.index(exclusive_access)
                        exclusive_access_history.pop(index)
                        exclusive_access_history.insert(index, [access[1], exclusive_access[1]])

                    # case 3
                    elif access[1] > exclusive_access[0] and access[2] > exclusive_access[1]:
                        index = exclusive_access_history.index(exclusive_access)
                        exclusive_access_history.pop(index)
                        exclusive_access_history.insert(index, [exclusive_access[0], access[2]])

                    # case 4
                    elif access[1] > exclusive_access[0] and access[2] < exclusive_access[1]:
                        continue

            if is_not_match:
                exclusive_access_history.append([access[1], access[2]])

        exclusive_access_count = 0

        for access in exclusive_access_history:
            exclusive_access_count = exclusive_access_count + (access[1] - access[0])

        if exclusive_access_count != 0 and file_size != 0:
            access_rate = float(exclusive_access_count) / float(file_size) * 100
        else:
            access_rate = 0

        msg = 'Exclusive Access Count : ' + str(exclusive_access_count) + '/' + str(file_size)
        msg += ' (' + str(access_rate) + '%)'
        self.translate.log(msg)
        self.total_file_size = self.total_file_size + file_size
        self.total_access_size = self.total_access_size + exclusive_access_count

    def sub_file(self, _syscall, _fd, _path):
        key = self.make_key(_syscall, _fd)

        try:
            closed_file = self.opened_files_dic[key]
        except KeyError:
            msg = '[Exception] There is not this key in opened_files_dic : '
            msg += key
            self.translate.log(msg)
        else:
            if closed_file.path == _path:
                # analysis access history
                file_size = closed_file.max_offset
                self.analysis_access_history(file_size, closed_file.access_history)

                # remove the file in opened_files_dic
                del self.opened_files_dic[key]
                del closed_file
                msg = 'The number of files in opened_files_dic : '
                msg += str(len(self.opened_files_dic))
                self.translate.log(msg)
            else:
                msg = '[Exception] Each path is different : '
                msg += _path + ', ' + closed_file.path
                self.translate.log(msg)
                return

            try:
                index = self.opened_files_list.index(key)
            except:
                msg = '[Exception] There is not this key in opened_files_list : '
                msg += key
                self.translate.log(msg)
                self.translate.log(sys.exc_info()[0])
                return -1
            else:
                self.make_testfile(_path, file_size)
                self.opened_files_list.pop(index)
                msg = 'The number of fds in opened_files_list : '
                msg += str(len(self.opened_files_list))
                self.translate.log(msg)
                return index

    def read_file(self, _syscall, _fd, _path, _request_size, _read_size):
        key = self.make_key(_syscall, _fd)

        try:
            read_file = self.opened_files_dic[key]

            if read_file.path == _path:
                cur_offset = read_file.cur_offset
                read_file.cur_offset = cur_offset + _read_size
                read_file.access_history.append(['read', cur_offset, cur_offset + _read_size])

                if read_file.cur_offset > read_file.max_offset:
                    read_file.max_offset = read_file.cur_offset

            else:
                cur_offset = -1
                msg = '[Exception] Each path is different : '
                msg += _path + ', ' + read_file.path
                self.translate.log(msg)
        except KeyError:
            cur_offset = -1
            msg = '[Exception] There is not this key in opened_files_dic : '
            msg += key
            self.translate.log(msg)

        try:
            index = self.opened_files_list.index(key)
        except:
            msg = '[Exception] There is not this key in opened_files_list : '
            msg += key
            self.translate.log(msg)
            self.translate.log(sys.exc_info()[0])
            index = -1

        return index, cur_offset

    def write_file(self, _syscall, _fd, _path, _request_size, _write_size):
        key = self.make_key(_syscall, _fd)

        try:
            write_file = self.opened_files_dic[key]

            if write_file.path == _path:
                cur_offset = write_file.cur_offset
                write_file.cur_offset = cur_offset + _write_size
                write_file.access_history.append(['write', cur_offset, cur_offset + _write_size])

                if write_file.cur_offset > write_file.max_offset:
                    write_file.max_offset = write_file.cur_offset

            else:
                cur_offset = -1
                msg = '[Exception] Each path is different : '
                msg += _path + ', ' + write_file.path
                self.translate.log(msg)
        except KeyError:
            cur_offset = -1
            self.translate.log('[Exception] There is not this key in opened_files_dic : ' + key)

        try:
            index = self.opened_files_list.index(key)
        except:
            self.translate.log('[Exception] There is not this key in opened_files_list : ' + key)
            self.translate.log(sys.exc_info()[0])
            index = -1

        return index, cur_offset



    def change_file_offset(self, syscall, fd, path, new_offset):
        key = str(syscall.tid) + str(fd)

        try:
            lseek_file = self.opened_files_dic[key]

            if lseek_file.path == path:
                del self.opened_files_dic[key]
                self.translate.log("previous offset=" + str(lseek_file.cur_offset))

                lseek_file.cur_offset = new_offset
                if lseek_file.max_offset < new_offset:
                    lseek_file.max_offset = new_offset

                self.translate.log("current offset=" + str(lseek_file.cur_offset))
                self.opened_files_dic[key] = lseek_file
                self.translate.log('The number of files in opened_files_dic : ' + str(len(self.opened_files_dic)))
            else:
                self.translate.log('[Exception] Each path is different : ' + path + ', ' + lseek_file.path)
        except KeyError:
            self.translate.log('[Exception] There is not this key in opened_files_dic : ' + key)

