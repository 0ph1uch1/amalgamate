#ifndef INCLUDE_H
#define INCLUDE_H

// removed
// removed
/// not removed

#include <iostream>

static const std::string s = "\
these codes are not removed:\
#include<cstddef>\
// slash comments\
/// comments\
     #define AAA 123\
"; // this is an invalid comment
/// the indent before #define should be kept
 #define BBB 12 /// the white space before #define should be deleted
inline void f()
{
    std::cout << "what" << std::endl;
}

#include "inc2.h"

#endif