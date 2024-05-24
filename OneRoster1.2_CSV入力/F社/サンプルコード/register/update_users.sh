#!/bin/bash
# **************************************************
# 28.update_users.sh
# ユーザー情報更新
# 引数
#    user_id            :ユーザーID
#    school_id          :学校ID
#    account_id         :account_id
#    role               :role
#    nickname           :nickname
#    DB					:Azureデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 6 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
user_id=$1
school_id=$2
account_id=\"$3\"
role=$4
nickname=\"$5\"
DB=$6
CMD_MYSQL="$DB"

# roleの変更
if [ $role = 1 ]; then
	role_name=\"student\"
else
	role_name=\"teacher\"
fi
# AIAIモンキーのusersテーブルのレコードを更新
QUERY="UPDATE users SET school_id = $school_id, nickname = $nickname, account_id = $account_id, role = $role_name, modified = now() WHERE id = $user_id"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:ユーザー情報の更新に失敗しました。user_id=$user_id,school_id=$school_id,account_id=$account_id,role=$role_name,nickname=$nickname"
	exit 1
fi

exit 0
