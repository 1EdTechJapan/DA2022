【サンプルコードに関する補足事項】
・パッケージ名やクラス名などについて、運用中のシステムに関連する一部の記述を
　削除または、「XXXXX」に文字列置換いたしました。


【各ソースの概要】
・StudyToolAccessService.java
　OIDC認証にて使用する要素を取得し、生成したHTMLをブラウザに出力する。

・XXXXXLoginRequest.java
　OIDCの認証のリクエストを行うためのHTMLを生成する。


※認証リクエスト等の処理は以下のライブラリを用いて実施しています。

https://shibboleth.net/downloads/identity-provider/plugins/oidc-common/
https://shibboleth.net/downloads/identity-provider/plugins/oidc-op/
