#!/bin/bash
# **************************************************
# 25.roop_users.sh
# ユーザー毎の処理
# 引数
#    school_code        :学校コード
#    classSourcedId     :classSourcedId
#    school_id          :学校ID
#    class_id           :クラスID
#    registered_at      :前回DB登録日時
#    DB_ONEROSTER       :OneRosterデータベース名
#    DB_AZURE           :Azureデータベース名
# 返却値
#    なし
# 
# ユーザー毎の処理を制御する
# ・ユーザー情報一覧の取得
# ・ユーザーID取得呼び出し
# ・ユーザー情報登録・更新呼び出し
# ・ユーザー・クラス情報の存在確認呼び出し
# ・ユーザー・クラス情報登録呼び出し
# **************************************************
# 引数のチェック
if [ $# -ne 7 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
school_code=\"$1\"
classSourcedId=\"$2\"
school_id=$3
class_id=$4
registered_at=$5
DB_ONEROSTER=$6
DB_AZURE=$7
CMD_MYSQL="$DB_ONEROSTER"
STATUS_DELETED=\"tobedeleted\"

# OneRosterDB users_exportから対象ユーザー数分取得
if [ -n "$registered_at" ]; then
	registered_at_chara=\"$registered_at\"
	QUERY="SELECT userSourcedId, account_id, password, student_number, role, nickname FROM users_export WHERE school_code = $school_code AND classSourcedId = $classSourcedId AND updated_at > $registered_at_chara AND status <> $STATUS_DELETED GROUP BY userSourcedId ORDER BY userSourcedId ASC"
else
	QUERY="SELECT userSourcedId, account_id, password, student_number, role, nickname FROM users_export WHERE school_code = $school_code AND classSourcedId = $classSourcedId AND status <> $STATUS_DELETED GROUP BY userSourcedId ORDER BY userSourcedId ASC"
fi
VALUES=`$CMD_MYSQL -e "$QUERY" -E | sed -e "1d" | sed -e 's/: /="/g' | sed -e 's/$/"/'`
if [ $? -ne 0 ]; then
	echo "$0:ユーザー情報一覧の取得に失敗しました。"
	exit 1
fi
echo "$0:ユーザー情報一覧の取得に成功しました。"

# 対象ユーザー数×項目数分繰り返し
echo "$VALUES" | while read data
do
	if [[ $data != userSourcedId* ]] && [[ $data != account_id* ]] && [[ $data != password* ]] && [[ $data != student_number* ]] && [[ $data != role* ]] && [[ $data != nickname* ]]; then
		continue
	fi
	eval $data

	# 取得した項目がnickname以外の場合はスキップ
	if [[ $data != nickname* ]]; then
		continue
	fi

	# Azure usersテーブルからユーザーID取得26get_user_id.sh
	user_id=`./get_user_id.sh $userSourcedId "$DB_AZURE"`
	if [ $? -ne 0 ]; then
		echo "$0:ユーザーIDの取得に失敗しました。userSourcedId=$userSourcedId"
	    exit 1
	fi

	# ユーザーID存在しない場合
	if [ ! -n "$user_id" ]; then
		# 27.ユーザー情報登録
		./register_users.sh $school_id $userSourcedId $account_id $password $role "$nickname" "$DB_AZURE"
		if [ $? -ne 0 ]; then
			echo "$0:ユーザー情報の登録に失敗しました。school_id=$school_id,userSourcedId=$userSourcedId,account_id=$account_id,password=$password,role=$role,nickname=$nickname"
		    exit 1
		fi
		echo "$0:ユーザー情報の登録に成功しました。school_id=$school_id,userSourcedId=$userSourcedId,account_id=$account_id,password=$password,role=$role,nickname=$nickname"

		# 取得したroleが1の場合のみ以下を実施
		if [ $role = "1" ]; then
			# 26.ユーザーID取得
			user_id=`./get_user_id.sh $userSourcedId "$DB_AZURE"`
			if [ $? -ne 0 ] || [ ! -n "$user_id" ]; then
				echo "$0:ユーザーIDの取得に失敗しました。userSourcedId=$userSourcedId"
			    exit 1
			fi
			echo "$0:ユーザーIDの取得に成功しました。user_id=$user_id,userSourcedId=$userSourcedId"
		fi
	else
		echo "$0:ユーザーID取得に成功しました。user_id=$user_id,userSourcedId=$userSourcedId"
		# 28.ユーザー情報更新
		./update_users.sh $user_id $school_id $account_id $role "$nickname" "$DB_AZURE"
		if [ $? -ne 0 ]; then
			echo "$0:ユーザー情報の更新に失敗しました。user_id=$user_id,school_id=$school_id,account_id=$account_id,role=$role,nickname=$nickname"
		    exit 1
		fi
		echo "$0:ユーザー情報の更新に成功しました。user_id=$user_id,school_id=$school_id,account_id=$account_id,role=$role,nickname=$nickname"
	fi

	# 取得したroleが1の場合のみ以下を実施
	if [ $role = "1" ]; then

		# 29.ユーザー・クラス情報存在確認
		COUNT=`./check_exist_user_owned_classes.sh $class_id $user_id "$DB_AZURE"`
		if [ $? -ne 0 ]; then
			echo "$0:ユーザー・クラス情報の存在確認に失敗しました。class_id=$class_id,user_id=$user_id"
		    exit 1
		fi
		echo "$0:ユーザー・クラス情報の存在確認に成功しました。class_id=$class_id,user_id=$user_id"

		# student_numberが空の場合は、0を入れる
		if [ -z $student_number ]; then
			student_number="0"
		fi

		# ユーザー・クラス情報存在しない場合
		if [ $COUNT = "0" ]; then
			# 30.ユーザー・クラス情報登録
			./register_user_owned_classes.sh $class_id $user_id $student_number "$DB_AZURE"
			if [ $? -ne 0 ]; then
				echo "$0:ユーザー・クラス情報の登録に失敗しました。class_id=$class_id,user_id=$user_id,student_number=$student_number"
			    exit 1
			fi
			echo "$0:ユーザー・クラス情報の登録に成功しました。class_id=$class_id,user_id=$user_id,student_number=$student_number"
		
		# ユーザー・クラス情報存在する場合
		else
			# 31.ユーザー・クラス情報更新
			./update_user_owned_classes.sh $class_id $user_id $student_number "$DB_AZURE"
			if [ $? -ne 0 ]; then
				echo "$0:ユーザー・クラス情報の更新に失敗しました。class_id=$class_id,user_id=$user_id,student_number=$student_number"
			    exit 1
			fi
			echo "$0:ユーザー・クラス情報の更新に成功しました。class_id=$class_id,user_id=$user_id,student_number=$student_number"
		fi
	fi
done

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
