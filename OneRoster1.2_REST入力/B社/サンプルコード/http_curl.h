/**
 * libcurl を利用する為の libcurl wrapper クラス
 */
#pragma once

#ifndef CHTTP_CLIENT_CURL_H_
#define CHTTP_CLIENT_CURL_H_

#include "util.h"

#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <cstring>
#include <vector>
#include <map>

#include <curl/curl.h>

using namespace std;

extern "C" {
};

/**
 * HttpRespose用 構造体
 */
struct SHttpResponse {
    int error_num;
    long status_code;
    string response_error_msg;
    string response_body;
};

/**
 * error 処理用クラス
 */
class CHttpClientError
{
public:
    /**
     * @enum ERROR_NUM エラー番号
     */
    enum ERROR_NUM {
        NO_ERROR = 0,
        URL_ERROR,
        OTHER_ERROR
    };
};

/**
 * libcurl を利用する為の libcurl wrapper クラス
 */
class CHttpClientCurl
{
public:
    /** http status 200 */
    static const long HTTP_STATUS_OK = 200L;
    /** http status 400 */
    static const long HTTP_STATUS_BAD_REQUEST  = 400L;
    /** http status 401 */
    static const long HTTP_STATUS_UNAUTHORIZED = 401L;
    /** http status 403 */
    static const long HTTP_STATUS_FORBIDDEN = 403L;
    /** http status 404 */
    static const long HTTP_STATUS_NOTFOUND = 404L;
    
    /**
     * @enum RECEIVE_TYPE 応答をファイルに出力するかメモリに持つか
     */
    enum RECEIVE_TYPE {
        ON_MEMORY = 1,
        OUT_FILE
    };
public:
    /** libcurl の初期化処理を呼ぶ wrapper 関数 */
    static bool LibraryGlobalInit();
    /** libcurl の終了処理を呼ぶ wrapper 関数 */
    static void LibraryGlobalCleanup();

public:
    /** constructor */
    CHttpClientCurl();
    /** destructor */
    virtual ~CHttpClientCurl();
    /** リクエストを送るURLを設定する。 */
    bool SetUrl(string url);
    /** リクエストする際の要求ヘッダの key, value を設定する。 */
    bool SetRequestHeader(string key, string value);
    /** リクエストする際のパラメータの key, value を設定する。 */
    bool SetParamData(string key, string value);
    /** 応答から取得する予定の ヘッダ名を設定する。 */
    bool SetHeaderWantToGet(string key);
    /** 応答ヘッダの値を取得する */
    string GetResponseHeader(string key);
    /** 応答bodyをファイルに出力するかメモリに持つかを設定する。 */
    bool SetReceiveType(RECEIVE_TYPE receive_type);
    /** 応答bodyをファイルに出力する場合の出力先ファイルパスを指定 */
    bool SetWriteFilePath(string write_file_path);
    /** 応答リクエストを指定されたURLにPOSTする。 */
    SHttpResponse DoPost();
    /** 応答リクエストを指定されたURLに GET でリクエストする。 */
    SHttpResponse DoGet();

private:
    string m_url;
    map<string, string> m_mapextend_header;
    map<string, string> m_mapparam_data;
    map<string, string> m_mapresponse_header;
    vector<string> m_vecheader_want;

    CHttpClientCurl::RECEIVE_TYPE m_receive_type; 
    string m_response_body;
    std::ofstream* m_ofs;
    FILE** m_out_file;
    string m_out_file_path;

    /** 応答ヘッダを指定する。内部関数。 */
    bool SetResponseHeader(string key, string val);
    /** 応答受信時に 複数回呼ばれるヘッダ解析用の処理 */
    size_t analizeHeader(char *buffer, size_t size, size_t nitems);
    /** 応答受信時に 複数回呼ばれるコールバック関数に呼ばれる文字列を記憶する処理. */
    size_t receiveResponse(char *buffer, size_t size, size_t nitems);

    /** 応答受信時に 複数回呼ばれるcallback */
    static size_t callBackFunction(char* buffer, size_t size, size_t nitems, void* http_curl);
    /** 応答受信時に 複数回呼ばれるヘッダ解析用の　callBack */
    static size_t callBackHeader(char *buffer, size_t size, size_t nitems, void *userdata);
};

#endif /* CHTTP_CLIENT_CURL_H_ */

