#!/bin/bash
# **************************************************
# 32.register_db_register.sh
# DB登録結果の登録
# 引数
#    DB			:OneRosterデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
DB=$1
CMD_MYSQL="$DB"

# DB登録結果を登録する
QUERY="INSERT INTO db_register ( registered_at, status, created_at, updated_at ) VALUES ( now(), 1, now(), now()) "
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:DB登録結果の登録に失敗しました。"
	exit 1
fi

exit 0
