// this file is auto generated by amalgamation.
// DO NOT EDIT this file.

#pragma once
/// include.h START

#ifndef INCLUDE_H
#define INCLUDE_H

/// not removed

#include <iostream>

static const std::string s = "\
these codes are not removed:\
#include<cstddef>\
// slash comments\
/// comments\
     #define AAA 123\
";
/// the indent before #define should be kept
#define BBB 12 /// the white space before #define should be deleted
inline void f()
{
    std::cout << "what" << std::endl;
}

/// inc2.h START

#include<cstdio>

#include<cstddef>
/// note that all "#pragma once" will be deleted

/// inc2.h END

#endif

/// include.h END
