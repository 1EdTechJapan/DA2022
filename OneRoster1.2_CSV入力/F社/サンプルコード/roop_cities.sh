#!/bin/bash
# **************************************************
# 自治体毎の処理
# 引数
#    ROOT_DIR    :ルートディレクトリ
#    DOWNLOAD_DIR:ダウンロード先ディレクトリ
#    DB          :OneRosterデータベース名
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 3 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
ROOT_DIR=$1
DOWNLOAD_DIR=$2
DB=$3

# ディレクトリ（自治体）一覧の取得
DIRS=$DOWNLOAD_DIR/*

# ディレクトリ（自治体）数分実施
for DIR_PATH in $DIRS
do
	if [ -d "$DIR_PATH" ] ; then
		# ZIPファイル一覧の取得
		FILES="$DIR_PATH/*"

		# ZIPファイル数分実施
		for FILE_PATH in $FILES
		do
			if [ -f "$FILE_PATH" ] ; then
				# 最後のディレクトリ名のみ取得
				DIR_NAME=`echo "${DIR_PATH##*/}"`
				DIR_NAME=\"$DIR_NAME\"

				# ファイル名のみ取得（拡張子ありとなし）
				FILE_NAME=`basename "$FILE_PATH"`
				FILE_NAME_NOT_EXT=`echo "$FILE_NAME" | sed 's/\.[^\.]*$//'`
				FILE_NAME=\"$FILE_NAME\"

				# CSVファイルのインポート結果の存在確認
				COUNT=`./check_exist_csv_import.sh "$DIR_NAME" "$FILE_NAME" "$DB"`
				if [ $? -ne 0 ]; then
					echo "$0:CSVファイルのインポート結果の存在確認に失敗しました。dir_name=$DIR_NAME, file_name=$FILE_NAME"
					exit 1
				fi

				# CSVファイルのインポート結果が存在する場合はZIPファイル解凍とcsvファイルインポートをスキップ
				if [ $COUNT != "0" ]; then
					echo "$0:CSVファイルのインポート結果は存在します。dir_name=$DIR_NAME, file_name=$FILE_NAME"
					continue
				fi
				echo "$0:CSVファイルのインポート結果は存在しません。dir_name=$DIR_NAME, file_name=$FILE_NAME"

				# CSVファイル解凍先のディレクトリの作成
				cd "$DIR_PATH"
				if [ ! -d "csv" ]; then
					mkdir csv
				fi
				cd csv
				if [ ! -d $FILE_NAME_NOT_EXT ]; then
					mkdir $FILE_NAME_NOT_EXT
				fi
				cd $ROOT_DIR

				# CSVファイル解凍
				unzip $FILE_PATH -d "$DIR_PATH/csv/$FILE_NAME_NOT_EXT"
				if [ $? -ne 0 ]; then
					echo "$0:CSVファイルの解凍に失敗しました。FILE_PATH=$FILE_PATH"
					exit 1
				else
					echo "$0:CSVファイルの解凍に成功しました。FILE_PATH=$FILE_PATH"
				fi

				# CSVファイルインポート
				./import_csv.sh "$DIR_PATH/csv/$FILE_NAME_NOT_EXT" "$DB" "$DIR_NAME"
				if [ $? -ne 0 ]; then
					echo "$0:CSVファイルのインポートに失敗しました。FILE_PATH=$FILE_PATH"
					exit 1
				fi

				# CSVファイルのインポート結果の登録
				./register_csv_import.sh "$DIR_NAME" "$FILE_NAME" "$DB"
				if [ $? -ne 0 ]; then
					echo "$0:CSVファイルのインポート結果の登録に失敗しました。dir_name=$DIR_NAME, file_name=$FILE_NAME"
					exit 1
				else
					echo "$0:CSVファイルのインポート結果の登録に成功しました。dir_name=$DIR_NAME, file_name=$FILE_NAME"
				fi
			fi
		done
	fi
done

if [ $? -eq 1 ]; then
	exit 1
fi
exit 0
