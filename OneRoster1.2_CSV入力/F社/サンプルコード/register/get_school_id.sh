#!/bin/bash
# **************************************************
# 21.get_school_id.sh
# 学校ID取得
# 引数
#    SCHOOL_CODE	:学校コード
#    DB         	:Azureデータベース名
# 返却値
#    school_id		:学校ID
# **************************************************
# 引数のチェック
if [ $# -ne 2 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
SCHOOL_CODE=\"$1\"
DB=$2
CMD_MYSQL="$DB"

# schoolsテーブルから学校コードをキーに学校IDを取得する
QUERY="SELECT id AS school_id FROM schools WHERE code = $SCHOOL_CODE"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:学校IDの取得に失敗しました。SCHOOL_CODE=$SCHOOL_CODE"
	exit 1
fi
eval $VALUE
echo $school_id

exit 0
