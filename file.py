__author__ = 'Jungsik Choi'


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


    def sub_file(self, syscall, fd, path):
        key = str(syscall.tid) + str(fd)

        try:
            closed_file = self.opened_files_dic[key]

            if closed_file.path == path:
                del self.opened_files_dic[key]
                del closed_file
                self.translate.log('The number of files in opened_files_dic : ' + str(len(self.opened_files_dic)))
            else:
                self.translate.log('[Exception] Each path is different : ' + path + ', ' + closed_file.path)
        except KeyError:
            self.translate.log('[Exception] There is not this key in opened_files_dic : ' + key)

        try:
            index = self.opened_files_list.index(key)
        except:
            self.translate.log('[Exception] There is not this key in opened_files_list : ' + key)
        else:
            self.opened_files_list.pop(index)
            self.translate.log('The number of fds in opened_files_list : ' + str(len(self.opened_files_list)))

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

