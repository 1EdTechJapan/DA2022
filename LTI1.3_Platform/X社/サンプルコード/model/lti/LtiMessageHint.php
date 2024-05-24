<?php

namespace app\models\lti;

class LtiMessageHint
{
    public const SECRET = '5XhQ$Hi!#:0[F{~!(3d,*FvOxV/z#pbs';

    public const TYPE_DEEP_LINKING = 1;
    public const TYPE_RESOURCE_LINK = 2;
    public const TYPE_RESOURCE_LINK_RESULT = 3;

    public int $type;
    public int $tenantId;
    public string $hostInfo;
    public string $userUuid;
    public string $examCategoryUuid;
    public string $examCategoryTitle;
    public ?string $examUuid;
    public ?string $examTitle;
    public ?string $examResultUuid;
    public string $schoolCode;
    public bool $isControl = false;         // 教育委員会からかどうか

    public static function createFromArray(array $src): self
    {
        $self = new self();
        $self->type = $src['type'] ?? 0;
        $self->tenantId = $src['tenantId'] ?? 0;
        $self->hostInfo = $src['hostInfo'] ?? '';
        $self->userUuid = $src['userUuid'] ?? '';
        $self->examCategoryUuid = $src['examCategoryUuid'] ?? '';
        $self->examCategoryTitle = $src['examCategoryTitle'] ?? '';
        $self->examUuid = $src['examUuid'] ?? null;
        $self->examTitle = $src['examTitle'] ?? null;
        $self->examResultUuid = $src['examResultUuid'] ?? null;
        $self->schoolCode = $src['schoolCode'] ?? '';
        $self->isControl = $src['isControl'] ?? false;

        return $self;
    }

    public function isDeepLinking(): int
    {
        return $this->type === self::TYPE_DEEP_LINKING;
    }

    public function isResourceLink(): int
    {
        return $this->type === self::TYPE_RESOURCE_LINK;
    }

    public function isResourceLinkResult(): int
    {
        return $this->type === self::TYPE_RESOURCE_LINK_RESULT;
    }
}