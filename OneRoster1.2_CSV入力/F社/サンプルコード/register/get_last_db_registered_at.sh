#!/bin/bash
# **************************************************
# 19.get_last_db_registered_at.sh
# 前回DB登録日時の取得
# 引数
#    DB				:OneRosterデータベース名
# 返却値
#    registered_at	:前回DB登録日時
# **************************************************
# 引数のチェック

if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
DB=$1
CMD_MYSQL="$DB"

# db_registerテーブルから最新レコードの前回DB登録日時を取得 /
QUERY="SELECT registered_at FROM db_register WHERE status = 1 ORDER BY registered_at DESC LIMIT 1"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:前回DB登録日時の取得に失敗しました。"
    exit 1
fi
eval $VALUE
echo $registered_at

exit 0
