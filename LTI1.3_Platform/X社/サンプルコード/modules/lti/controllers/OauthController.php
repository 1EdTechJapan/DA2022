<?php

namespace app\modules\lti\controllers;

use yii\web\Controller;
use Yii;
use Firebase\JWT\JWT;
use Firebase\JWT\JWK;
use yii\web\Response;

class OauthController extends Controller
{
    public $layout = false;
    public $enableCsrfValidation  = false;

    public function actionToken()
    {
        Yii::$app->response->format = Response::FORMAT_JSON;

        $post = $this->request->post();

        $params = Yii::$app->params['lti13tool'];
        $jwksJson = json_decode(file_get_contents($params['jwksUrl']), true);
        $jwks = JWK::parseKeySet($jwksJson);

        $jwt = JWT::decode($post['client_assertion'], $jwks, ['RS256']);

        return [
            // TODO: token発行処理の実装
            'access_token' => uniqid(),
            'token_type' => 'Bearer',
            'expires_in' => time() + 3600,
        ];
    }
}