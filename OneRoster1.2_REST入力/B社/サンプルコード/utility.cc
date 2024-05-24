
/**
 * utility 
 */
#include "utility.h"
#include <string>
#include <sstream>
#include <cstdio>
#include <cstdarg>

extern "C" {
}

using namespace std;

/**
 * printf 形式で文字列を作成し、std::string で返す
 * 
 * @param[in] const char* kpszFormat
 * @param[out] printf 形式の引数 
 * @return const string
 */
const string str_form(const char* kpszFormat, ...)
{
	va_list arg_list;
	size_t  iBuffSize;
	char*   pszBuff;
	string  strResult;

	va_start(arg_list, kpszFormat);
	iBuffSize = vsnprintf(NULL, 0, kpszFormat, arg_list) + 4;
	va_end(arg_list);

	pszBuff = new char[iBuffSize];

	va_start(arg_list, kpszFormat);
	vsnprintf(pszBuff, iBuffSize, kpszFormat, arg_list);
	va_end(arg_list);

	strResult = pszBuff;
	delete[] pszBuff;
	return strResult;
}
