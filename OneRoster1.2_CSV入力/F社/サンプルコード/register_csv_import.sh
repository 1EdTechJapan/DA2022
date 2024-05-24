#!/bin/bash
# **************************************************
# CSVファイルのインポート結果の登録
# 引数
#    DIR_NAME :ディレクトリ名（自治体名）
#    FILE_NAME:ファイル名（ZIPファイル名）
#    DB       :OneRosterデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
DIR_NAME=$1
FILE_NAME=$2
DB=$3
CMD_MYSQL="$DB"

# csvファイルのインポート結果の登録
QUERY="INSERT INTO csv_import (dir_name, file_name, imported_at, status, created_at, updated_at) VALUES($DIR_NAME, $FILE_NAME, now(), 1, now(), now())"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:csvファイルのインポート結果の登録に失敗しました。dir_name=$DIR_NAME, file_name=$FILE_NAME"
	exit 1
fi

exit 0
