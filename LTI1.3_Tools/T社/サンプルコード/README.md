# LTI 1.3ツール

このリポジトリには、LMSとアプリケーションをシームレスに統合するためのLTI 1.3ツールが含まれています。
このツールを使えば、LMSの中にアプリケーションを簡単に組み込むことができ、ユーザーにシームレスな体験を提供することができます。

# 前提条件

このアプリケーションを実行するためには、以下のものが必要です。

- Java 8 以上
- Apache Maven 3.6以上

# 依存関係

プロジェクト利用です。

- Spring Boot Starter Web
- Spring Boot Starter Thymeleaf
- Spring Boot Starterのセキュリティ
- Spring Security OAuth2 JOSE
- Spring Security Config
- Spring Boot Starter OAuth2クライアント（javax.mailを除外しています）
- Spring Boot Starterの検証
- Project Lombok
- Jackson Core
- Jackson Databind
- Java Servlet API（提供されたスコープを使用）

# 詳細説明

このプロジェクトはライブラリを参照してください： https://github.com/oxctl/spring-security-lti13

- OAuth2のサポートをベースにしたSpring SecurityのLTI 1.3実装です。
- libのすべてのソースコードは、パッケージ：com.group.lti.libに含まれています。
- [OIDCInitiatingLoginRequestResolver.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Flti%2Flib%2Foauth2%2Fclient%2Flti%2Fweb%2FOIDCInitiatingLoginRequestResolver.java)
  クラスは、API Initiateログインのために実装されています。ログイン開始：/lti/login_initiation/ims-ri
- [OAuth2LoginAuthenticationFilter.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Flti%2Fclient%2Flti%2Fweb%2FOAuth2LoginAuthenticationFilter.java)
  APIログイン認証のために実装されたクラスです。/lti/login
- 解決方法
  OIDCInitiatingLoginRequestResolver.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Flti%2Flib%2Foauth2%2Fclient%2Flti%2Fweb%2FOIDCInitiatingLoginRequestResolver.java)
  APIログインリクエストの入力検証を行うロジックを実装しました。/lti/login_initiation/ims-ri
- [OidcTokenValidator.java](src%2Fmain%2Fjava%2Fcom%2Fgroup%2Flti%2Flib%2Foauth2%2Fclient%2Flti%2Fauthentication%2FOidcTokenValidator.java)
  API ログイン認証の OIDC Token 検証のための実装です。ログイン認証：/lti/login

# はじめに

LTI 1.3ツールを使い始めるには、以下のステップを実行します。

- このリポジトリをローカルマシンにクローンします。
- mvn clean install`を実行して、必要な依存関係をインストールします。
- 開発環境でTLSをセットアップするには、次のことをお勧めします。
  install [mkcert](https://github.com/FiloSottile/mkcert) これは、信頼できるルート証明書をインストールし、その後に
  の証明書を生成します。インストールしたら、プロジェクトのルートで次のように実行します。
  mkcert -pkcs12 -p12-file config/keystore.p12 localhost` です。

# 使用方法

LTI 1.3ツールを使用するには、LMSに設定する必要があります。以下の手順で、ツールを設定してください。
https://ltiorc.edustd.jp/ と統合する例

- ログイン https://ltiorc.edustd.jp
- https://ltiorc.edustd.jp/prelink_info/ で。
  ```
  ログイン開始URL： $HOST$/lti/login_initiation/ims-ri
  リダイレクトURI（複数可）： $HOST$/lti/login
  ```
  ex:
    ```
  ログイン開始URL : https://ec2-54-249-61-217.ap-northeast-1.compute.amazonaws.com/lti/login_initiation/ims-ri
  リダイレクトURI（複数可） : https://ec2-54-249-61-217.ap-northeast-1.compute.amazonaws.com/lti/login
    ```
- config/application.propertiesファイル内の設定ツール。
    ```
    spring.security.oauth2.client.registration.ims-ri.client-id=2pnpz1F
    spring.security.oauth2.client.registration.ims-ri.client-secret=unused
    spring.security.oauth2.client.registration.ims-ri.authorization-grant-type=implicit
    spring.security.oauth2.client.registration.ims-ri.scope=openid
    spring.security.oauth2.client.registration.ims-ri.redirect-uri=https://1e27-2405-4802-2de-f6e0-c8d3-dd6f-bb8d-ede7.ap.ngrok.io/lti/login #redirect uri
    spring.security.oauth2.client.provider.ims-ri.authorization-uri=https://api.ltiorc.edustd.jp/platform/auth/LTN7E8BF6J #認証要求URLのプラットフォーム
    Spring.Security.oauth2.client.provider.ims-ri.token-uri=https://api.ltiorc.edustd.jp/lti
    spring.security.oauth2.client.provider.ims-ri.jwk-set-uri=https://api.ltiorc.edustd.jp/platform/jwks
    spring.security.oauth2.client.provider.ims-ri.user-name-attribute=sub
    spring.security.oauth2.client.provider.ims-ri.deployment-id=S_B113110000037
    ```
- mvn clean install` または `mvn package` を実行して、このプロジェクトを jar ファイルにパッケージングします。
- Dockerイメージの構築: プロジェクトのルートディレクトリで `docker build -t lti-dev-img .` を実行します。プロジェクトのルートディレクトリで `docker build -t lti-dev-img .
- docker run --name lti-dev-container -p 443:8443 lti-dev-img -d`でdockerコンテナを実行する。
