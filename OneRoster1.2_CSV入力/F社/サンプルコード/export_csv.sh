#!/bin/bash
# **************************************************
# CSVファイルエクスポート
# 引数
#    LAST_EXPORTED_AT :前回CSVファイルエクスポート日時
#    DB               :OneRosterデータベース名
#    SELECT_TYPE      :抽出区分（1:削除済み以外/2:削除済み）
#    EXPORT_USERS_FILE:エクスポートCSVファイル
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 4 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
LAST_EXPORTED_AT=$1
DB=$2
SELECT_TYPE=$3
EXPORT_FILE=$4
CMD_MYSQL="$DB"
STATUS_DELETED=\"tobedeleted\"

# users_exportテーブルから前回CSVファイルエクスポート日時以降のレコードを取得
# 削除済み以外を抽出の場合
if [ $SELECT_TYPE = 1 ]; then
	if [ -n "$LAST_EXPORTED_AT" ]; then
		LAST_EXPORTED_AT=\"$LAST_EXPORTED_AT\"
		QUERY="SELECT ue.school_code AS school_code, ue.account_id AS account_id, ue.password AS password, ue.school_year AS school_year, ue.class AS class, ue.student_number AS student_number, ue.expire_date AS expire_date, ue.role AS role, ue.trial, ue.nickname AS nickname FROM users_export AS ue WHERE NOT EXISTS (SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.updated_at > $LAST_EXPORTED_AT AND ue.status <> $STATUS_DELETED GROUP BY ue.school_code, ue.school_year, ue.class, ue.account_id ORDER BY ue.school_code ASC, ue.school_year ASC, ue.class ASC, ue.account_id ASC"
	else
		QUERY="SELECT ue.school_code AS school_code, ue.account_id AS account_id, ue.password AS password, ue.school_year AS school_year, ue.class AS class, ue.student_number AS student_number, ue.expire_date AS expire_date, ue.role AS role, ue.trial, ue.nickname AS nickname FROM users_export AS ue WHERE NOT EXISTS (SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.status <> $STATUS_DELETED GROUP BY ue.school_code, ue.school_year, ue.class, ue.account_id ORDER BY ue.school_code ASC, ue.school_year ASC, ue.class ASC, ue.account_id ASC"
	fi
# 削除済みを抽出の場合
else
	if [ -n "$LAST_EXPORTED_AT" ]; then
		LAST_EXPORTED_AT=\"$LAST_EXPORTED_AT\"
		QUERY="SELECT ue.school_code AS school_code, ue.account_id AS account_id, ue.password AS password, ue.school_year AS school_year, ue.class AS class, ue.student_number AS student_number, ue.expire_date AS expire_date, ue.role AS role, ue.trial, ue.nickname AS nickname FROM users_export AS ue WHERE NOT EXISTS (SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.updated_at > $LAST_EXPORTED_AT AND ue.status = $STATUS_DELETED GROUP BY ue.school_code, ue.school_year, ue.class, ue.account_id ORDER BY ue.school_code ASC, ue.school_year ASC, ue.class ASC, ue.account_id ASC"
	else
		QUERY="SELECT ue.school_code AS school_code, ue.account_id AS account_id, ue.password AS password, ue.school_year AS school_year, ue.class AS class, ue.student_number AS student_number, ue.expire_date AS expire_date, ue.role AS role, ue.trial, ue.nickname AS nickname FROM users_export AS ue WHERE NOT EXISTS (SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.status = $STATUS_DELETED GROUP BY ue.school_code, ue.school_year, ue.class, ue.account_id ORDER BY ue.school_code ASC, ue.school_year ASC, ue.class ASC, ue.account_id ASC"
	fi
fi

VALUES=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:CSVファイルエクスポート用のユーザー情報の取得に失敗しました。"
    exit 1
fi

# CSVファイルエクスポート（ヘッダー行）
echo "\"school_code\",\"account_id\",\"password\",\"school_year\",\"class\",\"student_number\",\"expire_date\",\"role\",\"trial\",\"nickname\"" >> $EXPORT_FILE

# 取得したレコード×項目数分実施
echo "${VALUES}" | while read data
do
	if [[ $data != school_code* ]] && [[ $data != account_id* ]] &&  [[ $data != password* ]] && [[ $data != school_year* ]] && [[ $data != class* ]] && [[ $data != student_number* ]] && [[ $data != expire_date* ]] && [[ $data != role* ]] && [[ $data != trial* ]] && [[ $data != nickname* ]]; then
		continue
	fi
	eval $data

	# 取得した項目がnicknameの場合
	if [[ $data == nickname* ]]; then
		# CSVファイルエクスポート（データ行）
		echo "\"${school_code}\",\"${account_id}\",\"${password}\",\"${school_year}\",\"${class}\",\"${student_number}\",\"${expire_date}\",\"${role}\",\"${trial}\",\"${nickname}\"" >> $EXPORT_FILE
	fi
done

exit 0
