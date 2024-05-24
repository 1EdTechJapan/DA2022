#!/bin/bash
# **************************************************
# CSVファイルエクスポート用テーブルへの登録
# 引数
#    LAST_EXPORTED_AT:前回CSVファイルエクスポート日時
#    DB              :OneRosterデータベース名
#    CLASS_TYPE      :クラス区分（1:年組を除く/2:年組を含む）
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
LAST_EXPORTED_AT=$1
DB=$2
CLASS_TYPE=$3
CMD_MYSQL="$DB"
DEF_TITLE="無所属"
DEF_SCHOOL_YEAR="99"
DEF_CLASS="未登録"
EXT_YEAR="年"
EXT_CLASS="組"
EXPIRE_DATE=\"2100-03-31\"
TRIAL=\"COMP\"

# csvファイルインポート先のテーブルから前回CSVファイルエクスポート日時以降のレコードを取得
if [ -n "$LAST_EXPORTED_AT" ]; then
	LAST_EXPORTED_AT=\"$LAST_EXPORTED_AT\"
	QUERY="SELECT ei.sourcedId AS sourcedId, oi.orgs_managementid AS school_code, ei.userSourcedId AS userSourcedId, ui.username AS account_id, ei.role AS role_name, ei.classSourcedId AS classSourcedId, ci.title AS title, ui.givenName AS given_name, ui.familyName AS family_name, ei.metadata_jp_ShussekiNo AS ShussekiNo, ei.status AS status FROM enrollments_import AS ei INNER JOIN orgs_import AS oi ON ei.schoolSourcedId = oi.sourcedId INNER JOIN classes_import AS ci ON ei.classSourcedId = ci.sourcedId INNER JOIN users_import AS ui ON ei.userSourcedId = ui.sourcedId WHERE ei.updated_at > $LAST_EXPORTED_AT AND oi.orgs_managementid IS NOT NULL"
else
	QUERY="SELECT ei.sourcedId AS sourcedId, oi.orgs_managementid AS school_code, ei.userSourcedId AS userSourcedId, ui.username AS account_id, ei.role AS role_name, ei.classSourcedId AS classSourcedId, ci.title AS title, ui.givenName AS given_name, ui.familyName AS family_name, ei.metadata_jp_ShussekiNo AS ShussekiNo, ei.status AS status FROM enrollments_import AS ei INNER JOIN orgs_import AS oi ON ei.schoolSourcedId = oi.sourcedId INNER JOIN classes_import AS ci ON ei.classSourcedId = ci.sourcedId INNER JOIN users_import AS ui ON ei.userSourcedId = ui.sourcedId WHERE oi.orgs_managementid IS NOT NULL"
fi
VALUES=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:ユーザー情報の取得に失敗しました。"
    exit 1
fi

# 取得したレコード×項目数分実施
echo "$VALUES" | while read data
do
	if [[ $data != sourcedId* ]] && [[ $data != school_code* ]] &&  [[ $data != userSourcedId* ]] && [[ $data != account_id* ]] && [[ $data != role_name* ]] && [[ $data != classSourcedId* ]] && [[ $data != title* ]] && [[ $data != given_name* ]] && [[ $data != family_name* ]] && [[ $data != ShussekiNo* ]] && [[ $data != status* ]]; then
		continue
	fi
	eval $data

	# sourcedIdの設定（取得した項目がsourcedIdの場合）
	if [[ $data == sourcedId* ]]; then
		ex_sourcedId=\"$sourcedId\"
	fi

	# 学校コードの設定（取得した項目がschool_codeの場合）
	if [[ $data == school_code* ]]; then
		ex_school_code=\"$school_code\"
	fi

	# userSourcedIdの設定（取得した項目がuserSourcedIdの場合）
	if [[ $data == userSourcedId* ]]; then
		ex_userSourcedId=\"$userSourcedId\"
	fi

	# account_idの設定（取得した項目がaccount_idの場合）
	if [[ $data == account_id* ]]; then
		ex_account_id=\"$account_id\"
	fi

	# roleの設定（取得した項目がrole_nameの場合）
	if [[ $data == role_name* ]]; then
		# 生徒の場合
		if [ $role_name = "student" ]; then
			ex_role="1"
		# 生徒以外の場合
		else
			ex_role="2"
		fi
	fi

	# classSourcedIdの設定（取得した項目がclassSourcedIdの場合）
	if [[ $data == classSourcedId* ]]; then
		ex_classSourcedId=\"$classSourcedId\"
	fi

	# titleとschool_yearとclassの設定（取得した項目がtitleの場合）
	if [[ $data == title* ]]; then
		ex_title=\"$title\"
		ex_school_year=""
		ex_class=""
		# 生徒の場合
		if [ $ex_role = "1" ]; then
			# titleが無所属または空の場合
			if [ "$title" = $DEF_TITLE ] || [ "$title" = "" ]; then
				ex_school_year=$DEF_SCHOOL_YEAR
				ex_class=$DEF_CLASS
			else
				# 学年の設定（①年以前の文字列を取得、②全角数字を半角数字に変換、③数字以外を除外、③左0埋めを除外）
				ex_school_year=`echo $title | sed 's/年.*//' | sed 'y/０１２３４５６７８９/0123456789/' | sed -e 's/[^0-9]//g' | sed -e 's/0*\([0-9]*[0-9]$\)/\1/g'`
				# 学年が空ではない場合
				if [ "$ex_school_year" != "" ]; then
					# クラスの設定（①年以降の文字列を取得、②組以前の文字列を取得）
					ex_class=`echo $title | sed 's/.*年//' | sed 's/組.*//'`
				fi
			fi
			# 学年が空の場合
			if [ "$ex_school_year" = "" ]; then
				# 学年に99を設定
				ex_school_year=$DEF_SCHOOL_YEAR
				# クラスにtitleを設定
				ex_class=$title
			fi
			# 年と組を含める場合
			if [ $CLASS_TYPE = 2 ]; then
				ex_school_year=$ex_school_year$EXT_YEAR
				# クラスが空ではない、かつ、title以外の場合
				if [ "$ex_class" != "" ] && [ "$ex_class" != "$title" ]; then
					ex_class=$ex_class$EXT_CLASS
				fi
			fi
		fi
		ex_school_year=\"$ex_school_year\"
		ex_class=\"$ex_class\"
	fi

	# ニックネームの設定（取得した項目がfamily_nameの場合）
	if [[ $data == family_name* ]]; then
		# 姓が-の場合はニックネームに含めない
		if [ "$family_name" = "-" ]; then
			family_name=""
		fi
		# 名が-の場合はニックネームに含めない
		if [ "$given_name" = "-" ]; then
			given_name=""
		fi
		ex_nickname=\"$family_name$given_name\"
	fi

	# 出席番号の設定（取得した項目がShussekiNoの場合）
	if [[ $data == ShussekiNo* ]]; then
		ex_ShussekiNo=\"$ShussekiNo\"
		# 出席番号が空ではない場合
		if [ "$ShussekiNo" != "" ]; then
			# 出席番号の設定（①全角数字を半角数字に変換、②数字以外を除外、③左0埋めを除外）
			ex_student_number=`echo $ShussekiNo | sed 'y/０１２３４５６７８９/0123456789/' | sed -e 's/[^0-9]//g' | sed -e 's/0*\([0-9]*[0-9]$\)/\1/g'`
		# 出席番号が空の場合
		else
			ex_student_number=""
		fi
		ex_student_number=\"$ex_student_number\"
	fi

	# statusの設定（取得した項目がstatusの場合）
	if [[ $data == status* ]]; then
		ex_status=\"$status\"
	fi

	# 取得した項目がstatus以外の場合はスキップ
	if [[ $data != status* ]]; then
		continue
	fi

	# users_exportテーブルからsourcedIdが一致するレコードを取得
	QUERY="SELECT school_code, account_id, title, ShussekiNo, role, nickname FROM users_export WHERE sourcedId = $ex_sourcedId"
	VALUE=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
	if [ $? -ne 0 ]; then
		echo "$0:CSVファイルエクスポート用のユーザー情報の取得に失敗しました。sourcedId=$ex_sourcedId"
		exit 1
	fi

	# レコード件数が0件ではない場合はUPDATE
	if [ -n "$VALUE" ]; then
		eval $VALUE
		school_code=\"$school_code\"
		account_id=\"$account_id\"
		title=\"$title\"
		ShussekiNo=\"$ShussekiNo\"
		role=\"$role\"
		ex_role=\"$ex_role\"
		nickname=\"$nickname\"
		
		# 更新先のレコードと値がすべて一致する場合
		if [[ $school_code = $ex_school_code ]] && [[ $account_id = $ex_account_id ]] && [[ $title = $ex_title ]] && [[ $ShussekiNo = $ex_ShussekiNo ]] && [[ $role = $ex_role ]] && [[ $nickname = $ex_nickname ]]; then
			QUERY=""

		# 更新先のレコードと値が一つでも一致しない場合
		else
			QUERY="UPDATE users_export SET school_code = $ex_school_code, userSourcedId = $ex_userSourcedId, account_id = $ex_account_id, classSourcedId = $ex_classSourcedId, title = $ex_title, school_year = $ex_school_year, class = $ex_class, ShussekiNo = $ex_ShussekiNo, student_number = $ex_student_number, role = $ex_role, nickname = $ex_nickname, status = $ex_status, updated_at = now() WHERE sourcedId = $ex_sourcedId"
		fi

	# レコード件数が0件の場合はINSERT
	else
		# passwordの設定（ランダムの6桁の数字）
		password=`echo $((RANDOM%100000+899999))`
		password=\"$password\"
		QUERY="INSERT INTO users_export VALUES($ex_sourcedId, $ex_school_code, $ex_userSourcedId, $ex_account_id, $password, $ex_classSourcedId, $ex_title, $ex_school_year, $ex_class, $ex_ShussekiNo, $ex_student_number, $EXPIRE_DATE, $ex_role, $TRIAL, $ex_nickname, $ex_status, now(), now())"
	fi
	if [ -n "$QUERY" ]; then
		`echo $QUERY | $CMD_MYSQL`
		if [ $? -ne 0 ]; then
			echo "$0:CSVファイルエクスポート用のユーザー情報の登録に失敗しました。sourcedId=$ex_sourcedId"
			exit 1
		fi
	fi
done

if [ $? -eq 1 ]; then
	exit 1
fi

exit 0
