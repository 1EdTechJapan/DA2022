#!/bin/bash
# **************************************************
# 18.oneroster_register.sh
# DB登録制御
# 引数
#	OUTPUT_DIR		:出力先ディレクトリ
# 返却値
#	なし
# DB登録を制御する
# ・前回DB登録日時の取得呼び出し
# ・クラス毎の処理呼び出し
# ・DB登録結果の登録呼び出し
# **************************************************
# 引数のチェック

if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。" 1>&2
	exit 1
fi
OUTPUT_DIR=$1
DB_ONEROSTER="mysql --defaults-extra-file=../conf/oneroster_db.conf -t --show-warnings oneroster_digital"
DB_AZURE="mysql --defaults-extra-file=../conf/aiai_monkey_db.conf -t --show-warnings dev.aiaimonkey"
ROOT_DIR=/home/ec2-user/work/oneroster_digital/register

cd $ROOT_DIR

# ログファイル
LOG_FILE=$OUTPUT_DIR/oneroster.log

# ログファイル出力開始
exec &> >(awk '{print strftime("[%Y/%m/%d %H:%M:%S] "),$0 } { fflush() } ' >> $LOG_FILE)

# 19.前回DB登録日時の取得
registered_at=`./get_last_db_registered_at.sh "$DB_ONEROSTER"`
if [ $? -ne 0 ]; then
	echo "$0:前回DB登録日時の取得に失敗しました。"
	exit 1
fi
echo "$0:前回DB登録日時の取得に成功しました。registered_at=$registered_at"

# 20.クラス毎の処理
./roop_classes.sh "$registered_at" "$DB_ONEROSTER" "$DB_AZURE"
if [ $? -ne 0 ]; then
	echo "$0:クラス毎の処理に失敗しました。"
	exit 1
fi
echo "$0:クラス毎の処理に成功しました。"

# 32.DB登録結果の登録
./register_db_register.sh "$DB_ONEROSTER"
if [ $? -ne 0 ]; then
	echo "$0:DB登録結果の登録に失敗しました。"
	exit 1
fi
echo "$0:DB登録結果の登録に成功しました。"

exit 0
