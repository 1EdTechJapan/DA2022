/**
 * OneRoster REST consumer test view クラス
 */
#pragma once

#include "view_base.h"

extern "C" {
};

class COneRosterRESTtestCgi;

/**
 * OneRoster REST consumer test view クラス定義
 */
class COneRosterRESTtestView : public CViewBase
{
public:
	/** constructor */
	COneRosterRESTtestView(COneRosterRESTtestCgi& cgi);	// default constructor
	/** destractor */
	virtual ~COneRosterRESTtestView();		// destructor
	/** クラスのメイン処理. template を読み込み書き換える */
	virtual void ExecElem(const string& elem_name, map<string,string>& attr_map);		// カスタム要素の出力

protected:
	COneRosterRESTtestCgi& m_Cgi;

};
