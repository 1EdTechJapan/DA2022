<?php
// システム特有のライブラリを読み込み
// include("hogehoge.php");

// ltiのライブラリを読み込み
//   https://github.com/1EdTech/lti-1-3-php-library
include("/vendor/autoload.php");
include("/src/lti/lti.php");
include("/db/example_database.php");

use \IMSGlobal\LTI;

try {
    // LTIメッセージオブジェクト生成
    $launch = new LTI\LTI_Message_Launch(new Example_Database());
    // LTI定義チェック
    $launch->validate();
    // SSOチェックオブジェクト生成
    $sso = new LtiSSO($log);
    // ログイン処理
    $sso->lti_login($launch->get_launch_data());
} catch (Exception $e) {
    // レスポンスコード設定
    http_response_code(500);
    // エラー詳細表示
    echo "Exception = ".$e->getMessage();
}

exit;
