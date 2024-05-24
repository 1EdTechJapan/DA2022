/**
 * OAuth2.0 Client クラス
 */
#pragma once

#ifndef COAUTH2_CLIENT_H_
#define COAUTH2_CLIENT_H_

#include "util.h"

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
 * OAuth2.0 Client クラス
 */
class COAuth2Client
{
public:
    /** @struct access token response */
    struct SAccessTokenResponse {
        string access_token;
        string token_type;
        string expires_in;
        string refresh_token;
        string scope;
    };

    /** @struct access token response */
    struct SAccessTokenErrorResponse {
        string error;
        string error_description;
        string error_uri;
    };

public:
    // const string AUTHORIZATION_ENDPOINT;
    // const string TOKEN_ENDPOINT;

    /* Authorization Request Parameters */
    // const string RESPONSE_TYPE_KEY;

    /* Access Token Request */
    static const char* GRANT_TYPE_KEY;
    static const char* GRANT_TYPE_VAL_CLIENT_CREDENTIALS;
    static const char* SCOPE_KEY; // use Access Token Response too.

    /* Access Token Response */
    static const char* ACCESS_TOKEN_KEY;
    static const char* TOKEN_TYPE_KEY;
    static const char* EXPIRES_IN_KEY;
    static const char* REFRESH_TOKEN_KEY;

public:
    COAuth2Client();
    virtual ~COAuth2Client();

    /* Authorization Server Endpoint */
    // void SetAuthorizationEndpoint(string endpoint); // Use Authorization Code Flow. 
    // string GetAuthorizationEndpoint();  // Use Authorization Code Flow.
    // void SetTokenEndpoint(string endpoint);
    // string GetTokenEndpoint();

    /* Client Endpoint */
    // void SetRedirectEndpoint(string endpoint);
    // string GetTokenEndpoint();

    /* Authorization Request Parameters */
    // void SetResponseType(string response_type);
    // string GetResponseType();

    /* AccessTokenRequest */
    bool SetTokenEndpoint(string endpoint);
    string GetTokenEndpoint();

    bool SetGrantType(string grant_type);
    string GetGrantType();

    bool SetScope(string scope);
    string GetScope();

    bool SetClientId(string client_id);
    string GetClientId();

    bool SetClientSecret(string client_secret);
    string GetClientSecret();

    /* doAccessTokenRequest */
    bool doAccessTokenRequest(string& errmsg);

    string getAccessToken();
    bool generateEncodeCredential(string & enc_credential);

    SAccessTokenResponse      getAccessTokenResponse() { return this->m_access_token_response; }
    SAccessTokenErrorResponse getErrorResponse() { return this->m_error_response; }

private:
    string m_token_endpoint;

    string m_client_id;
    string m_client_secret;

    /* authorization request */
    // string m_response_type;
    
    /* access token request */
    string m_grant_type;
    string m_scope;

    /* Access Token Response */
    SAccessTokenResponse     m_access_token_response;
    SAccessTokenErrorResponse m_error_response;

};

#endif /* CHTTP_CLIENT_CURL_H_ */

