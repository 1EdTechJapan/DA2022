#!/bin/bash
# **************************************************
# 全体制御
# 引数
#    DATA_DIR:データディレクトリ
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "指定された引数は$#個です。" 1>&2
	exit 1
fi
DATA_DIR=$1
DB_ONEROSTER="mysql --defaults-extra-file=conf/oneroster_db.conf -t --show-warnings oneroster_digital"
ROOT_DIR=/home/ec2-user/work/oneroster_digital

cd $ROOT_DIR

# ダウンロード先ディレクトリ
DOWNLOAD_DIR=$ROOT_DIR/data/$DATA_DIR

# ログファイル
LOG_FILE=$DOWNLOAD_DIR/oneroster.log

# ログファイル出力開始
exec &> >(awk '{print strftime("[%Y/%m/%d %H:%M:%S] "),$0 } { fflush() } ' >> $LOG_FILE)

# 自治体毎の処理（csvファイル解凍、CSVファイルインポート）
./roop_cities.sh $ROOT_DIR $DOWNLOAD_DIR "$DB_ONEROSTER"
if [ $? -ne 0 ]; then
	echo "$0:自治体毎の処理に失敗しました。"
	exit 1
fi
echo "$0:自治体毎の処理に成功しました。"

# 学校コード取得、学校コード登録、CSVファイルエクスポート
./oneroster_export.sh $DOWNLOAD_DIR
if [ $? -ne 0 ]; then
	echo "$0:学校コード取得、学校コード登録、CSVファイルエクスポートに失敗しました。"
	exit 1
fi
echo "$0:学校コード取得、学校コード登録、CSVファイルエクスポートに成功しました。"

exit 0
