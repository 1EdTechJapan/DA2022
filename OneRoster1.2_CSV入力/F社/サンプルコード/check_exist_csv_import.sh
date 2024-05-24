#!/bin/bash
# **************************************************
# CSVファイルのインポート結果の存在確認
# 引数
#    DIR_NAME :ディレクトリ名（自治体名）
#    FILE_NAME:ファイル名（ZIPファイル名）
#    DB       :OneRosterデータベース名
# 返却値
#    COUNT:取得件数
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
DIR_NAME=$1
FILE_NAME=$2
DB=$3
CMD_MYSQL="$DB"

# csv_importテーブルからディレクトリ名とファイル名をキーに件数を取得
QUERY="SELECT COUNT(id) AS count FROM csv_import WHERE dir_name = $DIR_NAME AND file_name = $FILE_NAME AND status = 1"
VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:csvファイルのインポート結果の存在確認に失敗しました。dir_name=$DIR_NAME, file_name=$FILE_NAME"
    exit 1
fi
eval $VALUE
echo $count

exit 0
