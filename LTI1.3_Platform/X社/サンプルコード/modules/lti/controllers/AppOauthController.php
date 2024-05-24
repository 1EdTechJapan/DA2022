<?php

namespace app\modules\lti\controllers;

use app\models\infrastructures\ManageApplicationUrl;
use yii\web\Controller;
use Yii;
use Firebase\JWT\JWT;
use Firebase\JWT\JWK;
use yii\db\Expression;
use yii\web\BadRequestHttpException;
use yii\web\Response;
use app\models\infrastructures\Tenant;
use app\models\infrastructures\ApplicationUrl;

class AppOauthController extends Controller
{
    public $layout = false;
    public $enableCsrfValidation  = false;

    public function actionToken(?string $tenantUuid = null, ?string $clientId = null)
    {
        Yii::$app->response->format = Response::FORMAT_JSON;

        $post = $this->request->post();

        // JWTのデコード
        [, $jwtBody, ] = explode('.', $post['client_assertion']);
        $jwt = JWT::jsonDecode(JWT::urlsafeB64Decode($jwtBody));
        if (!isset($jwt->iss)) {
            // Issuerが無い
            throw new BadRequestHttpException('No Iss');
        }
        if (($jwt->exp ?? 0) < time()) {
            // JWT期限切れ
            throw new BadRequestHttpException('Expired');
        }

        // client_idからパラメータ情報を取得
        if ($tenantUuid === null) {
            // 旧仕様（テナントが取得出来ないのでテンプレートから取得）
            /** @var ManageApplicationUrl|null */
            $applicationUrl = ManageApplicationUrl::find()->andWhere([
                '=', new Expression('param_json->"$.client_id"'), $jwt->iss,
            ])->one();
        } else {
            // テナントが特定出来るので、テナントを固定して取得
            $tenant = Tenant::findOne(['uuid' => $tenantUuid]);
            Yii::$app->db->tablePrefix = $tenant->tablePrefix;
            /** @var ApplicationUrl|null */
            $applicationUrl = ApplicationUrl::find()->andWhere([
                '=', new Expression('param_json->"$.client_id"'), $clientId ?? $jwt->iss,
            ])->one();
        }
        if (!$applicationUrl) {
            throw new BadRequestHttpException('No Client');
        }

        // JWT署名検証
        $jwksJson = json_decode(file_get_contents($applicationUrl->lti13Param->public_keyset), true);
        $jwks = JWK::parseKeySet($jwksJson);
        $jwt = JWT::decode($post['client_assertion'], $jwks, [
            'HS256', 'HS384', 'HS512',
            'RS256', 'RS384', 'RS512',
            'ES256', 'ES384',
        ]);

        // token発行
        $keyfile = Yii::getAlias('@app/../keys/l-gate.pem');
        $privateKey = file_get_contents($keyfile);
        $expire = time() + 3600;
        $payload = [
            'iss' => $jwt->iss,
            'exp' => $expire,
        ];
        $token = JWT::encode($payload, $privateKey, 'HS256');

        return [
            'access_token' => $token,
            'token_type' => 'Bearer',
            'expires_in' => $expire,
        ];
    }
}