# coding: utf-8
import os
import datetime
import copy
import uuid

from app.models.teacher_model import TeacherModel
from common.base_service import BaseService
from app.entities.teacher import Teacher
from common.crud_model import CRUDModel
from common.environment_service import EnvironmentService
from common.ldap_access_object import LdapAccessObject
from common.config import ldap
from common.config import scim
from common.config import static_code as STATIC_CODE
from common.config.static_code import RDS_TABLE, RDS_SEARCH_TYPE, APPLICATION_ID, ENVIRONMENT_NAME
from app.models.master_model import MasterModel
from common.master_entities.environment import Environment
from common.rds_access_object import RdsAccessObject
from common.master_entities.school_master import SchoolMaster
from common.master_entities.grade_master import GradeMaster
from common.master_entities.class_master import ClassMaster
from common.base_master_model import BaseMasterModel
from common.config import rds
from common.base import Base
from common.helper_encryption import encrypt_aes256
from app.config import org_env
from common.base import Base

class TeacherService(BaseService):
    """教員の参照、登録、削除、更新をするサービス

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
        # 　改修（DB構成変更対応）　START
        self.rds_access_object = RdsAccessObject(
            os.environ.get("RDS_RESOURCE_ARN"),
            os.environ.get("RDS_SECRET_ARN"),
            os.environ.get("RDS_DATABASE"),
        )
        self.teacher_model = TeacherModel(
            self.rds_access_object, self.ldap_access_object)
        # 　改修（DB構成変更対応）　END

    def insert(self, new_teacher):
        """
        教員を追加するサービスメソッド

        Parameters
        ----------
        new_teacher : Teacher
            LDAPに登録するTeacher情報

        Returns
        -------
        inserted_teacher : Teacher
            LDAPに登録されたTeacher情報
        """
        new_teacher_dict = self.delete_key(new_teacher.get_dict())
        self.log_info("教員登録, Operator : -" +
                      f" , Input : {new_teacher_dict}")
        try:
            self.log_info("バリデーション, Operator : - , Input : -")
            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (new_teacher.fiscal_year == year or new_teacher.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        new_teacher.fiscal_year,
                    ],
                )
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            curd_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_teacher, curd_model
            )
            # ユーザID自治体内ユニークID重複チェック
            collision_data = self.teacher_model.select(
                ["user_id", "persistent_uid"],
                Teacher(system_organization_name=new_teacher.system_organization_name),
                specify_filters=[
                    "|({user_id}=" + new_teacher.user_id + ")"
                    "({persistent_uid}=" + new_teacher.persistent_uid + ")"
                ],
            )
            # 　改修（マルチテナント化対応）　END
            if len(collision_data) > 1 or (
                len(collision_data) == 1
                and collision_data[0].user_id == new_teacher.user_id
                and collision_data[0].persistent_uid
                == new_teacher.persistent_uid
            ):
                # ユーザIDも自治体内ユニークIDが重複した場合
                # 重複レコード2つ以上、または1つで両方重複しているケース
                error_messages.append(
                    "ユーザID<{}>自治体ユニークID<{}>がすでに存在しています".format(
                        new_teacher.user_id, new_teacher.persistent_uid
                    )
                )
            elif len(collision_data) == 1:
                # ユーザIDまたは自治体内ユニークIDが重複した場合
                # ただし、両方重複しているケースは除く
                if collision_data[0].user_id == new_teacher.user_id:
                    # user_idが重複した場合
                    error_messages.append(
                        "ユーザID<{}>がすでに存在しています".format(new_teacher.user_id,)
                    )
                else:
                    # persistent_uidが重複した場合
                    error_messages.append(
                        "自治体内ユニークID<{}>がすでに存在しています".format(
                            new_teacher.persistent_uid
                        )
                    )
            # PIDユニークチェック(ユーザ削除テーブル)
            # 　改修（マルチテナント化対応）　START
            dn_condition = Teacher(
                system_organization_code=new_teacher.system_organization_code,
                persistent_uid=new_teacher.persistent_uid,
            )
            ret = curd_model.select_count(
                dn_condition.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                # 　改修（DB構成変更対応）　END
                dn_condition,
                exclusion_where_columns=[
                    "persistent_uid", "limit", "offset"],
                # 　改修（DB構成変更対応）　START
                specific_conditions=["persistent_uid=%(persistent_uid)s"],
                # 　改修（DB構成変更対応）　END
            )
            # 　改修（マルチテナント化対応）　END
            if (ret > 0):
                # persistent_uidが重複した場合
                error_messages.append(
                    "自治体内ユニークID<{}>がすでに存在しています".format(
                        new_teacher.persistent_uid
                    )
                )
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_teacher.relationgg) == 1 or\
                    int(new_teacher.relationwin) == 1 or int(new_teacher.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Teacher(
                    system_organization_name=new_teacher.system_organization_name
                )
                search_teacher = self.teacher_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_teacher.mail
                    ],
                )
                if len(search_teacher) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_teacher.mail
                        )
                    )
            # 　新規追加（案件７．メールの一意性チェック）　END

            # コード整合性エラーがあった場合例外発生
            if error_messages:
                self.log_info(
                    "バリデーションエラー , Operator : - , Output : " + "".join(error_messages))
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message=(",").join(error_messages),
                )

            #  新規追加(マルチテナント化対応) START
            # 環境情報取得
            environment_service = EnvironmentService(self.rds_access_object)
            environments = environment_service.select(Environment(system_organization_code=new_teacher.system_organization_code,
                                                                  application_id=APPLICATION_ID.Common.value,
                                                                  delete_flag=0))
            # opaqueIDの生成
            idp_entityid = environment_service.get_environment_value(environments,
                                                                     ENVIRONMENT_NAME.IDP_ENTITYID.value)
            windows_cooperation_flag = environment_service.get_environment_value(environments,
                                                                                 ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value)
            #  新規追加(マルチテナント化対応) END
            new_teacher.opaque_id = self.create_opaque_id(
                new_teacher.persistent_uid,
                # 　改修（マルチテナント化対応）　START
                idp_entityid,
                # 　改修（マルチテナント化対応）　END
                os.environ.get("OPAQUE_ID_SALT"),
            )
            # 　新規追加（文科省標準の学校コード追加）　START
			# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
            # mextUidを生成(OneRoster対応：値がある場合、再採番不要)
            if not new_teacher.mextUid:
                new_teacher.mextUid = str(uuid.uuid4())
			# ↑ここまで
            # 　新規追加（文科省標準の学校コード追加）　END

            #  改修(マルチテナント化対応) START
            str_system_date = self.create_update_date_str()
            # 登録日の追加
            new_teacher.reg_date = str_system_date
            # 更新日付の生成
            new_teacher.upd_date = str_system_date
            #  改修(マルチテナント化対応) END

            # Windows連携時のみ平文パスワードの追加
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                # 平文パスワードの設定
                # 復号キーの復号
                decryption_key = self.decrypt_message(
                    os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                # 暗号化
                enc_password = encrypt_aes256(
                    new_teacher.password, decryption_key.encode())
                new_teacher.enc_password = enc_password
            # 登録実行
            inserted_teacher = self.teacher_model.insert(new_teacher)
            inserted_teacher_dict = self.delete_key(
                inserted_teacher.get_dict())
            self.log_info("教員登録 コミット, Operator : -" +
                          f" , Output : {inserted_teacher_dict}")
        except Exception as exception:
            self.log_info("異常終了 , Operator : - , Output : -")
            raise (exception)
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        # このメソッドの返却値は挿入データ
        return inserted_teacher

    # 　改修（マルチテナント化対応）　START
    def update(self, update_teacher, windows_cooperation_flag):
        # 　改修（マルチテナント化対応）　END
        """
        教員情報を更新するサービスメソッド

        Parameters
        ----------
        update_teacher : Teacher
            更新するデータが含まれたOpeadmin情報
        windows_cooperation_flag : str
            Windows連携有無フラグ

        Returns
        -------
        updated_teacher : Teacher
            更新されたTeacher情報
        """
        log_update_teacher = update_teacher.get_dict()
        log_update_teacher = self.delete_key(log_update_teacher)
        self.log_info("教員情報更新 サービス 開始 , Operator : -" +
                      f" , Input : {log_update_teacher}")
        error_messages = ""
        # 学校コードチェック
        try:
            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (update_teacher.fiscal_year == year or update_teacher.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        update_teacher.fiscal_year,
                    ],
                )
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 　改修（DB構成変更対応）　END
            self.ldap_access_object.connect()
            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            # 　改修（DB構成変更対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                update_teacher, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(update_teacher.relationgg) == 1 or\
                    int(update_teacher.relationwin) == 1 or int(update_teacher.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Teacher(
                    system_organization_name=update_teacher.system_organization_name
                )
                search_teacher = self.teacher_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + update_teacher.mail,
                        "!({user_id}=" + update_teacher.user_id + ")"
                    ],
                )
                if len(search_teacher) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            update_teacher.mail
                        )
                    )
            # 　新規追加（案件７．メールの一意性チェック）　END

            # コード整合性エラーがあった場合例外発生
            if error_messages:
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message=(",").join(error_messages),
                )
            # Win連携フラグチェック
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                update_teacher = self.windows_cooperation_set(update_teacher)

            updated_teacher = self.teacher_model.update(update_teacher)
            # 更新後のデータを取得する
            updated_teacher = self.teacher_model.get(
                scim.SCIM_PUSH_TEACHER_ATTRIBUTES, update_teacher,
            )[0]
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info(
            "教員情報コミット , Operator : - , Output : -")
        log_update_teacher = self.delete_key(updated_teacher.get_dict())
        self.log_info("教員情報更新 サービス 終了 , Operator : -" +
                      f" , Output : {log_update_teacher}")

        # このメソッドの返却値は挿入データ
        return updated_teacher

    def windows_cooperation_set(self, update_teacher):
        """
        Windows連携サービスメソッド

        Parameters
        ----------
        update_teacher : Teacher
            更新するデータが含まれたOpeadmin情報

        Returns
        -------
        updated_teacher : Teacher
            更新されたTeacher情報
        """
        dn_condition = Teacher(
            system_organization_name=update_teacher.system_organization_name
        )
        collision_data = self.teacher_model.select(
            ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                STATIC_CODE.LDAP_SEARCH_TYPE.TEACHER_LIST
            ],
            dn_condition,
            specify_filters=["{user_id}=" + update_teacher.user_id],
        )
        if len(collision_data) > 0:
            update_teacher.befrelationwin = self.befreletionwin_set(
                collision_data)
            # メールアドレス変更可チェック
            if ((update_teacher.befrelationwin == "1" or update_teacher.befrelationwin == "2") and
                    (collision_data[0].mail != update_teacher.mail)):
                self.throw_error(
                    "ID_E_0042",
                    None,
                    format_message=[
                        update_teacher.mail,
                    ],
                )
            if (update_teacher.befrelationwin == "2" and update_teacher.relationwin == 1) or (
                    update_teacher.befrelationwin == "1" and update_teacher.relationwin == 2):
                self.throw_error(
                    "ID_E_0043",
                    None,
                )
            if (update_teacher.password is not None):
                # 平文パスワードの設定
                # 復号キーの復号
                decryption_key = self.decrypt_message(
                    os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                # 暗号化
                enc_password = encrypt_aes256(
                    update_teacher.password, decryption_key.encode())
                update_teacher.enc_password = enc_password
        return update_teacher

    def befreletionwin_set(self, collision_data):
        """
        Azure連携（以前）フラグを設定する

        Parameters
        ----------
        collision_data : Student
            更新する児童生徒エンティティ

        Returns
        -------
        befrelationwin : str
            Azure連携（以前）フラグ
        """
        # 現在の年月日を取得
        today = datetime.date.today()
        # 更新日を取得
        beforeday = datetime.datetime.strptime(
            collision_data[0].upd_date, '%Y%m%d%H%M%S').date()
        # 更新日が現在の年月日と異なる場合（前日以前とみなす）
        if (today != beforeday):
            # 連携フラグの値を連携（前）フラグに更新
            befrelationwin = str(collision_data[0].relationwin)
        else:
            # 連携（前）フラグの値を連携（前）フラグに更新
            befrelationwin = collision_data[0].befrelationwin

        return befrelationwin

    # 　改修（マルチテナント化対応）　START
    def change_user_ou(self, old_teacher, new_teacher, windows_cooperation_flag):
        # 　改修（マルチテナント化対応）　END
        """
        教員情報を更新するサービスメソッド(組織移動)

        Parameters
        ----------
        old_teacher : Teacher
            更新するデータが含まれたOpeadmin情報
        new_teacher : Teacher
            組織移動先のデータが含まれたOpeadmin情報
        windows_cooperation_flag : str
            Windows連携有無フラグ

        Returns
        -------
        updated_teacher : Teacher
            更新されたTeacher情報
        """
        log_old_teacher = old_teacher.get_dict()
        log_old_teacher = self.delete_key(log_old_teacher)
        log_new_teacher = new_teacher.get_dict()
        log_new_teacher = self.delete_key(log_new_teacher)
        self.log_info("教員情報更新(組織移動) サービス 開始 , Operator : -" +
                      f" , Input : {log_old_teacher}, {log_new_teacher}")
        error_messages = ""
        try:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 　改修（DB構成変更対応）　END
            self.ldap_access_object.connect()
            # ロールバック用に元データを取得
            before_dn_condition = Teacher(
                system_organization_name=old_teacher.system_organization_name
            )
            before_teacher = self.teacher_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                    STATIC_CODE.LDAP_SEARCH_TYPE.TEACHER_LIST
                ],
                before_dn_condition,
                specify_filters=["{user_id}=" + old_teacher.user_id],
            )
            if len(before_teacher) == 0:
                self.throw_error(
                    "ID_E_0004",
                    None,
                    format_message=old_teacher.user_id,
                )
            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (new_teacher.fiscal_year == year or new_teacher.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        new_teacher.fiscal_year,
                    ],
                )
            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            # 　改修（DB構成変更対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_teacher, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_teacher.relationgg) == 1 or\
                    int(new_teacher.relationwin) == 1 or int(new_teacher.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Teacher(
                    system_organization_name=new_teacher.system_organization_name
                )
                search_teacher = self.teacher_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_teacher.mail,
                        "!({user_id}=" + new_teacher.user_id + ")"
                    ],
                )
                if len(search_teacher) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_teacher.mail
                        )
                    )
            # 　新規追加（案件７．メールの一意性チェック）　END

            # コード整合性エラーがあった場合例外発生
            if error_messages:
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message=(",").join(error_messages),
                )
            # Win連携フラグチェック
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                new_teacher = self.windows_cooperation_set(new_teacher)
            updated_teacher = {}
            updated_teacher = copy.deepcopy(new_teacher)
            # 属性情報の更新
            updated_teacher.organization_code = before_teacher[0].organization_code
            updated_teacher.organization_name = before_teacher[0].organization_name
            updated_teacher.transfer_school_date = self.create_update_date_str()
            updated_teacher.from_organization_code = before_teacher[0].organization_code
            updated_teacher = self.attribute_update(
                updated_teacher, new_teacher)
            # 組織(ou)の更新
            updated_teacher.organization_code = before_teacher[0].organization_code
            updated_teacher.organization_name = before_teacher[0].organization_name
            updated_teacher = self.ou_update(
                before_teacher, updated_teacher, new_teacher)
            # 更新後のデータを取得する(SCIMプッシュ向け)
            updated_teacher = self.teacher_model.get(
                scim.SCIM_PUSH_TEACHER_ATTRIBUTES, new_teacher,
            )[0]
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info(
            "教員情報コミット , Operator : - , Output : -")
        log_updated_teacher = self.delete_key(updated_teacher.get_dict())
        self.log_info("教員情報更新(組織移動) サービス 終了 , Operator : -" +
                      f" , Output : {log_updated_teacher}")

        # このメソッドの返却値は挿入データ
        return updated_teacher

    def attribute_update(self, updated_teacher, new_teacher):
        """
        教員情報の属性情報を更新する

        Parameters
        ----------
        updated_teacher : Teacher
            更新する児童生徒エンティティ

        Returns
        -------
        updated_teacher : Teacher
            更新結果
        """
        try:
            updated_teacher = self.teacher_model.update_dn(
                updated_teacher, new_teacher)
        except Exception as exception:
            self.throw_error("ID_E_0001", exception)
            raise exception

        return updated_teacher

    def ou_update(self, before_teacher, updated_teacher, new_teacher):
        """
        教員情報のuidを更新する

        Parameters
        ----------
        before_teacher : Teacher
            ロールバック用の児童生徒エンティティ
        updated_teacher : Teacher
            更新対象となる児童生徒エンティティ
        new_teacher : Teacher
            移動先情報が含まれている児童生徒エンティティ

        Returns
        -------
        updated_teacher : Teacher
            更新結果
        """
        try:
            updated_teacher = self.teacher_model.update_user_change_ou(
                updated_teacher, new_teacher)
        except Exception as exception:
            # ロールバック（属性情報を戻す）
            self.attribute_update(updated_teacher, before_teacher)
            self.throw_error("ID_E_0001", exception)
            raise exception

        return updated_teacher

    def search(self, teacher_conditions):
        """
        教員を検索するサービスメソッド

        Parameters
        ----------
        teacher_conditions : Teacher
            LDAPから検索するTeacher条件

        Returns
        -------
        searched_teachers : list
            LDAPから検索されたTeacher（複数）
        """
        self.log_info("### START TEACHER SERVICE SEARCH ###")
        # 検索タイプ
        search_type = STATIC_CODE.LDAP_SEARCH_TYPE.TEACHER_LIST
        # 任意検索条件を設定
        optional_rule = ldap.LDAP_OPTIONAL_SEARCH_ATTRIBUTES[search_type]
        optional_filter = []
        if teacher_conditions.fiscal_year_from != None:
            optional_filter.append(
                "{fiscal_year}>=" + str(teacher_conditions.fiscal_year_from))
            teacher_conditions.fiscal_year_from = None
        if teacher_conditions.fiscal_year_to != None:
            optional_filter.append(
                "{fiscal_year}<=" + str(teacher_conditions.fiscal_year_to))
            teacher_conditions.fiscal_year_to = None
        for key in optional_rule:
            val = teacher_conditions.__dict__.get(key)
            if val == "" or val == [] or val == [""]:
                optional_filter.append("!({" + key + "}=*)")
                teacher_conditions.__dict__[key] = None
        # 部分一致検索条件の値に*を付加
        part_match_rule = ldap.LDAP_PART_MATCH_ATTRIBUTES[search_type]
        for key, val in teacher_conditions.get_dict().items():
            # 文字列以外は除外とする
            if key in part_match_rule and val.__class__ == str:
                teacher_conditions.__dict__[key] = "*" + val + "*"
        # enable_flag有効無効条件
        if teacher_conditions.enable_flag == 0:
            optional_filter.append(
                "{password_account_locked_time}=000001010000Z"
            )
        else:
            optional_filter.append(
                "!({password_account_locked_time}=000001010000Z)"
            )
        # 検索実行
        try:
            self.ldap_access_object.connect()
            searched_teachers = self.teacher_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[search_type],
                teacher_conditions,
                teacher_conditions,
                optional_filter,
            )
        finally:
            self.ldap_access_object.close()

        # 職階とユーザーIDで昇順で並び替える
        searched_teachers.sort(
            key=lambda x: (
                int(x.title_code[0])
                if x.title_code is not None and len(x.title_code) > 0
                else 9999,
                x.user_id,
            )
        )

        self.log_info("### END TEACHER SERVICE SEARCH ###")

        return searched_teachers

    # 　改修（マルチテナント化対応）　START
    def complement_and_alignment_user(self, teacher, crud_model):
        # 　改修（マルチテナント化対応）　END
        """
        学校(組織)コードチェック補完
        学年コードチェック補完
        組コードチェック補完
        表示名生成
        更新日付の設定

        Parameters
        ----------
        teacher : Teacher
            チェック 補完 対象Teacher情報
        crud_model : MasterModel
            チェック用モデル
        Returns
        -------
        error_messages : [str] | []
            発生したエラー情報

        Exceptions
        -------
        LambdaError(ID_E_0020) : 学校コードが見つからない時は途中終了
        """
        error_messages = []
        # 学校コードチェック
        # 　改修（マルチテナント化対応）　START
        schools = crud_model.select(
            teacher.system_organization_code,
            # 　改修（DB構成変更対応）　START
            RDS_TABLE.SCHOOL_MASTER,
            # 　改修（DB構成変更対応）　END
            # 　改修（文科省標準の学校コード追加）　START
            ["school_name", "school_name_ja", "school_type", "mextOuCode"],
            # 　改修（文科省標準の学校コード追加）　END
            SchoolMaster(system_organization_code=teacher.system_organization_code,
                         school_code=teacher.organization_code,
                         delete_flag=0),
            specific_conditions=[
                " show_no <> 0"
            ],
        )
        if len(schools) == 0:
            error_messages.append(
                "学校コード<{}>は存在しません".format(teacher.organization_code)
            )
            self.throw_error(
                "ID_E_0020", None, format_message=(",").join(error_messages)
            )
        # 学校情報補完
        teacher.organization_name = schools[0].school_name
        teacher.organization_name_ja = schools[0].school_name_ja
        teacher.organization_type = schools[0].school_type
        # 　新規追加（文科省標準の学校コード追加）　START
        teacher.mextOuCode = schools[0].mextOuCode
        # 　新規追加（文科省標準の学校コード追加）　END
        # 学年コードチェック(学年コードが空の時は学年名も空とする)
        if teacher.grade_code:
            master_grades = crud_model.select(
                teacher.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.GRADE_MASTER,
                # 　改修（DB構成変更対応）　END
                ["grade_code", "grade_name_ja"],
                GradeMaster(system_organization_code=teacher.system_organization_code,
                            school_code=teacher.organization_code,
                            grade_code=teacher.grade_code,
                            delete_flag=0,
                ),
            )
            if len(master_grades) == 0:
                error_messages.append(
                    "学校<{}>には学年コード<{}>が存在しません".format(
                        teacher.organization_name_ja, teacher.grade_code
                    )
                )
            else:
                teacher.grade_name = master_grades[0].grade_name_ja
        else:
            teacher.grade_name = teacher.grade_code
        # 組コードチェック(組コードがNoneの時は組コード、組名を空値とする)
        # 組コードはint型なので、単純なbool比較だと0がFalseになるので注意
        if teacher.class_code or teacher.class_code == 0:
            master_classes = crud_model.select(
                teacher.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.CLASS_MASTER,
                # 　改修（DB構成変更対応）　END
                ["class_code", "class_name_ja"],
                ClassMaster(system_organization_code=teacher.system_organization_code,
                            school_code=teacher.organization_code,
                            class_code=teacher.class_code,
                            delete_flag=0,
                ),
            )
            if len(master_classes) == 0:
                error_messages.append(
                    "学校<{}>には組コード<{}>が存在しません".format(
                        teacher.organization_name_ja, teacher.class_code
                    )
                )
            else:
                teacher.class_name = master_classes[0].class_name_ja
        else:
            teacher.class_code = ""
            teacher.class_name = ""
        # 　改修（マルチテナント化対応）　END
        # 表示名の作成
        teacher.display_name = f"{teacher.sur_name}　{teacher.given_name}"
        # 更新日付の生成
        teacher.upd_date = self.create_update_date_str()
        # パスワードの名称がIFで異なるため移し替え
        teacher.user_password = teacher.password

        return error_messages

    def delete(self, delete_teacher, delete_teacher_data):
        """
        教員情報を削除する

        Parameters
        ----------
        delete_teacher : Teacher
            学校を削除するための学校エンティティ

        Returns
        -------
        delete_teacher : Teacher
            削除結果
        """
        delete_teacher_dict = delete_teacher.get_dict()
        delete_teacher_dict_copy = delete_teacher_dict.copy()
        if ("password" in delete_teacher_dict_copy):
            delete_teacher_dict_copy.pop("password")
        if ("user_password" in delete_teacher_dict_copy):
            delete_teacher_dict_copy.pop("user_password")
        self.log_info("教員情報削除, Operator : -" +
                      f" , Input : {delete_teacher_dict_copy}")
        error_messages = []
        try:
            self.log_info("バリデーション, Operator : - , Input : -")
            self.ldap_access_object.connect()

            # 教員情報取得
            # 対象ユーザの存在チェック
            dn_condition = Teacher(
                system_organization_name=delete_teacher.system_organization_name
            )
            teacher_data = self.teacher_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                    STATIC_CODE.LDAP_SEARCH_TYPE.TEACHER_LIST_DELETE
                ],
                dn_condition,
                specify_filters=["{user_id}=" + delete_teacher.user_id,
                                 "{organization_name}=" + delete_teacher.organization_name],
            )
            if (len(teacher_data) == 0):
                # 対象ユーザが存在しなかった場合
                error_messages.append(
                    "対象のユーザ<{}>はすでに削除されています".format(delete_teacher.user_id)
                )
            # コード整合性エラーがあった場合例外発生
            if error_messages:
                self.log_info(
                    f"バリデーションエラー , Operator : - , Output : {error_messages}")
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message=(",").join(error_messages),
                )
        except Exception as exception:
            raise exception
        finally:
            self.ldap_access_object.close()
        try:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 　改修（DB構成変更対応）　END
            # ユーザ削除テーブルに削除対象ユーザの仮登録
            self.teacher_model.insert_user(
                teacher_data[0], delete_teacher_data)
            self.ldap_access_object.connect()
            # LDAPのユーザ削除
            self.teacher_model.delete(teacher_data[0])
            self.ldap_access_object.close()
            # ユーザ削除テーブルに削除対象ユーザのコミット
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.commit()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END
            self.log_info("教員情報削除 コミット, Operator : - , Output : -")
        except Exception as exception:
            self.log_info("異常終了 , Operator : - , Output : -")
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.rollback()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END
            self.throw_error("ID_E_0003", exception)
        return teacher_data[0].get_dict()

    def get_organization_name(self, conditions):
        """
        学校マスタから学校名を取得する

        Parameters
        ----------
        conditions : SchoolMaster
            検索条件の格納された学校エンティティ

        Returns
        -------
        return : dict('total': int, 'datas': list[SchoolMaster])
            DB検索結果（総計とデータ）
        """
        conditions_dict = conditions.get_dict()
        conditions_dict_copy = conditions_dict.copy()
        if ("password" in conditions_dict_copy):
            conditions_dict_copy.pop("password")
        if ("user_password" in conditions_dict_copy):
            conditions_dict_copy.pop("user_password")
        self.log_info(f"学校名取得, Operator : - , Input : {conditions_dict_copy}")
        try:
            # 　改修（マルチテナント化対応）　START
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            # 検索対象件数を取得
            total_school = crud_model.select_count(
                conditions.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.SCHOOL_MASTER,
                # 　改修（DB構成変更対応）　END
                conditions,
                specific_conditions=[
                    " show_no <> 0"
                ],
            )
            # 検索実行
            searched_schools = crud_model.select(
                conditions.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.SCHOOL_MASTER,
                rds.ALLOW_SEARCH_COLMUNS[
                    RDS_SEARCH_TYPE.SCHOOL_LIST_MASTERS
                ],
                # 　改修（DB構成変更対応）　END
                conditions,
                specific_conditions=[
                    " show_no <> 0"
                ],
            )
            # 　改修（マルチテナント化対応）　END
            self.log_info(
                f"学校名取得 コミット, Operator : - , Output : {total_school}, {searched_schools}")
        except Exception as exception:
            self.log_info("異常終了 , Operator : - , Output : -")
            raise exception
        finally:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        # このメソッドの返却値は検索データ
        return {"total": total_school, "datas": searched_schools}

    def search_delete_teacher(self, teacher_conditions):
        """
        無効ユーザを検索するサービスメソッド

        Parameters
        ----------
        teacher_conditions : Teacher
            検索条件の格納された教員エンティティ

        Returns
        -------
        return : dict('total': int, 'datas': list[SchoolMaster])
            DB検索結果（総計とデータ）
        """
        conditions_dict = self.delete_key(teacher_conditions.get_dict())
        self.log_info(f"無効ユーザ検索, Operator : - , Input : {conditions_dict}")

        try:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 部分一致検索設定
            search_type = STATIC_CODE.RDS_SEARCH_TYPE.DELETE_TEACHER_USER_LIST
            # 　改修（DB構成変更対応）　END
            specific_conditions = []
            condition = teacher_conditions.get_dict()
            # 　改修（DB構成変更対応）　START
            for key in rds.SELECT_LIKE_VALUE_COLMUNS[search_type]:
                # 　改修（DB構成変更対応）　END
                if key in condition and condition[key] is not None:
                    condition[key] = f"%{condition[key]}%"
                    specific_conditions.append(
                        # 　改修（DB構成変更対応）　START
                        f"{key} LIKE %({key})s"
                        # 　改修（DB構成変更対応）　END
                    )
            # 　新規追加（マルチテナント化対応）　START
            search_teacher_conditions = Teacher(**condition)
            # 　新規追加（マルチテナント化対応）　END
            # 削除した当日を検索対象に入れない
            now = Base.now()
            today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
            specific_conditions.append("entry_date_time<'" + str(today) + "'")
            # 　改修（マルチテナント化対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 検索対象件数を取得
            total_teacher = crud_model.select_count(
                teacher_conditions.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                # 　改修（DB構成変更対応）　END
                search_teacher_conditions,
                exclusion_where_columns=[
                    "sur_name", "given_name", "limit", "offset"],
                specific_conditions=specific_conditions,
            )
            # 検索実行
            searched_teachers = crud_model.select(
                teacher_conditions.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                rds.ALLOW_SEARCH_COLMUNS[
                    RDS_SEARCH_TYPE.DELETE_TEACHER_USER_LIST
                ] + ["DATE_FORMAT(entry_date_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS entry_date_time"],
                # 　改修（DB構成変更対応）　END
                search_teacher_conditions,
                exclusion_where_columns=[
                    "sur_name", "given_name", "limit", "offset"],
                specific_conditions=specific_conditions,
                # 　改修（DB構成変更対応）　START
                specific_tail="LIMIT %(limit)s OFFSET %(offset)s",
                # 　改修（DB構成変更対応）　END
            )
            # 　改修（マルチテナント化対応）　END
            self.log_info(
                f"無効ユーザ検索 コミット, Operator : - , Output : {total_teacher} , {searched_teachers}")
        except Exception as exception:
            self.log_info("異常終了 , Operator : - , Output : -")
            raise exception
        finally:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        # 文字列に変換
        for searched_teacher in searched_teachers:
            if searched_teacher.gender is not None:
                searched_teacher.gender = str(searched_teacher.gender)
            else:
                searched_teacher.gender = ""
        teacher_list = self.create_list(searched_teachers)
        return {"total": total_teacher, "datas": teacher_list}

    def create_list(self, users):
        """
        対象の値を配列に変換する

        Parameters
        ----------
        users : dict
            取得したユーザ情報

        Returns
        -------
        searched_users : dict
            取得したユーザ情報
        """
        # 配列に変換
        listed_rule = ldap.LDAP_ATTRIBUTE_LISTED_RULES
        user_list = []
        for user in users:
            teacher_dict = user.get_dict()
            for key in teacher_dict.keys():
                # カンマ区切り文字列に一致する場合の処理（配列展開）
                if key in listed_rule:
                    if teacher_dict[key]:
                        teacher_dict[key] = teacher_dict[key].split(",")
                # LDAP複数値項目は値が空の場合[]を返すので削除する
                elif teacher_dict[key] == "":
                    teacher_dict[key] = []
            user_list.append(Teacher(**teacher_dict))
        return user_list

    def recreate(self, new_teacher):
        """
        教員を再登録するサービスメソッド

        Parameters
        ----------
        new_teacher : Teacher
            LDAPに登録するTeacher情報

        Returns
        -------
        inserted_teacher : Teacher
            LDAPに登録されたTeacher情報
        """
        new_teacher_dict = self.delete_key(new_teacher.get_dict())
        self.log_info("教員再登録, Operator : -" +
                      f" , Input : {new_teacher_dict}")
        try:
            self.log_info("バリデーション, Operator : - , Input : -")

            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (new_teacher.fiscal_year == year or new_teacher.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        new_teacher.fiscal_year,
                    ],
                )
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            curd_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_teacher, curd_model
            )
            # 　改修（マルチテナント化対応）　END
            # ユーザID自治体内ユニークID重複チェック
            dn_condition = Teacher(
                system_organization_name=new_teacher.system_organization_name
            )
            collision_data = self.teacher_model.select(
                ["user_id", "persistent_uid"],
                dn_condition,
                specify_filters=[
                    "|({user_id}=" + new_teacher.user_id + ")"
                    "({persistent_uid}=" + new_teacher.persistent_uid + ")"
                ],
            )
            if len(collision_data) > 1 or (
                len(collision_data) == 1
                and collision_data[0].user_id == new_teacher.user_id
                and collision_data[0].persistent_uid
                == new_teacher.persistent_uid
            ):
                # ユーザIDも自治体内ユニークIDが重複した場合
                # 重複レコード2つ以上、または1つで両方重複しているケース
                error_messages.append(
                    "ユーザID<{}>自治体ユニークID<{}>がすでに存在しています".format(
                        new_teacher.user_id, new_teacher.persistent_uid
                    )
                )
            elif len(collision_data) == 1:
                # ユーザIDまたは自治体内ユニークIDが重複した場合
                # ただし、両方重複しているケースは除く
                if collision_data[0].user_id == new_teacher.user_id:
                    # user_idが重複した場合
                    error_messages.append(
                        "ユーザID<{}>がすでに存在しています".format(new_teacher.user_id,)
                    )
                else:
                    # persistent_uidが重複した場合
                    error_messages.append(
                        "自治体内ユニークID<{}>がすでに存在しています".format(
                            new_teacher.persistent_uid
                        )
                    )
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_teacher.relationgg) == 1 or\
                    int(new_teacher.relationwin) == 1 or int(new_teacher.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Teacher(
                    system_organization_name=new_teacher.system_organization_name
                )
                search_teacher = self.teacher_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_teacher.mail
                    ],
                )
                if len(search_teacher) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_teacher.mail
                        )
                    )
            # 　新規追加（案件７．メールの一意性チェック）　END

            # コード整合性エラーがあった場合例外発生
            if error_messages:
                self.log_info(
                    "バリデーションエラー , Operator : - , Output : " + "".join(error_messages))
                self.throw_error(
                    "ID_E_0020",
                    None,
                    format_message=(",").join(error_messages),
                )
            # ユーザ削除テーブルから対象ユーザの検索
            specific_conditions = []
            teacher_conditions = Teacher(persistent_uid=new_teacher.persistent_uid,
                                         limit=1, offset=0)
            # 　改修（マルチテナント化対応）　START
            total_teacher = curd_model.select_count(
                new_teacher.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                # 　改修（DB構成変更対応）　END
                teacher_conditions,
                exclusion_where_columns=[
                    "limit", "offset"],
                specific_conditions=specific_conditions,
            )
            if total_teacher < 1:
                self.throw_error(
                    "ID_E_0041",
                    None,
                    str(total_teacher),
                    format_message=new_teacher.persistent_uid,
                )
            # 検索実行
            searched_teachers = curd_model.select(
                new_teacher.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                rds.ALLOW_SEARCH_COLMUNS[
                    RDS_SEARCH_TYPE.DELETE_TEACHER_USER_LIST
                ] + ["DATE_FORMAT(entry_date_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS entry_date_time"],
                # 　改修（DB構成変更対応）　END
                teacher_conditions,
                exclusion_where_columns=[
                    "limit", "offset"],
                specific_conditions=specific_conditions,
                # 　改修（DB構成変更対応）　START
                specific_tail="LIMIT %(limit)s OFFSET %(offset)s",
                # 　改修（DB構成変更対応）　END
            )
            # 　改修（マルチテナント化対応）　END
            # opaqueIDの生成
            new_teacher.opaque_id = searched_teachers[0].opaque_id
            # 　新規追加（文科省標準の学校コード追加）　START
            # mextUid
            new_teacher.mextUid = searched_teachers[0].mextUid
            # 　削除（画面学校のmextOuCodeを設定）　START
            # # mextOuCode
            # new_teacher.mextOuCode = searched_teachers[0].mextOuCode
            # 　削除（画面学校のmextOuCodeを設定）　END
            # 　新規追加（文科省標準の学校コード追加）　END
            # ユーザ削除テーブルから対象のユーザを削除
            # 　改修（マルチテナント化対応）　START
            # self.teacher_model.delete_rds_user(new_teacher)
            delete_teacher = Teacher(system_organization_code=new_teacher.system_organization_code,
                                     persistent_uid=new_teacher.persistent_uid)
            curd_model.delete(new_teacher.system_organization_code,
                              RDS_TABLE.DELETE_USER,
                              delete_teacher)
            # 　改修（マルチテナント化対応）　END
            # 移動元学校と異動日の追加
            new_teacher.transfer_school_date = self.create_update_date_str()
            new_teacher.from_organization_code = searched_teachers[0].organization_code
            #  改修(マルチテナント化対応) START
            str_system_date = self.create_update_date_str()
            # 登録日の追加
            new_teacher.reg_date = str_system_date
            # 更新日付の生成
            new_teacher.upd_date = str_system_date
            #  改修(マルチテナント化対応) END

            #  新規追加(マルチテナント化対応) START
            environment_service = EnvironmentService(self.rds_access_object)
            windows_cooperation_flag = environment_service.select_by_key(
                Environment(system_organization_code=new_teacher.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            environment_name=ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value,
                            delete_flag=0))
            #  新規追加(マルチテナント化対応) END
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                # 平文パスワードの設定
                # 復号キーの復号
                decryption_key = self.decrypt_message(
                    os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                # 暗号化
                enc_password = encrypt_aes256(
                    new_teacher.password, decryption_key.encode())
                new_teacher.enc_password = enc_password
            # 登録実行
            inserted_teacher = self.teacher_model.insert(new_teacher)
            # 登録正常終了
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.commit()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

            inserted_teacher_dict = self.delete_key(
                inserted_teacher.get_dict())
            self.log_info("教員再登録 コミット, Operator : -" +
                          f" , Output : {inserted_teacher_dict}")
        except Exception as exception:
            self.log_info("異常終了 , Operator : - , Output : -")
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.rollback()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END
            raise (exception)
        finally:
            self.ldap_access_object.close()

        # このメソッドの返却値は挿入データ
        return inserted_teacher
