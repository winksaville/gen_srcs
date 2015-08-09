#!/usr/bin/env python3
# Generate C source files

import os.path, sys, argparse

version = '0.0.1'

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--version', action='store_true', dest='print_version',
        default=False, help='Print version.')

parser.add_argument('file_path', help='<file path>', nargs=1)
parser.add_argument('header_path', help='<header path>', nargs=1)

class Header:
    '''
    Generate C header files
    '''
    # Public fields
    name = ''
    comments = []
    includes = []
    sys_includes = []
    func_declarations = []

    # Initializer
    def __init__(self, name='', comments=[], includes=[], sys_includes=[],
            func_declarations=[]):
        self.name = name
        self.comments = comments
        self.includes = includes
        self.sys_includes = sys_includes
        self.func_declarations = func_declarations

    def append(self, func_sig):
        self.func_declarations.append(func_sig)

    def write(self, f):
        path = os.path.abspath(self.name)

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
        print('#ifdef  {0}'.format(conditional_name), file=f)
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
    name = ''
    rettype = ''
    params = []
    comments = []
    local_declarations = []
    body = []

    # Initializer
    def __init__(self, name='', rettype='void', params=[],
            comments=[], local_declarations=[], body=[]):
        self.name = name
        self.rettype = rettype
        self.params = params
        self.comments = comments
        self.local_declarations = local_declarations
        self.body = body


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

def create_files(function_count, file_path, header_path):
    '''
    Create files
    '''
    f = open(file_path, 'w')
    h = open(header_path, 'w')

    functions = []
    for i in range(function_count):
        func_name = 'func{0}'.format(i)
        func = Function(
                comments=['{0}'.format(func_name)],
                rettype='void',
                name=func_name,
                params=[],
                body=['printf("{0}")'.format(func_name)]
        )
        functions.append(func)
        func.write(f)

    header = Header(
            name=header_path,
            comments=['header....'],
            sys_includes=['stdio.h', 'string.h']
    )
    for func in functions:
        header.append(func.func_sig())

    header.write(h)

    f.close()
    h.close()


def main(args):
    '''
    Main program
    '''
    if sys.version_info < (3, 4):
        print('Need python 3.4+ current version is %s' % sys.version)
        sys.exit(1)

    options = parser.parse_args(args[1:])
    file_path = options.file_path
    header_path = options.header_path

    if options.print_version:
        print('Version %s' % version)
        return 0

    create_files(10, file_path[0], header_path[0])
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
