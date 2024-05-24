<?php

namespace app\modules\lti\controllers;

use app\models\infrastructures\Tenant;
use app\modules\lti\components\CommonController;
use Yii;
use Firebase\JWT\JWT;
use yii\web\BadRequestHttpException;
use yii\web\Response;
use app\models\lti\LtiAppMessageHint;
use app\models\infrastructures\Application;
use app\models\infrastructures\Belong;
use app\models\lti\Lti13Param;

class AppOidcController extends CommonController
{
    public $layout = false;
    public $enableCsrfValidation  = false;
    private array $ltiParams = [];

    public function init()
    {
        $this->ltiParams = Yii::$app->params['lti13tool'];

        parent::init();
    }

    public function actionJwks()
    {
        $this->response->format = Response::FORMAT_JSON;
        $this->response->content = file_get_contents(Yii::getAlias('@app/../keys/l-gate-jwks.json'));
    }

    public function actionAuth()
    {
        $requestData =
            $this->request->isPost ?
                $this->request->post() :
                ($this->request->isGet ? $this->request->get() : []);

        $hint = LtiAppMessageHint::createFromEncodedString($requestData['lti_message_hint']);

        // テナントに合わせてtable prefixを設定
        $tenant = Tenant::findOne($hint->tenantId);
        Yii::$app->db->tablePrefix = $tenant->tablePrefix;

        $application = Application::findOne($hint->applicationUuid);
        $lti13Param = $application->applicationUrl->lti13Param;

        // redirect_uriが事前共有されたものに合致するかチェック
        if (!in_array($requestData['redirect_uri'], (array)$lti13Param->redirect_uris)) {
            throw new BadRequestHttpException();
        }

        $payload = null;
        if ($hint->isResourceLink()) {
            $payload = $this->startResourceLink($application, $lti13Param, $hint);
        }
        if (!$payload) {
            throw new BadRequestHttpException();
        }
        $payload['nonce'] = $requestData['nonce'];

        $keyfile = Yii::getAlias('@app/../keys/l-gate.pem');
        $privateKey = file_get_contents($keyfile);

        return $this->render('auth', [
            'launchUrl' => $requestData['redirect_uri'],
            // 4番目の引数(kid)は、jwksのものに合わせる
            'idToken' => JWT::encode($payload, $privateKey, 'RS256', 'ランダムキー文字列'),
            'state' => $requestData['state'],
        ]);
    }

    private function startResourceLink(Application $application, Lti13Param $lti13Param, LtiAppMessageHint $hint): array
    {
        $belong = Belong::findOne(['uuid' => $hint->belongUuid]);
        $user = $belong->user;
        $schoolClass = $belong->schoolClass;
        $schoolClassName = $schoolClass->term->name . ':' . $schoolClass->name;

        $role = $belong->role->permission->isStudent() ? [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner',
        ] : [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor',
        ];

        $payload = [
            'iss' => $this->ltiParams['issuerId'],
            'sub' => $hint->userRelatedId,
            'aud' => [$lti13Param->client_id],
            'exp' => time() + 300,
            'iat' => time(),
            'https://purl.imsglobal.org/spec/lti/claim/message_type' => 'LtiResourceLinkRequest',
            'https://purl.imsglobal.org/spec/lti/claim/version' => '1.3.0',
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id' => $lti13Param->deployment_id,
            'https://purl.imsglobal.org/spec/lti/claim/target_link_uri' => $lti13Param->tool_url,
            'https://purl.imsglobal.org/spec/lti/claim/roles' => $role,
            'https://purl.imsglobal.org/spec/lti/claim/context' => [
                'id' => $schoolClass->uuid,
                'title' => $schoolClassName,
                'label' => $schoolClassName,
            ],
            'https://purl.imsglobal.org/spec/lti/claim/resource_link' => [
                'id' => $application->uuid,
                'title' => $application->title,
            ],
            'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint' => [
                "scope" => [
                    "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                    "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                    "https://purl.imsglobal.org/spec/lti-ags/scope/score"
                ],
                "lineitems" => "http://localhost/platform/services/ags/lineitems.php",
            ],
            'https://purl.imsglobal.org/spec/lti-nrps/claim/namesroleservice' => [
                'context_memberships_url' =>
                    sprintf('https://%s/lti/app-nrps/outcome/%d/%s/%s', $this->request->hostName, $hint->tenantId, $schoolClass->uuid, $application->uuid),
                'service_versions' => ['2.0'],

            ],
        ];

        if ($lti13Param->is_send_user_info) {
            $payload = array_merge($payload, [
                'name' => $user->last_name . ' '. $user->first_name,
                'given_name' => $user->first_name,
                'family_name' => $user->last_name,
                'middle_name' => '',
                'picture' => '',
                'email' => $user->login_id,
            ]);
        }

        return $payload;
    }
}