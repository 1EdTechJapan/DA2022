#!/bin/bash
# **************************************************
# 前回CSVファイルエクスポート日時の取得
# 引数
#    DB:OneRosterデータベース名
# 返却値
#    exported_at:前回CSVファイルエクスポート日時
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
DB=$1
CMD_MYSQL="$DB"

# csv_exportテーブルから最新レコードの前回CSVファイルエクスポート日時を取得
QUERY="SELECT exported_at FROM csv_export WHERE status = 1 ORDER BY exported_at DESC LIMIT 1"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:前回CSVファイルエクスポート日時の取得に失敗しました。"
    exit 1
fi
eval $VALUE
echo "$exported_at"

exit 0
