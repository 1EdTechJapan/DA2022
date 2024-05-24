<?php

namespace app\models\lti;

use Yii;

class LtiAppMessageHint
{
    private const SECRET = '>*[^mhgsfNa(/(WM6MV3]p5R!Ir}fG8isG@iY.:!9t]iTfh';

    public const TYPE_RESOURCE_LINK = 1;

    public int $type;
    public int $tenantId;
    public string $hostInfo;
    public string $belongUuid;
    public string $applicationUuid;
    public string $userRelatedId;       // ユーザー関係のID（現状uuidかlogin_idが入る）

    public static function createFromArray(array $src): self
    {
        $self = new self();
        $self->type = $src['type'] ?? 0;
        $self->tenantId = $src['tenantId'] ?? 0;
        $self->hostInfo = $src['hostInfo'] ?? '';
        $self->belongUuid = $src['belongUuid'] ?? '';
        $self->applicationUuid = $src['applicationUuid'] ?? '';
        $self->userRelatedId = $src['userRelatedId'] ?? '';

        return $self;
    }

    public static function createFromEncodedString(string $data)
    {
        return self::createFromArray(json_decode(Yii::$app->security->decryptByPassword(base64_decode($data), self::SECRET), true));
    }

    public function encode(): string
    {
        return base64_encode(Yii::$app->security->encryptByPassword(json_encode($this), self::SECRET));
    }

    public function isResourceLink(): int
    {
        return $this->type === self::TYPE_RESOURCE_LINK;
    }
}
