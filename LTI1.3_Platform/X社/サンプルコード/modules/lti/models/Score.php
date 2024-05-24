<?php

namespace app\modules\lti\models;

use yii\base\Model;

class Score extends Model
{
    public ?string $timestamp = null;
    public ?float $scoreGiven = null;
    public ?int $scoreMaximum = null;
    public ?string $comment = null;
    public ?string $activityProgress = null;
    public ?string $gradingProgress = null;
    public ?string $userId = null;

    public function formName()
    {
        return '';
    }

    public function rules()
    {
        return [
            [['timestamp', 'activityProgress', 'gradingProgress', 'userId'], 'required'],
            [['scoreGiven'], 'double'],
            [['scoreMaximum'], 'integer'],
            [['timestamp', 'comment', 'activityProgress', 'gradingProgress', 'userId'], 'string'],
        ];
    }
}