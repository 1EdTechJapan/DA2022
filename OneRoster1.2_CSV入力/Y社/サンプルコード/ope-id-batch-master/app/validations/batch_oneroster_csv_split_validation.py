# coding: utf-8
# 　新規追加
"""
cerberus OneRosterCSV入力バッチのバリデーションスキーマ
"""
# OneRosterCSV入力バッチバリデーションスキーマ
batch_request_param = {
    "s3_file_key": {
        "type": "string",
        "required": True,
        "empty": False
    }
}
batch_user_info_file_name = {
    "s3_file_key": {
        "type": "string",
        "required": True,
        "empty": False,
        "regex": "^RO_[0-9]{8}_[a-zA-Z0-9]+.zip"
    }
}
