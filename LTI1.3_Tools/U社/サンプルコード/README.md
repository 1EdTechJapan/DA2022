# LTI 1.3 Resource Link サンプル

Java、Spring Bootで作成したLTI 1.3のResource Link起動サンプルアプリケーションです。

## 環境

* Amazon Corretto 11
* SpringBoot2.2.6

## サンプルコードの構成と概要

```
コード_LTI
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
└─src
    └─main
        ├─java
        │  └─jp
        │      ├─co
        │      │  └─example
        │      │      │  Application.java [Spring Boot 起動クラス]
        │      │      │
        │      │      ├─osarai2
        │      │      │  ├─config
        │      │      │  │      ApplicationConfig.java [application.yml取得用クラス]
        │      │      │  │
        │      │      │  ├─controller
        │      │      │  │  └─digital
        │      │      │  │          LtiController.java [Resource Linkコントローラークラス]
        │      │      │  │
        │      │      │  ├─data
        │      │      │  │  └─lti [Resource Linkデータ定義クラス群]
        │      │      │  │          InitiationBaseData.java
        │      │      │  │          InitiationRequestData.java
        │      │      │  │          InitiationResponseData.java
        │      │      │  │          ResourceLinkData.java
        │      │      │  │
        │      │      │  ├─definition [Resource Link定数クラス群]
        │      │      │  │      digital.java
        │      │      │  │      lti_request.java
        │      │      │  │
        │      │      │  ├─service
        │      │      │  │  └─lti [Resource Linkロジッククラス群]
        │      │      │  │          InitiationService.java
        │      │      │  │          LaunchService.java
        │      │      │  │          SessionService.java
        │      │      │  │
        │      │      │  └─validation
        │      │      │      ├─constraints
        │      │      │      │      ResourceLink.java [ResourceLinkバリデーション制約クラス]
        │      │      │      │
        │      │      │      └─validator
        │      │      │              ResouceLinkValidator.java [ResourceLinkバリデーションロジッククラス]
        │      │      │
        │      │      └─springboot
        │      │          │  FQCNBeanNameGenerator.java [ComponentScan用のComponent作成クラス]
        │      │          │
        │      │          └─validation
        │      │                  ValidationUtility.java [バリデーションユーティリティクラス]
        │      │
        │      └─commoncode
        │          └─common
        │                  StringUtility.java [文字列ユーティリティクラス]
        │                  TimeUtility.java [Timestampユーティリティクラス]
        │
        └─resources
            ├─config
            │      application.yml [アプリケーション環境設定]
            │
            ├─i18n
            │      messages.properties [表示メッセージ設定]
            │
            ├─static
            │  └─osarai2
            │      └─css [Thymeleafテンプレート用CSS]
            │              main.css
            │
            └─templates
                └─lti [Thymeleafテンプレート群]
                        error.html
                        login.html
```

## サンプルコード実行

1. 下記ファイルの設定を環境に応じて設定。
  * src\main\resources\config\application.yml
```
settings:
  lti:
    id:
      platform: PlatformId
      deployment: DeploymentId
      client: ClientId
    url:
      launch: https://example.com/launch
      oidc-auth: https://example.com/auth
      jwks: https://example.com/jwks
```
2. 下記ファイルにパラメータ、およびリダイレクト先を設定。（HTMLテンプレートの利用は任意）
* src\main\java\jp\co\example\osarai2\controller\digital\LtiController.java#launches()
```
model.addAttribute("usertoken", "token");

return "lti/login";
```
* src\main\resources\templates\lti\login.html
```
var usertoken = /*[[ ${pusertoken} ]]*/ '';
localStorage.setItem('pusertoken', `"${usertoken}"`);
location.href = `/contents/user/login`;
```
3. 本ファイルのルートディレクトリで下記を実行。
```
./gradlew bootRun
```
4. 下記へResource LinkのInitiationリクエストをPOSTで送信。
```
http://localhost:8080/osarai/lti/initiation
```
