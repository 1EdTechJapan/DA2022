#!/bin/bash
# **************************************************
# 20.roop_classes.sh
# クラス毎の処理
# 引数
#    registered_at        :前回DB登録日時
#    DB_ONEROSTER         :OneRosterデータベース名
#    DB_AZURE             :Azureデータベース名
# 返却値
#    なし
# 
# クラス毎の処理を制御する
# ・クラス情報一覧の取得
# ・学校ID取得呼び出し
# ・クラスID取得呼び出し
# ・クラス情報登録・更新呼び出し
# ・ユーザー毎の処理呼び出し
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
registered_at=$1
DB_ONEROSTER=$2
DB_AZURE=$3
CMD_MYSQL="$DB_ONEROSTER"
STATUS_DELETED=\"tobedeleted\"
ROLE_STUDENT=\"1\"

# クラス情報一覧の取得
if [ -n "$registered_at" ]; then
	registered_at_chara=\"$registered_at\"
	QUERY="SELECT ue.classSourcedId AS classSourcedId, ue.school_year AS school_year, ue.class AS class, ue.school_code AS school_code FROM users_export AS ue WHERE NOT EXISTS ( SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.role = $ROLE_STUDENT AND ue.updated_at > $registered_at_chara AND ue.status <> $STATUS_DELETED GROUP BY ue.school_code, ue.classSourcedId ORDER BY ue.school_code ASC, ue.classSourcedId ASC"
else
	QUERY="SELECT ue.classSourcedId AS classSourcedId, ue.school_year AS school_year, ue.class AS class, ue.school_code AS school_code FROM users_export AS ue WHERE NOT EXISTS ( SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.role = $ROLE_STUDENT AND ue.status <> $STATUS_DELETED GROUP BY ue.school_code, ue.classSourcedId ORDER BY ue.school_code ASC, ue.classSourcedId ASC"
fi
VALUES=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:クラス情報一覧の取得に失敗しました。"
    exit 1
fi
echo "$0:クラス情報一覧の取得に成功しました。"

# 取得したレコード×項目数分実施
echo "$VALUES" | while read data
do
	if [[ $data != school_code* ]] && [[ $data != classSourcedId* ]] && [[ $data != school_year* ]] && [[ $data != class* ]]; then
		continue
	fi
	eval $data

	# 取得した項目がschool_code以外の場合はスキップ
	if [[ $data != school_code* ]]; then
		continue
	fi

	# 21.学校ID取得（$school_code、DB_AZUREより）
	SCHOOL_ID=`./get_school_id.sh $school_code "$DB_AZURE"`
	if [ $? -ne 0 ] || [ ! -n "$SCHOOL_ID" ]; then
		echo "$0:学校IDの取得に失敗しました。school_code=$school_code"
		exit 1
	fi
	echo "$0:学校IDの取得に成功しました。SCHOOL_ID=$SCHOOL_ID,school_code=$school_code"

	# 22.クラスID取得(1.21で取得したid,'=1）で取得したclassSourcedId)
	CLASS_ID=`./get_class_id.sh $SCHOOL_ID $classSourcedId "$DB_AZURE"`
	if [ $? -ne 0 ]; then
		echo "$0:クラスIDの取得に失敗しました。SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId"
		exit 1
	fi

	# クラスIDが存在しなかった場合
	if [ ! -n "$CLASS_ID" ]; then

		# 23.クラス情報登録→AIAIモンキーAzureclassesテーブル
		./register_classes.sh $SCHOOL_ID $classSourcedId "$school_year" "$class" "$DB_AZURE"
		if [ $? -ne 0 ]; then
			echo "$0:クラス情報の登録に失敗しました。SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId,school_year=$school_year,class=$class"
			exit 1
		fi
		echo "$0:クラス情報の登録に成功しました。SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId,school_year=$school_year,class=$class"

		# 22.クラスID取得 23で登録したAIAIモンキーテーブルから取得
		CLASS_ID=`./get_class_id.sh $SCHOOL_ID $classSourcedId "$DB_AZURE"`
		if [ $? -ne 0 ] || [ ! -n "$CLASS_ID" ]; then
			echo "$0:クラスIDの取得に失敗しました。SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId"
			exit 1
		fi
		echo "$0:クラスIDの取得に成功しました。CLASS_ID=$CLASS_ID,SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId"
	else
		# クラスIDは存在する場合
		echo "$0:クラスIDの取得に成功しました。CLASS_ID=$CLASS_ID,SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId"
		# 24.クラス情報更新→AIAIモンキーAzureclassesテーブル
		./update_classes.sh $CLASS_ID "$school_year" "$class" "$DB_AZURE"
		if [ $? -ne 0 ]; then
			echo "$0:クラス情報の更新に失敗しました。CLASS_ID=$CLASS_ID,school_year=$school_year,class=$class"
			exit 1
		fi
		echo "$0:クラス情報の更新に成功しました。CLASS_ID=$CLASS_ID,school_year=$school_year,class=$class"
	fi
done

if [ $? -eq 1 ]; then
	exit 1
fi

# クラス情報一覧の取得
if [ -n "$registered_at" ]; then
	registered_at_chara=\"$registered_at\"
	QUERY="SELECT ue.school_code AS school_code, ue.classSourcedId AS classSourcedId FROM users_export AS ue WHERE NOT EXISTS ( SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.updated_at > $registered_at_chara AND ue.status <> $STATUS_DELETED GROUP BY ue.school_code, ue.classSourcedId ORDER BY ue.school_code ASC, ue.classSourcedId ASC"
else
	QUERY="SELECT ue.school_code AS school_code, ue.classSourcedId AS classSourcedId FROM users_export AS ue WHERE NOT EXISTS ( SELECT * FROM not_export_schools AS nes WHERE ue.school_code = nes.school_code) AND ue.status <> $STATUS_DELETED GROUP BY ue.school_code, ue.classSourcedId ORDER BY ue.school_code ASC, ue.classSourcedId ASC"
fi
VALUES=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:クラス情報一覧の取得に失敗しました。"
    exit 1
fi
echo "$0:クラス情報一覧の取得に成功しました。"

# 取得したレコード×項目数分実施
echo "$VALUES" | while read data
do
	if [[ $data != school_code* ]] && [[ $data != classSourcedId* ]]; then
		continue
	fi
	eval $data

	# 取得した項目がclassSourcedId以外の場合はスキップ
	if [[ $data != classSourcedId* ]]; then
		continue
	fi

	# 21.学校ID取得（$school_code、DB_AZUREより）
	SCHOOL_ID=`./get_school_id.sh $school_code "$DB_AZURE"`
	if [ $? -ne 0 ] || [ ! -n "$SCHOOL_ID" ]; then
		echo "$0:学校IDの取得に失敗しました。school_code=$school_code"
	    exit 1
	fi
	echo "$0:学校IDの取得に成功しました。SCHOOL_ID=$SCHOOL_ID,school_code=$school_code"

	# 22.クラスID取得(1.21で取得したid,'=1）で取得したclassSourcedId)
	CLASS_ID=`./get_class_id.sh $SCHOOL_ID $classSourcedId "$DB_AZURE"`
	if [ $? -ne 0 ]; then
		echo "$0:クラスIDの取得に失敗しました。SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId"
	    exit 1
	fi
	if [ -n "$SCHOOL_ID" ]; then
		echo "$0:クラスIDの取得に成功しました。CLASS_ID=$CLASS_ID,SCHOOL_ID=$SCHOOL_ID,classSourcedId=$classSourcedId"
	else
		CLASS_ID=0
	fi

	# 25.ユーザー毎の処理
	./roop_users.sh $school_code $classSourcedId $SCHOOL_ID $CLASS_ID "$registered_at" "$DB_ONEROSTER" "$DB_AZURE"
	if [ $? -ne 0 ]; then
		echo "$0:ユーザー毎の処理に失敗しました。school_code=$school_code,classSourcedId=$classSourcedId,SCHOOL_ID=$SCHOOL_ID,CLASS_ID=$CLASS_ID"
	    exit 1
	fi
	echo "$0:ユーザー毎の処理に成功しました。school_code=$school_code,classSourcedId=$classSourcedId,SCHOOL_ID=$SCHOOL_ID,CLASS_ID=$CLASS_ID"
done

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
