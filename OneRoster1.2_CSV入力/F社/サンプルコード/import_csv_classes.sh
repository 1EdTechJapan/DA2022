#!/bin/bash
# **************************************************
# 学校クラスCSVファイルインポーﾄ
# 引数
#    CSV_FILE:学校クラスCSVファイル
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
array_subjectCodes=('P010' 'P020' 'P030' 'P040' 'P050' 'P060' 'P070' 'P080' 'P090' 'P100' 'J010' 'J020' 'J030' 'J040' 'J050' 'J060' 'J070' 'J080' 'J090')
array_singleKana=('ｱ' 'ｲ' 'ｳ' 'ｴ' 'ｵ' 'ｶ' 'ｷ' 'ｸ' 'ｹ' 'ｺ' 'ｻ' 'ｼ' 'ｽ' 'ｾ' 'ｿ' 'ﾀ' 'ﾁ' 'ﾂ' 'ﾃ' 'ﾄ' 'ﾅ' 'ﾆ' 'ﾇ' 'ﾈ' 'ﾉ' 'ﾊ' 'ﾋ' 'ﾌ' 'ﾍ' 'ﾎ' 'ﾏ' 'ﾐ' 'ﾑ' 'ﾒ' 'ﾓ' 'ﾔ' 'ﾕ' 'ﾖ' 'ﾗ' 'ﾘ' 'ﾙ' 'ﾚ' 'ﾛ' 'ﾜ' 'ｦ' 'ﾝ' 'ｧ' 'ｨ' 'ｩ' 'ｪ' 'ｫ' 'ｬ' 'ｭ' 'ｮ' 'ｯ' 'ﾞ' 'ﾟ')
grade=""
subjectCode=""
char=""

# ファイルの文字コード確認
if [[ $(file -i $CSV_FILE | grep -q "utf-8"; echo -n ${?} ) -ne 0 ]] && [[ $(file -i $CSV_FILE | grep -q "us-ascii"; echo -n ${?} ) -ne 0 ]]; then
	echo "$0:classes.csvの文字コードが不正です。"
	exit 1
fi

# 学校クラスファイルのインポート
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

		csv_title=`echo ${row} | cut -d , -f 4`
		# titleのヘッダーが不正
		if [[ $csv_title != "title" ]]; then
			echo "$0:titleのヘッダーが不正です。[$csv_title]"
			exit 1
		fi

		csv_grades=`echo ${row} | cut -d , -f 5`
		# gradesのヘッダーが不正
		if [[ $csv_grades != "grades" ]]; then
			echo "$0:gradesのヘッダーが不正です。[$csv_grades]"
			exit 1
		fi

		csv_courseSourcedId=`echo ${row} | cut -d , -f 6`
		# courseSourcedIdのヘッダーが不正
		if [[ $csv_courseSourcedId != "courseSourcedId" ]]; then
			echo "$0:courseSourcedIdのヘッダーが不正です。[$csv_courseSourcedId]"
			exit 1
		fi

		csv_classCode=`echo ${row} | cut -d , -f 7`
		# classCodeのヘッダーが不正
		if [[ $csv_classCode != "classCode" ]]; then
			echo "$0:classCodeのヘッダーが不正です。[$csv_classCode]"
			exit 1
		fi

		csv_classType=`echo ${row} | cut -d , -f 8`
		# classTypeのヘッダーが不正
		if [[ $csv_classType != "classType" ]]; then
			echo "$0:classTypeのヘッダーが不正です。[$csv_classType]"
			exit 1
		fi

		csv_location=`echo ${row} | cut -d , -f 9`
		# locationのヘッダーが不正
		if [[ $csv_location != "location" ]]; then
			echo "$0:locationのヘッダーが不正です。[$csv_location]"
			exit 1
		fi

		csv_schoolSourcedId=`echo ${row} | cut -d , -f 10`
		# schoolSourcedIdのヘッダーが不正
		if [[ $csv_schoolSourcedId != "schoolSourcedId" ]]; then
			echo "$0:schoolSourcedIdのヘッダーが不正です。[$csv_schoolSourcedId]"
			exit 1
		fi

		csv_termSourcedIds=`echo ${row} | cut -d , -f 11`
		# termSourcedIdsのヘッダーが不正
		if [[ $csv_termSourcedIds != "termSourcedIds" ]]; then
			echo "$0:termSourcedIdsのヘッダーが不正です。[$csv_termSourcedIds]"
			exit 1
		fi

		csv_subjects=`echo ${row} | cut -d , -f 12`
		# subjectsのヘッダーが不正
		if [[ $csv_subjects != "subjects" ]]; then
			echo "$0:subjectsのヘッダーが不正です。[$csv_subjects]"
			exit 1
		fi

		csv_subjectCodes=`echo ${row} | cut -d , -f 13`
		# subjectCodesのヘッダーが不正
		if [[ $csv_subjectCodes != "subjectCodes" ]]; then
			echo "$0:subjectCodesのヘッダーが不正です。[$csv_subjectCodes]"
			exit 1
		fi

		csv_periods=`echo ${row} | cut -d , -f 14 | sed -e "s/[\r\n]\+//g"`
		# periodsのヘッダーが不正
		if [[ $csv_periods != "periods" ]]; then
			echo "$0:periodsのヘッダーが不正です。[$csv_periods]"
			exit 1
		fi

		csv_metadata_jp_specialNeeds=`echo ${row} | cut -d , -f 15 | sed -e "s/[\r\n]\+//g"`
		# metadata.jp.specialNeedsのヘッダーが不正
		if [[ $csv_metadata_jp_specialNeeds != "metadata.jp.specialNeeds" ]]; then
			echo "$0:metadata.jp.specialNeedsのヘッダーが不正です。[$csv_metadata_jp_specialNeeds]"
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

	csv_title=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $4}' | sed 's/"//g'`
	# titleに値が入っていない
	if [ ! -n "$csv_title" ]; then
		echo "$0:titleに値が入っていません。$NUMBER行目"
		exit 1
	fi
	for char in ${array_singleKana[@]}; do
		# titleが不正
		if [[ "$csv_title" == *"$char"* ]]; then
			echo "$0:titleに半角カナが含まれています。$NUMBER行目:$csv_title"
			exit 1
		fi
	done
	if [ $? -eq 1 ]; then
		exit 1
	fi

	csv_grades=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $5}' | sed 's/"//g'`
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

	csv_courseSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $6}' | sed 's/"//g'`
	# courseSourcedIdに値が入っていない
	if [ ! -n "$csv_courseSourcedId" ]; then
		echo "$0:courseSourcedIdに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# UUID形式確認
	./check_uuid.sh "$csv_courseSourcedId"
	# courseSourcedIdが不正
	if [ $? -ne 0 ]; then
		echo "$0:courseSourcedIdがUUID形式ではありません。$NUMBER行目:$csv_courseSourcedId"
		exit 1
	fi

	csv_classCode=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $7}' | sed 's/"//g'`

	csv_classType=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $8}' | sed 's/"//g'`
	# classTypeに値が入っていない
	if [ ! -n "$csv_classType" ]; then
		echo "$0:classTypeに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# classTypeが不正
	if [[ $csv_classType != "homeroom" ]] && [[ $csv_classType != "scheduled" ]]; then
		echo "$0:classTypeが指定値以外の値です。$NUMBER行目:$csv_classType"
		exit 1
	fi

	csv_location=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $9}' | sed 's/"//g'`
	# locationに値が入っている
	if [ -n "$csv_location" ]; then
		for char in ${array_singleKana[@]}; do
			# locationが不正
			if [[ "$csv_location" == *"$char"* ]]; then
				echo "$0:locationに半角カナが含まれています。$NUMBER行目:$csv_location"
				exit 1
			fi
		done
		if [ $? -eq 1 ]; then
			exit 1
		fi
	fi

	csv_schoolSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $10}' | sed 's/"//g'`
	# schoolSourcedIdに値が入っていない
	if [ ! -n "$csv_schoolSourcedId" ]; then
		echo "$0:schoolSourcedIdに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# UUID形式確認
	./check_uuid.sh "$csv_schoolSourcedId"
	# schoolSourcedIdが不正
	if [ $? -ne 0 ]; then
		echo "$0:schoolSourcedIdがUUID形式ではありません。$NUMBER行目:$csv_schoolSourcedId"
		exit 1
	fi
	# orgs_importテーブルからschoolSourcedIdが一致するレコードを取得
	schoolSourcedId=\"$csv_schoolSourcedId\"
	QUERY="SELECT type FROM orgs_import WHERE sourcedId = $schoolSourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:orgs_importからのレコードの取得に失敗しました。sourcedId=$csv_schoolSourcedId"
		exit 1
	fi
	# レコード件数が0件ではない場合
	if [ -n "$VALUE" ]; then
		eval $VALUE
		# typeがdistrict
		if [[ $type = "district" ]]; then
			echo "$0:schoolSourcedIdの参照先のorgs.typeがdistrictです。$NUMBER行目:$csv_schoolSourcedId"
			exit 1
		fi
	# レコード件数が0件の場合
	else
		echo "$0:schoolSourcedIdがorgsに存在しません。$NUMBER行目:$csv_schoolSourcedId"
		exit 1
	fi

	csv_termSourcedIds=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $11}' | sed 's/"//g'`
	# termSourcedIdsに値が入っていない
	if [ ! -n "$csv_termSourcedIds" ]; then
		echo "$0:termSourcedIdsに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# UUID形式確認
	./check_uuid.sh "$csv_termSourcedIds"
	# termSourcedIdsが不正
	if [ $? -ne 0 ]; then
		echo "$0:termSourcedIdsがUUID形式ではありません。$NUMBER行目:$csv_termSourcedIds"
		exit 1
	fi

	csv_subjects=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $12}' | sed 's/"//g'`

	csv_subjectCodes=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $13}' | sed 's/"//g'`
	# subjectCodesに値が入っている
	if [ -n "$csv_subjectCodes" ]; then
		subjectCodes_list=(${csv_subjectCodes/,/ })
		for subjectCode in ${subjectCodes_list[@]}; do
			# subjectCodesが不正
			if [[ $(printf '%s\n' "${array_subjectCodes[@]}" | grep -qx "$subjectCode"; echo -n ${?} ) -ne 0 ]]; then
				echo "$0:subjectCodesが指定値以外の値です。$NUMBER行目:$csv_subjectCodes"
				exit 1
			fi
		done
		if [ $? -eq 1 ]; then
			exit 1
		fi
	fi

	csv_periods=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $14}' | sed 's/"//g'`

	csv_metadata_jp_specialNeeds=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $15}' | sed 's/"//g'`
	# 最後のカラムは改行コードを除外
	csv_metadata_jp_specialNeeds=`echo $csv_metadata_jp_specialNeeds | sed -e "s/[\r\n]\+//g"`
	# metadata.jp.specialNeedsに値が入っている
	if [ -n "$csv_metadata_jp_specialNeeds" ]; then
		# metadata.jp.specialNeedsが不正
		if [[ $csv_metadata_jp_specialNeeds != "true" ]] && [[ $csv_metadata_jp_specialNeeds != "false" ]]; then
			echo "$0:metadata.jp.specialNeedsが指定値以外の値です。$NUMBER行目:$csv_metadata_jp_specialNeeds"
			exit 1
		fi
	fi

	csv_sourcedId=\"$csv_sourcedId\"
	csv_status=\"$csv_status\"
	csv_dateLastModified=\"$csv_dateLastModified\"
	csv_title=\"$csv_title\"
	csv_grades=\"$csv_grades\"
	csv_courseSourcedId=\"$csv_courseSourcedId\"
	csv_classCode=\"$csv_classCode\"
	csv_classType=\"$csv_classType\"
	csv_location=\"$csv_location\"
	csv_schoolSourcedId=\"$csv_schoolSourcedId\"
	csv_termSourcedIds=\"$csv_termSourcedIds\"
	csv_subjects=\"$csv_subjects\"
	csv_subjectCodes=\"$csv_subjectCodes\"
	csv_periods=\"$csv_periods\"
	csv_metadata_jp_specialNeeds=\"$csv_metadata_jp_specialNeeds\"

	# classes_importテーブルからsourcedIdが一致するレコードを取得
	QUERY="SELECT status, dateLastModified, title, grades, courseSourcedId, classCode, classType, location, schoolSourcedId, termSourcedIds, subjects, subjectCodes, periods, metadata_jp_specialNeeds FROM classes_import WHERE sourcedId = $csv_sourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:classes_importからのレコードの取得に失敗しました。sourcedId=$csv_sourcedId"
		exit 1
	fi

	# レコード件数が0件ではない場合はUPDATE
	if [ -n "$VALUE" ]; then
		eval $VALUE
		status=\"$status\"
		dateLastModified=\"$dateLastModified\"
		title=\"$title\"
		grades=\"$grades\"
		courseSourcedId=\"$courseSourcedId\"
		classCode=\"$classCode\"
		classType=\"$classType\"
		location=\"$location\"
		schoolSourcedId=\"$schoolSourcedId\"
		termSourcedIds=\"$termSourcedIds\"
		subjects=\"$subjects\"
		subjectCodes=\"$subjectCodes\"
		periods=\"$periods\"
		metadata_jp_specialNeeds=\"$metadata_jp_specialNeeds\"

		# レコードとcsvファイルの内容が同じ場合
		if [[ $status = $csv_status ]] && [[ $dateLastModified = $csv_dateLastModified ]] && [[ $title = $csv_title ]] && [[ $grades = $csv_grades ]] && [[ $courseSourcedId = $csv_courseSourcedId ]] && [[ $classCode = $csv_classCode ]] && [[ $classType = $csv_classType ]] && [[ $location = $csv_location ]] && [[ $schoolSourcedId = $csv_schoolSourcedId ]] && [[ $termSourcedIds = $csv_termSourcedIds ]] && [[ $subjects = $csv_subjects ]] && [[ $subjectCodes = $csv_subjectCodes ]] && [[ $periods = $csv_periods ]] && [[ $metadata_jp_specialNeeds = $csv_metadata_jp_specialNeeds ]]; then
			QUERY=""

		# レコードとcsvファイルの内容が違う場合
		else
			QUERY="UPDATE classes_import SET status = $csv_status, dateLastModified = $csv_dateLastModified, title = $csv_title, grades = $csv_grades, courseSourcedId = $csv_courseSourcedId, classCode = $csv_classCode, classType = $csv_classType, location = $csv_location, schoolSourcedId = $csv_schoolSourcedId, termSourcedIds = $csv_termSourcedIds, subjects = $csv_subjects, subjectCodes = $csv_subjectCodes, periods = $csv_periods, metadata_jp_specialNeeds = $csv_metadata_jp_specialNeeds, updated_at = now() WHERE sourcedId = $csv_sourcedId"
		fi

	# レコード件数が0件の場合はINSERT
	else
		QUERY="INSERT INTO classes_import VALUES($csv_sourcedId, $csv_status, $csv_dateLastModified, $csv_title, $csv_grades, $csv_courseSourcedId, $csv_classCode, $csv_classType, $csv_location, $csv_schoolSourcedId, $csv_termSourcedIds, $csv_subjects, $csv_subjectCodes, $csv_periods, $csv_metadata_jp_specialNeeds, now(), now())"
	fi
	if [ -n "$QUERY" ]; then
		`echo $QUERY | $CMD_MYSQL`
		if [ $? -ne 0 ]; then
			echo "$0:classes.csvのインポートに失敗しました。sourcedId=$csv_sourcedId"
			exit 1
		fi
	fi
	NUMBER=$((++i))
done < "$CSV_FILE"

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
