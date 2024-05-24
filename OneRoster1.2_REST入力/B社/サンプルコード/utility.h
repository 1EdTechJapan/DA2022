/**
 * utility.h
 */

#pragma once 

#include <string>
#include <cstdlib>
#include <pthread.h>

using std::string;

/*
 * printf 形式で文字列を作成し、std::string で返す
 */
extern const string str_form(const char* kpszFormat, ...);
