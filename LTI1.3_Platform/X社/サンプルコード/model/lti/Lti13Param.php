<?php

namespace app\models\lti;


use yii\base\Model;

class Lti13Param extends Model
{
    public string  $tool_url;           // [OIDC target_link_uri][ResourceLinkRequest（受検）のtarget_link_uri]
    public string  $initiate_login_url; // [OIDCローンチURL]
    public string  $public_keyset;      // [jwksURL]
    public string  $login_hint;
    public string  $client_id;
    public ?string $deployment_id = null;

    /**
     * @var string|array
     */
    public $redirect_uris;

    public bool $is_send_user_info = false;

    public function formName(): string
    {
        return '';
    }

    public function rules(): array
    {
        return [
            [
                [
                    'tool_url',
                    'initiate_login_url',
                    'public_keyset',
                    'redirect_uris',
                    'login_hint',
                ],
                'required',
            ],
            [
                [
                    'tool_url',
                    'initiate_login_url',
                    'public_keyset',
                    'login_hint',
                    'client_id',
                    'deployment_id',
                ],
                'string',
            ],
            [['is_send_user_info'], 'boolean'],
            [['redirect_uris'], 'string', 'when' => fn() => !is_array($this->redirect_uris)],
            [['redirect_uris'], 'each', 'rule' => ['string'], 'when' => fn() => is_array($this->redirect_uris)],
        ];
    }
}
