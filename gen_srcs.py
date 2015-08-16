#!/usr/bin/env python3
# Generate C source files

import os.path, sys, argparse

version = '0.0.1'

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--version',
                    action='store_true',
                    dest='print_version',
                    default=False,
                    help='Print version.')

parser.add_argument('builder', help='<builder: cmake meson>', nargs=1)
parser.add_argument('hierarchy_path', help='<file path>', nargs=1)
parser.add_argument('library_count', help='<Library count>', nargs=1)
parser.add_argument('function_count_per_library',
                    help='<function count per library>',
                    nargs=1)


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
    def __init__(self,
                 file_path='',
                 comments=None,
                 includes=None,
                 sys_includes=None,
                 type_declarations=None,
                 func_declarations=None):
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
                break
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
    def __init__(self,
                 name='',
                 rettype='void',
                 params=None,
                 comments=None,
                 local_declarations=None,
                 body=None):
        self.name = name
        self.rettype = rettype
        self.params = params if params else []
        self.comments = comments if comments else []
        self.local_declarations = local_declarations if local_declarations else []
        self.body = body if body else []

    def getName(self):
        return self.name

    def getParams(self):
        return self.params

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
    def __init__(self,
                 file_path='',
                 func_range=range(0, 1),
                 comments=None,
                 includes=None,
                 sys_includes=None,
                 type_declarations=None,
                 header=None):
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

    def getFunctions(self):
        return self.functions

    def write(self, f):
        for i in self.func_range:
            func_name = 'func{0}'.format(i)
            func = Function(
                comments=['{0}'.format(func_name)],
                rettype='void',
                name=func_name,
                params=[],
                body=['printf("{0}\\n")'.format(func_name)])
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
    __lib_header = None
    __lib_source = None

    # Initializer
    def __init__(self, path='', func_range=range(0, 1)):
        self.lib_path = path
        self.func_range = func_range
        self.__lib_header = None
        self.__lib_source = None

    def getLibPath(self):
        return self.lib_path

    def getLibName(self):
        return os.path.basename(self.lib_path)

    def getLibHeaderName(self):
        return os.path.basename(self.__lib_header.get_name())

    def getFunctions(self):
        return self.__lib_source.getFunctions()

    def create(self):
        '''
        Create a library with the name of defined by the basename(lib_path)
        it will include a src/ and an include/ directory.
        '''
        lib_name = self.getLibName()
        os.makedirs(self.lib_path, exist_ok=True)

        header_path = self.lib_path + '/include/' + lib_name + '.h'
        os.makedirs(os.path.dirname(header_path), exist_ok=True)
        h = open(header_path, 'w')

        src_path = self.lib_path + '/src/' + lib_name + '.c'
        os.makedirs(os.path.dirname(src_path), exist_ok=True)
        f = open(src_path, 'w')

        self.__lib_header = Header(
            file_path=header_path,
            comments=['header....'],
            sys_includes=['stdio.h'],
            type_declarations=['typedef int {0}_status'.format(lib_name)])

        self.__lib_source = LibrarySrc(file_path=src_path,
                                       func_range=self.func_range,
                                       comments=['Test library 1'],
                                       includes=[self.__lib_header.get_name()],
                                       header=self.__lib_header)

        self.__lib_source.write(f)
        self.__lib_header.write(h)

        f.close()
        h.close()


class Application:
    '''
    Generate C test application
    '''
    __app_path = None
    __libraries = None

    # Initializer
    def __init__(self, path='', libraries=None):
        self.__app_path = path
        self.__libraries = libraries if libraries else []

    def getAppName(self):
        return os.path.basename(self.__app_path)

    def getLibraries(self):
        return self.__libraries

    def getAppPath(self):
        return self.__app_path

    def create(self):
        '''
        Create a test application with a src/main.c file
        and is dependent upon all of the libraries and invokes
        every library function.
        '''

        # Create a list of includes and body statements
        includes = []
        includes.append('<stdio.h>')
        body = []
        for lib in self.__libraries:
            includes.append('"{0}"'.format(lib.getLibHeaderName()))
            for func in lib.getFunctions():
                if len(func.params) != 0:
                    raise Exception(
                        'Only handles functions with no parameters: {0}:{1}'.format(
                            lib.getLibName(), func.func_sig()))
                body.append('{0}();'.format(func.getName()))

        # Create the test app
        src_path = self.__app_path + '/src/main.c'
        os.makedirs(os.path.dirname(src_path), exist_ok=True)

        f = open(src_path, 'w')
        for inc in includes:
            print('#include {0}'.format(inc), file=f)
        print('int main(void) {', file=f)
        for statement in body:
            print('  {0}'.format(statement), file=f)
        print('  return 0; // ok', file=f)
        print('}', file=f)
        f.close()


class MesonBuilder:
    __libraries_file = None
    __apps_file = None

    def __init__(self):
        pass

    def begRoot(self, root_path, applications_path, libraries_path):
        apps_rel_path = os.path.relpath(applications_path, root_path)
        libs_rel_path = os.path.relpath(libraries_path, root_path)
        r = open(root_path + '/meson.build', 'w')

        print("project('hierarchy', 'c')\n"
              "add_global_arguments('-std=c99', language : 'c')\n"
              "\n"
              "subdir(\'{0}\')\n"
              "subdir(\'{1}\')\n".format(libs_rel_path, apps_rel_path),
              file=r)

        r.close()

    def endRoot(self):
        pass

    def begAppBuilder(self, app_path):
        apps_path = app_path + '/meson.build'
        self.__apps_file = open(apps_path, 'w')

    def endAppBuilder(self):
        self.__apps_file.close()

    def addAppToAppBuilder(self, app):
        builder_path = app.getAppPath() + '/meson.build'
        os.makedirs(os.path.dirname(builder_path), exist_ok=True)
        b = open(builder_path, 'w')

        print("executable('{0}',\n"
              "  'src/main.c',\n"
              "  install : true,".format(app.getAppName()),
              file=b)
        print("  dependencies : [", file=b)
        for lib in app.getLibraries():
            print('    lib{0}_dep,'.format(lib.getLibName()), file=b)
        print("  ])", file=b)

        # Add a line for this library in the parent directory
        print('subdir(\'{0}\')'.format(app.getAppName()), file=self.__apps_file)

        b.close()

    def begLibBuilder(self, libraries_path):
        libraries_path = libraries_path + '/meson.build'
        self.__libraries_file = open(libraries_path, 'w')

    def endLibBuilder(self):
        self.__libraries_file.close()

    def addLibToLibBuilder(self, library):
        builder_path = library.getLibPath() + '/meson.build'
        os.makedirs(os.path.dirname(builder_path), exist_ok=True)
        b = open(builder_path, 'w')

        print(
            "incs = include_directories('include')\n"
            "lib{0} = static_library('{0}', 'src/{0}.c', include_directories: incs)\n"
            "lib{0}_dep = declare_dependency(include_directories : incs, link_with : lib{0})\n".format(
                library.getLibName()),
            file=b)

        # Add a line for this library in the parent directory
        print('subdir(\'{0}\')'.format(library.getLibName()),
              file=self.__libraries_file)

        b.close()


class CMakeBuilder:
    __libraries_file = None
    __apps_file = None

    def __init__(self):
        pass

    def begRoot(self, root_path, applications_path, libraries_path):
        apps_rel_path = os.path.relpath(applications_path, root_path)
        libs_rel_path = os.path.relpath(libraries_path, root_path)
        r = open(root_path + '/CMakeLists.txt', 'w')

        print('cmake_minimum_required (VERSION 3.2)\n'
              'project("hierarchy")\n'
              'enable_language(C)\n'
              '\n'
              'find_program(CCACHE_FOUND ccache)\n'
              'if(CCACHE_FOUND)\n'
              '      set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)\n'
              '      set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ccache)\n'
              '  endif(CCACHE_FOUND)\n'
              '\n'
              'add_subdirectory("{0}")\n'
              'add_subdirectory("{1}")\n'.format(libs_rel_path, apps_rel_path),
              file=r)

        r.close()

    def endRoot(self):
        pass

    def begAppBuilder(self, app_path):
        apps_path = app_path + '/CMakeLists.txt'
        self.__apps_file = open(apps_path, 'w')

    def endAppBuilder(self):
        self.__apps_file.close()

    def addAppToAppBuilder(self, app):
        builder_path = app.getAppPath() + '/CMakeLists.txt'
        os.makedirs(os.path.dirname(builder_path), exist_ok=True)
        b = open(builder_path, 'w')

        print('add_executable({0} src/main.c)\n'
              'target_link_libraries({0}'.format(app.getAppName()),
              file=b)
        for lib in app.getLibraries():
            print('    {0}'.format(lib.getLibName()), file=b)
        print(")", file=b)

        # Add a line for this library in the parent directory
        print('add_subdirectory("{0}")'.format(app.getAppName()),
              file=self.__apps_file)

        b.close()

    def begLibBuilder(self, libraries_path):
        libraries_path = libraries_path + '/CMakeLists.txt'
        self.__libraries_file = open(libraries_path, 'w')

    def endLibBuilder(self):
        self.__libraries_file.close()

    def addLibToLibBuilder(self, library):
        builder_path = library.getLibPath() + '/CMakeLists.txt'
        os.makedirs(os.path.dirname(builder_path), exist_ok=True)
        b = open(builder_path, 'w')

        print('add_library({0} STATIC\n'
              '    src/{0}.c\n'
              ')\n'
              'target_include_directories({0} PUBLIC "include")\n'.format(
                  library.getLibName()),
              file=b)

        # Add a line for this library in the parent directory
        print('add_subdirectory("{0}")'.format(library.getLibName()),
              file=self.__libraries_file)

        b.close()


class CreatorBuilder:

    def begRoot(self, root_path, applications_path, libraries_path):
        apps_path = os.path.relpath(applications_path, root_path)
        libs_path = os.path.relpath(libraries_path, root_path)
        with open(os.path.join(root_path, '.creator'), 'w') as fp:
            text = '''
# @creator.unit.name = hierarchy

define(':CFlags', ' -std=c99')
define(':BuildDir', '$ProjectPath/build')

workspace.path.append(e('$ProjectPath/{apps}'))
workspace.path.append(e('$ProjectPath/{libs}'))

load('apps')
load('libs')'''.strip().format(apps=apps_path, libs=libs_path)
            fp.write(text)

        with open(os.path.join(root_path, 'template.app.creator'), 'w') as fp:
            fp.write('''
# @creator.unit.name = template.app

load('platform', 'p')
load('compiler', 'c')

define('Sources', '$(wildcard $ProjectPath/src/*.c)')
define('Objects', '$(p:obj $(move $Sources, $ProjectPath/src, $BuildDir/obj/$self))')
define('Includes', '$ProjectPath/include')
define('Libs', '')
define('Bin', '$(p:bin $BuildDir/bin/${self}.)')

@target(abstract=True)
def obj():
  obj.build_each('$Sources', '$Objects',
    'ccache $c:cc $c:compileonly $(c:include $Includes) $CFlags $"< $(c:objout $@)')

@target(abstract=True)
def bin():
  bin.build('$Objects', '$Bin', 'ccache $c:cc $CFlags $!< $!Libs $(c:binout $@)')
'''.strip())

        with open(os.path.join(root_path, 'template.lib.creator'), 'w') as fp:
            fp.write('''
# @creator.unit.name = template.lib

load('platform', 'p')
load('compiler', 'c')

if not defined('BuildDir'):
  raise EnvironmentError('BuildDir is not defined')

define('Includes', '$ProjectPath/include')
define('Sources', '$(wildcard $ProjectPath/src/*.c)')
define('Objects', '$(p:obj $(move $Sources, $ProjectPath/src, $BuildDir/obj/$self))')
define('Lib', '$(p:lib $BuildDir/libs/$self)')

@target(abstract=True)
def obj():
  obj.build_each('$Sources', '$Objects', 'ccache $c:cc $c:compileonly $CFlags $(c:include $Includes) $(c:objout $@) $"<')

@target(obj, abstract=True)
def lib():
  lib.build('$Objects', '$Lib', 'ccache $(c:ar $@) $!<')
'''.strip())

    def endRoot(self):
        pass

    def begAppBuilder(self, app_path):
        self._apps_file = open(os.path.join(app_path, '.creator'), 'w')
        self._apps_file.write('# @creator.unit.name = apps\n')

    def endAppBuilder(self):
        self._apps_file.close()
        del self._apps_file

    def addAppToAppBuilder(self, app):
        self._apps_file.write("load('{0}')\n".format(app.getAppName()))

        with open(os.path.join(app.getAppPath(), '.creator'), 'w') as fp:
            fp.write('# @creator.unit.name = {0}\n'.format(app.getAppName()))
            fp.write("extends('template.app')\n")

            libs = ''
            includes = ''
            lib_deps = []
            for lib in app.getLibraries():
                fp.write("load('{0}')\n".format(lib.getLibName()))
                lib_deps.append(lib.getLibName() + ':lib')
                libs += ';${0}:Lib'.format(lib.getLibName())
                includes += ';${0}:Includes'.format(lib.getLibName())
            fp.write("append('Libs', {0!r})\n".format(libs))
            fp.write("append('Includes', {0!r})\n".format(includes))
            fp.write("[obj.requires(x) for x in %r]\n" % lib_deps)

    def begLibBuilder(self, libraries_path):
        self._libs_file = open(os.path.join(libraries_path, '.creator'), 'w')
        self._libs_file.write('# @creator.unit.name = libs\n')

    def endLibBuilder(self):
        self._libs_file.close()
        del self._libs_file

    def addLibToLibBuilder(self, lib):
        self._libs_file.write("load('{0}')\n".format(lib.getLibName()))

        with open(os.path.join(lib.getLibPath(), '.creator'), 'w') as fp:
            fp.write('# @creator.unit.name = {0}\n'.format(lib.getLibName()))
            fp.write("extends('template.lib')\n")


class Hierarchy:
    '''
    Generate a Hierarchy of C code
    '''
    hierarchy_path = None
    lib_count = None
    func_count_per_lib = None
    __builder = None

    def __init__(self, hierarchy_path, lib_count, func_count_per_lib, builder):
        self.hierarchy_path = hierarchy_path
        self.lib_count = int(lib_count)
        self.func_count_per_lib = int(func_count_per_lib)
        self.__builder = builder

    def create(self):
        '''
        Create files
        '''
        # Create root
        os.makedirs(self.hierarchy_path, exist_ok=True)

        # Create the apps and libs directories
        apps_path = self.hierarchy_path + '/apps'
        libraries_path = self.hierarchy_path + '/libs'

        # Create the libraries
        libraries = []
        for i in range(0, self.lib_count):
            base = i * self.func_count_per_lib
            lib_path = libraries_path + '/L{:03d}'.format(base)
            lib = Library(
                path=lib_path,
                func_range=range(base + 1, base + self.func_count_per_lib + 1))
            lib.create()
            libraries.append(lib)

        # Create a test app that invokes all of the library functions
        apps = []
        app_path = apps_path + '/testapp'
        app = Application(app_path, libraries=libraries)
        app.create()
        apps.append(app)

        # Create the Meson Builder in all of the directories
        #mesonBuilder = MesonBuilder()

        self.__builder.begRoot(self.hierarchy_path, apps_path, libraries_path)

        self.__builder.begAppBuilder(apps_path)
        for app in apps:
            self.__builder.addAppToAppBuilder(app)
        self.__builder.endAppBuilder

        self.__builder.begLibBuilder(libraries_path)
        for lib in libraries:
            self.__builder.addLibToLibBuilder(lib)
        self.__builder.endLibBuilder()

        self.__builder.endRoot()


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
    function_count_per_library = options.function_count_per_library

    if options.print_version:
        print('Version %s' % version)
        return 0

    builders = {'cmake': CMakeBuilder(), 'meson': MesonBuilder(),
                'creator': CreatorBuilder()}
    try:
        builder = builders[options.builder[0]]
    except:
        print("option builder is '{0}' must be 'cmake', 'creator' or 'meson'".format(
            options.builder))
        return 1

    hierarchy = Hierarchy(hierarchy_path[0], library_count[0],
                          function_count_per_library[0], builder)
    hierarchy.create()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
