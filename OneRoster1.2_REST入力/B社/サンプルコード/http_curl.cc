/**
 * libcurl を利用する為の libcurl wrapper クラス
 */
#include "http_curl.h"
#include "utility.h"

using namespace std;

/**
 * constructor 
 */
CHttpClientCurl::CHttpClientCurl()
{
    /* デフォルト受け取り方法 メモリ に受け取る */
    this->m_receive_type = RECEIVE_TYPE::ON_MEMORY;
}

/**
 * destructor 
 */
CHttpClientCurl::~CHttpClientCurl()
{
	return;
}

/**
 * リクエストを送るURLを設定する。
 * 
 * @param[in] std::string url リクエストを送るURL
 * @return bool
 */
bool CHttpClientCurl::SetUrl(string url)
{
    if ( url.empty() ) {
        return false;
    }
    this->m_url = string(url.c_str());

    return true;
}

/**
 * リクエストする際のパラメータの key, value を設定する。
 * 
 * すでに 同一 key が設定されている存在する場合は上書きする。
 * @param[in] std::string key パラメータキー
 * @param[in] std::string value パラメータ値
 * @return bool
 */
bool CHttpClientCurl::SetParamData(string key, string value)
{
     if ( key.empty() ) {
        return false;
    }
    if ( value.empty() ) {
        return false;
    }
    this->m_mapparam_data[key] = value;

    return true;
}

/**
 * リクエストする際の要求ヘッダの key, value を設定する。
 * 
 * すでに 同一 ヘッダ が設定されている存在する場合は上書きする。
 * @param[in] std::string key ヘッダ名
 * @param[in] std::string value ヘッダの値
 * @return bool
 */
bool CHttpClientCurl::SetRequestHeader(string key, string value)
{
    if ( key.empty() ) {
        return false;
    }
    if ( value.empty() ) {
        return false;
    }
    this->m_mapextend_header[key] = value;
    return true;
}

/**
 * 応答ヘッダを指定する。内部関数。
 * 
 * すでに 同一 ヘッダ が設定されている存在する場合は上書きする。
 * @param[in] std::string key ヘッダ名
 * @param[in] std::string value ヘッダの値
 * @return bool
 */
bool CHttpClientCurl::SetResponseHeader(string key, string value)
{
    if ( key.empty() ) {
        return false;
    }
    if ( value.empty() ) {
        return false;
    }
    this->m_mapresponse_header[key] = value;
    return true;
}

/**
 * 応答bodyをファイルに出力するかメモリに持つかを設定する。
 * 
 * @param[in] RECEIVE_TYPE receive_type
 * @return bool
 */
bool CHttpClientCurl::SetReceiveType(RECEIVE_TYPE receive_type)
{
    if ( !receive_type ) {
        return false;
    }
    if ( receive_type != RECEIVE_TYPE::ON_MEMORY && receive_type != RECEIVE_TYPE::OUT_FILE ) {
        return false;
    }
    this->m_receive_type = receive_type;
    return true;
}

/**
 * 応答bodyをファイルに出力する場合の出力先ファイルパスを指定
 * 
 * @param[in] std::string write_file_path
 * @return bool
 */
bool CHttpClientCurl::SetWriteFilePath(string write_file_path)
{
    if ( write_file_path.empty() ) {
        return false;
    }
    
    this->m_out_file_path = write_file_path;
    return true;
}

/**
 * 応答から取得する予定の ヘッダ名を設定する。
 * 
 * 予め設定しておかなければ取得できない。
 * @param[in] std::string key 
 * @return bool
 */
bool CHttpClientCurl::SetHeaderWantToGet(string key) 
{
    if ( key.empty() ) {
        return false;
    }
    if ( this->m_vecheader_want.size() > 0 ) {
        vector<string>::iterator it;
        for ( it = this->m_vecheader_want.begin(); it != this->m_vecheader_want.end(); it++ ) {
            if ( key.compare((*it).c_str()) == 0 ) {
                return false;
            }
        }
    }

    this->m_vecheader_want.push_back(key);

    return true;
}

/**
 * 応答ヘッダの値を取得する
 * 
 * 予め設定しておかなければ取得できない。
 * @param[in] std::string 応答ヘッダ名を指定 
 * @return std::string 
 */
string CHttpClientCurl::GetResponseHeader(const string key) {
    return this->m_mapresponse_header[key];
}

/**
 * 応答リクエストを指定されたURLにPOSTする。
 * 
 * @return SHttpResponse レスポンス構造体に必要な応答情報を格納し返す。
 */
SHttpResponse CHttpClientCurl::DoPost()
{
    SHttpResponse response;
    response.error_num = CHttpClientError::ERROR_NUM::NO_ERROR;
    response.response_body = "";

    if ( this->m_url.empty() ) {
        response.error_num =  CHttpClientError::ERROR_NUM::URL_ERROR;
        response.response_error_msg = "URL が 空です。";
        return response;
    }

    if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE && this->m_out_file_path.empty() ) {
        response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
        response.response_error_msg = "出力先ファイルパスが設定されていません。";
        return response;
    } 

    string param_data;
    if ( this->m_mapparam_data.size() > 0 ) {
        map<string, string>::iterator it;
        size_t cnt = 0;
        for (it = this->m_mapparam_data.begin(); it != this->m_mapparam_data.end(); it++, cnt++) {
            string key = it->first;
            string val = it->second;

            if ( !param_data.empty() ) {
                param_data += "&";
            }

            param_data += (key + "=" + val);
        }
    }

    CURL *curl;
    CURLcode res;
    curl = curl_easy_init();
    std::ofstream ofs;
    string header;
    struct curl_slist * headerList = NULL;
    if ( curl ) {
        if ( this->m_mapextend_header.size() > 0 ) {
            map<string, string>::iterator itr;
            for ( itr = this->m_mapextend_header.begin(); itr != this->m_mapextend_header.end(); itr++) {
                string key = itr->first;
                string val = itr->second;

                string header_string = ::str_form("%s: %s", key.c_str(), val.c_str());

                headerList = curl_slist_append(headerList, header_string.c_str());
            }

            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerList);
        }
        
        curl_easy_setopt(curl, CURLOPT_URL, this->m_url.c_str());
        
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, param_data.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, strlen(param_data.c_str()));

        curl_easy_setopt(curl, CURLOPT_PROXY, "");

        if ( this->m_vecheader_want.size() > 0) {
            curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION,CHttpClientCurl::callBackHeader);
            curl_easy_setopt(curl, CURLOPT_HEADERDATA, this);
        }

        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, CHttpClientCurl::callBackFunction);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, this);

        if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE ) {
            ofs.open(this->m_out_file_path, ios::out | ios::binary);
            this->m_ofs = &ofs;
        } 


        res = curl_easy_perform(curl);

        if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE && ofs.is_open()) {
            ofs.close();
        }
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response.status_code);
        curl_slist_free_all(headerList);
        curl_easy_cleanup(curl);
    }
    if ( res != CURLE_OK ) {
        if ( res == CURLE_UNSUPPORTED_PROTOCOL ) {
            response.error_num = CHttpClientError::ERROR_NUM::URL_ERROR;
            response.response_error_msg = "通信エラー: サポート外のプロトコルです。";
        } else if ( res == CURLE_FAILED_INIT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "内部エラー: ライブラリの初期化に失敗しました。";
        } else if ( res == CURLE_COULDNT_RESOLVE_HOST ) {
            response.error_num = CHttpClientError::ERROR_NUM::URL_ERROR;
            response.response_error_msg = "通信エラー: ホストを解決できませんでした。";
        } else if ( res == CURLE_COULDNT_CONNECT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: サーバへの接続に失敗しました。";
        } else if ( res == CURLE_OUT_OF_MEMORY ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "内部エラー: メモリ割り当てに失敗しました。";
        } else if ( res == CURLE_REMOTE_ACCESS_DENIED ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: アクセスが拒否されました。";
        } else if ( res == CURLE_OPERATION_TIMEDOUT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: タイムアウトしました。";
        } else if ( res == CURLE_SSL_CACERT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: 証明書関連のエラーが発生しました。";
        } else {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "その他のエラーが発生しました。";
        }
        return response;
    } 

    response.response_body = this->m_response_body;
    return response;
}

/**
 * 応答リクエストを指定されたURLに GET でリクエストする。
 * 
 * @return SHttpResponse レスポンス構造体に必要な応答情報を格納し返す。
 */
SHttpResponse CHttpClientCurl::DoGet()
{
    SHttpResponse response;
    response.error_num = CHttpClientError::ERROR_NUM::NO_ERROR;
    response.response_body = "";

    if ( this->m_url.empty()) {
        response.error_num =  CHttpClientError::ERROR_NUM::URL_ERROR;
        response.response_error_msg = "URL が 空です。";
        return response;
    }

    if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE && this->m_out_file_path.empty() ) {
        response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
        response.response_error_msg = "出力先ファイルパスが設定されていません。";
        return response;
    } 

    CURL *curl;
    CURLcode res;
    curl = curl_easy_init();
    std::ofstream ofs;
    string header;
    struct curl_slist * headerList = NULL;
    if ( curl ) {
        /* querystring を作成する */
        string query_string = "";
        if ( this->m_mapparam_data.size() > 0 ) {
            map<string, string>::iterator it;
            size_t cnt = 0;
            for ( it = this->m_mapparam_data.begin(); it != this->m_mapparam_data.end(); it++, cnt++ ) {
                string key = it->first;
                string val = it->second;
                char* encval = curl_easy_escape(curl, val.c_str(), strlen(val.c_str()));

                if ( !query_string.empty() ) {
                    query_string += "&";
                }

                query_string += (key + "=" + string(encval));
                curl_free(encval);
            }

            if ( query_string.empty() == false ) {
                query_string = "?" + query_string;
            }
        }
        string url = this->m_url + query_string;

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());

        if ( this->m_mapextend_header.size() > 0 ) {
            map<string, string>::iterator itr;
            for ( itr = this->m_mapextend_header.begin(); itr != this->m_mapextend_header.end(); itr++) {
                string key = itr->first;
                string val = itr->second;

                string header_string = ::str_form("%s: %s", key.c_str(), val.c_str());

                headerList = curl_slist_append(headerList, header_string.c_str());
            }
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headerList);
        }

        if ( this->m_vecheader_want.size() > 0) {
            curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION,CHttpClientCurl::callBackHeader);
            curl_easy_setopt(curl, CURLOPT_HEADERDATA, this);
        }

        curl_easy_setopt(curl, CURLOPT_PROXY, "");

        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, CHttpClientCurl::callBackFunction);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, this);

        if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE ) {
            ofs.open(this->m_out_file_path, ios::out | ios::binary);
            if ( !ofs ) {
            }
            this->m_ofs = &ofs;

        }

        res = curl_easy_perform(curl);

        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response.status_code);

        if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE && ofs.is_open()) {
            ofs.close();
        }
        curl_slist_free_all(headerList);
        curl_easy_cleanup(curl);

    }
    if ( res != CURLE_OK ) {
        if ( res == CURLE_UNSUPPORTED_PROTOCOL ) {
            response.error_num = CHttpClientError::ERROR_NUM::URL_ERROR;
            response.response_error_msg = "通信エラー: サポート外のプロトコルです。";
        } else if ( res == CURLE_FAILED_INIT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "内部エラー: ライブラリの初期化に失敗しました。";
        } else if ( res == CURLE_COULDNT_RESOLVE_HOST ) {
            response.error_num = CHttpClientError::ERROR_NUM::URL_ERROR;
            response.response_error_msg = "通信エラー: ホストを解決できませんでした。";
        } else if ( res == CURLE_COULDNT_CONNECT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: サーバへの接続に失敗しました。";
        } else if ( res == CURLE_OUT_OF_MEMORY ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "内部エラー: メモリ割り当てに失敗しました。";
        } else if ( res == CURLE_REMOTE_ACCESS_DENIED ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: アクセスが拒否されました。";
        } else if ( res == CURLE_OPERATION_TIMEDOUT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: タイムアウトしました。";
        } else if ( res == CURLE_SSL_CACERT ) {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "通信エラー: 証明書関連のエラーが発生しました。";
        } else {
            response.error_num = CHttpClientError::ERROR_NUM::OTHER_ERROR;
            response.response_error_msg = "その他のエラーが発生しました。";
        }
        return response;
    } 

    response.response_body = this->m_response_body;
    return response;
}

/**
 * 応答受信時に 複数回呼ばれるコールバック関数に呼ばれる文字列を記憶する処理.
 * 
 * RECIEVE_TYPE によって異なる先に書き込む。
 * @param[in] char* buffer 
 * @param[in] size_t size 
 * @param[in] size_t nitems 
 * @return size_t 
 */
size_t CHttpClientCurl::receiveResponse(char *buffer, size_t size, size_t nitems)
{
    int realsize = size * nitems;

    if (this->m_receive_type == RECEIVE_TYPE::ON_MEMORY) {
        this->m_response_body.append(buffer, realsize);
    } else if ( this->m_receive_type == RECEIVE_TYPE::OUT_FILE) {
        this->m_ofs->write(buffer, realsize);
    }

    return realsize;
}

/**
 * 応答受信時に 複数回呼ばれるヘッダ解析用の処理
 * 
 * 予め設定した取得したい応答ヘッダのみをメンバ変数に読み込む。
 * @param[in] char* buffer 
 * @param[in] size_t size 
 * @param[in] size_t nitems 
 * @return size_t 
 */
size_t CHttpClientCurl::analizeHeader(char *buffer, size_t size, size_t nitems)
{
    if ( this->m_vecheader_want.size() > 0 ) {
        vector<string>::iterator it;
        for ( it = this->m_vecheader_want.begin(); it != this->m_vecheader_want.end(); it++ ) {
            string search_header = *it + ":";
            size_t len = strlen(search_header.c_str());
            string bufstr = string(buffer);
            if ( bufstr.length() > len && 
                (bufstr.substr(0, len).compare(search_header.c_str()) == 0)) {
                if ( bufstr.substr(bufstr.length() - 2).compare("\r\n") == 0 ) {
                    bufstr = bufstr.substr(0, bufstr.length() - 2);
                }
                this->SetResponseHeader(*it, bufstr.substr(len));
            }
        }
    } 
    return nitems * size;
}

/**
 * 応答受信時に 複数回呼ばれるcallback
 * 
 * @param[in] char* buffer 
 * @param[in] size_t size 
 * @param[in] size_t nitems 
 * @return size_t 
 */
size_t CHttpClientCurl::callBackFunction(char* buffer, size_t size, size_t nitems, void* http_curl)
{
    CHttpClientCurl *client = ( CHttpClientCurl* ) http_curl;

    return client->receiveResponse(buffer, size, nitems);
}

/**
 * 応答受信時に 複数回呼ばれるヘッダ解析用の　callBack 
 * 
 * @param[in] char* buffer 
 * @param[in] size_t size 
 * @param[in] size_t nitems 
 * @return size_t 
 */
size_t CHttpClientCurl::callBackHeader(char *buffer, size_t size, size_t nitems, void *userdata)
{
    CHttpClientCurl *client = ( CHttpClientCurl* ) userdata;

    return client->analizeHeader(buffer, size, nitems);
}

/**
 * libcurl の初期化処理を呼ぶ wrapper 関数
 * 
 * @return bool
 */
bool CHttpClientCurl::LibraryGlobalInit()
{
    return curl_global_init(CURL_GLOBAL_DEFAULT);
}

/**
 * libcurl の終了処理を呼ぶ wrapper 関数
 * 
 * @return bool
 */
void CHttpClientCurl::LibraryGlobalCleanup()
{
    curl_global_cleanup();
}