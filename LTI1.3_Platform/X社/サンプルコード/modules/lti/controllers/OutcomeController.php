<?php

namespace app\modules\lti\controllers;

use app\components\LtiHelper;
use app\modules\admin\models\repositories\Context;
use Yii;
use yii\web\BadRequestHttpException;
use app\models\infrastructures\Result;
use app\models\infrastructures\ResultHistory;
use yii\web\ServerErrorHttpException;
use yii\web\UnauthorizedHttpException;
use yii\web\Response;
use app\components\CommonController;

class OutcomeController extends CommonController
{
    public function init()
    {
        parent::init();

        $response         = Yii::$app->response;
        $response->format = Response::FORMAT_RAW;
        $response->off(Response::EVENT_BEFORE_SEND);    // API用のイベントを削除しておく
        // レイアウト無し
        $this->layout = false;
        // CSRFオフ
        $this->enableCsrfValidation = false;
    }

    public function actionIndex()
    {
        $params = Yii::$app->request->get();
        $body = Yii::$app->request->rawBody;
        // bodyHashの検証
        $hash = base64_encode(sha1($body, true));
        if ($hash !== $params['oauth_body_hash']) {
            throw new BadRequestHttpException();
        }

        // 結果XMLのパース
        $xml = simplexml_load_string($body);
        if (!$xml) {
            throw new BadRequestHttpException('Invalid XML');
        }
        $resultRecord = $xml->imsx_POXBody->replaceResultRequest->resultRecord ?? null;
        if (!$resultRecord) {
            throw new BadRequestHttpException('"resultRecord" element not found');
        }
        $sourcedId = $resultRecord->sourcedGUID->sourcedId ?? null;
        if (!$sourcedId) {
            throw new BadRequestHttpException('"sourcedId" element not found');
        }
        $score = $resultRecord->result->resultScore->textString ?? null;
        if (!$score) {
            throw new BadRequestHttpException('"resultScore" element not found');
        }

        // 結果レコードの取得
        $result = Result::findOne($sourcedId);
        if (!$result) {
            throw new BadRequestHttpException('Invalid sourcedId');
        }

        // signatureの検証
        $ltiTool = $result->assessmentResourceLink->resourceLinkTemplate->ltiTool;
        $outcomeUrl = sprintf('https://%s/lti/outcome', Yii::$app->request->hostName);
        $oauthSignature = $params['oauth_signature'];
        unset($params['oauth_signature']);
        $signature = LtiHelper::calcSignature($outcomeUrl, $params, $ltiTool->secret);
        if ($signature !== $oauthSignature) {
            throw new UnauthorizedHttpException();
        }
        // 結果履歴の保存
        $resultHistory = new ResultHistory();
        $resultHistory->result_uuid = $result->uuid;
        $resultHistory->score = $score;
        if (!$resultHistory->save()) {
            Yii::error($resultHistory->errors);
            throw new ServerErrorHttpException();
        }
        $result->assessmentResourceLink->result_exists = true;
        if (!$result->assessmentResourceLink->save()) {
            Yii::error($result->assessmentResourceLink->errors);
            throw new ServerErrorHttpException();
        }
        $context = Context::findOne(['uuid' => $result->assessmentResourceLink->context_uuid]);
        $context->result_exists = true;
        if (!$context->save()) {
            Yii::error($context->errors);
            throw new ServerErrorHttpException();
        }
        return 'success';
    }
}