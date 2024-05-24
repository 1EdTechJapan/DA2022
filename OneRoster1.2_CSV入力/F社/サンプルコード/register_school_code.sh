#!/bin/bash
# **************************************************
# 学校コード登録
# 引数
#    SOURCED_ID :学校を一意に識別するID
#    SCHOOL_CODE:学校コード
#    DB         :OneRosterデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
SOURCED_ID=\"$1\"
SCHOOL_CODE=\"$2\"
DB=$3
CMD_MYSQL="$DB"

# orgs_importテーブルのsourcedIdが一致するレコードの学校コードを更新
QUERY="UPDATE orgs_import SET orgs_managementid = $SCHOOL_CODE, updated_at = now() WHERE sourcedId = $SOURCED_ID"
`echo $QUERY | $CMD_MYSQL`
if [ $? -ne 0 ]; then
	echo "$0:学校コードの登録に失敗しました。sourcedId=$SOURCED_ID, code=$SCHOOL_CODE"
	exit 1
fi

exit 0
