#!/bin/bash
# **************************************************
# ユーザーCSVファイルインポーﾄ
# 引数
#    CSV_FILE:ユーザーCSVファイル
#    DB      :OneRosterデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 2 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
CSV_FILE=$1
DB=$2
CMD_MYSQL="$DB"
array_grades=('P1' 'P2' 'P3' 'P4' 'P5' 'P6' 'J1' 'J2' 'J3')
array_singleKana=('ｱ' 'ｲ' 'ｳ' 'ｴ' 'ｵ' 'ｶ' 'ｷ' 'ｸ' 'ｹ' 'ｺ' 'ｻ' 'ｼ' 'ｽ' 'ｾ' 'ｿ' 'ﾀ' 'ﾁ' 'ﾂ' 'ﾃ' 'ﾄ' 'ﾅ' 'ﾆ' 'ﾇ' 'ﾈ' 'ﾉ' 'ﾊ' 'ﾋ' 'ﾌ' 'ﾍ' 'ﾎ' 'ﾏ' 'ﾐ' 'ﾑ' 'ﾒ' 'ﾓ' 'ﾔ' 'ﾕ' 'ﾖ' 'ﾗ' 'ﾘ' 'ﾙ' 'ﾚ' 'ﾛ' 'ﾜ' 'ｦ' 'ﾝ' 'ｧ' 'ｨ' 'ｩ' 'ｪ' 'ｫ' 'ｬ' 'ｭ' 'ｮ' 'ｯ' 'ﾞ' 'ﾟ')
grade=""
char=""

# ファイルの文字コード確認
if [[ $(file -i $CSV_FILE | grep -q "utf-8"; echo -n ${?} ) -ne 0 ]] && [[ $(file -i $CSV_FILE | grep -q "us-ascii"; echo -n ${?} ) -ne 0 ]]; then
	echo "$0:users.csvの文字コードが不正です。"
	exit 1
fi

# ユーザーファイルのインポート
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

		csv_enabledUser=`echo ${row} | cut -d , -f 4`
		# enabledUserのヘッダーが不正
		if [[ $csv_enabledUser != "enabledUser" ]]; then
			echo "$0:enabledUserのヘッダーが不正です。[$csv_enabledUser]"
			exit 1
		fi

		csv_username=`echo ${row} | cut -d , -f 5`
		# usernameのヘッダーが不正
		if [[ $csv_username != "username" ]]; then
			echo "$0:usernameのヘッダーが不正です。[$csv_username]"
			exit 1
		fi

		csv_userIds=`echo ${row} | cut -d , -f 6`
		# userIdsのヘッダーが不正
		if [[ $csv_userIds != "userIds" ]]; then
			echo "$0:userIdsのヘッダーが不正です。[$csv_userIds]"
			exit 1
		fi

		csv_givenName=`echo ${row} | cut -d , -f 7`
		# givenNameのヘッダーが不正
		if [[ $csv_givenName != "givenName" ]]; then
			echo "$0:givenNameのヘッダーが不正です。[$csv_givenName]"
			exit 1
		fi

		csv_familyName=`echo ${row} | cut -d , -f 8`
		# familyNameのヘッダーが不正
		if [[ $csv_familyName != "familyName" ]]; then
			echo "$0:familyNameのヘッダーが不正です。[$csv_familyName]"
			exit 1
		fi

		csv_middleName=`echo ${row} | cut -d , -f 9`
		# middleNameのヘッダーが不正
		if [[ $csv_middleName != "middleName" ]]; then
			echo "$0:middleNameのヘッダーが不正です。[$csv_middleName]"
			exit 1
		fi

		csv_identifier=`echo ${row} | cut -d , -f 10`
		# identifierのヘッダーが不正
		if [[ $csv_identifier != "identifier" ]]; then
			echo "$0:identifierのヘッダーが不正です。[$csv_identifier]"
			exit 1
		fi

		csv_email=`echo ${row} | cut -d , -f 11`
		# emailのヘッダーが不正
		if [[ $csv_email != "email" ]]; then
			echo "$0:emailのヘッダーが不正です。[$csv_email]"
			exit 1
		fi

		csv_sms=`echo ${row} | cut -d , -f 12`
		# smsのヘッダーが不正
		if [[ $csv_sms != "sms" ]]; then
			echo "$0:smsのヘッダーが不正です。[$csv_sms]"
			exit 1
		fi

		csv_phone=`echo ${row} | cut -d , -f 13`
		# phoneのヘッダーが不正
		if [[ $csv_phone != "phone" ]]; then
			echo "$0:phoneのヘッダーが不正です。[$csv_phone]"
			exit 1
		fi

		csv_agentSourcedIds=`echo ${row} | cut -d , -f 14`
		# agentSourcedIdsのヘッダーが不正
		if [[ $csv_agentSourcedIds != "agentSourcedIds" ]]; then
			echo "$0:agentSourcedIdsのヘッダーが不正です。[$csv_agentSourcedIds]"
			exit 1
		fi

		csv_grades=`echo ${row} | cut -d , -f 15`
		# gradesのヘッダーが不正
		if [[ $csv_grades != "grades" ]]; then
			echo "$0:gradesのヘッダーが不正です。[$csv_grades]"
			exit 1
		fi

		csv_password=`echo ${row} | cut -d , -f 16`
		# passwordのヘッダーが不正
		if [[ $csv_password != "password" ]]; then
			echo "$0:passwordのヘッダーが不正です。[$csv_password]"
			exit 1
		fi

		csv_userMasterIdentifier=`echo ${row} | cut -d , -f 17`
		# userMasterIdentifierのヘッダーが不正
		if [[ $csv_userMasterIdentifier != "userMasterIdentifier" ]]; then
			echo "$0:userMasterIdentifierのヘッダーが不正です。[$csv_userMasterIdentifier]"
			exit 1
		fi

		csv_resourceSourcedIds=`echo ${row} | cut -d , -f 18`
		# resourceSourcedIdsのヘッダーが不正
		if [[ $csv_resourceSourcedIds != "resourceSourcedIds" ]]; then
			echo "$0:resourceSourcedIdsのヘッダーが不正です。[$csv_resourceSourcedIds]"
			exit 1
		fi

		csv_preferredGivenName=`echo ${row} | cut -d , -f 19`
		# preferredGivenNameのヘッダーが不正
		if [[ $csv_preferredGivenName != "preferredGivenName" ]]; then
			echo "$0:preferredGivenNameのヘッダーが不正です。[$csv_preferredGivenName]"
			exit 1
		fi

		csv_preferredMiddleName=`echo ${row} | cut -d , -f 20`
		# preferredMiddleNameのヘッダーが不正
		if [[ $csv_preferredMiddleName != "preferredMiddleName" ]]; then
			echo "$0:preferredMiddleNameのヘッダーが不正です。[$csv_preferredMiddleName]"
			exit 1
		fi

		csv_preferredFamilyName=`echo ${row} | cut -d , -f 21`
		# preferredFamilyNameのヘッダーが不正
		if [[ $csv_preferredFamilyName != "preferredFamilyName" ]]; then
			echo "$0:preferredFamilyNameのヘッダーが不正です。[$csv_preferredFamilyName]"
			exit 1
		fi

		csv_primaryOrgSourcedId=`echo ${row} | cut -d , -f 22`
		# primaryOrgSourcedIdのヘッダーが不正
		if [[ $csv_primaryOrgSourcedId != "primaryOrgSourcedId" ]]; then
			echo "$0:primaryOrgSourcedIdのヘッダーが不正です。[$csv_primaryOrgSourcedId]"
			exit 1
		fi

		csv_pronouns=`echo ${row} | cut -d , -f 23`
		# pronounsのヘッダーが不正
		if [[ $csv_pronouns != "pronouns" ]]; then
			echo "$0:pronounsのヘッダーが不正です。[$csv_pronouns]"
			exit 1
		fi

		csv_metadata_jp_kanaGivenName=`echo ${row} | cut -d , -f 24`
		# metadata.jp.kanaGivenNameのヘッダーが不正
		if [[ $csv_metadata_jp_kanaGivenName != "metadata.jp.kanaGivenName" ]]; then
			echo "$0:metadata.jp.kanaGivenNameのヘッダーが不正です。[$csv_metadata_jp_kanaGivenName]"
			exit 1
		fi

		csv_metadata_jp_kanaFamilyName=`echo ${row} | cut -d , -f 25`
		# metadata.jp.kanaFamilyNameのヘッダーが不正
		if [[ $csv_metadata_jp_kanaFamilyName != "metadata.jp.kanaFamilyName" ]]; then
			echo "$0:metadata.jp.kanaFamilyNameのヘッダーが不正です。[$csv_metadata_jp_kanaFamilyName]"
			exit 1
		fi

		csv_metadata_jp_kanaMiddleName=`echo ${row} | cut -d , -f 26 | sed -e "s/[\r\n]\+//g"`
		# metadata.jp.kanaMiddleNameのヘッダーが不正
		if [[ $csv_metadata_jp_kanaMiddleName != "metadata.jp.kanaMiddleName" ]]; then
			echo "$0:metadata.jp.kanaMiddleNameのヘッダーが不正です。[$csv_metadata_jp_kanaMiddleName]"
			exit 1
		fi

		csv_metadata_jp_homeClass=`echo ${row} | cut -d , -f 27 | sed -e "s/[\r\n]\+//g"`
		# metadata.jp.homeClassのヘッダーが不正
		if [[ $csv_metadata_jp_homeClass != "metadata.jp.homeClass" ]]; then
			echo "$0:metadata.jp.homeClassのヘッダーが不正です。[$csv_metadata_jp_homeClass]"
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

	csv_enabledUser=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $4}' | sed 's/"//g'`
	# enabledUserに値が入っていない
	if [ ! -n "$csv_enabledUser" ]; then
		echo "$0:enabledUserに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# enabledUserが不正
	if [[ $csv_enabledUser != "true" ]]; then
		echo "$0:enabledUserが指定値以外の値です。$NUMBER行目:$csv_enabledUser"
		exit 1
	fi

	csv_username=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $5}' | sed 's/"//g'`
	# usernameに値が入っていない
	if [ ! -n "$csv_username" ]; then
		echo "$0:usernameに値が入っていません。$NUMBER行目"
		exit 1
	fi

	csv_userIds=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $6}' | sed 's/"//g'`
	# userIdsに値が入っている
	if [ -n "$csv_userIds" ]; then
		# userIdsが不正
		if [[ $(echo ${csv_userIds:0:1}) != "{" ]]; then
			echo "$0:userIdsが不正です。$NUMBER行目:$csv_userIds"
			exit 1
		fi
		if [[ $(echo ${csv_userIds:${#csv_userIds}-1:1}) != "}" ]]; then
			echo "$0:userIdsが不正です。$NUMBER行目:$csv_userIds"
			exit 1
		fi
	fi

	csv_givenName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $7}' | sed 's/"//g'`
	# givenNameに値が入っていない
	if [ ! -n "$csv_givenName" ]; then
		echo "$0:givenNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# givenNameが不正
		if [[ "$csv_givenName" == *"$char"* ]]; then
			echo "$0:givenNameに半角カナが含まれています。$NUMBER行目:$csv_givenName"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_familyName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $8}' | sed 's/"//g'`
	# familyNameに値が入っていない
	if [ ! -n "$csv_familyName" ]; then
		echo "$0:familyNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# familyNameが不正
		if [[ "$csv_familyName" == *"$char"* ]]; then
			echo "$0:familyNameに半角カナが含まれています。$NUMBER行目:$csv_familyName"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_middleName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $9}' | sed 's/"//g'`
	# middleNameに値が入っている
	if [ -n "$csv_middleName" ]; then
		for char in ${array_singleKana[@]}; do
			# middleNameが不正
			if [[ "$csv_middleName" == *"$char"* ]]; then
				echo "$0:middleNameに半角カナが含まれています。$NUMBER行目:$csv_middleName"
				exit 1
			fi
		done
		if [ $? -eq 1 ]; then
			exit 1
		fi
	fi

	csv_identifier=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $10}' | sed 's/"//g'`

	csv_email=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $11}' | sed 's/"//g'`

	csv_sms=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $12}' | sed 's/"//g'`

	csv_phone=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $13}' | sed 's/"//g'`

	csv_agentSourcedIds=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $14}' | sed 's/"//g'`

	csv_grades=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $15}' | sed 's/"//g'`
	# gradesに値が入っている
	if [ -n "$csv_grades" ]; then
		grades_list=(${csv_grades/,/ })
		for grade in ${grades_list[@]}; do
			# gradesが不正
			if [[ $(printf '%s\n' "${array_grades[@]}" | grep -qx "$grade"; echo -n ${?} ) -ne 0 ]]; then
				echo "$0:gradesが指定値以外の値です。$NUMBER行目:$csv_grades"
				exit 1
			fi
		done
		if [ $? -eq 1 ]; then
			exit 1
		fi
	fi

	csv_password=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $16}' | sed 's/"//g'`

	csv_userMasterIdentifier=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $17}' | sed 's/"//g'`
	# userMasterIdentifierに値が入っている
	if [ -n "$csv_userMasterIdentifier" ]; then
		# UUID形式確認
		./check_uuid.sh "$csv_userMasterIdentifier"
		# userMasterIdentifierが不正
		if [ $? -ne 0 ]; then
			echo "$0:userMasterIdentifierがUUID形式ではありません。$NUMBER行目:$csv_userMasterIdentifier"
			exit 1
		fi
		# users_importテーブルからuserMasterIdentifierが一致するレコードを取得
		userMasterIdentifier=\"$csv_userMasterIdentifier\"
		QUERY="SELECT sourcedId FROM users_import WHERE userMasterIdentifier = $userMasterIdentifier"
		VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
		if [ $? -ne 0 ]; then
			echo "$0:users_importからのレコードの取得に失敗しました。userMasterIdentifier=$csv_userMasterIdentifier"
			exit 1
		fi
		# レコード件数が0件ではない場合
		if [ -n "$VALUE" ]; then
			eval $VALUE
			# muserMasterIdentifierが重複
			if [[ $sourcedId != $csv_sourcedId ]]; then
				echo "$0:userMasterIdentifierが重複しています。$NUMBER行目:$csv_userMasterIdentifier"
				exit 1
			fi
		fi
	fi

	csv_resourceSourcedIds=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $18}' | sed 's/"//g'`

	csv_preferredGivenName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $19}' | sed 's/"//g'`
	# preferredGivenNameに値が入っていない
	if [ ! -n "$csv_preferredGivenName" ]; then
		echo "$0:preferredGivenNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# preferredGivenNameが不正
		if [[ "$csv_preferredGivenName" == *"$char"* ]]; then
			echo "$0:preferredGivenNameに半角カナが含まれています。$NUMBER行目:$csv_preferredGivenName"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_preferredMiddleName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $20}' | sed 's/"//g'`
	# preferredMiddleNameに値が入っている
	if [ -n "$csv_preferredMiddleName" ]; then
		for char in ${array_singleKana[@]}; do
			# preferredMiddleNameが不正
			if [[ "$csv_preferredMiddleName" == *"$char"* ]]; then
				echo "$0:preferredMiddleNameに半角カナが含まれています。$NUMBER行目:$csv_preferredMiddleName"
				exit 1
			fi
		done
		if [ $? -eq 1 ]; then
			exit 1
		fi
	fi

	csv_preferredFamilyName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $21}' | sed 's/"//g'`
	# preferredFamilyNameに値が入っていない
	if [ ! -n "$csv_preferredFamilyName" ]; then
		echo "$0:preferredFamilyNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# preferredFamilyNameが不正
		if [[ "$csv_preferredFamilyName" == *"$char"* ]]; then
			echo "$0:preferredFamilyNameに半角カナが含まれています。$NUMBER行目:$csv_preferredFamilyName"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_primaryOrgSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $22}' | sed 's/"//g'`
	# primaryOrgSourcedIdに値が入っている
	if [ -n "$csv_primaryOrgSourcedId" ]; then
		# UUID形式確認
		./check_uuid.sh "$csv_primaryOrgSourcedId"
		# primaryOrgSourcedIdが不正
		if [ $? -ne 0 ]; then
			echo "$0:primaryOrgSourcedIdがUUID形式ではありません。$NUMBER行目:$csv_primaryOrgSourcedId"
			exit 1
		fi
		# orgs_importテーブルからprimaryOrgSourcedIdが一致するレコードを取得
		primaryOrgSourcedId=\"$csv_primaryOrgSourcedId\"
		QUERY="SELECT type FROM orgs_import WHERE sourcedId = $primaryOrgSourcedId"
		VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
		if [ $? -ne 0 ]; then
			echo "$0:orgs_importからのレコードの取得に失敗しました。sourcedId=$csv_primaryOrgSourcedId"
			exit 1
		fi
		# レコード件数が0件ではない場合
		if [ -n "$VALUE" ]; then
			eval $VALUE
			# typeがdistrict
			if [[ $type = "district" ]]; then
				echo "$0:primaryOrgSourcedIdの参照先のorgs.typeがdistrictです。$NUMBER行目:$csv_primaryOrgSourcedId"
				exit 1
			fi
		# レコード件数が0件の場合
		else
			echo "$0:primaryOrgSourcedIdがorgsに存在しません。$NUMBER行目:$csv_primaryOrgSourcedId"
			exit 1
		fi
	fi

	csv_pronouns=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $23}' | sed 's/"//g'`

	csv_metadata_jp_kanaGivenName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $24}' | sed 's/"//g'`
	# metadata.jp.kanaGivenNameに値が入っていない
	if [ ! -n "$csv_metadata_jp_kanaGivenName" ]; then
		echo "$0:metadata.jp.kanaGivenNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# metadata.jp.kanaGivenNameが不正
		if [[ "$csv_metadata_jp_kanaGivenName" == *"$char"* ]]; then
			echo "$0:metadata.jp.kanaGivenNameに半角カナが含まれています。$NUMBER行目:$csv_metadata_jp_kanaGivenName"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_metadata_jp_kanaFamilyName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $25}' | sed 's/"//g'`
	# metadata.jp.kanaFamilyNameに値が入っていない
	if [ ! -n "$csv_metadata_jp_kanaFamilyName" ]; then
		echo "$0:metadata.jp.kanaFamilyNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# metadata.jp.kanaFamilyNameが不正
		if [[ "$csv_metadata_jp_kanaFamilyName" == *"$char"* ]]; then
			echo "$0:metadata.jp.kanaFamilyNameに半角カナが含まれています。$NUMBER行目:$csv_metadata_jp_kanaFamilyName"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_metadata_jp_kanaMiddleName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $26}' | sed 's/"//g'`
	# metadata.jp.kanaMiddleNameに値が入っている
	if [ -n "$csv_metadata_jp_kanaMiddleName" ]; then
		for char in ${array_singleKana[@]}; do
			# metadata.jp.kanaMiddleNameが不正
			if [[ "$csv_metadata_jp_kanaMiddleName" == *"$char"* ]]; then
				echo "$0:metadata.jp.kanaMiddleNameに半角カナが含まれています。$NUMBER行目:$csv_metadata_jp_kanaMiddleName"
				exit 1
			fi
		done
		if [ $? -eq 1 ]; then
			exit 1
		fi
	fi

	csv_metadata_jp_homeClass=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $27}' | sed 's/"//g'`
	# 最後のカラムは改行コードを除外
	csv_metadata_jp_homeClass=`echo $csv_metadata_jp_homeClass | sed -e "s/[\r\n]\+//g"`
	# metadata.jp.homeClassに値が入っていない
	if [ ! -n "$csv_metadata_jp_homeClass" ]; then
		echo "$0:metadata.jp.homeClassに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# metadata.jp.homeClassに値が入っている
	if [ -n "$csv_metadata_jp_homeClass" ]; then
		# UUID形式確認
		./check_uuid.sh "$csv_metadata_jp_homeClass"
		# metadata.jp.homeClassが不正
		if [ $? -ne 0 ]; then
			echo "$0:metadata.jp.homeClassがUUID形式ではありません。$NUMBER行目:$csv_metadata_jp_homeClass"
			exit 1
		fi
		# classes_importテーブルからmetadata.jp.homeClassが一致するレコードを取得
		metadata_jp_homeClass=\"$csv_metadata_jp_homeClass\"
		QUERY="SELECT sourcedId FROM classes_import WHERE sourcedId = $metadata_jp_homeClass"
		VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
		if [ $? -ne 0 ]; then
			echo "$0:classes_importからのレコードの取得に失敗しました。sourcedId=$csv_metadata_jp_homeClass"
			exit 1
		fi
		# レコード件数が0件の場合
		if [ ! -n "$VALUE" ]; then
			echo "$0:metadata.jp.homeClassがclassesに存在しません。$NUMBER行目:$csv_metadata_jp_homeClass"
			exit 1
		fi
	fi

	csv_sourcedId=\"$csv_sourcedId\"
	csv_status=\"$csv_status\"
	csv_dateLastModified=\"$csv_dateLastModified\"
	csv_enabledUser=\"$csv_enabledUser\"
	csv_username=\"$csv_username\"
	csv_userIds=\"$csv_userIds\"
	csv_givenName=\"$csv_givenName\"
	csv_familyName=\"$csv_familyName\"
	csv_middleName=\"$csv_middleName\"
	csv_identifier=\"$csv_identifier\"
	csv_email=\"$csv_email\"
	csv_sms=\"$csv_sms\"
	csv_phone=\"$csv_phone\"
	csv_agentSourcedIds=\"$csv_agentSourcedIds\"
	csv_grades=\"$csv_grades\"
	csv_password=\"$csv_password\"
	csv_userMasterIdentifier=\"$csv_userMasterIdentifier\"
	csv_resourceSourcedIds=\"$csv_resourceSourcedIds\"
	csv_preferredGivenName=\"$csv_preferredGivenName\"
	csv_preferredMiddleName=\"$csv_preferredMiddleName\"
	csv_preferredFamilyName=\"$csv_preferredFamilyName\"
	csv_primaryOrgSourcedId=\"$csv_primaryOrgSourcedId\"
	csv_pronouns=\"$csv_pronouns\"
	csv_metadata_jp_kanaGivenName=\"$csv_metadata_jp_kanaGivenName\"
	csv_metadata_jp_kanaFamilyName=\"$csv_metadata_jp_kanaFamilyName\"
	csv_metadata_jp_kanaMiddleName=\"$csv_metadata_jp_kanaMiddleName\"
	csv_metadata_jp_homeClass=\"$csv_metadata_jp_homeClass\"

	# users_importテーブルからsourcedIdが一致するレコードを取得
	QUERY="SELECT status, dateLastModified, enabledUser, username, userIds, givenName, familyName, middleName, identifier, email, sms, phone, agentSourcedIds, grades, password, userMasterIdentifier, resourceSourcedIds, preferredGivenName, preferredMiddleName, preferredFamilyName, primaryOrgSourcedId, pronouns, metadata_jp_kanaGivenName, metadata_jp_kanaFamilyName, metadata_jp_kanaMiddleName, metadata_jp_homeClass FROM users_import WHERE sourcedId = $csv_sourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:users_importからのレコードの取得に失敗しました。sourcedId=$csv_sourcedId"
		exit 1
	fi

	# レコード件数が0件ではない場合はUPDATE
	if [ -n "$VALUE" ]; then
		eval $VALUE
		status=\"$status\"
		dateLastModified=\"$dateLastModified\"
		enabledUser=\"$enabledUser\"
		username=\"$username\"
		userIds=\"$userIds\"
		givenName=\"$givenName\"
		familyName=\"$familyName\"
		middleName=\"$middleName\"
		identifier=\"$identifier\"
		email=\"$email\"
		sms=\"$sms\"
		phone=\"$phone\"
		agentSourcedIds=\"$agentSourcedIds\"
		grades=\"$grades\"
		password=\"$password\"
		userMasterIdentifier=\"$userMasterIdentifier\"
		resourceSourcedIds=\"$resourceSourcedIds\"
		preferredGivenName=\"$preferredGivenName\"
		preferredMiddleName=\"$preferredMiddleName\"
		preferredFamilyName=\"$preferredFamilyName\"
		primaryOrgSourcedId=\"$primaryOrgSourcedId\"
		pronouns=\"$pronouns\"
		metadata_jp_kanaGivenName=\"$metadata_jp_kanaGivenName\"
		metadata_jp_kanaFamilyName=\"$metadata_jp_kanaFamilyName\"
		metadata_jp_kanaMiddleName=\"$metadata_jp_kanaMiddleName\"
		metadata_jp_homeClass=\"$metadata_jp_homeClass\"

		# レコードとcsvファイルの内容が同じ場合
		if [[ $status = $csv_status ]] && [[ $dateLastModified = $csv_dateLastModified ]] && [[ $enabledUser = $csv_enabledUser ]] && [[ $username = $csv_username ]] && [[ $userIds = $csv_userIds ]] && [[ $givenName = $csv_givenName ]] && [[ $familyName = $csv_familyName ]] && [[ $middleName = $csv_middleName ]] && [[ $identifier = $csv_identifier ]] && [[ $email = $csv_email ]] && [[ $sms = $csv_sms ]] && [[ $phone = $csv_phone ]] && [[ $agentSourcedIds = $csv_agentSourcedIds ]] && [[ $grades = $csv_grades ]] && [[ $password = $csv_password ]] && [[ $userMasterIdentifier = $csv_userMasterIdentifier ]] && [[ $resourceSourcedIds = $csv_resourceSourcedIds ]] && [[ $preferredGivenName = $csv_preferredGivenName ]] && [[ $preferredMiddleName = $csv_preferredMiddleName ]] && [[ $preferredFamilyName = $csv_preferredFamilyName ]] && [[ $primaryOrgSourcedId = $csv_primaryOrgSourcedId ]] && [[ $pronouns = $csv_pronouns ]] && [[ $metadata_jp_kanaGivenName = $csv_metadata_jp_kanaGivenName ]] && [[ $metadata_jp_kanaFamilyName = $csv_metadata_jp_kanaFamilyName ]] && [[ $metadata_jp_kanaMiddleName = $csv_metadata_jp_kanaMiddleName ]] && [[ $metadata_jp_homeClass = $csv_metadata_jp_homeClass ]]; then
			QUERY=""

		# レコードとcsvファイルの内容が違う場合
		else
			QUERY="UPDATE users_import SET status = $csv_status, dateLastModified = $csv_dateLastModified, enabledUser = $csv_enabledUser, username = $csv_username, userIds = $csv_userIds, givenName = $csv_givenName, familyName = $csv_familyName, middleName = $csv_middleName, identifier = $csv_identifier, email = $csv_email, sms = $csv_sms, phone = $csv_phone, agentSourcedIds = $csv_agentSourcedIds, grades = $csv_grades, password = $csv_password, userMasterIdentifier = $csv_userMasterIdentifier, resourceSourcedIds = $csv_resourceSourcedIds, preferredGivenName = $csv_preferredGivenName, preferredMiddleName = $csv_preferredMiddleName, preferredFamilyName = $csv_preferredFamilyName, primaryOrgSourcedId = $csv_primaryOrgSourcedId, pronouns = $csv_pronouns, metadata_jp_kanaGivenName = $csv_metadata_jp_kanaGivenName, metadata_jp_kanaFamilyName = $csv_metadata_jp_kanaFamilyName, metadata_jp_kanaMiddleName = $csv_metadata_jp_kanaMiddleName, metadata_jp_homeClass = $csv_metadata_jp_homeClass, updated_at = now() WHERE sourcedId = $csv_sourcedId"
		fi

	# レコード件数が0件の場合はINSERT
	else
		QUERY="INSERT INTO users_import VALUES($csv_sourcedId, $csv_status, $csv_dateLastModified, $csv_enabledUser, $csv_username, $csv_userIds, $csv_givenName, $csv_familyName, $csv_middleName, $csv_identifier, $csv_email, $csv_sms, $csv_phone, $csv_agentSourcedIds, $csv_grades, $csv_password, $csv_userMasterIdentifier, $csv_resourceSourcedIds, $csv_preferredGivenName, $csv_preferredMiddleName, $csv_preferredFamilyName, $csv_primaryOrgSourcedId, $csv_pronouns, $csv_metadata_jp_kanaGivenName, $csv_metadata_jp_kanaFamilyName, $csv_metadata_jp_kanaMiddleName, $csv_metadata_jp_homeClass, now(), now())"
	fi
	if [ -n "$QUERY" ]; then
		`echo $QUERY | $CMD_MYSQL`
		if [ $? -ne 0 ]; then
			echo "$0:users.csvのインポートに失敗しました。sourcedId=$csv_sourcedId"
			exit 1
		fi
	fi
	NUMBER=$((++i))
done < "$CSV_FILE"

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
