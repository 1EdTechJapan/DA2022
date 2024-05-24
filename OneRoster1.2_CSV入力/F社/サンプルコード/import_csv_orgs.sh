#!/bin/bash
# **************************************************
# 学校CSVファイルインポーﾄ
# 引数
#    CSV_FILE:学校CSVファイル
#    DB      :OneRosterデータベース名
#    DIR_NAME:ディレクトリ名（自治体名）
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
CSV_FILE=$1
DB=$2
DIR_NAME=$3
CMD_MYSQL="$DB"
array_singleKana=('ｱ' 'ｲ' 'ｳ' 'ｴ' 'ｵ' 'ｶ' 'ｷ' 'ｸ' 'ｹ' 'ｺ' 'ｻ' 'ｼ' 'ｽ' 'ｾ' 'ｿ' 'ﾀ' 'ﾁ' 'ﾂ' 'ﾃ' 'ﾄ' 'ﾅ' 'ﾆ' 'ﾇ' 'ﾈ' 'ﾉ' 'ﾊ' 'ﾋ' 'ﾌ' 'ﾍ' 'ﾎ' 'ﾏ' 'ﾐ' 'ﾑ' 'ﾒ' 'ﾓ' 'ﾔ' 'ﾕ' 'ﾖ' 'ﾗ' 'ﾘ' 'ﾙ' 'ﾚ' 'ﾛ' 'ﾜ' 'ｦ' 'ﾝ' 'ｧ' 'ｨ' 'ｩ' 'ｪ' 'ｫ' 'ｬ' 'ｭ' 'ｮ' 'ｯ' 'ﾞ' 'ﾟ')
char=""

# ファイルの文字コード確認
if [[ $(file -i $CSV_FILE | grep -q "utf-8"; echo -n ${?} ) -ne 0 ]] && [[ $(file -i $CSV_FILE | grep -q "us-ascii"; echo -n ${?} ) -ne 0 ]]; then
	echo "$0:orgs.csvの文字コードが不正です。"
	exit 1
fi

# 学校ファイルのインポート
i=0
while read row
do
	# 1行目の場合
	if [ $i -eq 0 ]; then
		# csvファイルのヘッダー値取得
		csv_sourcedId=`echo ${row} | cut -d , -f 1`
		# sourcedIdのヘッダーが不正
		if [[ $csv_sourcedId != "sourcedId" ]]; then
			echo "$0:sourcedIdのヘッダーが不正です。[$csv_sourcedId]"
			exit 1
		fi

		csv_status=`echo ${row} | cut -d , -f 2`
		# statusのヘッダーが不正
		if [[ $csv_status != "status" ]]; then
			echo "$0:statusのヘッダーが不正です。[$csv_status]"
			exit 1
		fi

		csv_dateLastModified=`echo ${row} | cut -d , -f 3`
		# dateLastModifiedのヘッダーが不正
		if [[ $csv_dateLastModified != "dateLastModified" ]]; then
			echo "$0:dateLastModifiedのヘッダーが不正です。[$csv_dateLastModified]"
			exit 1
		fi

		csv_name=`echo ${row} | cut -d , -f 4`
		# nameのヘッダーが不正
		if [[ $csv_name != "name" ]]; then
			echo "$0:nameのヘッダーが不正です。[$csv_name]"
			exit 1
		fi

		csv_type=`echo ${row} | cut -d , -f 5`
		# typeのヘッダーが不正
		if [[ $csv_type != "type" ]]; then
			echo "$0:typeのヘッダーが不正です。[$csv_type]"
			exit 1
		fi

		csv_identifier=`echo ${row} | cut -d , -f 6 | sed -e "s/[\r\n]\+//g"`
		# identifierのヘッダーが不正
		if [[ $csv_identifier != "identifier" ]]; then
			echo "$0:identifierのヘッダーが不正です。[$csv_identifier]"
			exit 1
		fi

		csv_parentSourcedId=`echo ${row} | cut -d , -f 7 | sed -e "s/[\r\n]\+//g"`
		# parentSourcedIdのヘッダーが不正
		if [[ $csv_parentSourcedId != "parentSourcedId" ]]; then
			echo "$0:parentSourcedIdのヘッダーが不正です。[$csv_parentSourcedId]"
			exit 1
		fi

		NUMBER=$((++i))
		continue
	fi

	# csvファイルのカラム値取得
	csv_sourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $1}' | sed 's/"//g'`
	# sourcedIdに値が入っていない
	if [ ! -n "$csv_sourcedId" ]; then
		echo "$0:sourcedIdに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# UUID形式確認
	./check_uuid.sh "$csv_sourcedId"
	# sourcedIdが不正
	if [ $? -ne 0 ]; then
		echo "$0:sourcedIdがUUID形式ではありません。$NUMBER行目:$csv_sourcedId"
		exit 1
	fi

	csv_status=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $2}' | sed 's/"//g'`
	# statusに値が入っている
	if [ -n "$csv_status" ]; then
		# statusが不正
		if [[ $csv_status != "active" ]] && [[ $csv_status != "tobedeleted" ]]; then
			echo "$0:statusが指定値以外の値です。$NUMBER行目:$csv_status"
			exit 1
		fi
	fi

	csv_dateLastModified=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $3}' | sed 's/"//g'`
	# dateLastModifiedに値が入っている
	if [ -n "$csv_dateLastModified" ]; then
		date +'%Y-%m-%dT%H:%M:%S,%N%z' -d $csv_dateLastModified
		# dateLastModifiedが不正
		if [ $? -ne 0 ]; then
			echo "$0:dateLastModifiedが不正です。$NUMBER行目:$csv_dateLastModified"
			exit 1
		fi
	fi

	csv_name=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $4}' | sed 's/"//g'`
	# nameに値が入っていない
	if [ ! -n "$csv_name" ]; then
		echo "$0:nameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# nameが不正
		if [[ "$csv_name" == *"$char"* ]]; then
			echo "$0:nameに半角カナが含まれています。$NUMBER行目:$csv_name"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_type=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $5}' | sed 's/"//g'`
	# typeに値が入っていない
	if [ ! -n "$csv_type" ]; then
		echo "$0:typeに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# typeが不正
	if [[ $csv_type != "district" ]] && [[ $csv_type != "school" ]]; then
		echo "$0:typeが指定値以外の値です。$NUMBER行目:$csv_type"
		exit 1
	fi

	csv_identifier=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $6}' | sed 's/"//g'`
	# identifierに値が入っている
	if [ -n "$csv_identifier" ]; then
		# identifierが不正
		if [ ${#csv_identifier} != 13 ]; then
			echo "$0:identifierが不正です。$NUMBER行目:$csv_identifier"
			exit 1
		fi
	fi

	csv_parentSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $7}' | sed 's/"//g'`
	# 最後のカラムは改行コードを除外
	csv_parentSourcedId=`echo $csv_parentSourcedId | sed -e "s/[\r\n]\+//g"`
	# parentSourcedIdに値が入っている
	if [ -n "$csv_parentSourcedId" ]; then
		# UUID形式確認
		./check_uuid.sh "$csv_parentSourcedId"
		# parentSourcedIdが不正
		if [ $? -ne 0 ]; then
			echo "$0:parentSourcedIdがUUID形式ではありません。$NUMBER行目:$csv_parentSourcedId"
			exit 1
		fi
	fi
	# parentSourcedIdが不正
	if [[ $csv_type = "district" ]] && [ -n "$csv_parentSourcedId" ]; then
		echo "$0:parentSourcedIdに値が入っています。$NUMBER行目:type=$csv_type, parentSourcedId=$csv_parentSourcedId"
		exit 1
	fi

	csv_sourcedId=\"$csv_sourcedId\"
	csv_status=\"$csv_status\"
	csv_dateLastModified=\"$csv_dateLastModified\"
	csv_name=\"$csv_name\"
	csv_type=\"$csv_type\"
	csv_identifier=\"$csv_identifier\"
	csv_parentSourcedId=\"$csv_parentSourcedId\"

	# orgs_importテーブルからsourcedIdが一致するレコードを取得
	QUERY="SELECT status, dateLastModified, name, type, identifier, parentSourcedId FROM orgs_import WHERE sourcedId = $csv_sourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:orgs_importからのレコードの取得に失敗しました。sourcedId=$csv_sourcedId"
		exit 1
	fi

	# レコード件数が0件ではない場合はUPDATE
	if [ -n "$VALUE" ]; then
		eval $VALUE
		status=\"$status\"
		dateLastModified=\"$dateLastModified\"
		name=\"$name\"
		type=\"$type\"
		identifier=\"$identifier\"
		parentSourcedId=\"$parentSourcedId\"

		# レコードとcsvファイルの内容が同じ場合
		if [[ $status = $csv_status ]] && [[ $dateLastModified = $csv_dateLastModified ]] && [[ $name = $csv_name ]] && [[ $type = $csv_type ]] && [[ $identifier = $csv_identifier ]] && [[ $parentSourcedId = $csv_parentSourcedId ]]; then
			QUERY=""

		# レコードとcsvファイルの内容が違う場合
		else
			QUERY="UPDATE orgs_import SET status = $csv_status, dateLastModified = $csv_dateLastModified, name = $csv_name, type = $csv_type, identifier = $csv_identifier, parentSourcedId = $csv_parentSourcedId, updated_at = now() WHERE sourcedId = $csv_sourcedId"
		fi

	# レコード件数が0件の場合はINSERT
	else
		QUERY="INSERT INTO orgs_import VALUES($csv_sourcedId, $csv_status, $csv_dateLastModified, $csv_name, $csv_type, $csv_identifier, $csv_parentSourcedId, $DIR_NAME, null, now(), now())"
	fi
	if [ -n "$QUERY" ]; then
		`echo $QUERY | $CMD_MYSQL`
		if [ $? -ne 0 ]; then
			echo "$0:orgs.csvのインポートに失敗しました。sourcedId=$csv_sourcedId"
			exit 1
		fi
	fi
	NUMBER=$((++i))
done < "$CSV_FILE"

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
