# OneRoster CSV Import Tool
OneRoster CSV Import Toolは、CSVファイルからOneRoster対応の学習ツールにデータをインポートするためのツールです。このツールは、LMSへのデータインポートのプロセスを簡素化し、時間と労力を節約するために設計されています。

# 前提条件

このアプリケーションを実行するためには、以下のものが必要です。

- Java 8 以上
- Apache Maven 3.6以上
-PostgreSQL

# はじめに
OneRoster CSV Import Toolを使うには、以下の手順を実行します。

- このリポジトリをクローンします。
- mvn clean install`を実行して、必要な依存関係をインストールします。
- ファイル [application.properties](src%2Fmain%2Fresources%2Fapplication.properties) で環境設定を行う。

# 特徴
OneRoster CSVインポートツールには、以下の機能があります。
- ユーザー名とパスワードによる基本認証。
- CSVファイルからインポートしたユーザーを管理するためのダッシュボード
- インポートに成功したファイルや失敗したログファイルを管理するためのダッシュボード
- ログファイルを1つまたは複数のファイルとしてダウンロードできるようにする。

# エラー処理
- CSVファイルにエラーがある場合、エラーページにエラー一覧を表示し、データベースにエラー一覧のログを保存します。
エラーページのエラー一覧の表示や、ファイルログのダウンロードにより、CSVファイルのエラーを修正することができます。

# 詳細説明
- [FileRestController.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Foneroster%2Fweb%2Fcontrollers%2Frestapi%2FFileRestController.java): APIダウンロードのエラーファイルまたは成功ファイルを作成します。
- [FilesController.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Foneroster%2Fweb%2Fcontrollers%2Fview%2Fadmin%2FFilesController.java): CSVインポートAPIとインポートしたファイルを一覧表示するコントローラ
- [UsersController.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Foneroster%2Fweb%2Fcontrollers%2Fview%2Fadmin%2FUsersController.java): 学習ツールダッシュボードのユーザー一覧にインポート
- [OneRosterValidator.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Foneroster%2Fvalidator%2FOneRosterValidator.java): OneRoster標準のバリデーションに従ったCSVのバリデーションを行うロジックの実装

# 使用方法
docker-composerでアプリケーションを起動できる。
```
mvn clean install
docker-composer up -d
```
# 認証
テキスト
ユーザー名：admin
パスワード：admin
```
