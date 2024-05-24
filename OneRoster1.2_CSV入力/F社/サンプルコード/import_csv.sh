#!/bin/bash
# **************************************************
# CSVファイルインポーﾄ
# 引数
#    CSV_DIR :CSVファイル保存先ディレクトリ
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
CSV_DIR=$1
DB=$2
DIR_NAME=$3

# マニフェストファイルの確認
./check_manifest.sh "$CSV_DIR"
if [ $? -ne 0 ]; then
	echo "$0:manifest.csvの確認に失敗しました。CSV_DIR=$CSV_DIR"
	exit 1
fi
echo "$0:manifest.csvの確認に成功しました。CSV_DIR=$CSV_DIR"

# 学校ファイルのインポート
if [ -f $CSV_DIR/orgs.csv ]; then
	./import_csv_orgs.sh "$CSV_DIR/orgs.csv" "$DB" "$DIR_NAME"
	if [ $? -ne 0 ]; then
		echo "$0:orgs.csvのインポートに失敗しました。CSV_DIR=$CSV_DIR"
		exit 1
	fi
	echo "$0:orgs.csvのインポートに成功しました。CSV_DIR=$CSV_DIR"
fi

# 学校クラスファイルのインポート
if [ -f $CSV_DIR/classes.csv ]; then
	./import_csv_classes.sh "$CSV_DIR/classes.csv" "$DB"
	if [ $? -ne 0 ]; then
		echo "$0:classes.csvのインポートに失敗しました。CSV_DIR=$CSV_DIR"
		exit 1
	fi
	echo "$0:classes.csvのインポートに成功しました。CSV_DIR=$CSV_DIR"
fi

# ユーザーファイルのインポート
if [ -f $CSV_DIR/users.csv ]; then
	./import_csv_users.sh "$CSV_DIR/users.csv" "$DB"
	if [ $? -ne 0 ]; then
		echo "$0:users.csvのインポートに失敗しました。CSV_DIR=$CSV_DIR"
		exit 1
	fi
	echo "$0:users.csvのインポートに成功しました。CSV_DIR=$CSV_DIR"
fi

# enrollmentsファイルのインポート
if [ -f $CSV_DIR/enrollments.csv ]; then
	./import_csv_enrollments.sh "$CSV_DIR/enrollments.csv" "$DB"
	if [ $? -ne 0 ]; then
		echo "$0:enrollments.csvのインポートに失敗しました。CSV_DIR=$CSV_DIR"
		exit 1
	fi
	echo "$0:enrollments.csvのインポートに成功しました。CSV_DIR=$CSV_DIR"
fi

exit 0
