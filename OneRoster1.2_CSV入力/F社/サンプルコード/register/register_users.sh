#!/bin/bash
# **************************************************
# 27.register_users.sh
# ユーザー情報登録
# 引数
#	school_id			:学校ID
#	userSourcedId		:userSourcedId
#	account_id			:account_id
#	password			:password
#	role				:role
#	nickname			:nickname
#	DB					:Azureデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 7 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
school_id=$1
userSourcedId=\"$2\"
account_id=\"$3\"
password=\"$4\"
role=$5
nickname=\"$6\"
DB=$7
CMD_MYSQL="$DB"

# roleの変更
if [ $role = "1" ]; then
	role_name=\"student\"
else
	role_name=\"teacher\"
fi
# ユーザー情報を登録する
QUERY="INSERT INTO users ( created, modified, school_id, nickname, account_id, account_password, role, userssourcedId ) VALUES ( now(), now(), $school_id, $nickname, $account_id, $password, $role_name, $userSourcedId )"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:ユーザー情報の登録に失敗しました。school_id=$school_id,userSourcedID=$userSourcedId,account_id=$account_id,account_password=$password,role=$role_name,nickname=$nickname"
	exit 1
fi

exit 0
