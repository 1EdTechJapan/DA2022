# OneRoster REST 入力サンプル

Java、Spring Bootで作成したOneRoster REST入力サンプルアプリケーションです。
REST通信のコード生成にOpenApi generatorを利用します。

## 環境

* Amazon Corretto 11
* SpringBoot2.2.6
* OpenApi generator4.3.0

## サンプルコードの構成と概要

```
コード_OneRosterREST入力
│  README.md [サンプルコード情報記載ファイル]
│
├─openapi [OpenAPI関連ファイル群]
│  └─oneRoster
│      │  definition.yaml [OpenAPI定義ファイル]
│      │
│      └─config
│              java.json [OneRoster Java用OpenAPI設定ファイル]
│
├─sample [OneRosterREST取得サンプルファイル群]
│  └─oneRoster
│      └─v1
│              classes.json
│              enrollments.json
│              oauth2.json
│              orgs.json
│              users.json
│
└─server [OneRosterREST実行プログラムファイル群]
    │  [gradle管理ファイル群]
    │  .classpath
    │  .project
    │  build.gradle
    │  gradlew
    │  gradlew.bat
    │  settings.gradle
    │
    │  [gradle実行設定ファイル群]
    ├─gradle
    │  └─wrapper
    │          gradle-wrapper.jar
    │          gradle-wrapper.properties
    │
    └─src
        └─main
            ├─java
            │  └─jp
            │      └─co
            │          └─example
            │              │  Application.java [Spring Boot 起動クラス]
            │              │
            │              ├─osarai2
            │              │  ├─controller
            │              │  │  └─digital
            │              │  │          OneRosterController.java [OneRosterRESTコントローラークラス]
            │              │  │
            │              │  └─service
            │              │      └─oneRoster [OneRosterRESTロジッククラス]
            │              │              OrgService.java
            │              │              RoomService.java
            │              │              UserService.java
            │              │
            │              └─springboot
            │                      FQCNBeanNameGenerator.java [ComponentScan用のComponent作成クラス]
            │
            └─resources
                └─config
                        application.yml [アプリケーション環境設定]
```

## サンプルコード実行

1. 下記ファイルの通信先を環境に応じて変更。（本サンプルではローカルサーバーを設定）
  * openapi\oneRoster\definition.yaml
```
- url: http://localhost/osarai2/sample/oneRoster/v1/
```
2. 下記ファイルの出力内容を環境に応じて設定。
  * server\src\main\java\jp\co\example\osarai2\service\oneRoster\OrgService.java
  * server\src\main\java\jp\co\example\osarai2\service\oneRoster\RoomService.java
  * server\src\main\java\jp\co\example\osarai2\service\oneRoster\UserService.java
3. 本ファイルのルートディレクトリで下記を実行。
```
cd ./server
./gradlew bootRun
```
4. 下記のいずれかのREST通信実行用APIへGETで送信。
```
http://localhost:8080/osarai/oneRoster/orgs
http://localhost:8080/osarai/oneRoster/classes
http://localhost:8080/osarai/oneRoster/users
```
