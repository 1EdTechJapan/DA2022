#!/bin/bash
# **************************************************
# 30.register_user_owned_classes.sh
# ユーザー・クラス情報登録
# 引数
#    class_id           :クラスID
#    user_id            :ユーザーID
#    student_number     :student_number
#    DB					:Azureデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 4 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
class_id=$1
user_id=$2
student_number=$3
DB=$4
CMD_MYSQL="$DB"

# ユーザー・クラス情報を登録する
QUERY="INSERT INTO user_owned_classes ( created, modified, user_id, class_id, student_number ) VALUES ( now(), now(), $user_id, $class_id, $student_number )" 
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:クラス情報の登録に失敗しました。class_id=$class_id,user_id=$user_id,student_number=$student_number"
	exit 1
fi

exit 0
