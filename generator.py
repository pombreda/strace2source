__author__ = 'jchoi'

class SourceGenerator:
    def __init__(self):
        self.original_source = open('source/readwrite.c', 'w')
        self.changed_source_step1 = open('source/mmap.c', 'w')
        self.changed_source_step2 = open('source/intelligent.c', 'w')
        self.changed_source_step3 = open('source/async.c', 'w')
        self.copy_buf_max_size = 0

    def finish(self, _max_nr_fds):
        code = '\n\tfree(copy_buf, COPY_BUF_SIZE);\n'
        code += '\treturn 0;\n'
        code += '}\n'

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)

        self.original_source.close()
        self.changed_source_step1.close()
        self.changed_source_step2.close()
        self.changed_source_step3.close()

        self.header_file = open('source/header.h', 'w')
        code = '#define COPY_BUF_SIZE ' + str(self.copy_buf_max_size) + '\n'
        code += '#define NR_FDS ' + str(_max_nr_fds) + '\n'
        self.header_file.write(code)
        self.header_file.close()

    def prepare(self):
        code = '#include <fcntl.h>\n'
        code += '#include <sys/mman.h>\n'
        code += '#include <stdlib.h>\n'
        code += '#include <string.h>\n\n'
        code += 'int main(void) {\n'
        code += '\tint fd[NR_FDS];\n'
        code += '\tchar *mmaped_buf[NR_FDS];\n'
        code += '\tchar *copy_bur;\n\n'
        code += '\tcopy_buf = (char *)malloc(COPY_BUF_SIZE);\n'
        code += '\tif (copy_buf == NULL) {\n'
        code += '\t\tprintf("malloc is failed\\n");\n'
        code += '\t\texit(-1);\n'
        code += '\t}\n'

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)


    def open(self, _path, _oflag, _index):
        if _oflag.find('RDONLY') > 0:
            prot = 'PROT_READ'
        else:
            prot = 'PROT_READ|PROT_WRITE'
        code = '\n\t//open\n'
        code += '\tfd[' + str(_index) + '] = open("' + _path + '", ' + _oflag + ');\n'
        code += '\tmmaped_buf[' + str(_index) + '] = (char *)mmap(NULL, len, '
        code += prot + ', MAP_SHARED, fd[' + str(_index) + '], 0);\n'

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)

    def close(self, _index):
        code = '\n\t//close\n'
        code += '\tret = munmap(mmaped_buf[' + str(_index) + '], len);\n'
        code += '\tclose(fd[' + str(_index) + ']);\n'

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)

    def read(self, _index, _cur_offset, _read_size):
        code = '\n\t//read\n'
        code += '\tbuf = memcpy(copy_buf, mmaped_buf[' + str(_index) + '] + '
        code += str(_cur_offset) + ', ' + str(_read_size) + ');\n'

        if _read_size > self.copy_buf_max_size:
            self.copy_buf_max_size = _read_size

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)

    def write(self, _index, _cur_offset, _write_size):
        code = '\n\t//write\n'
        code += '\tbuf = memcpy(mmaped_buf[' + str(_index) + '] + ' + str(_cur_offset)
        code += ', copy_buf, ' + str(_write_size) + ');\n'

        if _write_size > self.copy_buf_max_size:
            self.copy_buf_max_size = _write_size

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)