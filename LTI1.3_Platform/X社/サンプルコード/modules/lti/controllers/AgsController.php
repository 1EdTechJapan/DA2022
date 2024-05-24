<?php

namespace app\modules\lti\controllers;

use app\models\infrastructures\Tenant;
use yii\web\Controller;
use Yii;
use app\modules\lti\models\Score;
use yii\web\BadRequestHttpException;
use yii\web\NotFoundHttpException;
use app\modules\school\models\repositories\ExamResult;
use app\modules\school\models\repositories\ExamResultHistory;
use yii\web\ServerErrorHttpException;
use Carbon\Carbon;
use app\models\infrastructures\ControlExamResult;
use app\models\infrastructures\ControlExamResultHistory;

class AgsController extends Controller
{
    public $layout = false;
    public $enableCsrfValidation  = false;

    public function actionOutcome(int $tenantId, string $uuid)
    {
        // TODO: トークンの検証

        // 結果のパースとチェック
        $score = new Score();
        if (!$score->load($this->request->post()) || !$score->validate()) {
            Yii::error('AGS結果パースエラー');
            Yii::error($score->errors);
            throw new BadRequestHttpException(print_r($score->errors, true));
        }
        // テナントの取得
        /** @var Tenant|null */
        $tenant = Tenant::findIsActive($tenantId)->one();
        if (!$tenant) {
            throw new NotFoundHttpException('Tenant not found.');
        }
        Yii::$app->db->tablePrefix = $tenant->tablePrefix;

        $result = ExamResult::findOne($uuid);
        if (!$result) {
            throw new NotFoundHttpException('Result not found.');
        }

        // TODO: 結果のチェック（時間とか）

        // 結果の書き込み
        $history = new ExamResultHistory();
        $history->exam_result_uuid = $result->uuid;
        $history->score = $score->scoreGiven;
        $history->max_score = $score->scoreMaximum;
        $history->activity_progress = $score->activityProgress;
        $history->grading_progress = $score->gradingProgress;
        $history->ags_timestamp = $score->timestamp;
        // timestampのパース
        // MySQL 8.0.19以降なら直接INSERT出来るが、Azureは8.0.15なのでPHP側でパースする必要がある
        $carbon = new Carbon($score->timestamp);
        $carbon->setTimezone('UTC');
        $history->ags_timestamp = $carbon->format('Y-m-d H:i:s.u');
        if (!$history->save()) {
            Yii::error('AGS結果保存エラー');
            Yii::error($history->errors);
            throw new ServerErrorHttpException(print_r($history->errors, true));
        }

        return '';
    }

    public function actionControlOutcome(int $tenantId, string $uuid)
    {
        // 結果のパースとチェック
        $score = new Score();
        if (!$score->load($this->request->post()) || !$score->validate()) {
            Yii::error('AGS結果パースエラー');
            Yii::error($score->errors);
            throw new BadRequestHttpException(print_r($score->errors, true));
        }
        // テナントの取得
        /** @var Tenant|null */
        $tenant = Tenant::findIsActive($tenantId)->one();
        if (!$tenant) {
            throw new NotFoundHttpException('Tenant not found.');
        }
        Yii::$app->db->tablePrefix = $tenant->tablePrefix;

        $result = ControlExamResult::findOne($uuid);
        if (!$result) {
            throw new NotFoundHttpException('Result not found.');
        }

        // 結果の書き込み
        $history = new ControlExamResultHistory();
        $history->exam_result_uuid = $result->uuid;
        $history->score = $score->scoreGiven;
        $history->max_score = $score->scoreMaximum;
        $history->activity_progress = $score->activityProgress;
        $history->grading_progress = $score->gradingProgress;
        $history->ags_timestamp = $score->timestamp;
        // timestampのパース
        // MySQL 8.0.19以降なら直接INSERT出来るが、Azureは8.0.15なのでPHP側でパースする必要がある
        $carbon = new Carbon($score->timestamp);
        $carbon->setTimezone('UTC');
        $history->ags_timestamp = $carbon->format('Y-m-d H:i:s.u');
        if (!$history->save()) {
            Yii::error('AGS結果保存エラー');
            Yii::error($history->errors);
            throw new ServerErrorHttpException(print_r($history->errors, true));
        }

        return '';
    }
}