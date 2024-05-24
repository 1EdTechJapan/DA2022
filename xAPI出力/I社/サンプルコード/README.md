# xAPI出力 サンプル

Java、Spring Bootで作成したxAPI出力サンプルアプリケーションです。

## 環境

* Amazon Corretto 11
* SpringBoot2.5.6

## サンプルコードの構成と概要

```
コード_xAPI出力
│  [gradle管理ファイル群]
│  .classpath
│  .project
│  build.gradle
│  gradlew
│  gradlew.bat
│  settings.gradle
│
│  [サンプルコード情報記載ファイル]
│  README.md
│
│  [gradle実行設定ファイル群]
├─gradle
│  └─wrapper
│          gradle-wrapper.jar
│          gradle-wrapper.properties
│
├─src
│  └─main
│      ├─java
│      │  └─jp
│      │      ├─co
│      │      │  └─example
│      │      │      │  Application.java [Spring Boot 起動クラス]
│      │      │      │
│      │      │      ├─programming
│      │      │      │  ├─config
│      │      │      │  │      ApplicationConfig.java [application.yml取得用クラス]
│      │      │      │  │
│      │      │      │  ├─controller
│      │      │      │  │  └─user
│      │      │      │  │          StudyApiController.java [学習結果登録コントローラークラス]
│      │      │      │  │
│      │      │      │  └─service
│      │      │      │      └─user
│      │      │      │              StudyLogService.java [学習結果登録ロジッククラス]
│      │      │      │
│      │      │      └─springboot
│      │      │              FQCNBeanNameGenerator.java [ComponentScan用のComponent作成クラス]
│      │      │
│      │      └─commoncode
│      │          └─common
│      │                  EncodingConst.java [エンコード定数定義クラス]
│      │                  FileUtility.java [ファイル操作ユーティリティクラス]
│      │                  TemplateLoader.java [テンプレート読み込みクラス]
│      │                  TimeUtility.java [Timestampユーティリティクラス]
│      │
│      └─resources
│          └─config
│                  application.yml [アプリケーション環境設定]
│
└─xAPI
    ├─output [xAPIファイル出力ディレクトリ]
    └─template
            profile.jsonld [xAPIプロファイルテンプレート]
```

## サンプルコード実行

1. 下記ファイルに任意のプロファイル内容を記載。置き換えを行いたい部分を下記を設定。
* xAPI\template\profile.jsonld
```
<%= [置換用変数名] =>
```
2. 下記ファイルに置換用変数名と置換内容を設定。
* src\main\java\jp\co\example\programming\service\user\StudyLogService.java
```
// テンプレートファイルの置換情報
Properties props = new Properties();
props.put("HOST_NAME", InetAddress.getLocalHost().getHostName());
```
3. 本ファイルのルートディレクトリで下記を実行。
```
./gradlew bootRun
```
4. 下記へPOST送信。
```
http://localhost:8080/programming/study
```
