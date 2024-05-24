# coding: utf-8
import os
import time
import traceback

from app.config import csv_roster_setting
from common.base_service import BaseService
from common.lambda_error import LambdaError
from common.rds_access_object import RdsAccessObject
from common.ldap_access_object import LdapAccessObject
from common.config.static_code import RDS_TABLE, APPLICATION_ID, ENVIRONMENT_NAME
from common.master_entities.school_master import SchoolMaster
from common.master_entities.grade_master import GradeMaster
from common.master_entities.class_master import ClassMaster
from common.master_entities.subject_master import SubjectMaster
from common.crud_model import CRUDModel
from common.system_organization_service import SystemOrganizationService
from common.environment_service import EnvironmentService
from common.master_entities.environment import Environment

from app.entities.user import User
from app.models.user_model import UserModel


class MasterService(BaseService):
    """
    マスター情報を扱うサービス
    """

    def __init__(self, rds_access_object, ldap_access_object):
        self.ldap_access_object = ldap_access_object
        self.rds_access_object = rds_access_object
        self.crud_model = CRUDModel(self.rds_access_object)
        self.user_model = UserModel(self.ldap_access_object)
        self.db_retry_count = int(os.environ.get("DB_RETRY_COUNT"))
        self.db_retry_interval = int(os.environ.get("DB_RETRY_INTERVAL"))
        self.is_retry = False

    def select_master_codes(self, row_info, system_organization_code):
        """
        学年コード、組コード、教科コード情報を一括取得する

        Parameters
        ----------
        row_info :
            検索対象ユーザ
        system_organization_code : String
            検索対象組織コード

        Returns
        -------
        masters : dict
            {
                "is_school_exist" : bool,
                "grade_codes": list[String],
                "class_codes": list[String],
                "subject_codes": list[String]
            }
        """
        self.log_info("### START MASTER SERVICE SELECT MASTER CODE ###")
        self.log_info("マスタ情報取得 , Operator : -" + f" , Input : {row_info.role}、{row_info.schoolCode}")

        school_code = row_info.schoolCode
        status = row_info.status
        role = row_info.role
        ret_value = {
            "school_master": None,
            "grades": None,
            "classes": None,
            "subjects": None,
            "top_organization": None,
            "system_organization": None,
            "environment": None,
            "delete_persistent_uids": None,
            "is_retry_last": False
        }

        i = 0
        while i < self.db_retry_count:
            is_retry_exception = True
            try:
                self.rds_access_object.begin()
                # 組織情報取得
                try:
                    if ret_value['system_organization'] is None:
                        system_organization_service = SystemOrganizationService(self.rds_access_object)
                        system_organization = system_organization_service.select_by_code(system_organization_code)
                        ret_value['system_organization'] = system_organization
                except Exception as exception:
                    # マスタが取得できない場合、リトライ処理が行わない
                    if exception.__class__ == LambdaError and exception.error_code == 'ID_E_0020':
                        is_retry_exception = False
                        raise exception
                    else:
                        raise exception

                # 組織の環境情報取得
                try:
                    if status != "tobedeleted" and ret_value['environment'] is None:
                        environment_service = EnvironmentService(self.rds_access_object)
                        environments = environment_service.select(
                            Environment(system_organization_code=system_organization_code,
                                        application_id=APPLICATION_ID.Common.value,
                                        delete_flag=0))

                        google_cooperation_flag = environment_service.get_environment_value(
                            environments,
                            ENVIRONMENT_NAME.GOOGLE_COOPERATION_FLAG.value)
                        windows_cooperation_flag = environment_service.get_environment_value(
                            environments,
                            ENVIRONMENT_NAME.WINDOWS_COOPERATION_FLAG.value)
                        idp_entityid = environment_service.get_environment_value(
                            environments,
                            ENVIRONMENT_NAME.IDP_ENTITYID.value)
                        environment = {"google_cooperation_flag": google_cooperation_flag,
                                       "windows_cooperation_flag": windows_cooperation_flag,
                                       "idp_entityid": idp_entityid}
                        ret_value['environment'] = environment
                except Exception as exception:
                    # マスタが取得できない場合、リトライ処理が行わない
                    if exception.__class__ == LambdaError and exception.error_code == 'ID_E_0020':
                        is_retry_exception = False
                        raise exception
                    else:
                        raise exception

                # OPE管理者の場合、表示No=0のレコードのみ検索
                if row_info.role == "admin":
                    specific_conditions = [" (show_no = 0)"]
                else:
                    specific_conditions = [" (school_code=%(school_code)s or show_no = 0)"]
                if ret_value['school_master'] is None:
                    # 学校コード取得
                    schools = self.crud_model.select(
                        system_organization_code,
                        RDS_TABLE.SCHOOL_MASTER,
                        ["school_code", "school_name", "school_name_ja",
                         "school_type", "show_no", "mextOuCode"],
                        SchoolMaster(system_organization_code=system_organization_code,
                                     school_code=school_code,
                                     delete_flag=0),
                        exclusion_where_columns=["school_code"],
                        specific_conditions=specific_conditions,
                    )

                    for school in schools:
                        if school.school_code == school_code:
                            school_master = school
                            ret_value['school_master'] = school_master
                        if school.show_no == 0:
                            top_organization = school
                            ret_value['top_organization'] = top_organization

                    # OPE管理者の場合、学校マスタの表示No=0の学校に所属する
                    if role == "admin":
                        ret_value["school_master"] = ret_value['top_organization']

                if ret_value['school_master'] is None or ret_value['top_organization'] is None:
                    return ret_value
                else:
                    # OPE管理者の場合、学年、組、教科が取得不要
                    if role != "admin":
                        if ret_value['grades'] is None:
                            # 学年コード取得
                            grades = self.crud_model.select(
                                system_organization_code,
                                RDS_TABLE.GRADE_MASTER,
                                ["grade_code", "grade_name_ja"],
                                GradeMaster(system_organization_code=system_organization_code,
                                            school_code=school_code,
                                            delete_flag=0),
                            )
                            ret_value['grades'] = grades

                        if ret_value['classes'] is None:
                            # 組コード取得
                            classes = self.crud_model.select(
                                system_organization_code,
                                RDS_TABLE.CLASS_MASTER,
                                ["class_code", "class_name_ja"],
                                ClassMaster(system_organization_code=system_organization_code,
                                            school_code=school_code,
                                            delete_flag=0),
                            )
                            ret_value['classes'] = classes

                        if ret_value['subjects'] is None:
                            # 教科コード取得
                            subjects = self.crud_model.select(
                                system_organization_code,
                                RDS_TABLE.SUBJECT_MASTER,
                                ["subject_code"],
                                SubjectMaster(system_organization_code=system_organization_code,
                                              school_code=school_code,
                                              delete_flag=0),
                            )
                            ret_value['subjects'] = subjects

                    if ret_value['delete_persistent_uids'] is None:
                        delete_users = self.crud_model.select(
                            system_organization_code,
                            RDS_TABLE.DELETE_USER,
                            ["persistent_uid"],
                            User(system_organization_code=system_organization_code),
                        )
                        ret_value['delete_persistent_uids'] = [user.persistent_uid for user in delete_users]
                break
            except Exception as exception:
                if is_retry_exception is False:
                    return ret_value
                if (i + 1) < self.db_retry_count:
                    self.log_info(f"RetryError : Retry processing(select_master_codes) for the {i + 1} time.")
                    # 次の試行まで待つ
                    time.sleep(self.db_retry_interval)
                    i += 1
                    continue
                else:
                    ret_value["is_retry_last"] = True
                    # トレースバック
                    self.log_error(traceback.format_exc())
                    return ret_value
            finally:
                self.rds_access_object.close()

        self.log_info("### END MASTER SERVICE SELECT MASTER CODE ###")

        # コードデータの配列にして返す
        return ret_value

    def get_user_info_by_id(self, system_organization_name, userMasterIdentifier, user_id):
        """
        ユーザー情報をLDAPから取得する

        Parameters
        ----------
        system_organization_name : str
             組織名
        userMasterIdentifier : str
            検索対象のユーザー一意識別子
        user_id : str
            検索対象のユーザID

        Returns
        -------
        ret : dict {
                    "is_success" : bool,
                        実行結果
                    "user_data" : list
                        検索結果
                    }
        """
        self.log_info("### START GET USER INFORMATION FUNCTION ###")
        ret = {}
        self.is_retry = False
        try:
            persistent_uid = userMasterIdentifier.replace("-", "")
            # ユーザ情報取得
            dn_condition = User(
                system_organization_name=system_organization_name
            )

            user_data = self.user_model.select_no_retry(
                csv_roster_setting.user_search,
                dn_condition,
                specify_filters=[
                    "|(|({persistent_uid}=" + persistent_uid + ")"
                    "({user_id}=" + user_id + "))"
                    "(mextUid=" + userMasterIdentifier + ")"
                ],
            )

            # ret["is_success"] = True
            # ret["user_data"] = user_data
        except Exception as exception:
            # トレースバック
            self.log_error(traceback.format_exc())
            # ret["is_success"] = False
            if self.user_model.is_retry:
                self.is_retry = self.user_model.is_retry
                # ret["exception"] = str(exception)
            raise exception
        self.log_info("### END GET USER INFORMATION FUNCTION ###")
        return user_data

    def get_del_ldap_datas(self, system_organization_name, row_info):
        """
        削除のLDAP情報を取得する

        Parameters
        ----------
        system_organization_name : 組織名
        row_info : CSVファイルデータ

            LDAPから検索するUser条件

        Returns
        -------
        seach_datas : list
            LDAPから検索されたユーザ（複数）
        """
        self.log_info("### START GET DELETE LDAP INFORMATION FUNCTION ###")
        self.is_retry = False
        # ユーザ情報取得
        # 対象ユーザの存在チェック
        dn_condition = User(
            system_organization_name=system_organization_name
        )
        try:
            user_datas = self.user_model.select_no_retry(
                ["user_id", "organization_name", "mextUid", "grade_code", "organization_code"],
                dn_condition,
                specify_filters=["mextUid=" + row_info.userMasterIdentifier],
            )
        except Exception as exception:
            # トレースバック
            self.log_error(traceback.format_exc())
            if self.user_model.is_retry:
                self.is_retry = self.user_model.is_retry
            raise exception

        self.log_info("### END GET DELETE LDAP INFORMATION FUNCTION ###")

        # このメソッドの返却値は検索データ
        return user_datas
