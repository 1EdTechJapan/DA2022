/**
 * OneRoster REST consumer test Cgi クラス
 */
#pragma once

#include "cgi_base.h"
#include "OneRosterRESTtestView.h"
#include "syslog_writer.h"
#include "oneroster_rest_consumer.h"
#include "http_curl.h"

#include <string>
#include <vector>
#include <map>
#include <cstdlib>

using std::string;
using std::vector;
using std::map;

extern "C" {
};

/**
 * OneRoster REST consumer test Cgi クラス
 */
class COneRosterRESTtestCgi : public CCgiBase
{
public:
	/** constructor */
	COneRosterRESTtestCgi(int argc,char** argv);
	/** destructor */
	virtual ~COneRosterRESTtestCgi();
	/** main Function から呼び出される処理 */
	void ExecMain();

public:
	/** view クラス */
	COneRosterRESTtestView  m_view;

	/** OneRosterREST Service Consumer クラス */
	COneRosterRestConsumer m_consumer;

protected:
	/** OneReosteRESTTest cgi のデフォルトアクション */
	void ActionIndex();

	/** メンバ変数 m_consumer COneRosterRestConsumer クラス インスタンス の getAccessToken を実行する。*/
	bool getAccessToken(string & access_token);
	/** 3つの引数を設けている getData メンバ関数を呼び出す Overload */
	bool getData(string & response_str, string mode);
	/** メンバ変数 m_consumer COneRosterRestConsumer クラス インスタンス の処理を実行し、OneRoster REST Service Provider に接続しデータを取得する。*/
	bool getData(string & response_str, string mode, string sourced_id);

	/** レスポンスを必要なものだけにして返却する。 */
	bool createFormattedResponse(string & formatted_response, string response);

};
