#!/bin/bash
# **************************************************
# 23.register_classes.sh
# クラス情報登録
# 引数
#    school_id          ：学校ID
#    classSourcedId     ：classSourcedId
#    school_year        ：学年
#    class              ：クラス組
#    DB        			：Azureデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 5 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
school_id=$1
classSourcedId=\"$2\"
school_year=\"$3\"
class=\"$4\"
DB=$5
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

# クラス情報を登録する
QUERY="INSERT INTO classes ( created, modified, school_id, grade_label, class_label, classsourcedId ) VALUES ( now(), now(), $school_id, $school_year, $class, $classSourcedId )"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:クラス情報の登録に失敗しました。school_id=$school_id,classSourcedId=$classSourcedId,school_year=$school_year,class=$class"
	exit 1
fi

exit 0
