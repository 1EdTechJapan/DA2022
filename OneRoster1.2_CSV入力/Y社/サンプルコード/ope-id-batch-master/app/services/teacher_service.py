# coding: utf-8
# 　新規追加
from common.base_service import BaseService
from common.config import csv_bulk_setting


class TeacherService(BaseService):
    """
    教員情報を扱うサービス
    """

    def set_rule(self, teacher_dict, operation_type):
        """教員情報のルールを適用する

        Parameters
        ----------
        self : para
        teacher_dict : dict
            教員情報
        operation_type : dict
            操作区分

        Returns
        -------
        なし
        """
        numeric_rules = csv_bulk_setting.numeric_rules[operation_type]
        list_rules = csv_bulk_setting.list_rules[operation_type]
        list_splitter = csv_bulk_setting.list_splitter
        # 数値型変換ルールの適用
        for numeric_rule in numeric_rules:
            teacher_dict[numeric_rule] = self.to_int_without_exception(
                teacher_dict[numeric_rule]
            )
        # 配列型変換ルールの適用
        for list_rule in list_rules:
            if teacher_dict.get(list_rule):
                teacher_dict[list_rule] = teacher_dict[list_rule].split(
                    list_splitter
                )
            else:
                teacher_dict[list_rule] = []
        return teacher_dict

    def check_master_code_integrity(self, teacher_dict, master_codes, error_messages):
        """教員一括登録データとマスタとの整合性をチェックする

        本モジュール（上述のコード）に依存したメソッドです
        sonar cube対策のため切り離しました。
        登録、更新間での共有は可能です。

        Parameters
        ----------
        teacher_dict : dict
            CSV1行のユーザデータ
        master_codes : dict
            本モジュールで比較に使われるマスタコード
        error_messages : list
            本モジュールで使われるエラーメッセージストック変数
        """
        # 学年コードの存在チェック
        grade_code = teacher_dict.get("grade_code", "")
        if (
            "学年コード" not in "".join(error_messages)
            and grade_code != ""
            and grade_code not in [grade.grade_code for grade in master_codes["grades"]]
        ):
            error_messages.append(
                "学年コード<{}>は登録されていません".format(grade_code)
            )
        # 組コードの存在チェック
        class_code = teacher_dict.get("class_code", "")
        if (
            "組コード" not in "".join(error_messages)
            and class_code != ""
            and class_code not in [clas.class_code for clas in master_codes["classes"]]
        ):
            error_messages.append(
                "組コード<{}>は登録されていません".format(class_code)
            )
        # 教科コードの存在チェック
        subject_code = teacher_dict.get("subject_code", "")
        for s_code in subject_code.split(","):
            if (
                "教科コード" not in "".join(error_messages)
                and s_code != ""
                and s_code not in [subject.subject_code for subject in master_codes["subjects"]]
            ):
                error_messages.append(
                    "教科コード<{}>は登録されていません".format(s_code)
                )

        return