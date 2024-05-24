<?php

namespace app\modules\lti\controllers;

use app\models\infrastructures\ControlExam;
use app\models\infrastructures\ControlExamResult;
use app\models\infrastructures\ExamResult;
use app\models\infrastructures\Tenant;
use app\models\lti\LtiMessageHint;
use app\modules\lti\components\CommonController;
use Yii;
use Firebase\JWT\JWT;
use yii\web\BadRequestHttpException;
use app\models\infrastructures\User;
use yii\web\Response;
use app\models\infrastructures\Exam;

class OidcController extends CommonController
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

        // redirect_uriが事前共有されたものに合致するかチェック
        if ($requestData['redirect_uri'] !== $this->ltiParams['oidcRedirectUrl']) {
            throw new BadRequestHttpException();
        }

        $data = base64_decode($requestData['lti_message_hint']);
        $ltiMessageHint = Yii::$app->security->decryptByPassword($data, LtiMessageHint::SECRET);
        $hint = LtiMessageHint::createFromArray(json_decode($ltiMessageHint, true));

        // TODO: 共通configに移す
        $keyfile = Yii::getAlias('@app/../keys/l-gate.pem');
        $privateKey = file_get_contents($keyfile);

        // テナントに合わせてtable prefixを設定
        $tenant = Tenant::findOne($hint->tenantId);
        Yii::$app->db->tablePrefix = $tenant->tablePrefix;

        $payload = null;
        if ($hint->isDeepLinking()) {
            $payload = $this->startDeepLinking($requestData, $hint);
        } elseif ($hint->isResourceLink()) {
            $payload = $this->startResourceLink($requestData, $hint);
        } elseif ($hint->isResourceLinkResult()) {
            $payload = $this->startResourceLinkResult($requestData, $hint);
        }
        if (!$payload) {
            throw new BadRequestHttpException();
        }
        $payload['nonce'] = $requestData['nonce'];

        return $this->render('auth', [
            'launchUrl' => $requestData['redirect_uri'],
            // 4番目の引数(kid)は、jwksのものに合わせる
            'idToken' => JWT::encode($payload, $privateKey, 'RS256', 'ランダムキー文字列'),
            'state' => $requestData['state'],
        ]);
    }

    private function startDeepLinking(array $requestData, LtiMessageHint $hint): array
    {
        $module = $hint->isControl ? 'control' : 'admin';
        $returnUrl = "{$hint->hostInfo}/{$module}/lti-launch/deep-linking-return";

        return [
            'iss' => $this->ltiParams['issuerId'],
            'sub' => $hint->userUuid,
            'aud' => [$this->ltiParams['clientId']],
            'exp' => time() + 300,
            'iat' => time(),
            'https://purl.imsglobal.org/spec/lti/claim/message_type' => 'LtiDeepLinkingRequest',
            'https://purl.imsglobal.org/spec/lti/claim/version' => '1.3.0',
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id' => $hint->schoolCode,
            'https://purl.imsglobal.org/spec/lti/claim/target_link_uri' => $this->ltiParams['deepLinkingUrl'],
            'https://purl.imsglobal.org/spec/lti/claim/roles' => $this->makeRolesFromUser(User::findOne($hint->userUuid), $hint->isControl),
            'https://purl.imsglobal.org/spec/lti/claim/context' => [
                'id' => $hint->examCategoryUuid,
                'title' => $hint->examCategoryTitle,
            ],
            'https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings' => [
                'deep_link_return_url' => $returnUrl,
                'accept_types' => ['ltiResourceLink'],
                'accept_presentation_document_targets' => ['window'],
                'accept_multiple' => true,
                'data' => $requestData['lti_message_hint'],
            ]
        ];
    }

    private function startResourceLink(array $requestData, LtiMessageHint $hint): array
    {
        // 試験の取得
        $exam = $hint->isControl ? ControlExam::findOne($hint->examUuid) : Exam::findOne($hint->examUuid);

        return [
            'iss' => $this->ltiParams['issuerId'],
            'sub' => $hint->userUuid,
            'aud' => [$this->ltiParams['clientId']],
            'exp' => time() + 300,
            'iat' => time(),
            'https://purl.imsglobal.org/spec/lti/claim/message_type' => 'LtiResourceLinkRequest',
            'https://purl.imsglobal.org/spec/lti/claim/version' => '1.3.0',
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id' => $hint->schoolCode,
            'https://purl.imsglobal.org/spec/lti/claim/target_link_uri' => $exam->url,
            'https://purl.imsglobal.org/spec/lti/claim/roles' => $this->makeRolesFromUser(User::findOne($hint->userUuid)),
            'https://purl.imsglobal.org/spec/lti/claim/context' => [
                'id' => $hint->examCategoryUuid,
                'title' => $hint->examCategoryTitle,
            ],
            'https://purl.imsglobal.org/spec/lti/claim/resource_link' => [
                'id' => $hint->examUuid,
                'title' => $hint->examTitle,
            ],
            'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint' => [
                'scope' => [
                    'https://purl.imsglobal.org/spec/lti-ags/scope/score'
                ],
                // NOTE: 外部からスコアが帰ってくるURL。開発環境ではngrok等のものに差し替える。
                'lineitem' => $this->makeAgsUrl($hint),
            ],
            // 現状は空でOKだが、キー自体は設定する必要がある
            'https://purl.imsglobal.org/spec/lti/claim/custom'=> [],
        ];
    }

    private function startResourceLinkResult(array $requestData, LtiMessageHint $hint): array
    {
        // 結果レコードの取得
        $result = $hint->isControl ? ControlExamResult::findOne($hint->examResultUuid) : ExamResult::findOne($hint->examResultUuid);

        return [
            'iss' => $this->ltiParams['issuerId'],
            'sub' => $hint->userUuid,
            'aud' => [$this->ltiParams['clientId']],
            'exp' => time() + 300,
            'iat' => time(),
            'https://purl.imsglobal.org/spec/lti/claim/message_type' => 'LtiResourceLinkRequest',
            'https://purl.imsglobal.org/spec/lti/claim/version' => '1.3.0',
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id' => $hint->schoolCode,
            'https://purl.imsglobal.org/spec/lti/claim/target_link_uri' => $result->exam->result_url,
            'https://purl.imsglobal.org/spec/lti/claim/roles' => $this->makeRolesFromUser(User::findOne($hint->userUuid)),
            'https://purl.imsglobal.org/spec/lti/claim/context' => [
                'id' => $hint->examCategoryUuid,
                'title' => $hint->examCategoryTitle,
            ],
            'https://purl.imsglobal.org/spec/lti/claim/resource_link' => [
                'id' => $hint->examUuid,
                'title' => $hint->examTitle,
            ],
            'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint' => [
                'scope' => [
                    'https://purl.imsglobal.org/spec/lti-ags/scope/score'
                ],
                // NOTE: 外部からスコアが帰ってくるURL。開発環境ではngrok等のものに差し替える。
                'lineitem' => $this->makeAgsUrl($hint),
            ],
            'https://purl.imsglobal.org/spec/lti/claim/custom'=> [
                'for_user_id' => $result->user_uuid,
                'for_roles' => $this->makeRolesFromUser($result->user),
                'custom_show_score'=> true,
                'custom_show_correct' => true,
            ],
        ];
    }

    private function makeRolesFromUser(User $user, bool $isControl = false): array
    {
        $student = [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner',
        ];
        $teacher = [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor',
        ];
        if ($isControl) {
            return [
                'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator',
                'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff',
                'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty',
            ];
        } elseif ($user->isStudent()) {
            // 今年度所属の生徒
            return $student;
        } elseif ($user->isTeacher() || $user->isAdministrator()) {
            // 今年度所属で生徒以外
            return $teacher;
        } elseif ($user->isTeacher(false) || $user->isAdministrator(false)) {
            // 年度関係なく教員以上の権限
            return $teacher;
        }
        // それ以外は生徒扱い
        return $student;
    }

    private function makeAgsUrl(LtiMessageHint $hint, ?string $hostName = null, bool $isHttps = true): string
    {
        $hostName ??= $this->request->hostName;
        $actionName = $hint->isControl ? 'control-outcome' : 'outcome';
        return ($isHttps ? 'https' : 'http') . "://{$hostName}/lti/ags/{$actionName}/{$hint->tenantId}/{$hint->examResultUuid}";
    }
}