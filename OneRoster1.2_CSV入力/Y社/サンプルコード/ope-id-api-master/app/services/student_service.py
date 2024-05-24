# coding: utf-8
import copy
import datetime
import os
import uuid

from app.entities.student import Student
from app.models.student_model import StudentModel
from common.base import Base
from common.base_service import BaseService
from common.config import ldap
from common.config import rds
from common.config import scim
from common.config import static_code as STATIC_CODE
from common.config.static_code import RDS_TABLE, RDS_SEARCH_TYPE, APPLICATION_ID, ENVIRONMENT_NAME
from common.crud_model import CRUDModel
from common.environment_service import EnvironmentService
from common.helper_encryption import encrypt_aes256
from common.ldap_access_object import LdapAccessObject
from common.master_entities.class_master import ClassMaster
from common.master_entities.environment import Environment
from common.master_entities.grade_master import GradeMaster
from common.master_entities.school_master import SchoolMaster
from common.rds_access_object import RdsAccessObject
from common.system_organization_service import SystemOrganizationService


class StudentService(BaseService):
    """児童生徒の参照、登録、削除、更新をするサービス

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

        self.student_model = StudentModel(
            self.rds_access_object, self.ldap_access_object)
        # 　改修（DB構成変更対応）　END

    def insert(self, new_student):
        """
        児童生徒を追加するサービスメソッド

        Parameters
        ----------
        new_student : Student
            LDAPに登録するStudent情報

        Returns
        -------
        inserted_student : Student
            LDAPに登録されたStudent情報
        """
        new_student_dict = self.delete_key(new_student.get_dict())
        self.log_info("児童生徒登録, Operator : -" +
                      f" , Input : {new_student_dict}")
        try:
            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (new_student.fiscal_year == year or new_student.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        new_student.fiscal_year,
                    ],
                )
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()

            #  新規追加(マルチテナント化対応) START
            # 組織情報
            system_organization_code = new_student.system_organization_code
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            system_organization = system_organization_service.select_by_code(system_organization_code)
            new_student.system_organization_name = system_organization.system_organization_name
            new_student.system_organization_name_ja = system_organization.system_organization_name_ja
            new_student.system_organization_type = system_organization.system_organization_type
            #  新規追加(マルチテナント化対応) END

            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_student, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            # ユーザID自治体内ユニークID重複チェック
            dn_condition = Student(
                system_organization_name=new_student.system_organization_name
            )
            collision_data = self.student_model.select(
                ["user_id", "persistent_uid"],
                dn_condition,
                specify_filters=[
                    "|({user_id}=" + new_student.user_id + ")"
                    "({persistent_uid}=" + new_student.persistent_uid + ")"
                ],
            )
            if len(collision_data) > 1 or (
                len(collision_data) == 1
                and collision_data[0].user_id == new_student.user_id
                and collision_data[0].persistent_uid
                == new_student.persistent_uid
            ):
                # ユーザIDも自治体内ユニークIDが重複した場合
                # 重複レコード2つ以上、または1つで両方重複しているケース
                error_messages.append(
                    "ユーザID<{}>自治体ユニークID<{}>がすでに存在しています".format(
                        new_student.user_id, new_student.persistent_uid
                    )
                )
            elif len(collision_data) == 1:
                # ユーザIDまたは自治体内ユニークIDが重複した場合
                # ただし、両方重複しているケースは除く
                if collision_data[0].user_id == new_student.user_id:
                    # user_idが重複した場合
                    error_messages.append(
                        "ユーザID<{}>がすでに存在しています".format(new_student.user_id,)
                    )
                else:
                    # persistent_uidが重複した場合
                    error_messages.append(
                        "自治体内ユニークID<{}>がすでに存在しています".format(
                            new_student.persistent_uid
                        )
                    )
            # PIDユニークチェック(ユーザ削除テーブル)
            # 　改修（マルチテナント化対応）　START
            # 　改修（DB構成変更対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            dn_condition = Student(
                system_organization_code=new_student.system_organization_code,
                persistent_uid=new_student.persistent_uid,
            )
            ret = crud_model.select_count(
                new_student.system_organization_code,
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
                        new_student.persistent_uid
                    )
                )
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_student.relationgg) == 1 or\
                    int(new_student.relationwin) == 1 or int(new_student.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Student(
                    system_organization_name=new_student.system_organization_name
                )
                search_student = self.student_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_student.mail
                    ],
                )
                if len(search_student) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_student.mail
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
            #  新規追加(マルチテナント化対応) START
            # 環境情報取得
            environment_service = EnvironmentService(self.rds_access_object)
            environments = environment_service.select(Environment(system_organization_code=new_student.system_organization_code,
                                                                  application_id=APPLICATION_ID.Common.value,
                                                                  delete_flag=0))
            # opaqueIDの生成
            idp_entityid = environment_service.get_environment_value(environments,
                                                                     ENVIRONMENT_NAME.IDP_ENTITYID.value)
            #  新規追加(マルチテナント化対応) END
            new_student.opaque_id = self.create_opaque_id(
                new_student.persistent_uid,
                # 　改修（マルチテナント化対応）　START
                # os.environ.get("IDP_ENTITYID"),
                idp_entityid,
                # 　改修（マルチテナント化対応）　END
                os.environ.get("OPAQUE_ID_SALT"),
            )
            # 　新規追加（文科省標準の学校コード追加）　START
			# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
            # mextUidを生成(OneRoster対応：値がある場合、再採番不要)
            if not new_student.mextUid:
                new_student.mextUid = str(uuid.uuid4())
			# ↑ここまで
            # 　新規追加（文科省標準の学校コード追加）　END
            #  改修(マルチテナント化対応) START
            str_system_date = self.create_update_date_str()
            # 登録日の追加
            new_student.reg_date = str_system_date
            # 更新日付の生成
            new_student.upd_date = str_system_date
            #  改修(マルチテナント化対応) END
            # Windows連携時のみ平文パスワードの追加
            # 　改修（マルチテナント化対応）　START
            windows_cooperation_flag = environment_service.get_environment_value(environments,
                                                                                 ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value)
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                # 平文パスワードの設定
                # 復号キーの復号
                decryption_key = self.decrypt_message(
                    os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                # 暗号化
                enc_password = encrypt_aes256(
                    new_student.password, decryption_key.encode())
                new_student.enc_password = enc_password
            # 登録実行
            inserted_student = self.student_model.insert(new_student)
        except Exception as exception:
            raise (exception)
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info("### END STUDENT SERVICE INSERT ###")

        # このメソッドの返却値は挿入データ
        return inserted_student

    def search(self, student_conditions):
        """
        児童生徒を検索するサービスメソッド

        Parameters
        ----------
        student_conditions : Student
            LDAPから検索するStudent条件

        Returns
        -------
        searched_students : list
            LDAPから検索されたStudent（複数）
        """
        self.log_info("### START STUDENT SERVICE SEARCH ###")
        # 検索タイプ
        search_type = STATIC_CODE.LDAP_SEARCH_TYPE.STUDENT_LIST
        # 任意検索条件を設定
        optional_rule = ldap.LDAP_OPTIONAL_SEARCH_ATTRIBUTES[search_type]
        optional_filter = []
        if student_conditions.fiscal_year_from != None:
            optional_filter.append(
                "{fiscal_year}>=" + str(student_conditions.fiscal_year_from))
            student_conditions.fiscal_year_from = None
        if student_conditions.fiscal_year_to != None:
            optional_filter.append(
                "{fiscal_year}<=" + str(student_conditions.fiscal_year_to))
            student_conditions.fiscal_year_to = None
        for key in optional_rule:
            val = student_conditions.__dict__.get(key)
            if val == "" or val == [] or val == [""]:
                optional_filter.append("!({" + key + "}=*)")
                student_conditions.__dict__[key] = None
        # 部分一致検索条件の値に*を付加
        part_match_rule = ldap.LDAP_PART_MATCH_ATTRIBUTES[search_type]
        for key, val in student_conditions.get_dict().items():
            # 文字列以外は除外とする
            if key in part_match_rule and val.__class__ == str:
                student_conditions.__dict__[key] = "*" + val + "*"
        # enable_flag有効無効条件
        if student_conditions.enable_flag == 0:
            optional_filter.append(
                "{password_account_locked_time}=000001010000Z"
            )
        else:
            optional_filter.append(
                "!({password_account_locked_time}=000001010000Z)"
            )
        try:
            self.ldap_access_object.connect()
            searched_students = self.student_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                    STATIC_CODE.LDAP_SEARCH_TYPE.STUDENT_LIST
                ],
                student_conditions,
                student_conditions,
                optional_filter,
            )
        finally:
            self.ldap_access_object.close()

        self.log_info("### END STUDENT SERVICE SEARCH ###")
        # 学年コード、組コードとユーザーIDで昇順に並び替える
        searched_students.sort(
            key=lambda x: (
                x.grade_code,
                int(x.class_code) if x.class_code is not None else 1000,
                int(x.student_number)
                if x.student_number is not None
                else 9999999999999999,
            )
        )

        # このメソッドの返却値は検索データ
        return searched_students

    def update(self, update_student):
        """
        児童生徒情報を更新するサービスメソッド

        Parameters
        ----------
        update_student : Student
            更新するデータが含まれたStudent情報

        Returns
        -------
        updated_opeadmin : Student
            更新されたStudent情報
        """
        log_update_student = update_student.get_dict()
        log_update_student = self.delete_key(log_update_student)
        self.log_info("児童生徒情報更新 サービス 開始 , Operator : -" +
                      f" , Input : {log_update_student}")
        try:
            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (update_student.fiscal_year == year or update_student.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        update_student.fiscal_year,
                    ],
                )
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()

            #  新規追加(マルチテナント化対応) START
            # 組織情報
            system_organization_code = update_student.system_organization_code
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            system_organization = system_organization_service.select_by_code(system_organization_code)
            update_student.system_organization_name = system_organization.system_organization_name
            #  新規追加(マルチテナント化対応) END

            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                update_student, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(update_student.relationgg) == 1 or\
                    int(update_student.relationwin) == 1 or int(update_student.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Student(
                    system_organization_name=update_student.system_organization_name
                )
                search_student = self.student_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + update_student.mail,
                        "!({user_id}=" + update_student.user_id + ")"
                    ],
                )
                if len(search_student) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            update_student.mail
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
            #  新規追加(マルチテナント化対応) START
            # 環境情報取得
            # Win連携フラグチェック
            environment_service = EnvironmentService(self.rds_access_object)
            windows_cooperation_flag = environment_service.select_by_key(
                Environment(system_organization_code=update_student.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            environment_name=ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value,
                            delete_flag=0))
            #  新規追加(マルチテナント化対応) END
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                update_student = self.windows_cooperation_set(update_student)
            # 更新実行
            self.student_model.update(update_student)
            # 更新後のデータを取得する(SCIM プッシュ向け）
            updated_student = self.student_model.get(
                scim.SCIM_PUSH_STUDENT_ATTRIBUTES, update_student,
            )[0]
        except Exception as exception:
            self.log_info("処理異常 , Operator : - , Output : -")
            raise (exception)
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info(
            "児童生徒情報コミット , Operator : - , Output : -")
        log_update_student = self.delete_key(updated_student.get_dict())
        self.log_info("児童生徒情報更新 サービス 終了 , Operator : -" +
                      f" , Output : {log_update_student}")

        # このメソッドの返却値は挿入データ
        return updated_student

    def relocation_grade(self, old_student, new_student):
        """
        児童・生徒情報を更新するサービスメソッド(学年を移動する)

        Parameters
        ----------
        old_student : Student
            更新するデータが含まれたStudent情報
        new_student : Student

        Returns
        -------
        updated_student : Student
            更新されたStudent情報
        """
        self.log_info("### START STUDENT SERVICE RELOCATION GRADE UPDATE ###")
        # 児童・生徒の登録
        try:
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()

            #  新規追加(マルチテナント化対応) START
            # 組織情報
            system_organization_code = new_student.system_organization_code
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            system_organization = system_organization_service.select_by_code(system_organization_code)
            new_student.system_organization_name = system_organization.system_organization_name
            old_student.system_organization_name = new_student.system_organization_name
            #  新規追加(マルチテナント化対応) END

            # 学校学年組共通チェック、補完
            # 　改修（マルチテナント化対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_student, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            old_student.organization_name = new_student.organization_name
            # ユーザID重複チェック
            dn_condition = Student(
                system_organization_name=new_student.system_organization_name
            )
            collision_data = self.student_model.select(
                ["user_id", "persistent_uid"],
                dn_condition,
                specify_filters=["{user_id}=" + new_student.user_id],
            )
            if (
                len(collision_data) > 0
                and collision_data[0].user_id == new_student.user_id
            ):
                # user_idが重複した場合
                error_messages.append(
                    "ユーザID<{}>がすでに存在しています".format(new_student.user_id,)
                )
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_student.relationgg) == 1 or\
                    int(new_student.relationwin) == 1 or int(new_student.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Student(
                    system_organization_name=new_student.system_organization_name
                )
                search_student = self.student_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_student.mail,
                        "!({user_id}=" + old_student.user_id + ")"
                    ],
                )
                if len(search_student) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_student.mail
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
            #  新規追加(マルチテナント化対応) START
            # 環境情報取得
            # Win連携フラグチェック
            environment_service = EnvironmentService(self.rds_access_object)
            windows_cooperation_flag = environment_service.select_by_key(
                Environment(system_organization_code=new_student.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            environment_name=ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value,
                            delete_flag=0))
            #  新規追加(マルチテナント化対応) END
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                new_student = self.windows_cooperation_set(
                    new_student, old_student.user_id)
            # 組織内移動
            self.student_model.update_user_id(old_student, new_student.user_id)
            # 組織内移動後属性更新
            updated_student = self.student_model.update(new_student)
            # 更新後のデータを取得する(SCIMプッシュ向け)
            updated_student = self.student_model.get(
                scim.SCIM_PUSH_STUDENT_ATTRIBUTES, new_student,
            )[0]
        except Exception as exception:
            raise exception
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info("### END STUDENT SERVICE RELOCATION GRADE UPDATE ###")

        # このメソッドの返却値は挿入データ
        return updated_student

    def change_user_ou(self, old_student, new_student):
        """
        児童・生徒情報を更新するサービスメソッド(組織移動)

        Parameters
        ----------
        old_student : Student
            更新するデータが含まれたStudent情報
        new_student : Student

        Returns
        -------
        updated_student : Student
            更新されたStudent情報
        """
        log_old_student = old_student.get_dict()
        log_old_student = self.delete_key(log_old_student)
        log_new_student = new_student.get_dict()
        log_new_student = self.delete_key(log_new_student)
        self.log_info("児童生徒情報更新(組織移動) サービス 開始 , Operator : -" +
                      f" , Input : {log_old_student}, {log_new_student}")

        # 児童・生徒の更新
        try:
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 　改修（DB構成変更対応）　END
            #  新規追加(マルチテナント化対応) START
            # 組織情報
            system_organization_code = new_student.system_organization_code
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            system_organization = system_organization_service.select_by_code(system_organization_code)
            new_student.system_organization_name = system_organization.system_organization_name
            old_student.system_organization_name = system_organization.system_organization_name
            #  新規追加(マルチテナント化対応) END

            # ロールバック用に元データを取得
            before_dn_condition = Student(
                system_organization_name=old_student.system_organization_name
            )
            before_students = self.student_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                    STATIC_CODE.LDAP_SEARCH_TYPE.STUDENT_LIST
                ],
                before_dn_condition,
                specify_filters=["{user_id}=" + old_student.user_id],
            )
            if len(before_students) == 0:
                self.throw_error(
                    "ID_E_0004",
                    None,
                    format_message=old_student.user_id,
                )
            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (new_student.fiscal_year == year or new_student.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        new_student.fiscal_year,
                    ],
                )
            # 学校学年組共通チェック、補完
            # 　改修（DB構成変更対応）　START
            # 　改修（マルチテナント化対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_student, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            # ユーザID重複チェック
            dn_condition = Student(
                system_organization_name=new_student.system_organization_name
            )
            collision_data = self.student_model.select(
                ["user_id"],
                dn_condition,
                specify_filters=["{user_id}=" + new_student.user_id],
            )
            if (
                len(collision_data) > 0
                and collision_data[0].user_id == new_student.user_id
            ):
                # user_idが重複した場合
                error_messages.append(
                    "ユーザID<{}>がすでに存在しています".format(new_student.user_id,)
                )
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_student.relationgg) == 1 or\
                    int(new_student.relationwin) == 1 or int(new_student.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Student(
                    system_organization_name=new_student.system_organization_name
                )
                search_student = self.student_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_student.mail,
                        "!({user_id}=" + old_student.user_id + ")"
                    ],
                )
                if len(search_student) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_student.mail
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
            updated_student = {}
            #  新規追加(マルチテナント化対応) START
            # 環境情報取得
            # Win連携フラグチェック
            environment_service = EnvironmentService(self.rds_access_object)
            windows_cooperation_flag = environment_service.select_by_key(
                Environment(system_organization_code=new_student.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            environment_name=ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value,
                            delete_flag=0))
            #  新規追加(マルチテナント化対応) END
            # 　改修（マルチテナント化対応）　START
            if windows_cooperation_flag == 1:
                # 　改修（マルチテナント化対応）　END
                new_student = self.windows_cooperation_set(
                    new_student, before_students[0].user_id)
            updated_student = copy.deepcopy(new_student)
            # 属性以外は更新しないので元データを上書き
            updated_student.user_id = before_students[0].user_id
            updated_student.organization_code = before_students[0].organization_code
            updated_student.organization_name = before_students[0].organization_name
            updated_student.transfer_school_date = self.create_update_date_str()
            updated_student.from_organization_code = before_students[0].organization_code
            # 属性情報の更新
            updated_student = self.attribute_update(
                updated_student, new_student)
            updated_student.organization_code = before_students[0].organization_code
            updated_student.organization_name = before_students[0].organization_name
            # uidの更新
            updated_student = self.uid_update(
                before_students, updated_student, new_student)
            # 組織(ou)の更新
            updated_student = self.ou_update(
                before_students, updated_student, new_student)
            # 更新後のデータを取得する(SCIMプッシュ向け)
            updated_student = self.student_model.get(
                scim.SCIM_PUSH_STUDENT_ATTRIBUTES, new_student,
            )[0]
        except Exception as exception:
            self.throw_error("ID_E_0001", exception)
            raise exception
        finally:
            self.ldap_access_object.close()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info(
            "児童生徒情報コミット , Operator : - , Output : -")
        log_old_student = self.delete_key(updated_student.get_dict())
        self.log_info("児童生徒情報更新(組織移動) サービス 終了 , Operator : -" +
                      f" , Output : {log_old_student}")

        # このメソッドの返却値は挿入データ
        return updated_student

    # 　改修（マルチテナント化対応）　START
    def complement_and_alignment_user(self, student, crud_model):
        # 　改修（マルチテナント化対応）　END
        """
        学校(組織)コードチェック補完
        学年コードチェック補完
        組コードチェック補完
        表示名生成
        更新日付の設定

        Parameters
        ----------
        student : Student
            チェック 補完 対象Student情報
        crud_model : CRUDModel
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
            student.system_organization_code,
            # 　改修（DB構成変更対応）　START
            RDS_TABLE.SCHOOL_MASTER,
            # 　改修（DB構成変更対応）　END
            # 　改修（文科省標準の学校コード追加）　START
            ["school_name", "school_name_ja", "school_type", "mextOuCode"],
            # 　改修（文科省標準の学校コード追加）　END
            SchoolMaster(system_organization_code=student.system_organization_code,
                         school_code=student.organization_code, delete_flag=0),
            specific_conditions=[
                " show_no <> 0"
            ],
        )
        if len(schools) == 0:
            # 学校コード不存在時はエラー終了
            error_messages.append(
                "学校コード<{}>は存在しません".format(student.organization_code)
            )
            self.throw_error(
                "ID_E_0020", None, format_message=(",").join(error_messages)
            )
        # 学校情報補完
        student.organization_name = schools[0].school_name
        student.organization_name_ja = schools[0].school_name_ja
        student.organization_type = schools[0].school_type
        # 　新規追加（文科省標準の学校コード追加）　START
        student.mextOuCode = schools[0].mextOuCode
        # 　新規追加（文科省標準の学校コード追加）　END
        # 学年コードチェック(学年コードが空の時は学年名も空とする)
        if student.grade_code:
            master_grades = crud_model.select(
                student.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.GRADE_MASTER,
                # 　改修（DB構成変更対応）　END
                ["grade_code", "grade_name_ja"],
                GradeMaster(
                    system_organization_code=student.system_organization_code,
                    school_code=student.organization_code,
                    grade_code=student.grade_code,
                    delete_flag=0,
                ),
            )
            if len(master_grades) == 0:
                error_messages.append(
                    "学校<{}>には学年コード<{}>が存在しません".format(
                        student.organization_name_ja, student.grade_code
                    )
                )
            else:
                student.grade_name = master_grades[0].grade_name_ja
        else:
            student.grade_name = student.grade_code
        # 組コードチェック(組コードがNoneの時は組コード、組名を空値とする)
        # 組コードはint型なので、単純なbool比較だと0がFalseになるので注意
        if student.class_code or student.class_code == 0:
            master_classes = crud_model.select(
                student.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.CLASS_MASTER,
                # 　改修（DB構成変更対応）　END
                ["class_code", "class_name_ja"],
                ClassMaster(
                    system_organization_code=student.system_organization_code,
                    school_code=student.organization_code,
                    class_code=student.class_code,
                    delete_flag=0,
                ),
            )
            if len(master_classes) == 0:
                error_messages.append(
                    "学校<{}>には組コード<{}>が存在しません".format(
                        student.organization_name_ja, student.class_code
                    )
                )
            else:
                student.class_name = master_classes[0].class_name_ja
        else:
            student.class_code = ""
            student.class_name = ""
        # 　改修（マルチテナント化対応）　END
        # 表示名の作成
        student.display_name = f"{student.sur_name}　{student.given_name}"
        # 更新日付の生成
        student.upd_date = self.create_update_date_str()
        # パスワードの名称がIFで異なるため移し替え
        student.user_password = student.password

        return error_messages

    def windows_cooperation_set(self, update_student, before_user_id=""):
        """
        Windows連携サービスメソッド

        Parameters
        ----------
        update_student : Student
            更新するデータが含まれたOpeadmin情報

        Returns
        -------
        updated_student : Student
            更新されたStudent情報
        """
        dn_condition = Student(
            system_organization_name=update_student.system_organization_name
        )
        # 組織移動の場合、元のユーザIDで検索
        if before_user_id != "":
            search_user_id = before_user_id
        else:
            search_user_id = update_student.user_id
        collision_data = self.student_model.select(
            ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                STATIC_CODE.LDAP_SEARCH_TYPE.STUDENT_LIST
            ],
            dn_condition,
            specify_filters=["{user_id}=" + search_user_id],
        )
        if len(collision_data) > 0:
            update_student.befrelationwin = self.befreletionwin_set(
                collision_data)
            # メールアドレス変更可チェック
            if ((update_student.befrelationwin == "1" or update_student.befrelationwin == "2") and
                    (collision_data[0].mail != update_student.mail)):
                self.throw_error(
                    "ID_E_0042",
                    None,
                    format_message=[
                        update_student.mail,
                    ],
                )
            if (update_student.befrelationwin == "2" and update_student.relationwin == 1) or (
                    update_student.befrelationwin == "1" and update_student.relationwin == 2):
                self.throw_error(
                    "ID_E_0043",
                    None,
                )
            if (update_student.password is not None):
                # 平文パスワードの設定
                # 復号キーの復号
                decryption_key = self.decrypt_message(
                    os.environ.get("LDAP_PASSWORD_ENCRYPT_KEY"))
                # 暗号化
                enc_password = encrypt_aes256(
                    update_student.password, decryption_key.encode())
                update_student.enc_password = enc_password
        return update_student

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

    def attribute_update(self, updated_student, new_student):
        """
        児童・生徒情報の属性情報を更新する

        Parameters
        ----------
        updated_student : Student
            更新する児童生徒エンティティ

        Returns
        -------
        updated_student : Student
            更新結果
        """
        try:
            updated_student = self.student_model.update_dn(
                updated_student, new_student)
        except Exception as exception:
            self.throw_error("ID_E_0001", exception)
            raise exception

        return updated_student

    def uid_update(self, before_students, updated_student, new_student):
        """
        児童・生徒情報のuidを更新する

        Parameters
        ----------
        before_students : Student
            ロールバック用の児童生徒エンティティ
        updated_student : Student
            更新対象となる児童生徒エンティティ
        new_student : Student
            移動先情報が含まれている児童生徒エンティティ

        Returns
        -------
        updated_student : Student
            更新結果
        """
        try:
            updated_student = self.student_model.update_user_id(
                updated_student, new_student.user_id)
        except Exception as exception:
            # ロールバック（属性情報を戻す）
            self.attribute_update(updated_student, before_students)
            self.throw_error("ID_E_0001", exception)
            raise exception

        return updated_student

    def ou_update(self, before_students, updated_student, new_student):
        """
        児童・生徒情報のuidを更新する

        Parameters
        ----------
        before_students : Student
            ロールバック用の児童生徒エンティティ
        updated_student : Student
            更新対象となる児童生徒エンティティ
        new_student : Student
            移動先情報が含まれている児童生徒エンティティ

        Returns
        -------
        updated_student : Student
            更新結果
        """
        try:
            updated_student.user_id = new_student.user_id
            updated_student = self.student_model.update_user_change_ou(
                updated_student, new_student)
        except Exception as exception:
            # ロールバック（uidを戻す）
            updated_student = self.uid_update(
                before_students, updated_student, before_students)
            # ロールバック（属性情報を戻す）
            self.attribute_update(updated_student, before_students)
            self.throw_error("ID_E_0001", exception)
            raise exception

        return updated_student

    def delete(self, delete_student, delete_student_data):
        """
        児童・生徒情報を削除する

        Parameters
        ----------
        delete_student : Student
            学校を削除するための学校エンティティ

        Returns
        -------
        delete_student : Student
            削除結果
        """
        self.log_info("### START STUDENT DELETE SERVICE ###")
        error_messages = []
        try:
            self.ldap_access_object.connect()

            # 児童・生徒情報取得
            # 対象ユーザの存在チェック
            dn_condition = Student(
                system_organization_name=delete_student.system_organization_name
            )
            student_data = self.student_model.select(
                ldap.LDAP_ALLOW_SEARCH_ATTRIBUTES[
                    STATIC_CODE.LDAP_SEARCH_TYPE.STUDENT_LIST_DELETE
                ],
                dn_condition,
                specify_filters=["{user_id}=" + delete_student.user_id,
                                 "{organization_name}=" + delete_student.organization_name],
            )
            if (len(student_data) == 0):
                # 対象ユーザが存在しなかった場合
                error_messages.append(
                    "対象のユーザ<{}>はすでに削除されています".format(delete_student.user_id)
                )
            # コード整合性エラーがあった場合例外発生
            if error_messages:
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
            self.student_model.insert_user(
                student_data[0], delete_student_data)
            self.ldap_access_object.connect()
            # LDAPのユーザ削除
            self.student_model.delete(student_data[0])
            self.ldap_access_object.close()
            # ユーザ削除テーブルに削除対象ユーザのコミット
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.commit()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END
        except Exception as exception:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.rollback()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END
            self.throw_error("ID_E_0003", exception)
        self.log_info("### END STUDENT DELETE SERVICE ###")
        return student_data[0].get_dict()

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
        self.log_info("### START STUDENT SERVICE GET ORGANIZATION NAME ###")
        try:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 　改修（マルチテナント化対応）　START
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
        except Exception as exception:
            raise exception
        finally:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        self.log_info("### END STUDENT SERVICE GET ORGANIZATION NAME ###")

        # このメソッドの返却値は検索データ
        return {"total": total_school, "datas": searched_schools}

    def search_delete_student(self, student_conditions):
        """
        無効ユーザを検索するサービスメソッド

        Parameters
        ----------
        student_conditions : Student
            検索条件の格納された児童生徒エンティティ

        Returns
        -------
        return : dict('total': int, 'datas': list[SchoolMaster])
            DB検索結果（総計とデータ）
        """
        self.log_info("### START STUDENT SERVICE SEARCH DELETE STUDENT ###")

        try:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()
            # 部分一致検索設定
            search_type = STATIC_CODE.RDS_SEARCH_TYPE.DELETE_USER_LIST
            # 　改修（DB構成変更対応）　END
            specific_conditions = []
            condition = student_conditions.get_dict()
            # 　改修（DB構成変更対応）　START
            for key in rds.SELECT_LIKE_VALUE_COLMUNS[search_type]:
                # 　改修（DB構成変更対応）　END
                if key in condition and condition[key] is not None:
                    condition[key] = f"%{condition[key]}%"
                    # 　改修（DB構成変更対応）　START
                    specific_conditions.append(
                        f"{key} LIKE %({key})s"
                    )
                    # 　改修（DB構成変更対応）　END
            # 　新規追加（マルチテナント化対応）　START
            search_student_conditions = Student(**condition)
            # 　新規追加（マルチテナント化対応）　END
            # 削除した当日を検索対象に入れない
            now = Base.now()
            today = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
            specific_conditions.append("entry_date_time<'" + str(today) + "'")
            # 　改修（マルチテナント化対応）　START
            # 　改修（DB構成変更対応）　START
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            # 検索対象件数を取得
            total_student = crud_model.select_count(
                student_conditions.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                # 　改修（DB構成変更対応）　END
                search_student_conditions,
                exclusion_where_columns=[
                    "sur_name", "given_name", "limit", "offset"],
                specific_conditions=specific_conditions,
            )
            # 検索実行
            searched_students = crud_model.select(
                student_conditions.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                rds.ALLOW_SEARCH_COLMUNS[
                    RDS_SEARCH_TYPE.DELETE_USER_LIST
                ] + ["DATE_FORMAT(entry_date_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS entry_date_time"],
                # 　改修（DB構成変更対応）　END
                search_student_conditions,
                exclusion_where_columns=[
                    "sur_name", "given_name", "limit", "offset"],
                specific_conditions=specific_conditions,
                # 　改修（DB構成変更対応）　START
                specific_tail="LIMIT %(limit)s OFFSET %(offset)s",
                # 　改修（DB構成変更対応）　END
            )
            # 　改修（マルチテナント化対応）　END
        except Exception as exception:
            raise exception
        finally:
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

        # 文字列に変換
        for searched_student in searched_students:
            if searched_student.gender is not None:
                searched_student.gender = str(searched_student.gender)
            else:
                searched_student.gender = ""

        self.log_info("### END STUDENT SERVICE SEARCH DELETE STUDENT ###")

        return {"total": total_student, "datas": searched_students}

    def recreate(self, new_student):
        """
        児童生徒を再登録するサービスメソッド

        Parameters
        ----------
        new_student : Student
            LDAPに登録するStudent情報

        Returns
        -------
        inserted_student : Student
            LDAPに登録されたStudent情報
        """
        new_student_dict = self.delete_key(new_student.get_dict())
        self.log_info("児童生徒再登録, Operator : -" +
                      f" , Input : {new_student_dict}")
        try:
            self.log_info("バリデーション, Operator : - , Input : -")

            # 有効年度の今年度・翌年度チェック
            year = Base.now().year
            month = Base.now().month
            if month >= 1 and month <= 3:
                year = year - 1
            if not (new_student.fiscal_year == year or new_student.fiscal_year == year + 1):
                self.throw_error(
                    "ID_E_0039",
                    None,
                    format_message=[
                        new_student.fiscal_year,
                    ],
                )
            self.ldap_access_object.connect()
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.begin()

            #  新規追加(マルチテナント化対応) START
            # 組織情報
            system_organization_code = new_student.system_organization_code
            system_organization_service = SystemOrganizationService(self.rds_access_object)
            system_organization = system_organization_service.select_by_code(system_organization_code)
            new_student.system_organization_name = system_organization.system_organization_name
            new_student.system_organization_name_ja = system_organization.system_organization_name_ja
            new_student.system_organization_type = system_organization.system_organization_type
            #  新規追加(マルチテナント化対応) END

            # 　改修（マルチテナント化対応）　START
            # 学校学年組共通チェック、補完
            crud_model = CRUDModel(self.rds_access_object)
            # 　改修（DB構成変更対応）　END
            error_messages = self.complement_and_alignment_user(
                new_student, crud_model
            )
            # 　改修（マルチテナント化対応）　END
            # ユーザID自治体内ユニークID重複チェック
            dn_condition = Student(
                system_organization_name=new_student.system_organization_name
            )
            collision_data = self.student_model.select(
                ["user_id", "persistent_uid"],
                dn_condition,
                specify_filters=[
                    "|({user_id}=" + new_student.user_id + ")"
                    "({persistent_uid}=" + new_student.persistent_uid + ")"
                ],
            )
            if len(collision_data) > 1 or (
                len(collision_data) == 1
                and collision_data[0].user_id == new_student.user_id
                and collision_data[0].persistent_uid
                == new_student.persistent_uid
            ):
                # ユーザIDも自治体内ユニークIDが重複した場合
                # 重複レコード2つ以上、または1つで両方重複しているケース
                error_messages.append(
                    "ユーザID<{}>自治体ユニークID<{}>がすでに存在しています".format(
                        new_student.user_id, new_student.persistent_uid
                    )
                )
            elif len(collision_data) == 1:
                # ユーザIDまたは自治体内ユニークIDが重複した場合
                # ただし、両方重複しているケースは除く
                if collision_data[0].user_id == new_student.user_id:
                    # user_idが重複した場合
                    error_messages.append(
                        "ユーザID<{}>がすでに存在しています".format(new_student.user_id,)
                    )
                else:
                    # persistent_uidが重複した場合
                    error_messages.append(
                        "自治体内ユニークID<{}>がすでに存在しています".format(
                            new_student.persistent_uid
                        )
                    )
            # 　新規追加（案件７．メールの一意性チェック）　START
            # Azure連携あり、またはGoogle連携ありモードの場合、メールの一意性チェックを実施する。
            if int(new_student.relationgg) == 1 or\
                    int(new_student.relationwin) == 1 or int(new_student.relationwin) == 2:
                # LDAPから対象ユーザの検索
                dn_condition = Student(
                    system_organization_name=new_student.system_organization_name
                )
                search_student = self.student_model.select(
                    ["user_id"],
                    dn_condition,
                    specify_filters=[
                        "{mail}=" + new_student.mail
                    ],
                )
                if len(search_student) > 0:
                    error_messages.append(
                        "メールアドレス<{}>がすでに存在しています".format(
                            new_student.mail
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
            student_conditions = Student(persistent_uid=new_student.persistent_uid,
                                         limit=1, offset=0)

            # 　改修（マルチテナント化対応）　START
            total_student = crud_model.select_count(
                new_student.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                # 　改修（DB構成変更対応）　END
                student_conditions,
                exclusion_where_columns=[
                    "limit", "offset"],
                specific_conditions=specific_conditions,
            )
            # 　改修（マルチテナント化対応）　END
            if total_student < 1:
                self.throw_error(
                    "ID_E_0041",
                    None,
                    str(total_student),
                    format_message=new_student.persistent_uid,
                )
            # 検索実行

            # 　改修（マルチテナント化対応）　START
            searched_students = crud_model.select(
                new_student.system_organization_code,
                # 　改修（DB構成変更対応）　START
                RDS_TABLE.DELETE_USER,
                rds.ALLOW_SEARCH_COLMUNS[
                    RDS_SEARCH_TYPE.DELETE_USER_LIST
                ] + ["DATE_FORMAT(entry_date_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS entry_date_time"],
                # 　改修（DB構成変更対応）　END
                student_conditions,
                exclusion_where_columns=[
                    "limit", "offset"],
                specific_conditions=specific_conditions,
                # 　改修（DB構成変更対応）　START
                specific_tail="LIMIT %(limit)s OFFSET %(offset)s",
                # 　改修（DB構成変更対応）　END
            )
            # 　改修（マルチテナント化対応）　END
            # opaqueIDの生成
            new_student.opaque_id = searched_students[0].opaque_id
            # 　新規追加（文科省標準の学校コード追加）　START
            # mextUid
            new_student.mextUid = searched_students[0].mextUid
            # 　削除（画面学校のmextOuCodeを設定）　START
            # # mextOuCode
            # new_student.mextOuCode = searched_students[0].mextOuCode
            # 　削除（画面学校のmextOuCodeを設定）　END
            # 　新規追加（文科省標準の学校コード追加）　END
            # ユーザ削除テーブルから対象のユーザを削除
            # 　改修（マルチテナント化対応）　START
            # self.student_model.delete_rds_user(new_student)
            delete_student = Student(system_organization_code=new_student.system_organization_code,
                                     persistent_uid=new_student.persistent_uid)
            crud_model.delete(new_student.system_organization_code,
                              RDS_TABLE.DELETE_USER,
                              delete_student)
            # 　改修（マルチテナント化対応）　END
            # 移動元学校と異動日の追加
            new_student.transfer_school_date = self.create_update_date_str()
            new_student.from_organization_code = searched_students[0].organization_code
            #  改修(マルチテナント化対応) START
            str_system_date = self.create_update_date_str()
            # 登録日の追加
            new_student.reg_date = str_system_date
            # 更新日付の生成
            new_student.upd_date = str_system_date
            #  改修(マルチテナント化対応) END

            #  新規追加(マルチテナント化対応) START
            environment_service = EnvironmentService(self.rds_access_object)
            windows_cooperation_flag = environment_service.select_by_key(
                Environment(system_organization_code=new_student.system_organization_code,
                            application_id=APPLICATION_ID.Common.value,
                            environment_name=ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value,
                            delete_flag=0))
            # Windows連携時のみ平文パスワードの追加
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
                    new_student.password, decryption_key.encode())
                new_student.enc_password = enc_password
            # 登録実行
            inserted_student = self.student_model.insert(new_student)
            # 登録正常終了
            # 　改修（DB構成変更対応）　START
            self.rds_access_object.commit()
            self.rds_access_object.close()
            # 　改修（DB構成変更対応）　END

            inserted_student_dict = self.delete_key(
                inserted_student.get_dict())
            self.log_info("児童生徒再登録 コミット, Operator : -" +
                          f" , Output : {inserted_student_dict}")
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
        return inserted_student
