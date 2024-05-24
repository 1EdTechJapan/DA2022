# OneRoster REST Service Consumer Sample Code README

## ・前提

当サンプルコードは実証用に作成したものであり、実際の運用の為の実装にはなっていません。

構成として CGI に接続し、HTML に 認可サーバのアクセスポイントや client_id, client_secret 等を 画面上の input に入力する構成をとっていますが、あくまで実際の運用ではなく実証用の為の実装という前提であるために現状のような構成になっています。

また OneRoster REST API との 通信を行う点に重点をおいていますので、取得した項目を登録する処理等は実装しておらず、サンプルコードに記載していません。

よろしくおねがいいたします。

## ・ファイル構成

### ・OAuth2.0 client クラス

* oauth2_client.h
* oauth2_client.cc

認可サーバへのアクセストークンリクエスト用クラスです。
OAuth2.0 Client Credentials Grant のみの実装です。

### ・OneRoster REST consumer クライアントクラス

* oneroster_rest_consumer.h
* oneroster_rest_consumer.cc

OneRoster REST Service Provider へのリクエスト用クラスです。
メンバ変数に OAuth2.0 client クラスインスタンス を持ち、認可リクエストは
そのメンバ変数で行いました。

### ・OneRoster REST consumer Test CGI クラス

* OneRosterRESTtest.h
* OneRosterRESTtest.cc

実証実験用CGI の Controller にあたるの処理を行うクラスです。

### ・OneRoster REST consumer Test View クラス

* OneRosterRESTtestView.h
* OneRosterRESTtestView.cc

実証実験用CGI の View にあたるの処理を行うクラスです。

### ・Http クライアントクラス

* http_curl.h
* http_curl.cc

libcurl の wrapper クラスです。
OAuth2.0 client クラス、OneRoster REST consumer クライアントクラスでの
http リクエストは 当クラスの処理を使用しています。

### ・Utility クラス

* utility.h
* utility.cc

共通で利用している Utilityクラスです。
