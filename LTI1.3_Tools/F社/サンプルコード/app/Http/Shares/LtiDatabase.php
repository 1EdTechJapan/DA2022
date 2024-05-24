<?php
namespace App\Http\Shares;

use IMSGlobal\LTI;

// configs下のファイルを読み取りファイル内の情報をセッションのissに格納
$_SESSION['iss'] = [];
$reg_configs = array_diff(scandir(__DIR__ . '/configs'), array('..', '.', '.DS_Store'));
foreach ($reg_configs as $key => $reg_config) {
    $_SESSION['iss'] = array_merge($_SESSION['iss'], json_decode(file_get_contents(__DIR__ . "/configs/$reg_config"), true));
}

class LtiDatabase implements LTI\Database {
    /**
     * Registration Dataの検索
     *
     * @param
     *    string iss   iss（学習eポータルのベースURL）
     *
     * @return object LTI_Registrationオブジェクト
     */
    public function find_registration_by_issuer($iss) {
        // セッションのissが空、または、連携されたissがセッションのissに存在しない場合は、falseを返却
        if (empty($_SESSION['iss']) || empty($_SESSION['iss'][$iss])) {
            return false;
        }
        return LTI\LTI_Registration::new()
        ->set_auth_login_url($_SESSION['iss'][$iss]['auth_login_url'] ?? null)
        ->set_auth_token_url($_SESSION['iss'][$iss]['auth_token_url'] ?? null)
        ->set_auth_server($_SESSION['iss'][$iss]['auth_server'] ?? null)
        ->set_client_id($_SESSION['iss'][$iss]['client_id'] ?? null)
        ->set_key_set_url($_SESSION['iss'][$iss]['key_set_url'] ?? null)
        ->set_kid($_SESSION['iss'][$iss]['kid'] ?? null)
        ->set_issuer($iss)
        ->set_tool_private_key($this->private_key($iss));
    }

    /**
     * deployment_idの検索
     *
     * @param
     *    string iss             iss（学習eポータルのベースURL）
     *    string deployment_id   deployment_id
     *
     * @return object LTI_Deploymentオブジェクト
     */
    public function find_deployment($iss, $deployment_id) {
        // 連携されたdeployment_idがセッションのissに存在しない場合はfalseを返却
        if (!in_array($deployment_id, $_SESSION['iss'][$iss]['deployment'])) {
            return false;
        }
        return LTI\LTI_Deployment::new()
        ->set_deployment_id($deployment_id);
    }

    /**
     * private_keyの取得
     *
     * @param
     *    string iss             iss（学習eポータルのベースURL）
     *
     * @return string private_key
     */
    private function private_key($iss) {
        return file_get_contents(__DIR__ . $_SESSION['iss'][$iss]['private_key_file']);
    }
}
