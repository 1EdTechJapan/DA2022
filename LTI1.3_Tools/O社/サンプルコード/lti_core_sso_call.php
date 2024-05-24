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

    // 接続オブジェクト生成
    $db = new Example_Database();
    // LTIオブジェクト生成
    $obj = new LTI\LTI_OIDC_Login($db);
    // リダイレクト処理
    $redirect = $obj->do_oidc_login_redirect();
    $redirect->do_redirect();

} catch (Exception $e) {
    // レスポンスコード設定
    http_response_code(500);
    // エラー詳細表示
    echo "Exception = ".$e->getMessage();
}

exit;
