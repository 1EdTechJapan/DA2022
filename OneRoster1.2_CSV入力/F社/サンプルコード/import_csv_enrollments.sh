#!/bin/bash
# **************************************************
# enrollmentCSVファイルインポーﾄ
# 引数
#    CSV_FILE:enrollmentCSVファイル
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

# ファイルの文字コード確認
if [[ $(file -i $CSV_FILE | grep -q "utf-8"; echo -n ${?} ) -ne 0 ]] && [[ $(file -i $CSV_FILE | grep -q "us-ascii"; echo -n ${?} ) -ne 0 ]]; then
	echo "$0:enrollments.csvの文字コードが不正です。"
	exit 1
fi

# enrollmentsファイルのインポート
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

		csv_classSourcedId=`echo ${row} | cut -d , -f 4`
		# classSourcedIdのヘッダーが不正
		if [[ $csv_classSourcedId != "classSourcedId" ]]; then
			echo "$0:classSourcedIdのヘッダーが不正です。[$csv_classSourcedId]"
			exit 1
		fi

		csv_schoolSourcedId=`echo ${row} | cut -d , -f 5`
		# schoolSourcedIdのヘッダーが不正
		if [[ $csv_schoolSourcedId != "schoolSourcedId" ]]; then
			echo "$0:schoolSourcedIdのヘッダーが不正です。[$csv_schoolSourcedId]"
			exit 1
		fi

		csv_userSourcedId=`echo ${row} | cut -d , -f 6`
		# userSourcedIdのヘッダーが不正
		if [[ $csv_userSourcedId != "userSourcedId" ]]; then
			echo "$0:userSourcedIdのヘッダーが不正です。[$csv_userSourcedId]"
			exit 1
		fi

		csv_role=`echo ${row} | cut -d , -f 7`
		# roleのヘッダーが不正
		if [[ $csv_role != "role" ]]; then
			echo "$0:roleのヘッダーが不正です。[$csv_role]"
			exit 1
		fi

		csv_csv_primary=`echo ${row} | cut -d , -f 8`
		# primaryのヘッダーが不正
		if [[ $csv_csv_primary != "primary" ]]; then
			echo "$0:primaryのヘッダーが不正です。[$csv_csv_primary]"
			exit 1
		fi

		csv_beginDate=`echo ${row} | cut -d , -f 9`
		# beginDateのヘッダーが不正
		if [[ $csv_beginDate != "beginDate" ]]; then
			echo "$0:beginDateのヘッダーが不正です。[$csv_beginDate]"
			exit 1
		fi

		csv_endDate=`echo ${row} | cut -d , -f 10`
		# endDateのヘッダーが不正
		if [[ $csv_endDate != "endDate" ]]; then
			echo "$0:endDateのヘッダーが不正です。[$csv_endDate]"
			exit 1
		fi

		csv_metadata_jp_ShussekiNo=`echo ${row} | cut -d , -f 11 | sed -e "s/[\r\n]\+//g"`
		# metadata.jp.ShussekiNoのヘッダーが不正
		if [[ $csv_metadata_jp_ShussekiNo != "metadata.jp.ShussekiNo" ]]; then
			echo "$0:metadata.jp.ShussekiNoのヘッダーが不正です。[$csv_metadata_jp_ShussekiNo]"
			exit 1
		fi

		csv_metadata_jp_PublicFlg=`echo ${row} | cut -d , -f 12 | sed -e "s/[\r\n]\+//g"`
		# metadata.jp.PublicFlgのヘッダーが不正
		if [[ $csv_metadata_jp_PublicFlg != "metadata.jp.PublicFlg" ]]; then
			echo "$0:metadata.jp.PublicFlgのヘッダーが不正です。[$csv_metadata_jp_PublicFlg]"
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

	csv_classSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $4}' | sed 's/"//g'`
	# classSourcedIdに値が入っていない
	if [ ! -n "$csv_classSourcedId" ]; then
		echo "$0:classSourcedIdに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# UUID形式確認
	./check_uuid.sh "$csv_classSourcedId"
	# classSourcedIdが不正
	if [ $? -ne 0 ]; then
		echo "$0:classSourcedIdがUUID形式ではありません。$NUMBER行目:$csv_classSourcedId"
		exit 1
	fi
	# classes_importテーブルからclassSourcedIdが一致するレコードを取得
	classSourcedId=\"$csv_classSourcedId\"
	QUERY="SELECT sourcedId FROM classes_import WHERE sourcedId = $classSourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:classes_importからのレコードの取得に失敗しました。sourcedId=$csv_classSourcedId"
		exit 1
	fi
	# レコード件数が0件の場合
	if [ ! -n "$VALUE" ]; then
		echo "$0:classSourcedIdがclassesに存在しません。$NUMBER行目:$csv_classSourcedId"
		exit 1
	fi

	csv_schoolSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $5}' | sed 's/"//g'`
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

	csv_userSourcedId=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $6}' | sed 's/"//g'`
	# userSourcedIdに値が入っていない
	if [ ! -n "$csv_userSourcedId" ]; then
		echo "$0:userSourcedIdに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# UUID形式確認
	./check_uuid.sh "$csv_userSourcedId"
	# userSourcedIdが不正
	if [ $? -ne 0 ]; then
		echo "$0:userSourcedIdがUUID形式ではありません。$NUMBER行目:$csv_userSourcedId"
		exit 1
	fi
	# users_importテーブルからuserSourcedIdが一致するレコードを取得
	userSourcedId=\"$csv_userSourcedId\"
	QUERY="SELECT sourcedId FROM users_import WHERE sourcedId = $userSourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:users_importからのレコードの取得に失敗しました。sourcedId=$csv_userSourcedId"
		exit 1
	fi
	# レコード件数が0件の場合
	if [ ! -n "$VALUE" ]; then
		echo "$0:userSourcedIdがusersに存在しません。$NUMBER行目:$csv_userSourcedId"
		exit 1
	fi

	csv_role=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $7}' | sed 's/"//g'`
	# roleに値が入っていない
	if [ ! -n "$csv_role" ]; then
		echo "$0:roleに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# roleが不正
	if [[ $csv_role != "student" ]] && [[ $csv_role != "teacher" ]] && [[ $csv_role != "administrator" ]] && [[ $csv_role != "proctor" ]]; then
		echo "$0:roleが指定値以外の値です。$NUMBER行目:$csv_role"
		exit 1
	fi

	csv_csv_primary=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $8}' | sed 's/"//g'`
	# primaryに値が入っていない
	if [ ! -n "$csv_csv_primary" ]; then
		echo "$0:primaryに値が入っていません。$NUMBER行目"
		exit 1
	fi
	# primaryが不正
	if [[ $csv_csv_primary != "true" ]] && [[ $csv_csv_primary != "false" ]]; then
		echo "$0:primaryが指定値以外の値です。$NUMBER行目:$csv_csv_primary"
		exit 1
	fi
	if [[ $csv_role = "student" ]] && [[ $csv_csv_primary = "true" ]]; then
		echo "$0:primaryが不正です。$NUMBER行目:role=$csv_role,primary=$csv_csv_primary"
		exit 1
	fi

	csv_beginDate=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $9}' | sed 's/"//g'`
	# beginDateに値が入っている
	if [ -n "$csv_beginDate" ]; then
		date +'%Y-%m-%d' -d $csv_beginDate
		# beginDateが不正
		if [ $? -ne 0 ]; then
			echo "$0:beginDateが不正です。$NUMBER行目:$csv_beginDate"
			exit 1
		fi
	fi

	csv_endDate=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $10}' | sed 's/"//g'`
	# endDateに値が入っている
	if [ -n "$csv_endDate" ]; then
		date +'%Y-%m-%d' -d $csv_endDate
		# endDateが不正
		if [ $? -ne 0 ]; then
			echo "$0:endDateが不正です。$NUMBER行目:$csv_endDate"
			exit 1
		fi
	fi

	csv_metadata_jp_ShussekiNo=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $11}' | sed 's/"//g'`

	csv_metadata_jp_PublicFlg=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $12}' | sed 's/"//g'`
	# 最後のカラムは改行コードを除外
	csv_metadata_jp_PublicFlg=`echo $csv_metadata_jp_PublicFlg | sed -e "s/[\r\n]\+//g"`
	# metadata.jp.PublicFlgに値が入っている
	if [ -n "$csv_metadata_jp_PublicFlg" ]; then
		# metadata.jp.PublicFlgが不正
		if [[ $csv_metadata_jp_PublicFlg != "true" ]] && [[ $csv_metadata_jp_PublicFlg != "false" ]]; then
			echo "$0:metadata.jp.PublicFlgが指定値以外の値です。$NUMBER行目:$csv_metadata_jp_PublicFlg"
			exit 1
		fi
	fi

	csv_sourcedId=\"$csv_sourcedId\"
	csv_status=\"$csv_status\"
	csv_dateLastModified=\"$csv_dateLastModified\"
	csv_classSourcedId=\"$csv_classSourcedId\"
	csv_schoolSourcedId=\"$csv_schoolSourcedId\"
	csv_userSourcedId=\"$csv_userSourcedId\"
	csv_role=\"$csv_role\"
	csv_csv_primary=\"$csv_csv_primary\"
	csv_beginDate=\"$csv_beginDate\"
	csv_endDate=\"$csv_endDate\"
	csv_metadata_jp_ShussekiNo=\"$csv_metadata_jp_ShussekiNo\"
	csv_metadata_jp_PublicFlg=\"$csv_metadata_jp_PublicFlg\"

	# enrollments_importテーブルからclassSourcedIdとschoolSourcedIdとuserSourcedIdが一致するレコードを取得
	QUERY="SELECT status, dateLastModified, classSourcedId, schoolSourcedId, userSourcedId, role, csv_primary, beginDate, endDate, metadata_jp_ShussekiNo, metadata_jp_PublicFlg FROM enrollments_import WHERE classSourcedId = $csv_classSourcedId AND schoolSourcedId = $csv_schoolSourcedId AND userSourcedId = $csv_userSourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:enrollments_importからのレコードの取得に失敗しました。classSourcedId=$csv_classSourcedId,schoolSourcedId=$csv_schoolSourcedId,userSourcedId=$csv_userSourcedId"
		exit 1
	fi

	# レコード件数が0件ではない場合はUPDATE
	if [ -n "$VALUE" ]; then
		eval $VALUE
		status=\"$status\"
		dateLastModified=\"$dateLastModified\"
		classSourcedId=\"$classSourcedId\"
		schoolSourcedId=\"$schoolSourcedId\"
		userSourcedId=\"$userSourcedId\"
		role=\"$role\"
		csv_primary=\"$csv_primary\"
		beginDate=\"$beginDate\"
		endDate=\"$endDate\"
		metadata_jp_ShussekiNo=\"$metadata_jp_ShussekiNo\"
		metadata_jp_PublicFlg=\"$metadata_jp_PublicFlg\"

		# レコードとcsvファイルの内容が同じ場合
		if [[ $status = $csv_status ]] && [[ $dateLastModified = $csv_dateLastModified ]] && [[ $role = $csv_role ]] && [[ $csv_primary = $csv_csv_primary ]] && [[ $beginDate = $csv_beginDate ]] && [[ $endDate = $csv_endDate ]] && [[ $metadata_jp_ShussekiNo = $csv_metadata_jp_ShussekiNo ]] && [[ $metadata_jp_PublicFlg = $csv_metadata_jp_PublicFlg ]]; then
			QUERY=""

		# レコードとcsvファイルの内容が違う場合
		else
			QUERY="UPDATE enrollments_import SET status = $csv_status, dateLastModified = $csv_dateLastModified, role = $csv_role, csv_primary = $csv_csv_primary, beginDate = $csv_beginDate, endDate = $csv_endDate, metadata_jp_ShussekiNo = $csv_metadata_jp_ShussekiNo, metadata_jp_PublicFlg = $csv_metadata_jp_PublicFlg, updated_at = now() WHERE classSourcedId = $csv_classSourcedId AND schoolSourcedId = $csv_schoolSourcedId AND userSourcedId = $csv_userSourcedId"
		fi

	# レコード件数が0件の場合はINSERT
	else
		QUERY="INSERT INTO enrollments_import VALUES($csv_sourcedId, $csv_status, $csv_dateLastModified, $csv_classSourcedId, $csv_schoolSourcedId, $csv_userSourcedId, $csv_role, $csv_csv_primary, $csv_beginDate, $csv_endDate, $csv_metadata_jp_ShussekiNo, $csv_metadata_jp_PublicFlg, now(), now())"
	fi
	if [ -n "$QUERY" ]; then
		`echo $QUERY | $CMD_MYSQL`
		if [ $? -ne 0 ]; then
			echo "$0:enrollments.csvのインポートに失敗しました。classSourcedId=$csv_classSourcedId,schoolSourcedId=$csv_schoolSourcedId,userSourcedId=$csv_userSourcedId"
			exit 1
		fi
	fi
	NUMBER=$((++i))
done < "$CSV_FILE"

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
