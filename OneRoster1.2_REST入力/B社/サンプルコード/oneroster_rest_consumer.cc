/**
 * OneRoster REST Consumer client クラス
 */
#include "oneroster_rest_consumer.h"

#include "http_curl.h"

#include "oauth2_client.h"
#include "utility.h"

using namespace std;
using namespace picojson;

extern "C" {
};

/** Rostering Service 固定 path */
const char* COneRosterRestConsumer::ROSTERING_ENDPOINT_PATH_BASE = "/ims/oneroster/rostering/v1p2/";

/**
 * Constructor
 */
COneRosterRestConsumer::COneRosterRestConsumer()
{

}

/**
 * Destructor
 */
COneRosterRestConsumer::~COneRosterRestConsumer()
{
	return;
}

/**
 * 組織リストを取得する API にリクエストを行う
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * doAccessTokenRequest() を呼び出し元で実行しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response 取得したレスポンスボディを格納
 * @param[in] int offset 取得するリストの開始順番を指定する。
 * @param[in] int limit 取得するリストの件数を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getAllOrgs(string & response, int offset, int limit)
{
    string endpoint = this->m_provider_url 
        + ROSTERING_ENDPOINT_PATH_BASE + "orgs";
    int _limit = limit;
    int _offset = offset;
    if ( _limit <= 0 ) { 
        _limit = 100;
    }
    if ( _offset < 0 ) {
        _offset = 0;
    }
    endpoint += ::str_form("?limit=%d&offset=%d", _limit, _offset);
    try {
        if ( this->getData(response, endpoint, this->params) == false ) {
            return false;
        }
    } catch ( const char* e ) {
        this->m_error_message = e;
        return false;
    }
    return true;
}

/**
 * ユーザーリストを取得する API にリクエストを行う
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * doAccessTokenRequest() を呼び出し元で実行しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response_str 取得したレスポンスボディを格納
 * @param[in] int offset 取得するリストの開始順番を指定する。
 * @param[in] int limit 取得するリストの件数を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getAllUsers(string & response_str, int offset, int limit)
{
    string endpoint = this->m_provider_url 
        + ROSTERING_ENDPOINT_PATH_BASE + "users";

    return true;
}

/**
 * studentをリストで取得する API にリクエストを行う
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * doAccessTokenRequest() を呼び出し元で実行しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response_str 取得したレスポンスボディを格納
 * @param[in] int offset 取得するリストの開始順番を指定する。
 * @param[in] int limit 取得するリストの件数を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getAllStudents(string & response_str, int offset, int limit)
{
    string endpoint = this->m_provider_url 
        + ROSTERING_ENDPOINT_PATH_BASE + "students";
    int _limit = limit;
    int _offset = offset;
    if ( _limit <= 0 ) { 
        _limit = 100;
    }
    if ( _offset < 0 ) {
        _offset = 0;
    }
    endpoint += ::str_form("?limit=%d&offset=%d", _limit, _offset);
    endpoint += ::str_form("?limit=%d", _limit);
    try {
        if ( this->getData(response_str, endpoint, this->params) == false ) {
            return false;
        }
    } catch ( const char* e ) {
        this->m_error_message = e;
        return false;
    }
    return true;
}

/**
 * 指定した school ( org ) の sourcedId に紐づくstudentをリストで取得する API にリクエストを行う
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * doAccessTokenRequest() を呼び出し元で実行しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response_str 取得したレスポンスボディを格納
 * @param[in] std::string school_sourced_id student を取得する組織の sourcedId を指定する。
 * @param[in] int offset 取得するリストの開始順番を指定する。
 * @param[in] int limit 取得するリストの件数を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getStudentsForSchool(string & response_str, string school_sourced_id, int offset, int limit)
{
    string endpoint = this->m_provider_url 
        + ROSTERING_ENDPOINT_PATH_BASE + "schools/" + school_sourced_id + "/students";
    int _limit = limit;
    int _offset = offset;
    if ( _limit <= 0 ) { 
        _limit = 100;
    }
    if ( _offset < 0 ) {
        _offset = 0;
    }
    endpoint += ::str_form("?limit=%d&offset=%d", _limit, _offset);
    try {
        if ( this->getData(response_str, endpoint, this->params) == false ) {
            return false;
        }
    } catch ( const char* e ) {
        this->m_error_message = e;
        return false;
    }
    return true;
}

/**
 * teacher をリストで取得する API にリクエストを行う
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * doAccessTokenRequest() を呼び出し元で実行しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response_str 取得したレスポンスボディを格納
 * @param[in] int offset 取得するリストの開始順番を指定する。
 * @param[in] int limit 取得するリストの件数を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getAllTeachers(string & response_str, int offset, int limit)
{
    string endpoint = this->m_provider_url 
        + ROSTERING_ENDPOINT_PATH_BASE + "teachers";
    int _limit = limit;
    int _offset = offset;
    if ( _limit <= 0 ) { 
        _limit = 100;
    }
    if ( _offset < 0 ) {
        _offset = 0;
    }
    endpoint += ::str_form("?limit=%d&offset=%d", _limit, _offset);
    
    try {
        if ( this->getData(response_str, endpoint, this->params) == false ) {
            return false;
        }
    } catch ( const char* e ) {
        this->m_error_message = e;
        return false;
    }
    return true;
}

/**
 * 指定した school ( org ) の sourcedId に紐づく teacher をリストで取得する API にリクエストを行う
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * doAccessTokenRequest() を呼び出し元で実行しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response_str 取得したレスポンスボディを格納
 * @param[in] std::string school_sourced_id teacher を取得する組織の sourcedId を指定する。
 * @param[in] int offset 取得するリストの開始順番を指定する。
 * @param[in] int limit 取得するリストの件数を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getTeachersForSchool(string & response_str, string school_sourced_id, int offset, int limit)
{
    string endpoint = this->m_provider_url 
        + ROSTERING_ENDPOINT_PATH_BASE + "schools/" + school_sourced_id + "/teachers";
    int _limit = limit;
    int _offset = offset;
    if ( _limit <= 0 ) { 
        _limit = 100;
    }
    if ( _offset < 0 ) {
        _offset = 0;
    }
    endpoint += ::str_form("?limit=%d&offset=%d", _limit, _offset);
    try {
        if ( this->getData(response_str, endpoint, this->params) == false ) {
            return false;
        }
    } catch ( const char* e ) {
        this->m_error_message = e;
        return false;
    }
    return true;
}

/**
 * Service Provder に リクエストを行う private メンバ関数
 * 
 * AccessToken は すでに設定済の前提で動作する為、
 * あらかじめ doAccessTokenReques() で access token request を行い 
 * access token を取得しておくか、
 * setAccessToken() で 設定しておく必要がある。
 * @param[out] std::string response_str 取得したレスポンスボディを格納
 * @param[in] std::string endpoint 接続する URL を指定する。
 * @param[in] std::map<std::string, std::string> & params リクエストパラメータの名前と値の map を指定する。
 * @return bool
 */
bool COneRosterRestConsumer::getData(string & response_str, string endpoint, map<string, string> & params) 
{
    
    
    /* client credentials grant */

	CHttpClientCurl http();

    http.SetUrl(endpoint);
    http.SetRequestHeader("Authorization", ::str_form("bearer %s", this->m_access_token.c_str()));

    map<string, string>::iterator it;
    for ( it = params.begin(); it != params.end(); it++ ) {
        http.SetParamData(it->first, it->second);
    }
    SHttpResponse response = http.DoGet();
    if ( response.error_num != CHttpClientError::ERROR_NUM::NO_ERROR ) {
        this->m_error_message = ::str_form(
			"error [%d][status]:%d  [msg]: %s", 
			response.error_num,
			response.status_code,
			response.response_error_msg.c_str()
		));
        return false;
    }

    /* HTTP status 200 以外 の場合も reponse_body を使用する */
    response_str = response.response_body;

    try {
        // https://www.imsglobal.org/sites/default/files/spec/oneroster/v1p2/rostering-restbinding/OneRosterv1p2RosteringService_RESTBindv1p0.html#Main6p15
        if ( CHttpClientCurl::HTTP_STATUS_OK != response.status_code ) {
            string json_str = CUtil::HTMLDecode(response.response_body);
            picojson::value v;
            string err;
            parse(v, json_str.c_str(), json_str.c_str() + strlen(json_str.c_str()), &err);
            if ( !err.empty() ) {
                this->m_error_message = "レスポンスデータのパース時にエラーが発生しました。";
                return false;
            }
            picojson::object json = v.get<picojson::object>();
            if ( json.count("imsx_codeMajor") > 0 ) {
                if ( this->m_error_message.empty() == false ) { this->m_error_message += " "; }
                this->m_error_message += json["imsx_codeMajor"].to_str();
            }
            if ( json.count("imsx_severity") > 0 ) {
                if ( this->m_error_message.empty() == false ) { this->m_error_message += " "; }
                this->m_error_message += json["imsx_severity"].to_str();
            }
            if ( json.count("imsx_description") > 0 ) {
                if ( this->m_error_message.empty() == false ) { this->m_error_message += " "; }
                this->m_error_message += json["imsx_description"].to_str();
            }

            return false;
        } 
    } catch ( const char* e ) {
        this->m_error_message = e;
        return false;
    }
    
    return true;
}

/**
 * 認可サーバ に Access Token Request を行う
 * 
 * COAuth2Client class インスタンス の doAccessTokenRequest() を実行し、
 * access token request を行う。
 * 取得した access token は メンバ 変数 m_access_token に格納する。
 * @return bool
 */
bool COneRosterRestConsumer::doAccessTokenRequest() 
{
    if ( this->m_oauth2_client.GetTokenEndpoint().empty() ) {
        return false;
    }
    if ( this->m_oauth2_client.GetClientId().empty() ) {
        return false;
    }
    if ( this->m_oauth2_client.GetClientSecret().empty() ) {
        return false;
    }
    /* scope は optional */
    // if ( this->m_oauth2_client.GetScope().empty() ) {
    //     return false;
    // }

	if ( this->m_oauth2_client.doAccessTokenRequest(this->m_error_message) == false ) {
        if ( this->m_error_message.empty() == false ) {
            /* 認可エラーレスポンスではない部分のエラーメッセージ ( 通信エラー等も含む ) */
        } else if ( this->m_oauth2_client.getErrorResponse().error.empty() == false ) {
            /* リクエストは成功したが、認可エラーレスポンスが返っている */
            this->m_error_message += this->m_oauth2_client.getErrorResponse().error;
            if ( this->m_oauth2_client.getErrorResponse().error_description.empty() == false ) {
                this->m_error_message += (" description: " + this->m_oauth2_client.getErrorResponse().error_description);
            }
        }
        return false;
    }

    this->m_access_token = this->m_oauth2_client.getAccessToken();
    return true;
}

/**
 * メンバ変数 m_access_token の値を取得する。
 * 
 * @return std::string
 */
string COneRosterRestConsumer::getAccessToken() 
{
    return this->m_access_token;
}

/**
 * メンバ変数 m_access_token に 値を設定する。
 * 
 * @param[in] std::string accessToken
 * @return bool
 */
bool COneRosterRestConsumer::setAccessToken(string accessToken) 
{
    this->m_access_token = accessToken;
    return true;
}

/**
 * メンバ変数の COAuth2Client class インスタンス に access token request endpoint を設定する.
 * 
 * @param[in] std::string endpoint
 * @return bool
 */
bool COneRosterRestConsumer::setOAuth2TokenEndpoint(string endpoint) 
{
    return this->m_oauth2_client.SetTokenEndpoint(endpoint);
}

/**
 * メンバ変数の COAuth2Client class インスタンス に access token request 用の client id を設定する。
 * 
 * @param[in] std::string client_id
 * @return bool
 */
bool COneRosterRestConsumer::setOAuth2CliendId(string client_id) 
{
    return this->m_oauth2_client.SetClientId(client_id);
}

/**
 * メンバ変数の COAuth2Client class インスタンス に access token request 用の client secret を設定する。
 * 
 * @param[in] std::string secret
 * @return bool
 */
bool COneRosterRestConsumer::setOAuth2clientSecret(string secret) 
{
    return this->m_oauth2_client.SetClientSecret(secret);
}

/**
 * メンバ変数の COAuth2Client class インスタンス に access token request 用の scope を設定する。
 * 
 * @param[in] std::string scope
 * @return bool
 */
bool COneRosterRestConsumer::setOAuth2Scope(string scope) 
{
    return this->m_oauth2_client.SetScope(scope);
}

/**
 * メンバ変数の COAuth2Client class インスタンス に設定されているaccess token request endpoint を取得する。
 * 
 * @return std::string
 */
string COneRosterRestConsumer::getOAuth2TokenEndpoint() 
{
    return this->m_oauth2_client.GetTokenEndpoint();
}

/**
 * メンバ変数の COAuth2Client class インスタンス に設定されている client id の値を取得する。
 * 
 * @return std::string
 */
string COneRosterRestConsumer::getOAuth2CliendId() 
{
    return this->m_oauth2_client.GetClientId();
}

/**
 * メンバ変数の COAuth2Client class インスタンス に設定されている client secret の値を取得する。
 * 
 * @return std::string
 */
string COneRosterRestConsumer::getOAuth2clientSecret() 
{
    return this->m_oauth2_client.GetClientSecret();
}

/**
 * メンバ変数の COAuth2Client class インスタンス に設定されている scope の値を取得する。
 * 
 * @return std::string
 */
string COneRosterRestConsumer::getOAuth2Scope() 
{
    return this->m_oauth2_client.GetScope();
}

/**
 * OneRosterREST Service Provider の サーバ URL を指定する。
 * 
 * 固定パスの /ims/oneroster/rostering/v1p2/ は 処理内で接続時に
 * 付与する為、不要。
 * @param[in] std::string provider_url
 * @return bool
 */
bool COneRosterRestConsumer::setProviderUrl(string provider_url) 
{
    this->m_provider_url = provider_url;
    return true;
}

/**
 * メンバ変数 から error message を 取得する。
 * 
 * 処理内でエラーが起こった場合等にエラーメッセージが格納されている。
 * @return std::string
 */
string COneRosterRestConsumer::getErrorMessage()
{
    return this->m_error_message;
}