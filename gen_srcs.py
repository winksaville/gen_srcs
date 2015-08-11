#!/usr/bin/env python3
# Generate C source files

import os.path, sys, argparse

version = '0.0.1'

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--version', action='store_true', dest='print_version',
        default=False, help='Print version.')

parser.add_argument('hierarchy_path', help='<file path>', nargs=1)
parser.add_argument('library_count', help='<library count>', nargs=1)
parser.add_argument('function_count_per_lib', help='<function count per library>', nargs=1)

class Header:
    '''
    Generate C header files
    '''
    # Public fields
    file_path = ''
    comments = None
    includes = None
    sys_includes = None
    func_declarations = None

    # Initializer
    def __init__(self, file_path='', comments=None, includes=None, sys_includes=None,
            type_declarations=None, func_declarations=None):
        self.file_path = file_path
        self.comments = comments if comments else []
        self.includes = includes if includes else []
        self.sys_includes = sys_includes if sys_includes else []
        self.type_declarations = type_declarations if type_declarations else []
        self.func_declarations = func_declarations if func_declarations else []

    def get_name(self):
        return os.path.basename(self.file_path)

    def append_func_declaration(self, func_sig):
        self.func_declarations.append(func_sig)

    def append_type_declaration(self, type_declaration):
        self.type_declarations.append(func)

    def write(self, f):
        path = os.path.abspath(self.file_path)
        parts = []
        while True:
            head, tail = os.path.split(path)
            if tail == '':
                break;
            parts.append(tail)
            path = head
        conditional_name = '__'
        for part in reversed(parts):
            conditional_name += part.upper()
            conditional_name += '_'
        conditional_name += '_'
        conditional_name = conditional_name.replace('.', '_')

        for line in self.comments:
            print('// {0}'.format(line), file=f)
        print('', file=f)
        print('#ifndef  {0}'.format(conditional_name), file=f)
        print('#define {0}'.format(conditional_name), file=f)
        print('', file=f)
        if self.includes:
            for line in self.includes:
                print('#include "{0}"'.format(line), file=f)
            print('', file=f)

        if self.sys_includes:
            for line in self.sys_includes:
                print('#include <{0}>'.format(line), file=f)
            print('', file=f)
        
        if self.type_declarations:
            for line in self.type_declarations:
                print('{0};'.format(line), file=f)
            print('', file=f)

        if self.func_declarations:
            for line in self.func_declarations:
                print('{0};'.format(line), file=f)
            print('', file=f)

        print('#endif // {0}'.format(conditional_name), file=f)

class Function:
    '''
    Generate a C function
    '''
    # Public fields
    name = None
    rettype = None
    params = None
    comments = None
    local_declarations = None
    body = None

    # Initializer
    def __init__(self, name='', rettype='void', params=None,
            comments=None, local_declarations=None, body=None):
        self.name = name
        self.rettype = rettype
        self.params = params if params else []
        self.comments = comments if comments else []
        self.local_declarations = local_declarations if local_declarations else []
        self.body = body if body else []

    def func_sig(self):
        s = '{0} {1}('.format(self.rettype, self.name)
        if self.params:
            first_param = True
            for param in self.params:
                if not first_param:
                    s += ', '
                first_param = False
                s += '{0}'.format(param)
        else:
            s += 'void'
        s += ')'
        return s

    def write(self, f):
        for line in self.comments:
            print('// {0}'.format(line), file=f)
        signature = '{0} {{'.format(self.func_sig())
        print(signature, file=f)
        if self.local_declarations:
            for line in self.local_declarations:
                print('    {0};'.format(line), file=f)
            print('') 
        
        if self.body:
            for line in self.body:
                print('    {0};'.format(line), file=f)

        print('}', file=f)

class LibrarySrc:
    '''
    Generate C library source file
    '''
    # Public fields
    file_path = ''
    comments = None
    includes = None
    sys_includes = None
    type_declarations = None
    header = None
    func_range = range(0, 1)
    functions = None

    # Initializer
    def __init__(self, file_path='', func_range=range(0,1), comments=None,
            includes=None, sys_includes=None, type_declarations=None, header=None):
        self.file_path = file_path
        self.func_range = func_range
        self.comments = comments if comments else []
        self.includes = includes if includes else []
        self.sys_includes = sys_includes if sys_includes else []
        self.type_declarations = type_declarations if type_declarations else []

        self.header = header
        self.functions = []

    def __append_func(self, func):
        self.header.append_func_declaration(func.func_sig())
        self.functions.append(func)

    def write(self, f):
        for i in self.func_range:
            func_name = 'func{0}'.format(i)
            func = Function(
                    comments=['{0}'.format(func_name)],
                    rettype='void',
                    name=func_name,
                    params=[],
                    body=['printf("{0}\\n")'.format(func_name)]
            )
            self.__append_func(func)

        for line in self.comments:
            print('// {0}'.format(line), file=f)
        print('', file=f)
        if self.includes:
            for line in self.includes:
                print('#include "{0}"'.format(line), file=f)
            print('', file=f)

        if self.sys_includes:
            for line in self.sys_includes:
                print('#include <{0}>'.format(line), file=f)
            print('', file=f)

        if self.type_declarations:
            for line in self.type_declarations:
                print('{0};'.format(line), file=f)
                print('', file=f)
            print('', file=f)

        if self.functions:
            for func in self.functions:
                func.write(f)
                print('', file=f)
            print('', file=f)


class Library:
    '''
    Generate C library
    '''
    # Public fields
    lib_path = None
    func_range = None

    # Initializer
    def __init__(self, path='', func_range=range(0, 1)):
        self.lib_path = path
        self.func_range = func_range

    def create(self):
        '''
        Create a library with the name of defined by the basename(lib_path)
        it will include a src/ and an include/ directory.
        '''
        lib_name = os.path.basename(self.lib_path)
        os.makedirs(self.lib_path, exist_ok=True)

        header_path = self.lib_path + '/include/' + lib_name + '.h'
        os.makedirs(os.path.dirname(header_path), exist_ok=True)
        h = open(header_path, 'w')

        src_path = self.lib_path + '/src/' + lib_name + '.c'
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        f = open(src_path, 'w')

        lib_header = Header(file_path=header_path,
            comments=['header....'],
            sys_includes=['stdio.h'],
            type_declarations=['typedef int {0}_status'.format(lib_name)])

        lib_source = LibrarySrc(file_path=src_path, func_range=self.func_range,
                comments=['Test library 1'], includes=[lib_header.get_name()],
                header=lib_header)

        lib_source.write(f)
        lib_header.write(h)

        f.close()
        h.close()


class Hierarchy:
    '''
    Generate a Hierarchy of C code
    '''
    hierarchy_path = None
    lib_count = None
    func_count_per_lib = None

    def __init__(self, hierarchy_path,  lib_count, func_count_per_lib):
        self.hierarchy_path = hierarchy_path
        self.lib_count = int(lib_count)
        self.func_count_per_lib = int(func_count_per_lib)

    def create(self):
        '''
        Create files
        '''
        # Create root
        os.makedirs(self.hierarchy_path, exist_ok=True)

        library = []
        for i in range(0, self.lib_count):
            base = i * self.func_count_per_lib
            lib_path = self.hierarchy_path + '/libs' + '/L{:03d}'.format(base)
            lib = Library(path=lib_path, func_range=
                    range(base + 1, base + self.func_count_per_lib + 1))
            library.append(lib)
            lib.create()


def main(args):
    '''
    Main program
    '''
    if sys.version_info < (3, 4):
        print('Need python 3.4+ current version is %s' % sys.version)
        sys.exit(1)

    options = parser.parse_args(args[1:])
    hierarchy_path = options.hierarchy_path
    library_count = options.library_count
    function_count_per_lib = options.function_count_per_lib

    if options.print_version:
        print('Version %s' % version)
        return 0

    hierarchy = Hierarchy(hierarchy_path[0], library_count[0], function_count_per_lib[0])
    hierarchy.create()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
