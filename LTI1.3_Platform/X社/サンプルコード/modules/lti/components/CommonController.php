<?php

namespace app\modules\lti\components;

use Yii;
use yii\web\Controller;

class CommonController extends Controller
{
    public function init()
    {
        parent::init();

        Yii::$app->response->headers->set('Content-Language', 'ja-JP');
    }
}