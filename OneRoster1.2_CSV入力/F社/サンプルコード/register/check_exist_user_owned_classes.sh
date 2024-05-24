#!/bin/bash
# **************************************************
# 29.check_exist_user_owned_classes.sh
# ユーザー・クラス情報の存在確認
# 引数
#    class_id           :クラスID
#    user_id            :ユーザーID
#    DB					:Azureデータベース名
# 返却値
#    count				:取得件数
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
class_id=$1
user_id=$2
DB=$3
CMD_MYSQL="$DB"

# ユーザー・クラス情報が存在するか確認する
# AIAIモンキーのuser_owned_classesテーブル
QUERY="SELECT COUNT(id) AS count FROM user_owned_classes WHERE class_id = $class_id AND user_id = $user_id"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:ユーザー・クラス情報の存在確認に失敗しました。class_id=$class_id,user_id=$user_id"
    exit 1
fi
eval $VALUE
echo $count

exit 0
