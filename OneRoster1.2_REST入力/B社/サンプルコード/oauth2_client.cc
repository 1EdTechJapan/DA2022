/**
 * OAuth2.0 Client クラス
 */
#include "oauth2_client.h"

#include "http_curl.h"
#include "base64.h"
#include "utility.h"

using namespace std;
// using namespace picojson;

extern "C" {
};

const char* COAuth2Client::GRANT_TYPE_KEY = "grant_type";
const char* COAuth2Client::GRANT_TYPE_VAL_CLIENT_CREDENTIALS = "client_credentials";

const char* COAuth2Client::SCOPE_KEY = "scope";

/* access_token REQUIERD Access Token Response Param */
const char* COAuth2Client::ACCESS_TOKEN_KEY = "access_token";
/* token_type REQUIERD Access Token Response Param */
const char* COAuth2Client::TOKEN_TYPE_KEY   = "token_type";
/* expires_in REQUIERD Access Token Response Param */
const char* COAuth2Client::EXPIRES_IN_KEY    = "expires_in";
/* refresh_token OPTIONAL Access Token Response Param */
const char* COAuth2Client::REFRESH_TOKEN_KEY    = "refresh_token";

/**
 * Constructor
 */
COAuth2Client::COAuth2Client()
{

}

/**
 * Destructor
 */
COAuth2Client::~COAuth2Client()
{
	return;
}

/**
 * access token request 接続先 endpoint 設定
 * 
 * @param[in] std::string endpoint
 * @return bool
 */
bool COAuth2Client::SetTokenEndpoint(string endpoint)
{
    if ( endpoint.empty() ) {
        return false;
    }
    this->m_token_endpoint = string(endpoint.c_str());

    return true;
}

/**
 * access token request 接続先 endpoint 取得
 * 
 * @return std::string
 */
string COAuth2Client::GetTokenEndpoint()
{
    return this->m_token_endpoint;
}

/**
 * access token request parameter grant_type 設定
 * 
 * @param[in] std::string grant_type
 * @return bool
 */
bool COAuth2Client::SetGrantType(string grant_type)
{
    if ( grant_type.empty() ) {
        return false;
    }
    this->m_grant_type = string(grant_type.c_str());

    return true;
}

/**
 * access token request parameter grant type 取得
 * 
 * @return std::string
 */
string COAuth2Client::GetGrantType()
{
    return this->m_grant_type;
}

/**
 * access token request parameter scope 設定
 * 
 * @param[in] std::string scope
 * @return bool
 */
bool COAuth2Client::SetScope(string scope)
{
    if ( scope.empty() ) {
        return false;
    }
    this->m_scope = string(scope.c_str());

    return true;
}

/**
 * access token request parameter scope 取得
 * 
 * @return std::string
 */
string COAuth2Client::GetScope()
{
    return this->m_scope;
}

/**
 * access token request authorization client_id 設定
 * 
 * @param[in] std::string client_id
 * @return bool
 */
bool COAuth2Client::SetClientId(string client_id)
{
    if ( client_id.empty() ) {
        return false;
    }
    this->m_client_id = string(client_id.c_str());

    return true;
}

/**
 * access token request authorization client_id 取得
 * 
 * @return std::string
 */
string COAuth2Client::GetClientId()
{
    return this->m_client_id;
}

/**
 * access token request authorization client_secret 設定
 * 
 * @param[in] std::string client_secret
 * @return bool
 */
bool COAuth2Client::SetClientSecret(string client_secret)
{
    if ( client_secret.empty() ) {
        return false;
    }
    this->m_client_secret = string(client_secret.c_str());

    return true;
}

/**
 * access token request authorization client_secret 取得
 * 
 * @return std::string
 */
string COAuth2Client::GetClientSecret()
{
    return this->m_client_secret;
}

/**
 * access token request を 認可サーバ に要求
 * 
 * 取得したaccess_token は メンバ変数の 
 * SAccessTokenResponse 構造体 インスタンスに格納する
 * @param[out] std::string errmsg エラー時、エラーメッセージを格納
 * @return bool
 */
bool COAuth2Client::doAccessTokenRequest(string& errmsg) 
{
    if ( this->m_token_endpoint.empty() ) {
        errmsg = "Access Token Request の Endpoint が指定されていません。";
        return false;
    }
    if ( this->m_client_id.empty() ) {
        errmsg = "client id が指定されていません。";
        return false;
    }
    if ( this->m_client_secret.empty() ) {
        errmsg = "client_secret が指定されていません。";
        return false;
    }
    if ( this->m_grant_type.empty() ) {
        this->m_grant_type = COAuth2Client::GRANT_TYPE_VAL_CLIENT_CREDENTIALS;
    }

    string credential;
    this->generateEncodeCredential(credential);

	CHttpClientCurl http();

    http.SetUrl(this->m_token_endpoint);
    http.SetRequestHeader("Authorization", ::str_form("basic %s", credential.c_str()));

    http.SetParamData(COAuth2Client::GRANT_TYPE_KEY, this->m_grant_type);
    if ( this->m_scope.empty() == false ) {
        http.SetParamData(COAuth2Client::SCOPE_KEY,      this->m_scope);
    }

    SHttpResponse response = http.DoPost();
    if ( response.error_num != CHttpClientError::ERROR_NUM::NO_ERROR ) {
        string msg = ::str_form(
			"error num:%d status:%d msg:%s", 
			response.error_num,
			response.status_code,
			response.response_error_msg.c_str()
		);
        errmsg = msg;
        return false;
    }

    try {
        string json_str = CUtil::HTMLDecode(response.response_body);
        picojson::value v;
        string err;
        parse(v, json_str.c_str(), json_str.c_str() + strlen(json_str.c_str()), &err);
        if ( !err.empty() ) {
            errmsg = "レスポンスデータのパース時にエラーが発生しました。";
            return false;
        }

        picojson::object json = v.get<picojson::object>();
        if ( response.status_code == CHttpClientCurl::HTTP_STATUS_BAD_REQUEST || json.count("error") > 0 ) {
            /* 認可エラーレスポンス */
            if ( json.count("error") > 0 ) {
                this->m_error_response.error = json["error"].to_str();
            }
            if ( json.count("error_description") > 0 ) {
                this->m_error_response.error_description = json["error_description"].to_str();
            }
            if ( json.count("error_uri") > 0 ) {
                this->m_error_response.error_description = json["error_uri"].to_str();
            }
            return false;
        }
        
        /* 成功 */
        /* 必須項目 */
        if ( json.count(COAuth2Client::ACCESS_TOKEN_KEY) > 0 ) {
            this->m_access_token_response.access_token = json[COAuth2Client::ACCESS_TOKEN_KEY].to_str();
        }
        /* 必須項目 */
        if ( json.count(COAuth2Client::TOKEN_TYPE_KEY) > 0 ) {
            this->m_access_token_response.token_type = json[COAuth2Client::TOKEN_TYPE_KEY].to_str();
        }
        /* 必須項目 */
        if ( json.count(COAuth2Client::EXPIRES_IN_KEY) > 0 ) {
            this->m_access_token_response.expires_in = json[COAuth2Client::EXPIRES_IN_KEY].to_str();
        }
        /* OPTIONAL */
        if ( json.count(COAuth2Client::REFRESH_TOKEN_KEY) > 0 ) {
            this->m_access_token_response.refresh_token = json[COAuth2Client::REFRESH_TOKEN_KEY].get<string>();
        }
        /* リクエストで state を送信した場合は 必須 */
        if ( json.count(COAuth2Client::SCOPE_KEY) > 0 ) {
            this->m_access_token_response.scope = json[COAuth2Client::SCOPE_KEY].get<string>();
        }

    } catch ( const char* e ) {
        errmsg = e;
        return false;
    }

    return true;
}

/**
 * メンバ変数 SAccessTokenResponse 構造体インスタンス に格納されている、
 * access_token を取得する。
 * 
 * 認可サーバへの access token request が成功した場合のみ値が格納されている。
 * 呼び出す前に doAccessTokenRequest() を呼び出し認可サーバに access token request 
 * を行う必要がある。
 * @return std::string
 */
string COAuth2Client::getAccessToken()
{
    return this->m_access_token_response.access_token;
}

/**
 * client_id , client_secret を Ahthorization Header 用の 文字列に変換する。
 * 
 * あらかじめ メンバ変数の m_client_id と m_client_secret に値が設定されている必要がある。
 * @param[out] std::string& enc_credential 連結し base64 encode を行った文字列を格納する。
 * @return bool
 */
bool COAuth2Client::generateEncodeCredential(string & enc_credential)
{
    string credential = ::str_form("%s:%s", this->GetClientId().c_str(), this->GetClientSecret().c_str());
    char *encBuf;
    unsigned int isize = credential.size();
    unsigned int nEncBufLenfth;
    ::b64_encode(credential.c_str(), &encBuf, isize, &nEncBufLenfth);

    enc_credential = string(encBuf);

    free(encBuf);

    return true;
}
