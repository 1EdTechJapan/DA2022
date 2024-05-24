# coding: utf-8
from common import base_validation
"""
cerberus OneRoster Rest Apiバッチのバリデーションスキーマ
"""

export_term = {
    "type": "integer",
    "required": False,
    "empty": True,
    "min": 0,
    "max": 999,
    "regex": "^[0-9]+$",
}
hours_ago = {
    "type": "integer",
    "required": False,
    "empty": True,
    "min": 0,
    "max": 999,
    "regex": "^[0-9]+$",
}
export_type = {
    "type": "string",
    "required": True,
    "empty": False,
    "allowed": ["bulk", "delta"],
}
secret_arn = {
    "type": "string",
    "required": True,
    "empty": False,
}

# バリデーションスキーマ
batch_oneroster_api_validation_request = {
    'system_organization_code': base_validation.system_organization_code,
    'export_type': export_type,
    'export_term': export_term,
    'hours_ago': hours_ago,
    'secret_arn': secret_arn
}
