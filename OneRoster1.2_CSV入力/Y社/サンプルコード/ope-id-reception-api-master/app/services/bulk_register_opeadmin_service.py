import logging
from common.config import csv_bulk_setting
from common.config.static_code import APPLICATION_ID
from common.environment_service import EnvironmentService
from common.master_entities.environment import Environment
from common.base_service import BaseService
from common.config.static_code import ENVIRONMENT_NAME

logger = logging.getLogger()


class BulkRegisterOpeadminService(BaseService):
    """OPE管理者一括登録のサービス
    """

    def processing_insert_admin(self, admin_dict, google_cooperation_flag):
        """OPE管理者一括登録、受付後段CSVデータを登録可能なデータに変換にする

        CSV1行の処理をハンドラーから任される

        Parameters
        ----------
        admin_dict : dict
            OPE管理者情報
        google_cooperation_flag: str
            Google連携有無フラグ

        Returns
        -------
        admin_dict : dict
            変換後のOPE管理者情報
        """
        # 各ルールの取得
        operation_type = "admin11"
        numeric_rules = csv_bulk_setting.numeric_rules.get(operation_type, [])
        list_rules = csv_bulk_setting.list_rules.get(operation_type, [])
        list_splitter = csv_bulk_setting.list_splitter
        # 数値型変換ルールの適用
        for numeric_rule in numeric_rules:
            admin_dict[numeric_rule] = self.to_int_without_exception(
                admin_dict[numeric_rule]
            )
        # 配列型変換ルールの適用
        for list_rule in list_rules:
            if admin_dict.get(list_rule):
                # 重複排除list(set(data))を行っています
                # 並び替え昇順 sorted()を行っています
                admin_dict[list_rule] = sorted(list(
                    set(admin_dict[list_rule].split(list_splitter))
                ))
            else:
                admin_dict[list_rule] = []
        # 教育委員会がGoogleアカウント作成しない場合は、各ユーザーのGoogleアカウント作成有無フラグを0に書き換える
        if google_cooperation_flag == 0:
            admin_dict["relationgg"] = 0

        return admin_dict

    def processing_update_admin(self, admin_dict, google_cooperation_flag):
        """OPE管理者一括更新、受付後段CSVを登録可能な変換にする

        CSV1行の処理をハンドラーから任される

        Parameters
        ----------
        admin_dict : dict
            OPE管理者情報
        google_cooperation_flag: int
            Google連携有無フラグ

        Returns
        -------
        admin_dict : dict
            変換後のOPE管理者情報
        """
        log_admin_dict = admin_dict.copy()
        log_admin_dict = self.delete_key(log_admin_dict['user'])
        self.log_info("受付前段CSVデータ変換 , Operator : -" +
                      f" , Input : {log_admin_dict}")
        operation_type = "admin12"
        numeric_rules = csv_bulk_setting.numeric_rules.get(operation_type, [])
        list_rules = csv_bulk_setting.list_rules.get(operation_type, [])
        list_splitter = csv_bulk_setting.list_splitter
        # 数値型変換ルールの適用
        for numeric_rule in numeric_rules:
            admin_dict["user"][numeric_rule] = self.to_int_without_exception(
                admin_dict["user"][numeric_rule]
            )
        # 配列型変換ルールの適用
        for list_rule in list_rules:
            if admin_dict["user"].get(list_rule):
                admin_dict["user"][list_rule] = admin_dict["user"][list_rule].split(
                    list_splitter
                )
            else:
                admin_dict["user"][list_rule] = []
        # 教育委員会がGoogleアカウント作成しない場合は、各ユーザーのGoogleアカウント作成有無フラグを0に書き換える
        if google_cooperation_flag == 0:
            admin_dict["user"]["relationgg"] = 0

        return admin_dict

    def processing_delete_admin(self, admin_dict, google_cooperation_flag):
        """OPE管理者一括削除、受付後段CSVを登録可能な変換にする

        CSV1行の処理をハンドラーから任される

        Parameters
        ----------
        admin_dict : dict
            OPE管理者情報
        google_cooperation_flag: int
            Google連携有無フラグ

        Returns
        -------
        admin_dict : dict
            変換後のOPE管理者情報
        """
        operation_type = "admin13"
        numeric_rules = csv_bulk_setting.numeric_rules.get(operation_type, [])
        list_rules = csv_bulk_setting.list_rules.get(operation_type, [])
        list_splitter = csv_bulk_setting.list_splitter
        # 数値型変換ルールの適用
        for numeric_rule in numeric_rules:
            admin_dict[numeric_rule] = self.to_int_without_exception(
                admin_dict[numeric_rule]
            )
        # 配列型変換ルールの適用
        for list_rule in list_rules:
            if admin_dict.get(list_rule):
                admin_dict[list_rule] = admin_dict[list_rule].split(
                    list_splitter
                )
            else:
                admin_dict[list_rule] = []
        # 教育委員会がGoogleアカウント作成しない場合は、各ユーザーのGoogleアカウント作成有無フラグを0に書き換える
        if google_cooperation_flag == 0:
            admin_dict["relationgg"] = 0

        return admin_dict
