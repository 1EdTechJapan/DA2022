#!/bin/bash
# **************************************************
# 学校コード取得
# 引数
#    SCHOOL_NAME:学校名
#    DB         :Azureデータベース名
# 返却値
#    code:学校コード
# **************************************************
# 引数のチェック
if [ $# -ne 2 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
SCHOOL_NAME=\"$1\"
DB=$2
CMD_MYSQL="$DB"

# schoolsテーブルから学校名をキーに学校コードを取得
QUERY="SELECT code FROM schools WHERE name = $SCHOOL_NAME"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:学校コードの取得に失敗しました。name=$SCHOOL_NAME"
	exit 1
fi
eval $VALUE
echo $code

exit 0
