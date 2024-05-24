#!/bin/bash
# **************************************************
# 学校毎の処理
# 引数
#    LAST_EXPORTED_AT     :前回CSVファイルエクスポート日時
#    DB_ONEROSTER         :OneRosterデータベース名
#    DB_AZURE             :Azureデータベース名
#    SCHOOL_CODE_NULL_FILE:学校コードnullファイル
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 4 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
LAST_EXPORTED_AT=$1
DB_ONEROSTER=$2
DB_AZURE=$3
SCHOOL_CODE_NULL_FILE=$4
CMD_MYSQL="$DB_ONEROSTER"

# CSVファイルインポート先のテーブルから前回CSVファイルエクスポート日時以降かつ学校コードがnullのレコードの一覧取得
if [ -n "$LAST_EXPORTED_AT" ]; then
	LAST_EXPORTED_AT=\"$LAST_EXPORTED_AT\"
	QUERY="SELECT oi.sourcedId AS sourcedId, oi.city_name AS city_name, oi.name AS name FROM orgs_import AS oi INNER JOIN enrollments_import AS ei ON oi.sourcedId = ei.schoolSourcedId WHERE ei.updated_at > $LAST_EXPORTED_AT AND oi.orgs_managementid IS NULL GROUP BY oi.sourcedId ORDER BY oi.city_name ASC, oi.sourcedId ASC"
else
	QUERY="SELECT oi.sourcedId AS sourcedId, oi.city_name AS city_name, oi.name AS name FROM orgs_import AS oi INNER JOIN enrollments_import AS ei ON oi.sourcedId = ei.schoolSourcedId WHERE oi.orgs_managementid IS NULL GROUP BY oi.sourcedId ORDER BY oi.city_name ASC, oi.sourcedId ASC"
fi
VALUES=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:学校コードがnullのレコードの一覧取得に失敗しました。"
    exit 1
fi
echo "$0:学校コードがnullのレコードの一覧取得に成功しました。"

# 取得したレコード×項目数分実施
echo "$VALUES" | while read data
do
	if [[ $data != sourcedId* ]] && [[ $data != city_name* ]] &&  [[ $data != name* ]]; then
		continue
	fi
	eval $data

	# 取得した項目がname以外の場合はスキップ
	if [[ $data != name* ]]; then
		continue
	fi

	# 学校コード取得
	SCHOOL_CODE=`./get_school_code.sh "$name" "$DB_AZURE"`
	if [ $? -ne 0 ]; then
		echo "$0:学校コードの取得に失敗しました。sourcedId=$sourcedId, city_name=$city_name, name=$name"
		exit 1
	fi

	# 学校コードが取得できなかった場合
	if [ ! -n "$SCHOOL_CODE" ]; then
		echo "$0:学校コードは取得できません。sourcedId=$sourcedId, city_name=$city_name, name=$name"
		# 学校コードnullファイルに出力
		echo "sourcedId=$sourcedId, city_name=$city_name, name=$name" >> $SCHOOL_CODE_NULL_FILE
		continue
	fi
	echo "$0:学校コードは取得できました。sourcedId=$sourcedId, city_name=$city_name, name=$name, code=$SCHOOL_CODE"

	# 学校コード登録
	./register_school_code.sh $sourcedId $SCHOOL_CODE "$DB_ONEROSTER"
	if [ $? -ne 0 ]; then
		echo "$0:学校コードの登録に失敗しました。sourcedId=$sourcedId, city_name=$city_name, name=$name, code=$SCHOOL_CODE"
		exit 1
	else
		echo "$0:学校コードの登録に成功しました。sourcedId=$sourcedId, city_name=$city_name, name=$name, code=$SCHOOL_CODE"
	fi
done

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
