#!/bin/bash
# **************************************************
# CSVファイルエクスポート結果の登録
# 引数
#    DB:OneRosterデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
DB=$1
CMD_MYSQL="$DB"

# csvファイルのエクスポート結果の登録
QUERY="INSERT INTO csv_export (exported_at, status, created_at, updated_at) VALUES(now(), 1, now(), now())"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:csvファイルのエクスポート結果の登録に失敗しました。"
	exit 1
fi

exit 0
