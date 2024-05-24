# coding: utf-8
import os
import datetime
import uuid

from app.models.opeadmin_model import OpeadminModel
from app.entities.opeadmin import Opeadmin
from common.environment_service import EnvironmentService
from common.base_service import BaseService
from common.ldap_access_object import LdapAccessObject
from common.helper_encryption import encrypt_aes256
from common.config import ldap
from common.config import static_code as STATIC_CODE
from common.master_entities.environment import Environment
from common.rds_access_object import RdsAccessObject
from common.config.static_code import RDS_TABLE, APPLICATION_ID, ENVIRONMENT_NAME
from common.crud_model import CRUDModel
from common.system_organization_service import SystemOrganizationService

class OpeadminService(BaseService):
    """OPE管理者の参照、登録、削除、更新をするサービス

    Attributes
    ----------
    ldap_access_object : LdapAccessObject
        LDAP接続クラス
    rds_access_object : RdsAccessObject
        RDS接続クラス
    """

    def __init__(self):
        self.ldap_access_object = LdapAccessObject(
            os.environ.get("LDAP_URL"),
            os.environ.get("LDAP_USER"),
            os.environ.get("LDAP_PASSWORD"),
        )
        # 　改修（案件７．メールの一意性チェック）　START
        self.rds_access_object = RdsAccessObject(
            os.environ.get("RDS_RESOURCE_ARN"),
            os.environ.get("RDS_SECRET_ARN"),
            os.environ.get("RDS_DATABASE"),
        )
        # 　改修（案件８．OPE管理者の削除）　START
        self.opeadmin_model = OpeadminModel(self.rds_access_object, self.ldap_access_object)
		# 　改修（案件８．OPE管理者の削除）　END
    	# 　改修（案件７．メールの一意性チェック）　END

        #  新規追加(マルチテナント化対応) START
        self.environment_service = EnvironmentService(self.rds_access_object)
        #  新規追加(マルチテナント化対応) END

    def insert(self, new_opeadmin):
        """
        OPE管理者を追加するサービスメソッド

        Parameters
        ----------
        new_opeadmin : Opeadmin
            LDAPに登録するOpeadmin情報

        Returns
        -------
        inserted_opeadmin : Opeadmin
            LDAPに登録されたOpeadmin情報
        """
        log_new_opeadmin = new_opeadmin.get_dict()
        log_new_opeadmin = self.delete_key(log_new_opeadmin)
        self.log_info("OPE管理者情報登録 サービス 開始 , Operator : -" +
                      f" , Input : {log_new_opeadmin}")
        try:
            self.ldap_access_object.connect()
            # 　新規追加（案件７．メールの一意性チェック）　START
            self.rds_access_object.begin()
            # 　新規追加（案件７．メールの一意性チェック）　END
            # 　改修（マルチテナント化対応）　START
            # TOP組織情報
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            top_organization = system_organization_service.select_top_organization(new_opeadmin.system_organization_code)
            # 組織情報をconfigデータから補完
            new_opeadmin.organization_name = top_organization.school_name
            new_opeadmin.organization_name_ja = (
                top_organization.school_name_ja
            )
            # 　新規追加（文科省標準の学校コード追加）　START
            new_opeadmin.mextOuCode = top_organization.mextOuCode
            # 　新規追加（文科省標準の学校コード追加）　END
            new_opeadmin.organization_type = top_organization.school_type
            # ユーザID自治体内ユニークID重複チェック
            collision_data = self.opeadmin_model.select(
                ["user_id", "persistent_uid"],
                Opeadmin(system_organization_name=new_opeadmin.system_organization_name),
                specify_filters=[
                    "|({user_id}=" + new_opeadmin.user_id + ")"
                    "({persistent_uid}=" + new_opeadmin.persistent_uid + ")"
                ],
            )
            # 　改修（マルチテナント化対応）　END
            if len(collision_data) > 1 or (
                len(collision_data) == 1
                and collision_data[0].user_id == new_opeadmin.user_id
                and collision_data[0].persistent_uid == new_opeadmin.persistent_uid
            ):
                # ユーザIDも自治体内ユニークIDが重複した場合
                # 重複レコード2つ以上、または1つで両方重複しているケース
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message="ユーザID<{}>自治体内ユニークID<{}>がすでに存在しています".format(
                        new_opeadmin.user_id, new_opeadmin.persistent_uid
                    ),
                )
            elif len(collision_data) == 1:
                # ユーザIDまたは自治体内ユニークIDが重複した場合
                # ただし、両方重複しているケースは除く
                if collision_data[0].user_id == new_opeadmin.user_id:
                    # user_idが重複した場合
                    self.throw_error(
                        "ID_E_0020",
                        None,
                        format_message="ユーザID<{}>がすでに存在しています".format(
                            new_opeadmin.user_id
                        ),
                    )
                else:
                    # persistent_uidが重複した場合
                    self.throw_error(
                        "ID_E_0020",
                        None,
                        format_message="自治体内ユニークID<{}>がすでに存在しています".format(
                            new_opeadmin.persistent_uid
                        ),
                    )

            # 　新規追加（ユーザ削除テーブルの自治体内ユニークID重複チェックを追加）　START
            # PIDユニークチェック(ユーザ削除テーブル)
            # 　改修（マルチテナント化対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            dn_condition = Opeadmin(
                system_organization_code=new_opeadmin.system_organization_code,
                persistent_uid=new_opeadmin.persistent_uid,
            )
            ret = crud_model.select_count(
                new_opeadmin.system_organization_code,
                RDS_TABLE.DELETE_USER,
                dn_condition,
                exclusion_where_columns=[
                    "persistent_uid", "limit", "offset"],
                specific_conditions=["persistent_uid=%(persistent_uid)s"],
            )
            # 　改修（マルチテナント化対応）　END
            if ret > 0:
                # persistent_uidが重複した場合
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message="自治体内ユニークID<{}>がすでに存在しています".format(
                        new_opeadmin.persistent_uid
                    ),
                )
            # 　新規追加（ユーザ削除テーブルの自治体内ユニークID重複チェックを追加）　END
            # Persistent_uid useridの重複チェックここまで

            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_opeadmin.relationgg) == 1 or\
                    int(new_opeadmin.relationwin) == 1 or int(new_opeadmin.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Opeadmin(
                    system_organization_name=new_opeadmin.system_organization_name
                )
                search_opeadmin = self.opeadmin_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_opeadmin.mail
                    ],
                )
                if len(search_opeadmin) > 0:
                    self.throw_error(
                        "ID_E_0020",
                        None,
                        format_message="メールアドレス<{}>がすでに存在しています".format(
                            new_opeadmin.mail
                        ),
                    )
            # 　新規追加（案件７．メールの一意性チェック）　END

            # LDAPの日本語属性値、表示名を設定
            new_opeadmin.display_name = (
                f"{new_opeadmin.sur_name}　{new_opeadmin.given_name}"
            )
            # opaqueIDの生成
            # 　改修（マルチテナント化対応）　START
            environments = self.environment_service.select(
                Environment(system_organization_code=new_opeadmin.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            delete_flag=0))
            idp_entityid = self.environment_service.get_environment_value(environments,
                                                                          ENVIRONMENT_NAME.IDP_ENTITYID.value)
            # 　改修（マルチテナント化対応）　END
            new_opeadmin.opaque_id = self.create_opaque_id(
                new_opeadmin.persistent_uid,
                # 　改修（マルチテナント化対応）　START
                # os.environ.get("IDP_ENTITYID"),
                idp_entityid,
                # 　改修（マルチテナント化対応）　END
                os.environ.get("OPAQUE_ID_SALT"),
            )
            # 　新規追加（文科省標準の学校コード追加）　START
            # mextUidを生成
			# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
            # mextUidを生成(OneRoster対応：値がある場合、再採番不要)
            if not new_opeadmin.mextUid:
                new_opeadmin.mextUid = str(uuid.uuid4())
			# ↑ここまで
            # 　新規追加（文科省標準の学校コード追加）　END
            # 登録日付の生成
            new_opeadmin.reg_date = self.create_update_date_str()
            # 更新日付の生成
            new_opeadmin.upd_date = self.create_update_date_str()
            # パスワードの設定
            new_opeadmin.user_password = new_opeadmin.password
            # 　改修（マルチテナント化対応）　START
            windows_cooperation_flag = \
                self.environment_service.get_environment_value(environments,
                                                               ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value)
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                # 平文パスワードを暗号化して設定
                decrypt_key = self.decrypt_message(
                    os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                enc_password = encrypt_aes256(
                    new_opeadmin.password, decrypt_key.encode())
                new_opeadmin.enc_password = enc_password
            # 登録実行
            inserted_opeadmin = self.opeadmin_model.insert(new_opeadmin)
        except Exception as exception:
            raise (exception)
        finally:
            self.ldap_access_object.close()
            # 　新規追加（案件７．メールの一意性チェック）　START
            self.rds_access_object.close()
            # 　新規追加（案件７．メールの一意性チェック）　END

        # OPE管理者登録で返される属性に絞る(inとoutの形式が違うため)
        rule = ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
            STATIC_CODE.LDAP_SEARCH_TYPE.OPEADMIN_LIST
        ]
        keys = inserted_opeadmin.get_dict().keys()
        for key in keys:
            if key not in rule:
                inserted_opeadmin.__dict__[key] = None

        self.log_info(
            "OPE管理者情報コミット , Operator : - , Output : -")
        log_inserted_opeadmin = self.delete_key(inserted_opeadmin.get_dict())
        self.log_info("OPE管理者情報登録 サービス 終了 , Operator : -" +
                      f" , Output : {log_inserted_opeadmin}")

        # このメソッドの返却値は挿入データ
        return inserted_opeadmin

    # 　改修（マルチテナント化対応）　START
    def update_password(self, update_opeadmin, windows_cooperation_flag):
    # 　改修（マルチテナント化対応）　END
        """
        OPE管理者を追加するサービスメソッド

        Parameters
        ----------
        update_opeadmin : Opeadmin
            更新するパスワードが含まれたOpeadmin情報

        Returns
        -------
        ret_opeadmin : Opeadmin
            Windows連携有の場合、更新後のOpeadmin情報を返却
            Windows連携無の場合、Noneを返却
        """
        self.log_info("### START OPEADMIN SERVICE UPDATE PASSWORD ###")
        #  新規追加（案件２１AzureADへパスワードを即時連携） START
        ret_opeadmin = None
        #  新規追加（案件２１AzureADへパスワードを即時連携） END

        # システム付加情報を設定
        # 更新日付の生成
        update_opeadmin.upd_date = self.create_update_date_str()

        # 　改修（マルチテナント化対応）　START
        if windows_cooperation_flag == 1:
            # 　改修（マルチテナント化対応）　END
            # 平文パスワードを暗号化して設定
            decrypt_key = self.decrypt_message(
                os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
            enc_password = encrypt_aes256(
                update_opeadmin.user_password, decrypt_key.encode())
            update_opeadmin.enc_password = enc_password
        try:
            self.ldap_access_object.connect()
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 更新日とWindows連携フラグを取得
                dn_condition = Opeadmin(
                    system_organization_name=update_opeadmin.system_organization_name,
                    organization_name=update_opeadmin.organization_name
                )
                # 　改修（マルチテナント化対応）　END
                searched_opeadmins = self.opeadmin_model.select(
                    ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                        STATIC_CODE.LDAP_SEARCH_TYPE.OPEADMIN_LIST
                    ],
                    dn_condition,
                    specify_filters=["{user_id}=" + update_opeadmin.user_id],
                )
                # 現在の年月日を取得
                today = datetime.date.today()
                # 更新日を取得
                beforeday = datetime.datetime.strptime(
                    searched_opeadmins[0].upd_date, '%Y%m%d%H%M%S').date()
                # 更新日が現在の年月日と異なる場合（前日以前とみなす）
                if (today != beforeday):
                    # 連携フラグの値を連携（前）フラグに更新
                    update_opeadmin.befrelationwin = searched_opeadmins[0].relationwin

                #  新規追加（案件２１AzureADへパスワードを即時連携） START
                ret_opeadmin = searched_opeadmins[0]
                ret_opeadmin.user_password = update_opeadmin.user_password
                ret_opeadmin.enc_password = update_opeadmin.user_password
                ret_opeadmin.befrelationwin = update_opeadmin.befrelationwin
                #  新規追加（案件２１AzureADへパスワードを即時連携） END
            self.opeadmin_model.update(update_opeadmin)
        finally:
            self.ldap_access_object.close()

        self.log_info("### END OPEADMIN SERVICE UPDATE PASWORD ###")

        #  改修（案件２１AzureADへパスワードを即時連携） START
        return ret_opeadmin
        #  改修（案件２１AzureADへパスワードを即時連携） END

    def search(self, opeadmin_conditions):
        """
        OPE管理者を検索するサービスメソッド

        Parameters
        ----------
        opeadmin_conditions : Opeadmin
            LDAPから検索するOpeadmin条件

        Returns
        -------
        searched_opeadmins : list
            LDAPから検索されたOpeadmin（複数）
        """
        self.log_info("### START OPEADMIN SERVICE SEARCH ###")
        # 検索タイプ
        search_type = STATIC_CODE.LDAP_SEARCH_TYPE.OPEADMIN_LIST
        # 任意検索条件を設定
        optional_rule = ldap.LDAP_OPTIONAL_SEARCH_ATTRIBUTES[search_type]
        optional_filter = []
        for key in optional_rule:
            val = opeadmin_conditions.__dict__.get(key)
            if val == "" or val == [] or val == [""]:
                optional_filter.append("!({" + key + "}=*)")
                opeadmin_conditions.__dict__[key] = None
        # 部分一致検索条件の値に*を付加
        part_match_rule = ldap.LDAP_PART_MATCH_ATTRIBUTES[search_type]
        for key, val in opeadmin_conditions.get_dict().items():
            # 文字列以外は除外とする
            if key in part_match_rule and val.__class__ == str:
                opeadmin_conditions.__dict__[key] = "*" + val + "*"
        # enable_flag有効無効条件
        if opeadmin_conditions.enable_flag == 0:
            enable_filter = "{password_account_locked_time}=000001010000Z"
        else:
            enable_filter = "!({password_account_locked_time}=000001010000Z)"
        try:
            self.ldap_access_object.connect()
            searched_opeadmins = self.opeadmin_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[search_type],
                opeadmin_conditions,
                opeadmin_conditions,
                [enable_filter],
            )
        finally:
            self.ldap_access_object.close()

        # 職階とユーザーIDで昇順で並び替える
        searched_opeadmins.sort(
            key=lambda x: (
                int(x.title_code[0])
                if x.title_code is not None and len(x.title_code) > 0
                else 9999,
                x.user_id,
            )
        )
        self.log_info("### END OPEADMIN SERVICE SEARCH ###")

        return searched_opeadmins

    def update(self, update_opeadmin):
        """
        OPE管理者情報を更新するサービスメソッド

        Parameters
        ----------
        update_opeadmin : Opeadmin
            更新するデータが含まれたOpeadmin情報

        Returns
        -------
        updated_opeadmin : Opeadmin
            更新されたOpeadmin情報
        """
        log_update_opeadmin = update_opeadmin.get_dict()
        log_update_opeadmin = self.delete_key(log_update_opeadmin)
        self.log_info("OPE管理者情報更新 サービス 開始 , Operator : -" +
                      f" , Input : {log_update_opeadmin}")
        # システム付加情報を設定
        # 表示名の作成
        update_opeadmin.display_name = (
            f"{update_opeadmin.sur_name}　{update_opeadmin.given_name}"
        )
        try:
            self.ldap_access_object.connect()
            # 　新規追加（案件７．メールの一意性チェック）　START
            self.rds_access_object.begin()
            # 　新規追加（案件７．メールの一意性チェック）　END
            # 　改修（マルチテナント化対応）　START
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            system_organization_code = update_opeadmin.system_organization_code
            system_organization = system_organization_service.select_by_code(system_organization_code)
            update_opeadmin.system_organization_name = system_organization.system_organization_name
            update_opeadmin.system_organization_name_ja = system_organization.system_organization_name_ja
            update_opeadmin.system_organization_type = system_organization.system_organization_type

            windows_cooperation_flag = self.environment_service.select_by_key(
                Environment(system_organization_code=update_opeadmin.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            environment_name=ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value,
                            delete_flag=0))
            if windows_cooperation_flag == 1:
                # 更新日とWindows連携フラグを取得
                dn_condition = Opeadmin(
                    system_organization_name=update_opeadmin.system_organization_name,
                    organization_name=update_opeadmin.organization_name
                )
                # 　改修（マルチテナント化対応）　END
                searched_opeadmins = self.opeadmin_model.select(
                    ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                        STATIC_CODE.LDAP_SEARCH_TYPE.OPEADMIN_LIST
                    ],
                    dn_condition,
                    specify_filters=["{user_id}=" + update_opeadmin.user_id],
                )
                # 現在の年月日を取得
                today = datetime.date.today()
                # 更新日を取得
                beforeday = datetime.datetime.strptime(
                    searched_opeadmins[0].upd_date, '%Y%m%d%H%M%S').date()
                # 更新日が現在の年月日と異なる場合（前日以前とみなす）
                if (today != beforeday):
                    # 連携フラグの値を連携（前）フラグに更新
                    update_opeadmin.befrelationwin = searched_opeadmins[0].relationwin
                # メールアドレス変更可チェック
                if (update_opeadmin.befrelationwin == 1 or update_opeadmin.befrelationwin == 2) and (searched_opeadmins[0].mail != update_opeadmin.mail):
                    self.throw_error(
                        "ID_E_0042",
                        None,
                        format_message=[
                            update_opeadmin.mail,
                        ],
                    )
                if (update_opeadmin.password is not None):
                    # 平文パスワードを暗号化して設定
                    decrypt_key = self.decrypt_message(
                        os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                    enc_password = encrypt_aes256(
                        update_opeadmin.password, decrypt_key.encode())
                    update_opeadmin.enc_password = enc_password
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(update_opeadmin.relationgg) == 1 or\
                    int(update_opeadmin.relationwin) == 1 or int(update_opeadmin.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Opeadmin(
                    system_organization_name=update_opeadmin.system_organization_name
                )
                search_opeadmin = self.opeadmin_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + update_opeadmin.mail,
                        "!({user_id}=" + update_opeadmin.user_id + ")"
                    ],
                )
                if len(search_opeadmin) > 0:
                    self.throw_error(
                        "ID_E_0020",
                        None,
                        format_message="メールアドレス<{}>がすでに存在しています".format(
                            update_opeadmin.mail
                        ),
                    )
            # 　新規追加（案件７．メールの一意性チェック）　END

            # 更新日付の生成
            update_opeadmin.upd_date = self.create_update_date_str()
            # 組織情報をconfigデータから補完
            # 　改修（マルチテナント化対応）　START
            # TOP組織情報
            top_organization = system_organization_service.select_top_organization(
                update_opeadmin.system_organization_code)
            update_opeadmin.organization_name = top_organization.school_name
            update_opeadmin.organization_name_ja = (
                top_organization.school_name_ja
            )
            update_opeadmin.organization_type = top_organization.school_type
            # 　改修（マルチテナント化対応）　END
            # パスワードの名称がIFで異なるため移し替え
            update_opeadmin.user_password = update_opeadmin.password
            updated_opeadmin = self.opeadmin_model.update(update_opeadmin)
        finally:
            self.ldap_access_object.close()
            # 　新規追加（案件７．メールの一意性チェック）　START
            self.rds_access_object.close()
            # 　新規追加（案件７．メールの一意性チェック）　END

        # OPE管理者更新で返される属性に絞る(inとoutの形式が違うため)
        rule = ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
            STATIC_CODE.LDAP_SEARCH_TYPE.OPEADMIN_LIST
        ]
        keys = updated_opeadmin.get_dict().keys()
        for key in keys:
            if key not in rule:
                updated_opeadmin.__dict__[key] = None

        self.log_info(
            "OPE管理者情報コミット , Operator : - , Output : -")
        log_updated_opeadmin = self.delete_key(updated_opeadmin.get_dict())
        self.log_info("OPE管理者情報更新 サービス 終了 , Operator : -" +
                      f" , Output : {log_updated_opeadmin}")

        return updated_opeadmin

    # 　新規追加（案件８．OPE管理者の削除）　START
    def delete(self, delete_opeadmin, delete_opeadmin_data):
        """
        OPE管理者情報情報を削除する

        Parameters
        ----------
        delete_opeadmin : Opeadmin
            学校を削除するための学校エンティティ

        Returns
        -------
        delete_opeadmin : Opeadmin
            削除結果
        """
        delete_opeadmin_dict = delete_opeadmin.get_dict()
        delete_opeadmin_dict_copy = delete_opeadmin_dict.copy()
        if "password" in delete_opeadmin_dict_copy:
            delete_opeadmin_dict_copy.pop("password")
        if "user_password" in delete_opeadmin_dict_copy:
            delete_opeadmin_dict_copy.pop("user_password")
        self.log_info("OPE管理者情報削除, Operator : -" +
                      f" , Input : {delete_opeadmin_dict_copy}")
        error_messages = []
        try:
            self.log_info("バリデーション, Operator : - , Input : -")
            self.ldap_access_object.connect()

            # OPE管理者情報取得
            # 対象ユーザの存在チェック
            dn_condition = Opeadmin(
                system_organization_name=delete_opeadmin.system_organization_name
            )
            # 　改修（マルチテナント化対応）　START
            opeadmin_data = self.opeadmin_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                    STATIC_CODE.LDAP_SEARCH_TYPE.OPEADMIN_LIST_DELETE
                ],
                dn_condition,
                specify_filters=["{user_id}=" + delete_opeadmin.user_id,
                                 "{organization_name}=" + delete_opeadmin.organization_name]
            )
            # 　改修（マルチテナント化対応）　END
            if len(opeadmin_data) == 0:
                # 対象ユーザが存在しなかった場合
                error_messages.append(
                    "対象のユーザ<{}>はすでに削除されています".format(delete_opeadmin.user_id)
                )
            # コード整合性エラーがあった場合例外発生
            if error_messages:
                self.log_info(
                    f"バリデーションエラー , Operator : - , Output : {error_messages}")
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message=",".join(error_messages),
                )
        except Exception as exception:
            raise exception
        finally:
            self.ldap_access_object.close()
        try:
            self.rds_access_object.begin()
            # ユーザ削除テーブルに削除対象ユーザの仮登録
            self.opeadmin_model.insert_user(
                opeadmin_data[0], delete_opeadmin_data)
            self.ldap_access_object.connect()
            # LDAPのユーザ削除
            self.opeadmin_model.delete(opeadmin_data[0])
            self.ldap_access_object.close()
            # ユーザ削除テーブルに削除対象ユーザのコミット
            self.rds_access_object.commit()
            self.rds_access_object.close()
            self.log_info("OPE管理者情報削除 コミット, Operator : - , Output : -")
        except Exception as exception:
            self.log_info("異常終了 , Operator : - , Output : -")
            self.rds_access_object.rollback()
            self.rds_access_object.close()
            self.throw_error("ID_E_0003", exception)
        return opeadmin_data[0].get_dict()
    # 　新規追加（案件８．OPE管理者の削除）　END
