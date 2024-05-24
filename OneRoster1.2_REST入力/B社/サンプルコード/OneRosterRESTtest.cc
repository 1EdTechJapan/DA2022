/**
 * OneRoster REST consumer test Cgi クラス
 */
#include "OneRosterRESTtest.h"

#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <map>
#include <cstring>
#include <ctime>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <math.h>
#include <cstdlib>
#include <regex.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>

#include "utility.h"
#include "base64.h"

using namespace std;

extern "C" {
};

/**
 * Main Function
 */
int main(int argc, char** argv)
{
	static COneRosterRESTtestCgi inCgi(argc, argv);
	inCgi.ExecMain();
}

/**
 * constructor
 */
COneRosterRESTtestCgi::COneRosterRESTtestCgi(int argc, char** argv) :
	CCgiBase(argc, argv)
	,m_view(*this)
	,m_consumer()
{
	// スキン設定
	this->m_view.SetSkinFile("index", "skin_text.html");

	return;
}

/**
 * destractor
 */
COneRosterRESTtestCgi::~COneRosterRESTtestCgi()
{
	return;
}

/**
 * main Function から呼び出される処理。
 * 
 * @return void
 */
void
COneRosterRESTtestCgi::ExecMain()
{
	// 親クラス CCgiBase::ExecMain() 内の処理は自社独自領域の為詳細は割愛
	// CCgiにリクエストされた parameter の parse 等を行う。
	CCgiBase::ExecMain();

	// ACTIOM_MAP_BEGIN(), ACTION_MAP(), ACTION_MAP_END() ないの処理については 自社独自領域の為詳細は割愛
	// URL に指定された アクション名によって処理を分岐する
	ACTION_MAP_BEGIN()
	ACTION_MAP("index",                         ActionIndex)
	ACTION_MAP_END()

	// ビューの実行
	m_view.Send();
}

/**
 * OneReosteRESTTest cgi のデフォルトアクション
 * 
 * 画面操作でモード毎に処理がわかれている。
 * @return void
 */
void COneRosterRESTtestCgi::ActionIndex()
{
	// libcurl ライブラリ初期化 処理の wrapper 処理を実行
	CHttpClientCurl::LibraryGlobalInit();

	// Http request parameter mode の値で処理を変更
	// Http request を std::map m_mapstrstrHttp_params メンバ変数に格納する処理は割愛
	string mode = this->m_mapstrstrHttp_params["mode"];
	bool   isSuccess = true;
	string okmsg = "";
	string errmsg = "";
	try { 
		if ( mode == "GETTOKEN" ) {
			// Access Token Request を行うモード 
			string accessToken;
			isSuccess = this->getAccessToken(accessToken);
			okmsg = "getAccessToken success.";
			this->m_mapstrstrHttp_params["access_token"] = accessToken;
		}
		if ( mode == "GETALLORG" ) {
			// getAllOrgs を リクエストするモード
			string response;
			isSuccess = this->getData(response, "getAllOrgs");
			okmsg = "getAllOrgs success.";
			picojson::array org_list_response;
			try {
				picojson::value v;
				string err;
				parse(v, response.c_str(), response.c_str() + strlen(response.c_str()), &err);
				if ( !err.empty() ) {
					throw err;
				}
				picojson::object payload = v.get<picojson::object>();
				if ( payload.count("orgs") > 0 ) {
					picojson::array org_list = payload["orgs"].get<picojson::array>();
					picojson::array::iterator it;
					int idx = 0;
					for ( it = org_list.begin(); it != org_list.end(); it++, idx++ ) {
						if ( idx > 105 ) break;
						picojson::object format_org;
						picojson::object org = it->get<object>();
						if ( org.count("sourcedId") > 0 ) {
							format_org.insert(make_pair("sourcedId", picojson::value(org["sourcedId"].to_str())));
						} else {
							format_org.insert(make_pair("sourcedId", picojson::value("")));
						}

						if ( org.count("name") > 0 ) {
							format_org.insert(make_pair("name", picojson::value(org["name"].to_str())));
						} else {
							format_org.insert(make_pair("name", picojson::value("")));
						}
						org_list_response.push_back(picojson::value(format_org));
					}
				}
			} catch ( const char* e ) {
				this->m_mapstrstrHttp_params["errmsg"] += e;
			}
			picojson::object wrapper;
			wrapper.insert(make_pair("orgs", picojson::value(org_list_response)));
			this->m_mapstrstrHttp_params["array_org_list"] = picojson::value(wrapper).serialize();
		}
		if ( mode == "GETALLTEA") {
			// getAllTeachers を リクエストするモード
			string response;
			isSuccess = this->getData(response, "getAllTeachers");
			okmsg = "getAllTeachers success.";
			// this->m_mapstrstrHttp_params["all_tea_response"] = response;
			string formattedResponse;
			this->createFormattedResponse( formattedResponse, response);
			this->m_mapstrstrHttp_params["array_all_tea_list"] = formattedResponse;
		}
		if ( mode == "GETTEASCH" ) {
			// getTeachersForSchool を リクエストするモード
			string response;
			isSuccess = this->getData(response, "getTeachersForSchool", this->m_mapstrstrHttp_params["tea_sch_souced_id"]);
			okmsg = "getTeachersForSchool success.";
			string formattedResponse;
			this->createFormattedResponse( formattedResponse, response);
			this->m_mapstrstrHttp_params["array_tea_for_sch"] = formattedResponse;
		}
		if ( mode == "GETALLSTU" ) {
			// getAllStudents を リクエストするモード
			string response;
			isSuccess = this->getData(response, "getAllStudents");
			okmsg = "getAllStudents success.";
			string formattedResponse;
			this->createFormattedResponse( formattedResponse, response);
			this->m_mapstrstrHttp_params["array_all_stu_list"] = formattedResponse;
		}
		if ( mode == "GETSTUSCH" ) {
			// getStudentsForSchool を リクエストするモード
			string response;
			isSuccess = this->getData(response, "getStudentsForSchool", this->m_mapstrstrHttp_params["stu_sch_souced_id"]);
			okmsg = "getStudentsForSchool success.";
			string formattedResponse;
			this->createFormattedResponse( formattedResponse, response);
			this->m_mapstrstrHttp_params["array_stu_for_sch"] = formattedResponse;
		}

		if ( !isSuccess ) {
			this->m_mapstrstrHttp_params["errmsg"] += this->m_consumer.getErrorMessage().c_str();
		} else {
			this->m_mapstrstrHttp_params["okmsg"]  = okmsg;
		}
	} catch ( const char* e ) {
		this->m_mapstrstrHttp_params["errmsg"] = e;
	}

	// libcurl ライブラリ 終了処理の wrapper 処理を実行
	CHttpClientCurl::LibraryGlobalCleanup();

	return;
}

/**
 * レスポンスを必要なものだけにして返却する。
 * 
 * @param[out] std::string& formatted_response response に指定した json 文字列 user リストから 各ユーザーの property を 必要なものだけに絞り、ユーザー数も 100件までに絞った json に変換し格納する。
 * @param[in] std::string response Service Provider からのレスポンス の jSON 文字列
 * @return bool
 */
bool COneRosterRESTtestCgi::createFormattedResponse(string & formatted_response, string response) 
{
	try {
		picojson::object formated_response_wrap;
		picojson::array formated_response_array;

		picojson::value v;
		string err;
		parse(v, response.c_str(), response.c_str() + strlen(response.c_str()), &err);
		if ( !err.empty() ) {
			throw err;
		}
		picojson::object payload = v.get<picojson::object>();
		if ( payload.count("users") > 0 ) {
			picojson::array user_list = payload["users"].get<picojson::array>();
			picojson::array::iterator it;
			int idx = 0;
			for ( it = user_list.begin(); it != user_list.end(); it++, idx++ ) {
				if ( idx > 99 ) break;
				picojson::object format_user;
				picojson::object row = it->get<object>();
				if ( row.count("sourcedId") > 0 ) {
					format_user.insert(make_pair("sourcedId", picojson::value(row["sourcedId"].to_str())));
				} else {
					format_user.insert(make_pair("sourcedId", picojson::value("")));
				}

				if ( row.count("username") > 0 ) {
					format_user.insert(make_pair("username", picojson::value(row["username"].to_str())));
				} else {
					format_user.insert(make_pair("username", picojson::value("")));
				}

				if ( row.count("userIds") > 0 ) {
					format_user.insert(make_pair("userIds", picojson::value(row["userIds"].to_str())));
				} else {
					format_user.insert(make_pair("userIds", picojson::value("")));
				}

				if ( row.count("identifier") > 0 ) {
					format_user.insert(make_pair("identifier", picojson::value(row["identifier"].to_str())));
				} else {
					format_user.insert(make_pair("identifier", picojson::value("")));
				}

				formated_response_array.push_back(picojson::value(format_user));
			}
		}
		formated_response_wrap.insert(make_pair("users", picojson::value(formated_response_array)));
		formatted_response = picojson::value(formated_response_wrap).serialize();
	} catch ( const char* e ) {
		this->m_mapstrstrHttp_params["errmsg"] += e;
		return false;
	}

	return true;
}

/**
 * メンバ変数 m_consumer COneRosterRestConsumer クラス インスタンス の
 * getAccessToken を実行する。
 * 
 * @param[out] access_token アクセストークン
 * @return bool
 */
bool COneRosterRESTtestCgi::getAccessToken(string & access_token) 
{
	try {
		this->m_consumer.setOAuth2TokenEndpoint(this->m_mapstrstrHttp_params["authz_endpoint"]);
		this->m_consumer.setOAuth2CliendId(this->m_mapstrstrHttp_params["client_id"]);
		this->m_consumer.setOAuth2clientSecret(this->m_mapstrstrHttp_params["client_secret"]);
		if ( this->m_mapstrstrHttp_params["scope"].empty() == false ) {
			this->m_consumer.setOAuth2Scope(this->m_mapstrstrHttp_params["scope"]);
		}
		if ( this->m_consumer.doAccessTokenRequest() == false ) {
			return false;
		}
		access_token = this->m_consumer.getAccessToken();
	} catch ( const char* e ) {
		throw e;
	}
	return true;
}

/**
 * 3つの引数を設けている getData メンバ関数を呼び出す Overload
 * 
 * @param[out] std::string& response_str アクセストークン
 * @param[in] std::string mode モード文字列
 * @return bool
 */
bool COneRosterRESTtestCgi::getData(string & response_str, string mode) 
{
	return this->getData(response_str, mode, "");
}

/**
 * メンバ変数 m_consumer COneRosterRestConsumer クラス インスタンス の処理を
 * 実行し、OneRoster REST Service Provider に接続しデータを取得する。
 * 
 * @param[out] std::string& response_str レスポンス文字列を格納する。
 * @param[in] std::string mode 実行する処理モードを指定
 * @param[in] std::string sourced_id getStudentsForSchool, getTeachersForSchool 実行する場合に org の sourcedId を指定する。
 * @return bool
 */
bool COneRosterRESTtestCgi::getData(string & response_str, string mode, string sourced_id) 
{
	try {
		this->m_consumer.setProviderUrl(this->m_mapstrstrHttp_params["provider_url"]);
		this->m_consumer.setAccessToken(this->m_mapstrstrHttp_params["access_token"]);

		bool isSuccess = false;
		if ( mode == "getAllOrgs") {
			isSuccess = this->m_consumer.getAllOrgs(response_str, 0, 100);
		} else if ( mode == "getAllTeachers" ) {
			isSuccess = this->m_consumer.getAllTeachers(response_str, 0, 100);
		} else if ( mode == "getAllStudents" ) {
			isSuccess = this->m_consumer.getAllStudents(response_str, 0, 100);
		} else if ( mode == "getStudentsForSchool" ) {
			isSuccess = this->m_consumer.getStudentsForSchool(response_str, sourced_id, 0, 100);
		} else if ( mode ==  "getTeachersForSchool" ) {
			isSuccess = this->m_consumer.getTeachersForSchool(response_str, sourced_id, 0, 100);
		}

		if ( isSuccess == false ) {
			return false;
		} 
	} catch ( const char* e ) {
		throw e;
	}
	return true;
}
