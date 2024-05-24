# -*- coding: utf-8 -*-

class ErrorCode():
    def get_error_reason(self, code):
        if code not in self.error_string:
            print('This code does not found [%2d]' % code)
            return '不明なコード [%d]' % code
        return self.error_string[code]
    
    # 変換成功
    convert_success = 0
    convert_error = 1

    # CSVファイルの検証エラー

    # onerosterの妥当性検証でのエラー
    not_found_manifest = 101
    invalid_manifest = 102

    error_string = {
        convert_success: '変換に成功しました。',
        convert_error  : '変換に失敗しました。',
        not_found_manifest : 'manifestファイルが見つかりません。',
        invalid_manifest : 'manifestファイルのフォーマットが不正です。',
    }


    