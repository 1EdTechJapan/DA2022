/**
 * OneRoster REST Consumer client クラス
 */
#pragma once

#ifndef ONEROSTER_REST_CONSUMER_H_
#define ONEROSTER_REST_CONSUMER_H_

#include "util.h"
#include "oauth2_client.h"

#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <cstring>
#include <vector>
#include <map>

#include <picojson.h>

using namespace std;

extern "C" {
};

/**
 * OneRoster REST Consumer client クラス
 */
class COneRosterRestConsumer
{
public:
    static const char* ROSTERING_ENDPOINT_PATH_BASE;

public:
    /** Constructor */
    COneRosterRestConsumer();
    /** Destructor */
    virtual ~COneRosterRestConsumer();

    /** OneRosterREST Service Provider の サーバ URL を指定する。 */
    bool setProviderUrl(string provider_url);

    /** 組織リストを取得する API にリクエストを行う */
    bool getAllOrgs(string & response_str, int offset, int limit);
    /** ユーザーリストを取得する API にリクエストを行う */
    bool getAllUsers(string & response_str, int offset, int limit);
    /** studentをリストで取得する API にリクエストを行う */
    bool getAllStudents(string & response_str, int offset, int limit);
    /** 指定した school ( org ) の sourcedId に紐づくstudentをリストで取得する API にリクエストを行う */
    bool getStudentsForSchool(string & response_str, string school_sourced_id, int offset, int limit);
    /** teacher をリストで取得する API にリクエストを行う */
    bool getAllTeachers(string & response_str, int offset, int limit);
    /** 指定した school ( org ) の sourcedId に紐づく teacher をリストで取得する API にリクエストを行う */
    bool getTeachersForSchool(string & response_str, string school_sourced_id, int offset, int limit);

    /** メンバ変数の COAuth2Client class インスタンス に access token request endpoint を設定する. */
    bool setOAuth2TokenEndpoint(string endpoint);
    /** メンバ変数の COAuth2Client class インスタンス に access token request 用の client id を設定する。 */
    bool setOAuth2CliendId(string client_id);
    /** メンバ変数の COAuth2Client class インスタンス に access token request 用の client secret を設定する。 */
    bool setOAuth2clientSecret(string client_secret);
    /** メンバ変数の COAuth2Client class インスタンス に access token request 用の scope を設定する。 */
    bool setOAuth2Scope(string scope);

    /** メンバ変数の COAuth2Client class インスタンス に設定されているaccess token request endpoint を取得する。 */
    string getOAuth2TokenEndpoint();
    /** メンバ変数の COAuth2Client class インスタンス に設定されている client id の値を取得する。 */
    string getOAuth2CliendId();
    /** メンバ変数の COAuth2Client class インスタンス に設定されている client secret の値を取得する。 */
    string getOAuth2clientSecret();
    /** メンバ変数の COAuth2Client class インスタンス に設定されている scope の値を取得する。 */
    string getOAuth2Scope();

    /** Service Provder に リクエストを行う private メンバ関数 */
    bool getData(string & response_str, string endpoint, map<string, string> & params);

    /** 認可サーバ に Access Token Request を行う */
    bool doAccessTokenRequest();
    /** メンバ変数 m_access_token の値を取得する。 */
    string getAccessToken();
    /** メンバ変数 m_access_token に 値を設定する。 */
    bool setAccessToken(string accessToken); 
    /** メンバ変数 から error message を 取得する。 */
    string getErrorMessage();

private:
    COAuth2Client m_oauth2_client;

    string m_provider_url;

    map<string, string> params;

    string m_access_token;
    string m_error_message;

};

#endif /* CHTTP_CLIENT_CURL_H_ */

