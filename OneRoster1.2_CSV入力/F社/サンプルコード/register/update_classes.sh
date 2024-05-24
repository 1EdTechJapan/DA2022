#!/bin/bash
# **************************************************
# 24.update_classes.sh
# クラス情報更新
# 引数
#    class_id 		:クラスID
#    school_year 	:学年
#    class		 	:組
#    DB         	:Azureデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 4 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
class_id=$1
school_year=\"$2\"
class=\"$3\"
DB=$4
CMD_MYSQL="$DB"
DEF_SCHOOL_YEAR=\"99年\"
DEF_CLASS=\"未登録組\"
EX_SCHOOL_YEAR=""
EX_CLASS=""

# 学年が99年の場合は空文字に変換
if [[ $school_year = $DEF_SCHOOL_YEAR ]]; then
	school_year=\"$EX_SCHOOL_YEAR\"
fi

# クラスが未登録組の場合は空文字に変換
if [[ $class = $DEF_CLASS ]]; then
	class=\"$EX_CLASS\"
fi

# AIAIモンキーのclassesテーブルのレコードを更新
QUERY="UPDATE classes SET grade_label = $school_year, class_label = $class, modified = now() WHERE id = $class_id"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:クラス情報の更新に失敗しました。class_id=$class_id,school_year=$school_year,class=$class"
	exit 1
fi

exit 0
