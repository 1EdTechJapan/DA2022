#!/bin/bash
# **************************************************
# UUID形式確認
# 引数
#    uuid:UUID
# 返却値
#    なし
# **************************************************
# 引数のチェック
if [ $# -ne 1 ]; then
	echo "$0:指定された引数は$#個です。"
	exit 1
fi
uuid=$1
array_hexadecimal=('0' '1' '2' '3' '4' '5' '6' '7' '8' '9' 'a' 'b' 'c' 'd' 'e' 'f')
array_89ab=('8' '9' 'a' 'b')
char=""
i=0

# 文字数の確認
if [ ${#uuid} != 36 ]; then
	echo "$0:UUIDの文字数が違います。[$uuid] "
	exit 1
fi

# 1文字ずつ確認
for ((i=1; i <= 36; i++)); do
	char=`echo ${uuid:$i-1:1}`
	if [ $i = 9 ] || [ $i = 14 ] || [ $i = 19 ] || [ $i = 24 ]; then
		if [ $char != "-" ]; then
			echo "$0:UUIDの$i文字目が違います。[$uuid, $char] "
			exit 1
		fi
	elif [ $i = 15 ]; then
		if [ $char != "4" ]; then
			echo "$0:UUIDの$i文字目が違います。[$uuid, $char] "
			exit 1
		fi
	elif [ $i = 20 ]; then
		if [[ $(printf '%s\n' "${array_89ab[@]}" | grep -qx "$char"; echo -n ${?} ) -ne 0 ]]; then
			echo "$0:UUIDの$i文字目が違います。[$uuid, $char] "
			exit 1
		fi
	else
		if [[ $(printf '%s\n' "${array_hexadecimal[@]}" | grep -qx "$char"; echo -n ${?} ) -ne 0 ]]; then
			echo "$0:UUIDの$i文字目が違います。[$uuid, $char] "
			exit 1
		fi
	fi
done
if [ $? -eq 1 ]; then
	exit 1
fi

exit 0
