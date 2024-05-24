<?php

namespace Src\Lti;

use \IMSGlobal\LTI;

/**
 * LTI用の情報を定義するクラス
 */
class LtiDatabase implements LTI\Database
{
    /**
     * LTIの情報を定義
     */
    public function find_registration_by_issuer($iss)
    {
        $ltiConfig = \ConfigService::get('lti');
        // ConfigServiceについて：configに定義した情報を取得する処理

        return LTI\LTI_Registration::new()
            ->set_auth_login_url($ltiConfig[$iss]['auth_login_url'])
            ->set_auth_token_url($ltiConfig[$iss]['auth_token_url'])
            ->set_auth_server($ltiConfig[$iss]['auth_server'])
            ->set_client_id($ltiConfig[$iss]['client_id'])
            ->set_key_set_url($ltiConfig[$iss]['key_set_url'])
            ->set_kid($ltiConfig[$iss]['kid'])
            ->set_issuer($iss)
            ->set_tool_private_key($this->private_key($iss));
    }

    /**
     * deploymentがLTIの定義にあるか確認
     */
    public function find_deployment($iss, $deployment_id)
    {
        $ltiConfig = \ConfigService::get('lti');
        // ConfigServiceについて：configに定義した情報を取得する処理

        if (!in_array($deployment_id, $ltiConfig[$iss]['deployment'])) {
            return false;
        }

        return LTI\LTI_Deployment::new()->set_deployment_id($deployment_id);
    }

    /**
     * 指定のpribate_keyを取得
     */
    private function private_key($iss)
    {
        $ltiConfig = \ConfigService::get('lti');

        return file_get_contents(__DIR__ . $ltiConfig[$iss]['private_key_file']);
    }
}
