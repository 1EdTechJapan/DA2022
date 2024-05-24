<?php

use yii\web\Request;
use yii\web\JsonParser;

return [
    'id'                  => 'yii2-lti',
    'controllerNamespace' => 'app\modules\lti\controllers',
    'components'          => [
        'errorHandler' => [
            'class'       => 'yii\web\ErrorHandler',
            'errorAction' => 'default/error',
        ],
        'request' => [
            'class' => Request::class,
            // HTTPエラーをスローした時に怒られるので無効にしておく
            'enableCookieValidation' => false,
            'parsers' => [
                'application/vnd.ims.lis.v1.score+json' => JsonParser::class,
            ],
        ],
    ],
];