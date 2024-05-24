#!/bin/bash
# **************************************************
# マニフェストファイルの確認
# 引数
#    CSV_DIR :CSVファイル保存先ディレクトリ
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
CSV_DIR=$1
exist_academicSessions=0
exist_classes=0
exist_courses=0
exist_enrollments=0
exist_orgs=0
exist_roles=0
exist_users=0
exist_demographics=0
exist_userProfiles=0
manifest_version=0
oneroster_version=0
file_academicSessions=0
file_classes=0
file_courses=0
file_enrollments=0
file_orgs=0
file_roles=0
file_users=0
file_demographics=0
file_userProfiles=0

# academicSessionsファイルの存在確認
if [ -f $CSV_DIR/academicSessions.csv ]; then
	exist_academicSessions=1
fi

# classesファイルの存在確認
if [ -f $CSV_DIR/classes.csv ]; then
	exist_classes=1
fi

# coursesファイルの存在確認
if [ -f $CSV_DIR/courses.csv ]; then
	exist_courses=1
fi

# enrollmentsファイルの存在確認
if [ -f $CSV_DIR/enrollments.csv ]; then
	exist_enrollments=1
fi

# orgsファイルの存在確認	
if [ -f $CSV_DIR/orgs.csv ]; then
	exist_orgs=1
fi

# rolesファイルの存在確認
if [ -f $CSV_DIR/roles.csv ]; then
	exist_roles=1
fi

# usersファイルの存在確認
if [ -f $CSV_DIR/users.csv ]; then
	exist_users=1
fi

# demographicsファイルの存在確認
if [ -f $CSV_DIR/demographics.csv ]; then
	exist_demographics=1
fi

# userProfilesファイルの存在確認
if [ -f $CSV_DIR/userProfiles.csv ]; then
	exist_userProfiles=1
fi

# manifestファイルの存在確認
if [ ! -f $CSV_DIR/manifest.csv ]; then
	echo "$0:manifest.csvファイルが存在しません。CSV_DIR=$CSV_DIR"
	exit 1
fi

# ファイルの文字コード確認
if [[ $(file -i $CSV_DIR/manifest.csv | grep -q "utf-8"; echo -n ${?} ) -ne 0 ]] && [[ $(file -i $CSV_DIR/manifest.csv | grep -q "us-ascii"; echo -n ${?} ) -ne 0 ]]; then
	echo "$0:manifest.csvの文字コードが不正です。"
	exit 1
fi

# manifestファイルの内容確認
i=0
while read row
do
	# 1行目の場合
	if [ $i -eq 0 ]; then
		# csvファイルのヘッダー値取得
		csv_propertyName=`echo ${row} | cut -d , -f 1`
		# propertyNameのヘッダーが不正
		if [[ $csv_propertyName != "propertyName" ]]; then
			echo "$0:propertyNameのヘッダーが不正です。[$csv_propertyName]"
			exit 1
		fi
		csv_value=`echo ${row} | cut -d , -f 2`
		# 最後のカラムは改行コードを除外
		csv_value=`echo $csv_value | sed -e "s/[\r\n]\+//g"`
		# valueのヘッダーが不正
		if [[ $csv_value != "value" ]]; then
			echo "$0:valueのヘッダーが不正です。[$csv_value]"
			exit 1
		fi

		NUMBER=$((++i))
		continue
	fi

	# csvファイルのカラム値取得
	csv_propertyName=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $1}' | sed 's/"//g'`
	# propertyNameに値が入っていない
	if [ ! -n "$csv_propertyName" ]; then
		echo "$0:propertyNameに値が入っていません。$NUMBER行目"
		exit 1
	fi
	csv_value=`echo ${row} | gawk -v FPAT='([^,]+)|(\"[^\"]+\")' '{print $2}' | sed 's/"//g'`
	# 最後のカラムは改行コードを除外
	csv_value=`echo $csv_value | sed -e "s/[\r\n]\+//g"`
	# valueに値が入っていない
	if [ ! -n "$csv_value" ]; then
		echo "$0:valueに値が入っていません。$NUMBER行目"
		exit 1
	fi

	# manifest.versionの確認
	if [[ $csv_propertyName = "manifest.version" ]]; then
		if [[ $csv_value = "1.0" ]]; then
			manifest_version=1
		else
			echo "$0:manifest.versionが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# oneroster.versionの確認
	elif [[ $csv_propertyName = "oneroster.version" ]]; then
		if [[ $csv_value = "1.2" ]]; then
			oneroster_version=1
		else
			echo "$0:oneroster.versionが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.academicSessionsの確認
	elif [[ $csv_propertyName = "file.academicSessions" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_academicSessions = 1 ]]; then
				file_academicSessions=1
			else
				echo "$0:file.academicSessionsが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_academicSessions = 0 ]]; then
				file_academicSessions=1
			else
				echo "$0:file.academicSessionsが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.academicSessionsが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.classesの確認
	elif [[ $csv_propertyName = "file.classes" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_classes = 1 ]]; then
				file_classes=1
			else
				echo "$0:file.classesが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_classes = 0 ]]; then
				file_classes=1
			else
				echo "$0:file.classesが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.classesが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.coursesの確認
	elif [[ $csv_propertyName = "file.courses" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_courses = 1 ]]; then
				file_courses=1
			else
				echo "$0:file.coursesが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_courses = 0 ]]; then
				file_courses=1
			else
				echo "$0:file.coursesが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.coursesが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.demographicsの確認
	elif [[ $csv_propertyName = "file.demographics" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_demographics = 1 ]]; then
				file_demographics=1
			else
				echo "$0:file.demographicsが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_demographics = 0 ]]; then
				file_demographics=1
			else
				echo "$0:file.demographicsが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.demographicsが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.enrollmentsの確認
	elif [[ $csv_propertyName = "file.enrollments" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_enrollments = 1 ]]; then
				file_enrollments=1
			else
				echo "$0:file.enrollmentsが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_enrollments = 0 ]]; then
				file_enrollments=1
			else
				echo "$0:file.enrollmentsが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.enrollmentsが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.orgsの確認
	elif [[ $csv_propertyName = "file.orgs" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_orgs = 1 ]]; then
				file_orgs=1
			else
				echo "$0:file.orgsが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_orgs = 0 ]]; then
				file_orgs=1
			else
				echo "$0:file.orgsが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.orgsが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.rolesの確認
	elif [[ $csv_propertyName = "file.roles" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_roles = 1 ]]; then
				file_roles=1
			else
				echo "$0:file.rolesが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_roles = 0 ]]; then
				file_roles=1
			else
				echo "$0:file.rolesが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.rolesが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.userProfilesの確認
	elif [[ $csv_propertyName = "file.userProfiles" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_userProfiles = 1 ]]; then
				file_userProfiles=1
			else
				echo "$0:file.userProfilesが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_userProfiles = 0 ]]; then
				file_userProfiles=1
			else
				echo "$0:file.userProfilesが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.userProfilesが指定値以外の値です。[$csv_value]"
			exit 1
		fi

	# file.usersの確認
	elif [[ $csv_propertyName = "file.users" ]]; then
		if [[ $csv_value = "bulk" ]] || [[ $csv_value = "delta" ]]; then
			if [[ $exist_users = 1 ]]; then
				file_users=1
			else
				echo "$0:file.usersが不正です。[$csv_valueでファイルが存在しない]"
				exit 1
			fi
		elif [[ $csv_value = "absent" ]]; then
			if [[ $exist_users = 0 ]]; then
				file_users=1
			else
				echo "$0:file.usersが不正です。[$csv_valueでファイルが存在する]"
				exit 1
			fi
		else
			echo "$0:file.usersが指定値以外の値です。[$csv_value]"
			exit 1
		fi
	fi

	NUMBER=$((++i))
done < "$CSV_DIR/manifest.csv"

if [ $? -eq 1 ]; then
	exit 1
fi

if [[ $manifest_version = 0 ]]; then
	echo "$0:manifest.versionが存在しません。"
	exit 1
fi

if [[ $oneroster_version = 0 ]]; then
	echo "$0:oneroster.versionが存在しません。"
	exit 1
fi

if [[ $file_academicSessions = 0 ]]; then
	echo "$0:file.academicSessionsが存在しません。"
	exit 1
fi

if [[ $file_classes = 0 ]]; then
	echo "$0:file.classesが存在しません。"
	exit 1
fi

if [[ $file_courses = 0 ]]; then
	echo "$0:file.coursesが存在しません。"
	exit 1
fi

if [[ $file_enrollments = 0 ]]; then
	echo "$0:file.enrollmentsが存在しません。"
	exit 1
fi

if [[ $file_orgs = 0 ]]; then
	echo "$0:file.orgsが存在しません。"
	exit 1
fi

if [[ $file_roles = 0 ]]; then
	echo "$0:file.rolesが存在しません。"
	exit 1
fi

if [[ $file_users = 0 ]]; then
	echo "$0:file.usersが存在しません。"
	exit 1
fi

if [[ $file_demographics = 0 ]]; then
	echo "$0:file.demographicsが存在しません。"
	exit 1
fi

if [[ $file_userProfiles = 0 ]]; then
	echo "$0:file.userProfilesが存在しません。"
	exit 1
fi

exit 0
