LTI v1.3 Core Tool

前提条件
 ・Laravelを使用すること
 ・PHP7.3以上がインストールされていること

各フォルダについて
 ・app/Http/Controllers/Member：必要なControllerが格納先
 ・config：config情報の格納先
 ・routers：routering情報の格納先
 ・src/Lti：LTIに必要な追加ロジックの格納先また、pribate.keyが必要な場合にもこちらに格納する
 ・compooser.json：Ltiライブラリを読み込むために必要な情報

注意点
 src/Lti/LtiDtabase.phpを読み込むためには下記のようにautoloadへの処理が必要となる 
"autoload": {
    "classmap": [
    ],
    "psr-4": {
        "Src\\": "src/"
    }
},

リクエストされる処理について
1./lti/redirect(init処理)
 app/Http/Controllers/Member/LtiLoginController.php -> redirect
 上記が呼び出され実行される

2./lti/login（ログイン処理）
 app/Http/Controllers/Member/LtiLoginController.php -> login
 上記が呼び出され実行される

その他注意点
 ・本システムでは、department_idにて定義された学校コードを特定のルールにて変換した値がシステムのデータベースに記録されていない場合にはログインができないため注意が必要
 ・conposer.jsonには、LTIライブラリを実行するためだけに必要な処理のみを明記している。こちらにlaravelのライブラリを呼び出す仕組みも必要となる。