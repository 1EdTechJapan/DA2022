<?php
// ltiのライブラリを読み込み
//   https://github.com/1EdTech/lti-1-3-php-library
require_once '/vendor/autoload.php';
require_once '/src/lti/Database.php';
require_once '/src/lti/LTI_Registration.php';

define("TOOL_HOST", ($_SERVER['HTTP_X_FORWARDED_PROTO'] ?: $_SERVER['REQUEST_SCHEME']) . '://' . $_SERVER['HTTP_HOST']);
session_start();
use \IMSGlobal\LTI;

$_SESSION['iss'] = [];
$reg_configs = array_diff(scandir('/db/configs'), array('..', '.', '.DS_Store'));
foreach ($reg_configs as $key => $reg_config) {
    $_SESSION['iss'] = array_merge($_SESSION['iss'], json_decode(file_get_contents("/db/configs/$reg_config"), true));
}

class Example_Database implements LTI\Database {

    /**
     * 接続情報保存
     */
    public function find_registration_by_issuer($iss) {
        if (empty($_SESSION['iss']) || empty($_SESSION['iss'][$iss])) {
            return false;
        }

        $obj = new LTI\LTI_Registration();
        $obj->set_auth_login_url($_SESSION['iss'][$iss]['auth_login_url']);
        $obj->set_auth_token_url($_SESSION['iss'][$iss]['auth_token_url']);
        $obj->set_auth_server($_SESSION['iss'][$iss]['auth_server']);
        $obj->set_client_id($_SESSION['iss'][$iss]['client_id']);
        $obj->set_key_set_url($_SESSION['iss'][$iss]['key_set_url']);
        $obj->set_kid($_SESSION['iss'][$iss]['kid']);
        $obj->set_issuer($iss);
        $obj->set_tool_private_key($this->private_key($iss));

        return $obj;
    }

    /**
     * デプロイメント取得
     */
    public function find_deployment($iss, $deployment_id) {
        if (!in_array($deployment_id, $_SESSION['iss'][$iss]['deployment'])) {
            return false;
        }

        $obj = new LTI\LTI_Deployment();
        $obj->set_deployment_id($deployment_id);
        return $obj;
    }

    /**
     * プライベートキー読込
     */
    private function private_key($iss) {
        return file_get_contents(LOG_DIR . $_SESSION['iss'][$iss]['private_key_file']);
    }

    /**
     * リダイレクトURL取得
     */
    public function get_redirect_url($iss) {
        return $_SESSION['iss'][$iss]['redirect_url'];
    }
}