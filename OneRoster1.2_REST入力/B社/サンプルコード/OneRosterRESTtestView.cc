/**
 * OneRoster REST consumer test view クラス
 */
#include "OneRosterRESTtestView.h"
#include "OneRosterRESTtest.h"

extern "C" {
};

using namespace std;

/**
 * constructor
 */
COneRosterRESTtestView::COneRosterRESTtestView(COneRosterRESTtestCgi& cgi) :
	CViewBase(cgi),
	m_Cgi(cgi)
{
	return;
}

/**
 * destructor
 */
COneRosterRESTtestView::~COneRosterRESTtestView()
{
	return;
}

/**
 * カスタム要素の解析と出力を行う
 * 
 * @param[in] elem_name  カスタム要素の要素名
 * @param[in] attr_map カスタム要素の属性マップ
 * @return void
 */
void COneRosterRESTtestView::ExecElem(const string& elem_name, map<string,string>& attr_map)
{

	// this->CViewBase::ExecElem() の処理は 自社独自領域の為詳細は割愛
	// template ファイルの カスタム要素を変数値などに書き換える。
	// カスタム要素は <## SomeName ##> のような形となっている。
	// m_Cgi の メンバ変数 m_mapstrstrHttp_params std::map の 要素を出力する場合は
	// <## Param name="some_name" ##> という形で
	this->CViewBase::ExecElem(elem_name, attr_map);

	return;

}

