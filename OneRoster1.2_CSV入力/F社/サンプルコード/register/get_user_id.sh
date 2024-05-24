#!/bin/bash
# **************************************************
# 26.get_user_id.sh
# ユーザーID取得
# 引数
#    userSourcedId      :userSourcedId
#    DB					:Azureデータベース名
# 返却値
#    user_id            :ユーザーID
# **************************************************
# 引数のチェック
if [ $# -ne 2 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
userSourcedId=\"$1\"
DB=$2
CMD_MYSQL="$DB"

# enrollments_importテーブルからuserSourcedIdをキーにユーザーIDを取得する
QUERY="SELECT id AS user_id FROM users WHERE userssourcedId = $userSourcedId"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:ユーザーIDの取得に失敗しました。userSourcedId=$userSourcedId"
	exit 1
fi
eval $VALUE
echo $user_id

exit 0
