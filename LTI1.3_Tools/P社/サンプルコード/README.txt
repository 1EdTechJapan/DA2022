# poc-LTI
## 概要
- LTI1.3認証後対象のドメイン情報及びログインユーザ情報を別ツールに送信し結果を画面表示するpocアプリ

## ローカル起動方法方法
    localtest.ps1

## API仕様
    /login　　　OIDCログインAPI
    /launch　　resourcelink用API
## 環境
    OS	    ：	最新のChrome OS （Chromebook）
    アプリ	：	Google Chrome v96以上
    メモリ	：	4GB以上
    その他	：	Wi-Fi,Ethernet機能またはLTE通信機能を有すること
         　　 インターネットに接続されていること
        
## library
    PyLTI1p3 2.0.0
- https://pypi.org/project/PyLTI1p3/