#!/bin/bash
# **************************************************
# 22.get_class_id.sh
# 学校IDとclassSourcedIdをキーにクラスIDを取得する
# 引数
#    school_id			:学校ID
#    classSourcedId		:classSourcedId
#    DB         		:Azureデータベース名
# 返却値
#    class_id			:学校ID
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
school_id=$1
classSourcedId=\"$2\"
DB=$3
CMD_MYSQL="$DB"

# classesテーブルから学校IDとclassSourcedIdをキーにクラスIDを取得する
QUERY="SELECT id AS class_id FROM classes WHERE school_id = $school_id and classsourcedId=$classSourcedId"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:クラスIDの取得に失敗しました。school_id=$school_id,classSourcedId=$classSourcedId"
	exit 1
fi
eval $VALUE
echo $class_id

exit 0
