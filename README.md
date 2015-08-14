# Generate sources
==================
A program to generate source tree which is used
to test different build systems performance.

It currenly supports cmake and meson. To generate
a tree execute gen_srcs.py with 4 parameters:
```
./gen_srcs.py <builder> <directory> <number of libraries> <number of functions per library>
```
Below is an example of with the meson builder the directory
is test and there is one library and one fuction per library:
```
$ ./gen_srcs.py meson test 1 1

$ tree test
test
├── apps
│   ├── meson.build
│   └── testapp
│       ├── meson.build
│       └── src
│           └── main.c
├── libs
│   ├── L000
│   │   ├── include
│   │   │   └── L000.h
│   │   ├── meson.build
│   │   └── src
│   │       └── L000.c
│   └── meson.build
└── meson.build

7 directories, 8 files

$ cat test/apps/testapp/src/main.c
#include <stdio.h>
#include "L000.h"
int main(void) {
  func1();
  return 0; // ok
}

$ cat test/libs/L000/include/L000.h 
// header....

#ifndef  __HOME_WINK_PRGS_TEST_GEN_SRCS_TEST_LIBS_L000_INCLUDE_L000_H__
#define __HOME_WINK_PRGS_TEST_GEN_SRCS_TEST_LIBS_L000_INCLUDE_L000_H__

#include <stdio.h>

typedef int L000_status;

void func1(void);

#endif // __HOME_WINK_PRGS_TEST_GEN_SRCS_TEST_LIBS_L000_INCLUDE_L000_H__

$ cat test/libs/L000/src/L000.c 
// Test library 1

#include "L000.h"

// func1
void func1(void) {
    printf("func1\n");
}
```

To test
```
mkdir test/build
cd test/build
meson ..
ninja
./apps/testapp/testapp
```
And the output would be:
```
$ mkdir test/build

$ cd test/build

$ meson ..
The Meson build system
Version: 0.26.0-research
Source dir: /home/wink/prgs/test/gen_srcs/test
Build dir: /home/wink/prgs/test/gen_srcs/test/build
Build type: native build
Build machine cpu: x86_64
Project name: hierarchy
Native c compiler: ccache cc (gcc 4.9.2-10ubuntu13)
Build targets in project: 2

$ ninja
[4/4] Linking target apps/testapp/testapp

$ ./apps/testapp/testapp
func1
```
