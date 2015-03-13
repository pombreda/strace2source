__author__ = 'jchoi'

class SourceGenerator:
    def __init__(self):
        self.original_source = open('source/readwrite.c', 'w')
        self.changed_source_step1 = open('source/mmap.c', 'w')
        self.changed_source_step2 = open('source/intelligent.c', 'w')
        self.changed_source_step3 = open('source/async.c', 'w')

    def __del__(self):
        self.original_source.close()
        self.changed_source_step1.close()
        self.changed_source_step2.close()
        self.changed_source_step3.close()

    def prepare(self):
        code = '#include <fcntl.h>\n'
        code += '#include <sys/mman.h>\n\n'
        code += 'int main(void) {\n'
        code += '\tint fd[NR_FDS];\n'
        #code += '\treturn 0;\n'
        #code += '}\n'

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
        code += '\tmmaped_buf[' + str(_index) + '] = mmap(NULL, len, '
        code += prot + ', MAP_SHARED, fd[' + str(_index) + '], 0);\n'

        self.original_source.write(code)
        self.changed_source_step1.write(code)
        self.changed_source_step2.write(code)
        self.changed_source_step3.write(code)