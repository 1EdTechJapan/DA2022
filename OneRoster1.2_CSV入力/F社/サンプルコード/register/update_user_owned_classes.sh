#!/bin/bash
# **************************************************
# 31.update_user_owned_classes.sh
# ユーザー・クラス情報更新
# 引数
#   class_id            ：クラスＩＤ
#   user_id             ：ユーザーID
#   student_number      ：student_number
#   DB                  ：Azureデータベース名
# 返却値
#    なし
# **************************************************
if [ $# -ne 4 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
class_id=$1
user_id=$2
student_number=$3
DB=$4
CMD_MYSQL="$DB"

# AIAIモンキーのuser_owned_classesテーブルのレコードを更新
QUERY="UPDATE user_owned_classes SET student_number = $student_number, modified = now() WHERE user_id = $user_id AND class_id = $class_id"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:ユーザー・クラス情報の更新に失敗しました。class_id=$class_id,user_id=$user_id,student_number=$student_number"
	exit 1
fi

exit 0
