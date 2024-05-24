<?php

namespace app\modules\lti;

use app\modules\ReconfigureTrait;

/**
 * Class Module
 *
 * @package app\modules\lti
 */
class Module extends \yii\base\Module
{
    use ReconfigureTrait;

    public $controllerNamespace = 'app\modules\lti\controllers';

    public function init()
    {
        parent::init();

        $this->reconfigure(require __DIR__ . '/config/lti.php');
    }
}
