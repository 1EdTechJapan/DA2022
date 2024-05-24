<?php

namespace app\modules\lti\controllers;

use app\models\infrastructures\SchoolClass;
use app\modules\control\models\repositories\Belong;
use app\modules\control\models\repositories\Permission;
use app\modules\control\models\repositories\Role;
use yii\web\Controller;
use app\modules\control\models\repositories\User;
use yii\web\UnauthorizedHttpException;
use Yii;
use yii\web\Response;
use Firebase\JWT\JWT;
use yii\data\ActiveDataProvider;
use yii\web\BadRequestHttpException;
use yii\web\NotFoundHttpException;
use app\models\infrastructures\Tenant;
use app\models\infrastructures\Application;

class AppNrpsController extends Controller
{
    public $layout = false;
    public $enableCsrfValidation  = false;

    private const ROLE_TABLE = [
        'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student'
            => Permission::CODE_STUDENT,
        'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner'
            => Permission::CODE_STUDENT,
        'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty'
            => Permission::CODE_TEACHER,
        'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor'
            => Permission::CODE_TEACHER,
    ];
    private const CODE_TABLE = [
        Permission::CODE_STUDENT => [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner',
        ],
        Permission::CODE_TEACHER => [
            'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty',
            'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor',
        ],
    ];

    public function init()
    {
        ini_set('memory_limit', '4G');
        Yii::$app->response->format = Response::FORMAT_JSON;
    }

    public function actionOutcome(int $tenantId, string $schoolClassUuid, string $applicationUuid, string $role = null, int $limit = 100, int $page = 0)
    {
        $request = Yii::$app->request;
        // トークンの検証
        $match = [];
        if (!preg_match('/^Bearer\s+(.*?)$/', $request->headers['Authorization'], $match)) {
            throw new UnauthorizedHttpException();
        }
        $token = $match[1];
        $keyfile = Yii::getAlias('@app/../keys/l-gate.pem');
        $privateKey = file_get_contents($keyfile);
        JWT::decode($token, $privateKey, ['HS256']);

        // テナントに合わせてtable prefixを設定
        $tenant = Tenant::findOne($tenantId);
        Yii::$app->db->tablePrefix = $tenant->tablePrefix;

        // クラス情報の取得
        $schoolClass = SchoolClass::findOne($schoolClassUuid);
        if (!$schoolClass) {
            throw new NotFoundHttpException();
        }
        $schoolClassName = $schoolClass->term->name . ':' . $schoolClass->name;

        // roleからコードへの変換
        if ($role !== null && !isset(self::ROLE_TABLE[$role])) {
            // 対応してないroleの場合は空を返す
            return [
                'id' => sprintf('https://%s/%s', $request->hostName, $request->pathInfo),
                'context' => [
                    'id' => $schoolClass->uuid,
                    'label' => $schoolClassName,
                    'title' => $schoolClassName,
                ],
                'members' => [],
            ];
        }
        $permissionCode = self::ROLE_TABLE[$role] ?? null;

        // アプリの取得
        $application = Application::findOne($applicationUuid);
        if (!$application) {
            throw new NotFoundHttpException();
        }
        $lti13Param = $application->applicationUrl->lti13Param;

        // ユーザー検索
        // 後続の処理でクラスで絞り込んだ情報が必要なため、belongを基点にする
        $query = Belong::find()
            ->joinWith('user')
            ->joinWith('role')
            ->andFilterWhere([
                User::tableName() . '.is_deleted' => 0,
                Belong::tableName() . '.school_class_uuid' => $schoolClassUuid,
                Role::tableName() . '.permission_code' => $permissionCode ?? array_keys(self::CODE_TABLE),
            ])
            ->orderBy([User::tableName() . '.created_at' => SORT_ASC]);

        $dataProvider = new ActiveDataProvider([
            'query' => $query,
            'pagination' => [
                'pageSizeParam' => 'limit',
            ],
        ]);

        $members = array_map(fn(Belong $belong) => [
            'status' => 'Active',
            'name' => $belong->user->last_name . ' ' . $belong->user->first_name,
            'picture' => '',
            'given_name' => $belong->user->first_name,
            'family_name' => $belong->user->last_name,
            'middle_name' => '',
            'email' => $belong->user->login_id,
            'user_id' => $lti13Param->login_hint === '{{LGATE_USER_UUID}}' ? $belong->user->uuid : $belong->user->login_id,
            'lis_person_sourcedid' => '',
            'roles' => self::CODE_TABLE[$belong->role->permission_code],
        ], $dataProvider->models);

        $links = $dataProvider->pagination->links;
        if (isset($links['next'])) {
            Yii::$app->response->headers->add('Link', sprintf('<https://%s%s>; rel="next"', $request->hostName, $links['next']));
        }

        return [
            'id' => sprintf('https://%s/%s', $request->hostName, $request->pathInfo),
            'context' => [
                'id' => $schoolClass->uuid,
                'label' => $schoolClassName,
                'title' => $schoolClassName,
            ],
            'members' => $members,
        ];
    }
}