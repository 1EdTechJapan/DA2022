# coding: utf-8
# 　新規追加
import json
import os
import time
from common.base_model import BaseModel
from common.config import ldap
from common.config import static_code as STATIC_CODE

from app.entities.user import User
from app.entities.oneroster_user import Oneroster_user


class UserModel(BaseModel):
    """ユーザ（OPE管理者、教員、児童生徒）にアクセスするモデル(DAO)

    Attributes
    ----------
    ldap_access_object : LdapAccessObject
        LDAP接続クラス
    """

    def __init__(self, ldap_access_object):
        super().__init__()
        self.ldap_access_object = ldap_access_object
		# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
        self.is_retry = False
		# ↑ここまで

    def select(
            self,
            attributes,
            dn_condition,
            entity_model,
            filter_condition=None,
            specify_filters=[],
    ):
        """
        LDAPからデータを検索する

        Parameters
        ----------
        attributes : list[str]
            LDAPから取得する列名(エンティティ列名)
        dn_condition : User
            検索ベースを指定するためのUserエンティティ
        entity_model : Entity（クラス）
            返却時に変換対象となるEntity
        filter_condition : User
            単純にand条件で取得する場合に指定
        specify_filters : list[str]
            直接フィルターを指定する場合に指定

        Returns
        -------
        searched_users : list
            LDAPから取得したUser情報（複数）
        """
        self.log_info("### START USER DB MODEL SELECT ###")

        # attributeをLDAPの名称に変換する
        convert_rule = ldap.LDAP_ATTRIBUTE_NAME_CONVERT_RULE
        converted_attributes = [
            convert_rule[attribute]
            for attribute in attributes
            if convert_rule.get(attribute)  # 変換表にないものは除外する
        ]
        # 単純and検索のエンティティ列名をLDAP列名に変換する
        converted_conditions = None
        if filter_condition:
            converted_conditions = {
                convert_rule[key]: val
                for key, val in (
                    filter_condition.get_dict_below_userid().items()
                )
                if convert_rule.get(key)  # 変換表にないものは除外する
            }
        # specify_filtersのエンティティ列名をLDAP列名に変換する
        converted_specify_filters = [
            val.format(**convert_rule) for val in specify_filters
        ]
        # DNを生成
        converted_dn_dict = self.convert_user_to_ldap(
            dn_condition.get_dict_search_dn()
        )
        search_base_dn = self.generate_dn(converted_dn_dict)
        # LDAP検索フィルターを単純AND+個別指定で生成
        ldap_filter = self.generate_ldap_simple_search_filter(
            converted_conditions, specify_filters=converted_specify_filters
        )

        # リトライ回数は環境変数.リトライ回数とする。
        retry_count = int(os.environ.get("LDAP_RETRY_COUNT"))

        for i in range(retry_count):
            try:
                # LDAPへの接続開始を行う
                self.ldap_access_object.connect()

                # LDAPからデータを検索する
                ret = self.ldap_access_object.select(
                    search_base_dn, ldap_filter, converted_attributes
                )

                # ldap3はサーバー側エラーでExceptionを返さないので、失敗の場合
                if ret["is_success"] is False:
                    self.throw_error("ID_E_0003", None, str(ret["result"]))

                # 正常のため、ループを終了する
                break
            except Exception as exception:
                # 異常発生した場合
                if (i + 1) < retry_count:
                    # RetryErrorを出力する
                    self.log_info(f"RetryError : Retry processing(select) for the {str(i + 1)} time.")
                    # 次の試行まで待つ
                    time.sleep(int(os.environ.get("LDAP_RETRY_INTERVAL")))
                    continue
                else:
                    # 例外情報を出力する
                    self.log_error("exception :" + str(exception))
                    raise exception
            finally:
                # LDAPへの接続終了を行う
                self.ldap_access_object.close()

        # LDAP取得データをエンティティのリストに変換する
        searched_users = self.convert_data_from_ldap_records(
            ret["records"],
			# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
            User,
            listed_rule=ldap.LDAP_ATTRIBUTE_LISTED_RULES_ATT,
            numeric_rule=ldap.LDAP_ATTRIBUTE_NUMERIC_RULES_ATT,
            recognize_str_rule=ldap.LDAP_ATTRIBUTE_RECOGNIZE_STR_RULES_ATT,
        )

        self.log_info("### END USER DB MODEL SELECT ###")
        # エンティティに格納したデータ（複数）を返す
        return searched_users

    def select_no_retry(
            self,
            attributes,
            dn_condition,
            filter_condition=None,
            specify_filters=[],
    ):
        """
        LDAPからデータを検索する

        Parameters
        ----------
        attributes : list[str]
            LDAPから取得する列名(エンティティ列名)
        dn_condition : User
            検索ベースを指定するためのUserエンティティ
        filter_condition : User
            単純にand条件で取得する場合に指定
        specify_filters : list[str]
            直接フィルターを指定する場合に指定

        Returns
        -------
        searched_Users : list
            LDAPから取得したUser情報（複数）
        """
        self.log_info("### START USER DB MODEL SEARCH ###")
        self.is_retry = False
        # attributeをLDAPの名称に変換する
        convert_rule = ldap.LDAP_ATTRIBUTE_NAME_CONVERT_RULE
        converted_attributes = [
            convert_rule[attribute]
            for attribute in attributes
            if convert_rule.get(attribute)  # 変換表にないものは除外する
        ]
        # 単純and検索のエンティティ列名をLDAP列名に変換する
        converted_conditions = None
        if filter_condition:
            converted_conditions = {
                convert_rule[key]: val
                for key, val in (
                    filter_condition.get_dict_below_userid().items()
                )
                if convert_rule.get(key)  # 変換表にないものは除外する
            }
        # specify_filtersのエンティティ列名をLDAP列名に変換する
        converted_specify_filters = [
            val.format(**convert_rule) for val in specify_filters
        ]
        # DNを生成
        converted_dn_dict = self.convert_user_to_ldap(
            dn_condition.get_dict_search_dn()
        )
        search_base_dn = self.generate_dn(converted_dn_dict)
        # LDAP検索フィルターを単純AND+個別指定で生成
        ldap_filter = self.generate_ldap_simple_search_filter(
            converted_conditions, specify_filters=converted_specify_filters
        )
        try:
            # 検索を実行
            ret = self.ldap_access_object.select(
                search_base_dn, ldap_filter, converted_attributes
            )
            # ldap3はサーバー側エラーでExceptionを返さないので、失敗の場合
            if ret["is_success"] is False:
                if ret["result"]["result"] == STATIC_CODE.LDAP_NO_SUCH_OBJECT:
                    # DNが見つからない場合(ou不正)
                    self.throw_error(
                        "ID_E_0002",
                        None,
                        inner_message=str(ret["result"]),
                        format_message={"organization_name": ["Invalid value"]},
                    )
                else:
                    self.is_retry = True
                    self.throw_error("ID_E_0003", None, str(ret["result"]))

            # LDAP取得データをエンティティのリストに変換する
            searched_users = self.convert_data_from_ldap_records(
                ret["records"],
                User,
                listed_rule=ldap.LDAP_ATTRIBUTE_LISTED_RULES_ATT,
                numeric_rule=ldap.LDAP_ATTRIBUTE_NUMERIC_RULES_ATT,
                recognize_str_rule=ldap.LDAP_ATTRIBUTE_RECOGNIZE_STR_RULES_ATT,
            )
        except Exception as exception:
            self.is_retry = True
            self.throw_error("ID_E_0003", exception)

        self.log_info("### END USER DB MODEL INSERT ###")
        # エンティティに格納したデータ（複数）を返す
        return searched_users

    def bulk_delete_select(
            self,
            attributes,
            dn_condition,
            filter_condition=None,
            specify_filters=[],
    ):
        """
        LDAPからデータを検索する

        Parameters
        ----------
        attributes : list[str]
            LDAPから取得する列名(エンティティ列名)
        dn_condition : User
            検索ベースを指定するためのUserエンティティ
        filter_condition : User
            単純にand条件で取得する場合に指定
        specify_filters : list[str]
            直接フィルターを指定する場合に指定

        Returns
        -------
        searched_users : list
            LDAPから取得したUser情報（複数）
        """
        self.log_info("### START USER DB MODEL SELECT ###")

        # attributeをLDAPの名称に変換する
        convert_rule = ldap.LDAP_ATTRIBUTE_NAME_CONVERT_RULE
        converted_attributes = [
            convert_rule[attribute]
            for attribute in attributes
            if convert_rule.get(attribute)  # 変換表にないものは除外する
        ]
        # 単純and検索のエンティティ列名をLDAP列名に変換する
        converted_conditions = None
        if filter_condition:
            converted_conditions = {
                convert_rule[key]: val
                for key, val in (
                    filter_condition.get_dict_below_userid().items()
                )
                if convert_rule.get(key)  # 変換表にないものは除外する
            }
        # specify_filtersのエンティティ列名をLDAP列名に変換する
        converted_specify_filters = [
            val.format(**convert_rule) for val in specify_filters
        ]
        # DNを生成
        converted_dn_dict = self.convert_user_to_ldap(
            dn_condition.get_dict_search_dn()
        )
        search_base_dn = self.generate_dn(converted_dn_dict)
        # LDAP検索フィルターを単純AND+個別指定で生成
        ldap_filter = self.generate_ldap_simple_search_filter(
            converted_conditions, specify_filters=converted_specify_filters
        )

        # リトライ回数は環境変数.リトライ回数とする。
        retry_count = int(os.environ.get("LDAP_RETRY_COUNT"))

        for i in range(retry_count):
            try:
                # LDAPへの接続開始を行う
                self.ldap_access_object.connect()

                # LDAPからデータを検索する
                ret = self.ldap_access_object.select(
                    search_base_dn, ldap_filter, converted_attributes
                )

                # ldap3はサーバー側エラーでExceptionを返さないので、失敗の場合
                if ret["is_success"] is False:
                    if ret["result"]["result"] == STATIC_CODE.LDAP_NO_SUCH_OBJECT:
                        # DNが見つからない場合(ou不正)
                        self.throw_error(
                            "ID_E_0002",
                            None,
                            inner_message=str(ret["result"]),
                            format_message={"organization_name": ["Invalid value"]},
                        )
                    else:
                        self.throw_error("ID_E_0003", None, str(ret["result"]))

                # 正常のため、ループを終了する
                break
            except Exception as exception:
                # 異常発生した場合
                if (i + 1) < retry_count:
                    # RetryErrorを出力する
                    self.log_info(f"RetryError : Retry processing(delete_ldap_select) for the {str(i + 1)} time.")
                    # 次の試行まで待つ
                    time.sleep(int(os.environ.get("LDAP_RETRY_INTERVAL")))
                    continue
                else:
                    # 例外情報を出力する
                    self.log_error("exception :" + str(exception))
                    raise exception
            finally:
                # LDAPへの接続終了を行う
                self.ldap_access_object.close()

        # LDAP取得データをエンティティのリストに変換する
        searched_users = self.convert_data_from_ldap_records(
            ret["records"],
            Oneroster_user,
            listed_rule=ldap.LDAP_ATTRIBUTE_LISTED_RULES_ATT,
            numeric_rule=ldap.LDAP_ATTRIBUTE_NUMERIC_RULES_ATT,
            recognize_str_rule=ldap.LDAP_ATTRIBUTE_RECOGNIZE_STR_RULES_ATT,
        )
		# ↑ここまで
        self.log_info("### END USER DB MODEL SELECT ###")
        # エンティティに格納したデータ（複数）を返す
        return searched_users
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    def get_organization_names(self, system_organization_name, ldap_access_object, search_filter):
        """
        LDAPからOUの一覧を取得する

        Parameters
        ----------
        system_organization_name : str
            ouの所属するo名
        ldap_access_object : LdapAccessObject
        search_filter : list
            検索条件

        Returns
        -------
        ret : list
            organization_nameの一覧
        """
        self.log_info(f"### LDAP SEARCH BASE= {system_organization_name}")
        search_base_dn = self.generate_dn({"o": system_organization_name})
        ldap_filter = "(uid=*)"
        ldap_filter = f'{ldap_filter}({")(".join(search_filter)})'
        ldap_filter = "(&" + ldap_filter + ")"
        ret = ldap_access_object.select(search_base_dn, ldap_filter, ["ou"])
        # ldap3はサーバー側エラーでExceptionを返さないので、検索失敗の場合
        if ret["is_success"] is False:
            self.throw_error("ID_E_0003", None, str(ret["result"]))

        # organization_name部分のみを抜き出し
        organization_names = []
        for rec in ret["records"]:
            if rec["attributes"]["ou"] and \
                    len(rec["attributes"]["ou"]) > 0 and \
                    rec["attributes"]["ou"][0] not in organization_names:
                organization_names.append(rec["attributes"]["ou"][0])

        return organization_names
		# ↑ここまで
