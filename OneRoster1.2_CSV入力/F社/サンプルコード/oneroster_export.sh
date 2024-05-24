#!/bin/bash
# **************************************************
# 学校コード取得、学校コード登録、CSVファイルエクスポート制御
# 引数
#    OUTPUT_DIR:出力先ディレクトリ
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "指定された引数は$#個です。" 1>&2
	exit 1
fi
OUTPUT_DIR=$1
DB_ONEROSTER="mysql --defaults-extra-file=conf/oneroster_db.conf -t --show-warnings oneroster_digital"
DB_AZURE="mysql --defaults-extra-file=conf/aiai_monkey_db.conf -t --show-warnings dev.aiaimonkey"
CLASS_TYPE=2

# ログファイル
LOG_FILE=$OUTPUT_DIR/oneroster.log

# 学校コードnullファイル（学校コードがnullの学校を格納）
SCHOOL_CODE_NULL_FILE=$OUTPUT_DIR/school_code_null.txt

# ユーザー情報エクスポート用csvファイル
EXPORT_USERS_FILE=$OUTPUT_DIR/users.csv

# 削除ユーザー情報エクスポート用csvファイル
EXPORT_USERS_DELETED_FILE=$OUTPUT_DIR/users_deleted.csv

# ログファイル出力開始
exec &> >(awk '{print strftime("[%Y/%m/%d %H:%M:%S] "),$0 } { fflush() } ' >> $LOG_FILE)

# 前回CSVファイルエクスポート日時の取得
LAST_EXPORTED_AT=`./get_last_exported_at.sh "$DB_ONEROSTER"`
if [ $? -ne 0 ]; then
	echo "$0:前回CSVファイルエクスポート日時の取得に失敗しました。"
    exit 1
fi
echo "$0:前回CSVファイルエクスポート日時の取得に成功しました。exported_at=$LAST_EXPORTED_AT"

# 学校毎の処理（学校コード取得、学校コード登録）
./roop_schools.sh "$LAST_EXPORTED_AT" "$DB_ONEROSTER" "$DB_AZURE" $SCHOOL_CODE_NULL_FILE
if [ $? -ne 0 ]; then
	echo "$0:学校毎の処理に失敗しました。"
	exit 1
fi
echo "$0:学校毎の処理に成功しました。"

# 学校コードnullファイルが存在する場合
if [ -f $SCHOOL_CODE_NULL_FILE ]; then
	echo "$0:学校コードがnullのレコードが存在します。"
	exit 1
fi
echo "$0:学校コードがnullのレコードは存在しません。"

# CSVファイルエクスポート用のユーザー情報の登録
./register_users_export.sh "$LAST_EXPORTED_AT" "$DB_ONEROSTER" $CLASS_TYPE
if [ $? -ne 0 ]; then
	echo "$0:CSVファイルエクスポート用のユーザー情報の登録に失敗しました。"
	exit 1
fi
echo "$0:CSVファイルエクスポート用のユーザー情報の登録に成功しました。"

# ユーザー情報CSVファイルエクスポート
./export_csv.sh "$LAST_EXPORTED_AT" "$DB_ONEROSTER" 1 $EXPORT_USERS_FILE
if [ $? -ne 0 ]; then
	echo "$0:ユーザー情報CSVファイルエクスポートに失敗しました。"
	exit 1
fi
echo "$0:ユーザー情報CSVファイルエクスポートに成功しました。"

# 削除ユーザー情報CSVファイルエクスポート
./export_csv.sh "$LAST_EXPORTED_AT" "$DB_ONEROSTER" 2 $EXPORT_USERS_DELETED_FILE
if [ $? -ne 0 ]; then
	echo "$0:削除ユーザー情報CSVファイルエクスポートに失敗しました。"
	exit 1
fi
echo "$0:削除ユーザー情報CSVファイルエクスポートに成功しました。"

# CSVファイルのエクスポート結果の登録
./register_csv_export.sh "$DB_ONEROSTER"
if [ $? -ne 0 ]; then
	echo "$0:CSVファイルのエクスポート結果の登録に失敗しました。"
	exit 1
fi
echo "$0:CSVファイルのエクスポート結果の登録に成功しました。"

# DB登録を制御する
./register/oneroster_register.sh $OUTPUT_DIR
if [ $? -ne 0 ]; then
	echo "$0:DB登録制御に失敗しました。"
	exit 1
fi

exit 0
