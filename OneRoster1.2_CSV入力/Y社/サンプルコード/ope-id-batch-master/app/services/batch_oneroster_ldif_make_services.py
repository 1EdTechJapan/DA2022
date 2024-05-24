# coding: utf-8
import csv
import traceback

import paramiko
import boto3
import io
import os
import re
import time

from common.base_service import BaseService
from common.config import csv_setting
from common.config.static_code import RDS_TABLE
from common.crud_model import CRUDModel
from common.lambda_error import LambdaError
from common.ldap_access_object import LdapAccessObject
from common.master_entities.school_master import SchoolMaster
from common.rds_access_object import RdsAccessObject
from common.s3_access_object import S3AccessObject
from common.apply_info import ApplyInfo
from app.entities.oneroster_user import Oneroster_user
from app.config import csv_roster_setting
from app.models.user_model import UserModel
from common.system_organization_service import SystemOrganizationService


class LdifFileMakeService(BaseService):
    """
    一括モード：LDIFファイルを生成サービス
    """

    # 　改修（マルチテナント化対応）　START
    def __init__(self, system_organization_code):

        self.ldap_access_object = LdapAccessObject(
            os.environ.get("LDAP_URL"),
            os.environ.get("LDAP_USER"),
            os.environ.get("LDAP_PASSWORD"),
        )
        self.system_organization_code = system_organization_code
        self.rds_access_object = RdsAccessObject(
            os.environ.get("RDS_RESOURCE_ARN"),
            os.environ.get("RDS_SECRET_ARN"),
            os.environ.get("RDS_DATABASE"),
        )
        self.crud_model = CRUDModel(self.rds_access_object)
        self.s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)

    def ldif_file_make(self,
                       oneroster_directory,
                       add_teacher,
                       add_student,
                       add_admin,
                       mod1_teacher,
                       mod1_student,
                       mod1_admin,
                       mod2_teacher,
                       mod2_student,
                       before_info,
                       master_codes,
                       file_current):

        """
        一括モード：LDIFファイルを生成サービス
        """

        self.log_info("### START LDIF FILE MAKE SERVICE ###")

        # 学校情報
        school = master_codes["school_master"]
        system_organization_code = self.system_organization_code
        all_schools_code_dict = {system_organization_code: master_codes["top_organization"], school.school_code: school}
        # 組情報
        all_classes = master_codes.get("classes")
        all_classes_dict = {}
        if all_classes:
            for tmp_class in all_classes:
                all_classes_dict[tmp_class.class_code] = tmp_class

        # 学年情報
        all_grades = master_codes.get("grades")
        all_grades_dict = {}
        if all_grades:
            for grade in all_grades:
                all_grades_dict[grade.grade_code] = grade
        # 申込情報
        teacher_add_apply_info = {}
        teacher_mod1_apply_info = {}
        teacher_mod2_apply_info = {}
        student_add_apply_info = {}
        student_mod1_apply_info = {}
        student_mod2_apply_info = {}
        admin_add_apply_info = {}
        admin_mod1_apply_info = {}

        # 処理に対するldifの実行時間
        system_time = self.create_update_date_str()
        self.log_info(f"system_time: {system_time}")

        # ファイル名により、処理を切り分ける
        if len(add_teacher) > 0:
            # 教員一括登録
            ldif_teacher_add_data = []
            idp_entityid = master_codes["environment"]["idp_entityid"]
            # 教員データの件数分、教員一括登録ldifデータを生成
            for dict_data in add_teacher:
                self.edit_ldif_teacher_add(
                    teacher_add_apply_info,
                    ldif_teacher_add_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    all_grades_dict,
                    all_classes_dict,
                    idp_entityid)
            # 教員一括登録ldifデータあるの場合
            if len(ldif_teacher_add_data) > 0:
                # 教員一括登録ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/add'
                self.output_ldif_file_to_s3(out_file_path, f"add_teacher_{file_current}.ldif", ldif_teacher_add_data)
        if len(add_admin) > 0:
            # OPE管理者一括登録
            ldif_admin_add_data = []
            idp_entityid = master_codes["environment"]["idp_entityid"]
            # OPE管理者データの件数分、OPE管理者一括登録ldifデータを生成
            for dict_data in add_admin:
                self.edit_ldif_admin_add(
                    admin_add_apply_info,
                    ldif_admin_add_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    idp_entityid)
            # OPE管理者一括登録ldifデータあるの場合
            if len(ldif_admin_add_data) > 0:
                # 教員一括登録ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/add'
                self.output_ldif_file_to_s3(out_file_path, f"add_admin_{file_current}.ldif", ldif_admin_add_data)

        if len(mod1_teacher) > 0:
            # 教員一括更新（組織変更なし）
            ldif_teacher_mod1_data = []
            # 教員データの件数分、教員一括更新ldifデータを生成
            for dict_data in mod1_teacher:
                self.edit_ldif_teacher_mod1(
                    teacher_mod1_apply_info,
                    ldif_teacher_mod1_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    all_grades_dict,
                    all_classes_dict,
                    before_info)
            # 教員一括更新ldifデータあるの場合
            if len(ldif_teacher_mod1_data) > 0:
                # 教員一括更新ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/update'
                self.output_ldif_file_to_s3(out_file_path, f"update_teacher_{file_current}.ldif",
                                            ldif_teacher_mod1_data)

        if len(mod1_admin) > 0:
            # OPE管理者一括更新（組織変更なし）
            ldif_admin_mod1_data = []
            # OPE管理者データの件数分、OPE管理者一括更新ldifデータを生成
            for dict_data in mod1_admin:
                self.edit_ldif_admin_mod1(
                    admin_mod1_apply_info,
                    ldif_admin_mod1_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    before_info)
            # OPE管理者一括更新ldifデータあるの場合
            if len(ldif_admin_mod1_data) > 0:
                # OPE管理者一括更新ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/update'
                self.output_ldif_file_to_s3(out_file_path, f"update_admin_{file_current}.ldif",
                                            ldif_admin_mod1_data)

        if len(mod2_teacher) > 0:
            # 教員一括異動（組織変更）
            ldif_teacher_mod2_data = []
            # 教員データの件数分、教員一括更新ldifデータを生成
            for dict_data in mod2_teacher:
                self.edit_ldif_teacher_mod2(
                    teacher_mod2_apply_info,
                    ldif_teacher_mod2_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    all_grades_dict,
                    all_classes_dict,
                    before_info
                )
            # 教員一括異動ldifデータあるの場合
            if len(ldif_teacher_mod2_data) > 0:
                # 教員一括異動ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/transfer'
                self.output_ldif_file_to_s3(out_file_path, f"transfer_teacher_{file_current}.ldif",
                                            ldif_teacher_mod2_data)

        if len(add_student) > 0:
            # 児童・生徒一括登録
            ldif_student_add_data = []
            idp_entityid = master_codes["environment"]["idp_entityid"]
            # 児童・生徒データの件数分、児童・生徒一括登録ldifデータを生成
            for dict_data in add_student:
                self.edit_ldif_student_add(
                    student_add_apply_info,
                    ldif_student_add_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    all_grades_dict,
                    all_classes_dict,
                    school.school_code,
                    idp_entityid
                )
            # 児童・生徒一括登録ldifデータあるの場合
            if len(ldif_student_add_data) > 0:
                # 児童・生徒一括登録ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/add'
                self.output_ldif_file_to_s3(out_file_path, f"add_student_{file_current}.ldif", ldif_student_add_data)

        if len(mod1_student) > 0:
            # 児童・生徒進級
            ldif_student_mod1_data = []
            # 児童・生徒データの件数分、児童・生徒進級ldifデータを生成
            for dict_data in mod1_student:
                self.edit_ldif_student_mod1(
                    student_mod1_apply_info,
                    ldif_student_mod1_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    all_grades_dict,
                    all_classes_dict,
                    school.school_code,
                    before_info
                )
            # 児童・生徒進級ldifデータあるの場合
            if len(ldif_student_mod1_data) > 0:
                # 児童・生徒進級ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/update'
                self.output_ldif_file_to_s3(out_file_path, f"update_student_{file_current}.ldif",
                                            ldif_student_mod1_data)

        if len(mod2_student) > 0:
            # 児童・生徒進学
            ldif_student_mod2_data = []
            # 児童・生徒データの件数分、児童・生徒進学ldifデータを生成
            for dict_data in mod2_student:
                self.edit_ldif_student_mod2(
                    student_mod2_apply_info,
                    ldif_student_mod2_data,
                    dict_data,
                    system_organization_code,
                    system_time,
                    all_schools_code_dict,
                    all_grades_dict,
                    all_classes_dict,
                    school.school_code,
                    before_info,
                )
            # 児童・生徒進学ldifデータあるの場合
            if len(ldif_student_mod2_data) > 0:
                # 児童・生徒進学ldifファイルをS3へ出力
                out_file_path = f'{oneroster_directory}/ldif/transfer'
                self.output_ldif_file_to_s3(out_file_path, f"transfer_student_{file_current}.ldif",
                                            ldif_student_mod2_data)

        result = self.excute_ldif_file(
            file_current,
            oneroster_directory,
            student_add_apply_info,
            student_mod1_apply_info,
            student_mod2_apply_info,
            teacher_add_apply_info,
            teacher_mod1_apply_info,
            teacher_mod2_apply_info,
            admin_add_apply_info,
            admin_mod1_apply_info,
        )

        self.log_info("### END LDIF FILE MAKE SERVICE ###")

        return result

    def output_ldif_file_to_s3(self, out_file_path, file_name, file_data):
        """
        ldifファイルを出力し、S3に格納
        :param file_path:ファイルパス
        :param file_name:ファイル名
        :param file_data:ファイル内容
        """
        self.log_info("### START MASTER SERVICE OUTPUT LDIF FILE TO S3 ###")
        self.log_info(f"OUTPUT FILE :<{file_name}>")

        csv_io = io.StringIO()
        csv_writer = csv.writer(
            csv_io, quotechar='', quoting=csv.QUOTE_NONE, lineterminator="\n", escapechar="\\"
        )

        for val in file_data:
            tmp_val = val.encode('utf-8').decode("utf-8")
            csv_writer.writerow([tmp_val])
        csv_value = csv_io.getvalue().replace('\\', '')

        self.s3_access_object.export(
            out_file_path + "/" + file_name,
            csv_value,
        )

        self.log_info("### END MASTER SERVICE OUTPUT LDIF FILE TO S3 ###")

    def edit_ldif_teacher_add(
            self,
            teacher_add_apply_info,
            ldif_teacher_add_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            all_grades_dict,
            all_classes_dict,
            idp_entityid):
        """
        「教員新規」のldifファイルを作成
        :param teacher_add_apply_info: 戻り値
        :param ldif_teacher_add_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param all_grades_dict:学年マスタ情報
        :param all_classes_dict:組マスタ情報
        :param idp_entityid:idp

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF TEACHER ADD ###")

        ldif_data = []

        # user_id
        user_id = data_dict.get("user_id")
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織コード(学校コード)
        organization_code = data_dict.get("organization_code")
        # 下部組織名(英語)(学校名)
        organization_name = all_schools_dict[organization_code].school_name

        ldif_data.append(f"dn: uid={user_id},ou={organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        # 組織名
        ldif_data.append(f"o: {system_organization_name}")
        # 組織名(日本語)
        system_organization_name_ja = all_schools_dict[system_organization_code].school_name_ja
        ldif_data.append(f"o;lang-ja: {system_organization_name_ja}")
        # 組織コード
        ldif_data.append(f"jsFedO: {system_organization_code}")
        # 組織タイプ
        system_organization_type = all_schools_dict[system_organization_code].school_type
        ldif_data.append(f"jsFedOType: {system_organization_type}")
        # 下部組織名(英語)(学校名)
        ldif_data.append(f"ou: {organization_name}")
        # 下部組織名(日本語)(学校名)
        organization_name_ja = all_schools_dict[organization_code].school_name_ja
        ldif_data.append(f"ou;lang-ja: {organization_name_ja}")
        # 下部組織コード(学校コード)
        ldif_data.append(f"jsFedOu: {organization_code}")
        # 下部組織タイプ(学校タイプ)
        organization_type = all_schools_dict[organization_code].school_type
        ldif_data.append(f"jsFedOuType: {organization_type}")
        # uid
        ldif_data.append(f"uid: {user_id}")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"gender: {gender}")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        # ユーザＩＤ(暗号化)
        persistent_uid = data_dict.get("persistent_uid")
        # opaqueIDの生成
        js_fed_opaque_id = self.create_opaque_id(
            persistent_uid,
            idp_entityid,
            os.environ.get("OPAQUE_ID_SALT")
        )
        ldif_data.append(f"jsFedOpaqueID: {js_fed_opaque_id}")
        # 自治体内ユニークのID
        persistent_uid = data_dict.get("persistent_uid")
        ldif_data.append(f"PersistentUid: {persistent_uid}")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"mail: {mail}")
        # 学年コード 追加
        grade_code = data_dict.get("grade_code")
        if grade_code:
            ldif_data.append(f"jsFedGrade: {grade_code}")
            # 学年表示名　(日本語) 追加
            grade_name = all_grades_dict[grade_code].grade_name_ja
            ldif_data.append(f"jsFedJaGradeName: {grade_name}")
        # 組コード 追加
        class_code = data_dict.get("class_code")
        if class_code:
            ldif_data.append(f"jsFedClass: {class_code}")
            # 組表示名　(日本語) 追加
            class_name = all_classes_dict[class_code].class_name_ja
            ldif_data.append(f"jsFedJaClassName: {class_name}")
        # 職階
        edu_person_affiliation = "teacher"
        ldif_data.append(f"eduPersonAffiliation: {edu_person_affiliation}")
        # 権限
        role = data_dict.get("role")
        ldif_data.append(f"jsFedRole: {role}")
        # 教科
        subject_code = data_dict.get("subject_code")
        if subject_code:
            ldif_data.append(f"jsFedSubject: {subject_code}")
        # 登録日時
        ldif_data.append(f"RegDate: {system_time}")
        # Google 連携フラグ
        relationgg = data_dict.get("relationgg")
        ldif_data.append(f"relationgg: {relationgg}")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        ldif_data.append(f"relationwin: {relationwin}")
        # befrelationwin
        befrelationwin = 0
        ldif_data.append(f"befrelationwin: {befrelationwin}")
        # 年度 追加
        fiscal_year = data_dict.get("fiscal_year")
        ldif_data.append(f"jsFedFiscalYear: {fiscal_year}")
        # mextUid
        mextUid = data_dict.get('mextUid')
        ldif_data.append(f"mextUid: {mextUid}")
        # mextOuCode
        mextOuCode = all_schools_dict[organization_code].mextOuCode
        ldif_data.append(f"mextOuCode: {mextOuCode}")
        # userPassword
        user_password = data_dict.get("password")
        ldif_data.append(f"userPassword: {user_password}")
        # パスワード変更フラグ
        password_flg = 0
        ldif_data.append(f"Passwordflg: {password_flg}")
        # 更新日時
        ldif_data.append(f"UpdDate: {system_time}")
        # 固定値
        ldif_data.append(f"jasn:'""'")
        ldif_data.append(f"cn:'""'")
        ldif_data.append(f"pwdAttribute: userPassword")
        ldif_data.append(f"pwdLockout: TRUE")
        ldif_data.append(f"pwdLockoutDuration: 900")
        ldif_data.append(f"pwdMaxFailure: 10")
        ldif_data.append(f"pwdFailureCountInterval: 900")
        ldif_data.append(f"objectClass: top")
        ldif_data.append(f"objectClass: eduPerson")
        ldif_data.append(f"objectClass: eduMember")
        ldif_data.append(f"objectClass: jsFedPerson")
        ldif_data.append(f"objectClass: jaPerson")
        ldif_data.append(f"objectClass: gakuninPerson")
        ldif_data.append(f"objectClass: inetOrgPerson")
        ldif_data.append(f"objectClass: jaOrganization")
        ldif_data.append(f"objectClass: jsOpePerson")
        ldif_data.append(f"objectClass: mext")
        ldif_data.append(f"objectClass: pwdPolicy")
        ldif_data.append(f"\n")

        ldif_teacher_add_data.extend(ldif_data)
        # 申込情報
        teacher_add_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="teacher11",
            target_id=user_id,
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF TEACHER ADD ###")

    def edit_ldif_admin_add(
            self,
            admin_add_apply_info,
            ldif_admin_add_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            idp_entityid):
        """
        「OPE管理者新規登録」のldifファイルを作成
        :param admin_add_apply_info: 戻り値
        :param ldif_admin_add_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param idp_entityid:idp

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF ADMIN ADD ###")

        ldif_data = []

        # user_id
        user_id = data_dict.get("user_id")
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織コード(学校コード)
        organization_code = data_dict.get("organization_code")
        # 下部組織名(英語)(学校名)
        organization_name = all_schools_dict[organization_code].school_name

        ldif_data.append(f"dn: uid={user_id},ou={organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        # 組織名
        ldif_data.append(f"o: {system_organization_name}")
        # 組織名(日本語)
        system_organization_name_ja = all_schools_dict[system_organization_code].school_name_ja
        ldif_data.append(f"o;lang-ja: {system_organization_name_ja}")
        # 組織コード
        ldif_data.append(f"jsFedO: {system_organization_code}")
        # 組織タイプ
        system_organization_type = all_schools_dict[system_organization_code].school_type
        ldif_data.append(f"jsFedOType: {system_organization_type}")
        # 下部組織名(英語)(学校名)
        ldif_data.append(f"ou: {organization_name}")
        # 下部組織名(日本語)(学校名)
        organization_name_ja = all_schools_dict[organization_code].school_name_ja
        ldif_data.append(f"ou;lang-ja: {organization_name_ja}")
        # 下部組織コード(学校コード)
        ldif_data.append(f"jsFedOu: {organization_code}")
        # 下部組織タイプ(学校タイプ)
        organization_type = all_schools_dict[organization_code].school_type
        ldif_data.append(f"jsFedOuType: {organization_type}")
        # uid
        ldif_data.append(f"uid: {user_id}")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"gender: {gender}")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        # ユーザＩＤ(暗号化)
        persistent_uid = data_dict.get("persistent_uid")
        # opaqueIDの生成
        js_fed_opaque_id = self.create_opaque_id(
            persistent_uid,
            idp_entityid,
            os.environ.get("OPAQUE_ID_SALT")
        )
        ldif_data.append(f"jsFedOpaqueID: {js_fed_opaque_id}")
        # 自治体内ユニークのID
        persistent_uid = data_dict.get("persistent_uid")
        ldif_data.append(f"PersistentUid: {persistent_uid}")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"mail: {mail}")
        # 職階
        edu_person_affiliation = "admin"
        ldif_data.append(f"eduPersonAffiliation: {edu_person_affiliation}")
        # 権限
        role = data_dict.get("role")
        ldif_data.append(f"jsFedRole: {role}")
        # 職階
        title_code = data_dict.get("title_code")
        ldif_data.append(f"jsFedTitle: {title_code}")
        # 登録日時
        ldif_data.append(f"RegDate: {system_time}")
        # Google 連携フラグ
        relationgg = data_dict.get("relationgg")
        ldif_data.append(f"relationgg: {relationgg}")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        ldif_data.append(f"relationwin: {relationwin}")
        # befrelationwin
        befrelationwin = 0
        ldif_data.append(f"befrelationwin: {befrelationwin}")
        # mextUid
        mextUid = data_dict.get('mextUid')
        ldif_data.append(f"mextUid: {mextUid}")
        # mextOuCode
        mextOuCode = all_schools_dict[organization_code].mextOuCode
        ldif_data.append(f"mextOuCode: {mextOuCode}")
        # userPassword
        user_password = data_dict.get("password")
        ldif_data.append(f"userPassword: {user_password}")
        # パスワード変更フラグ
        password_flg = 0
        ldif_data.append(f"Passwordflg: {password_flg}")
        # 更新日時
        ldif_data.append(f"UpdDate: {system_time}")
        # 固定値
        ldif_data.append(f"jasn:'""'")
        ldif_data.append(f"cn:'""'")
        ldif_data.append(f"pwdAttribute: userPassword")
        ldif_data.append(f"pwdLockout: TRUE")
        ldif_data.append(f"pwdLockoutDuration: 900")
        ldif_data.append(f"pwdMaxFailure: 10")
        ldif_data.append(f"pwdFailureCountInterval: 900")
        ldif_data.append(f"objectClass: top")
        ldif_data.append(f"objectClass: eduPerson")
        ldif_data.append(f"objectClass: eduMember")
        ldif_data.append(f"objectClass: jsFedPerson")
        ldif_data.append(f"objectClass: jaPerson")
        ldif_data.append(f"objectClass: gakuninPerson")
        ldif_data.append(f"objectClass: inetOrgPerson")
        ldif_data.append(f"objectClass: jaOrganization")
        ldif_data.append(f"objectClass: jsOpePerson")
        ldif_data.append(f"objectClass: mext")
        ldif_data.append(f"objectClass: pwdPolicy")
        ldif_data.append(f"\n")

        ldif_admin_add_data.extend(ldif_data)
        # 申込情報
        admin_add_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="admin11",
            target_id=user_id,
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF ADMIN ADD ###")

    def edit_ldif_student_add(
            self,
            student_add_apply_info,
            ldif_student_add_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            all_grades_dict,
            all_classes_dict,
            organization_code,
            idp_entityid):
        """
        「児童・生徒新規」のldifファイルを作成
        :param student_add_apply_info: 戻り値
        :param ldif_student_add_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param all_grades_dict:学年マスタ情報
        :param all_classes_dict:組マスタ情報
        :param organization_code:学校コード
        :param idp_entityid idp

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF STUDENT ADD ###")

        ldif_data = []

        # 文字型（１～256）「学校コード」＋「学年コード」＋「ログインID」等
        user_id = "{0}{1}{2}".format(
            organization_code,
            data_dict.get("grade_code"),
            data_dict.get("user_id"),
        )
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織名(英語)(学校名)
        organization_name = all_schools_dict[organization_code].school_name

        ldif_data.append(f"dn: uid={user_id},ou={organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        # 組織名
        ldif_data.append(f"o: {system_organization_name}")
        # 組織名(日本語)
        system_organization_name_ja = all_schools_dict[system_organization_code].school_name_ja
        ldif_data.append(f"o;lang-ja: {system_organization_name_ja}")
        # 組織コード
        ldif_data.append(f"jsFedO: {system_organization_code}")
        # 組織タイプ
        system_organization_type = all_schools_dict[system_organization_code].school_type
        ldif_data.append(f"jsFedOType: {system_organization_type}")
        # 下部組織名(英語)(学校名)
        ldif_data.append(f"ou: {organization_name}")
        # 下部組織名(日本語)(学校名)
        organization_name_ja = all_schools_dict[organization_code].school_name_ja
        ldif_data.append(f"ou;lang-ja: {organization_name_ja}")
        # 下部組織コード(学校コード)
        ldif_data.append(f"jsFedOu: {organization_code}")
        # 下部組織タイプ(学校タイプ)
        organization_type = all_schools_dict[organization_code].school_type
        ldif_data.append(f"jsFedOuType: {organization_type}")
        # uid
        ldif_data.append(f"uid: {user_id}")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"gender: {gender}")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        # 自治体内ユニークのID
        persistent_uid = data_dict.get("persistent_uid")
        ldif_data.append(f"PersistentUid: {persistent_uid}")
        # ユーザＩＤ(暗号化)
        # opaqueIDの生成
        js_fed_opaque_id = self.create_opaque_id(
            persistent_uid,
            idp_entityid,
            os.environ.get("OPAQUE_ID_SALT")
        )
        ldif_data.append(f"jsFedOpaqueID: {js_fed_opaque_id}")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"mail: {mail}")
        # 学年コード 追加
        grade_code = data_dict.get("grade_code")
        ldif_data.append(f"jsFedGrade: {grade_code}")
        # 学年表示名　(日本語) 追加
        grade_name = all_grades_dict[grade_code].grade_name_ja
        ldif_data.append(f"jsFedJaGradeName: {grade_name}")
        # 組コード 追加
        class_code = data_dict.get("class_code")
        if class_code:
            ldif_data.append(f"jsFedClass: {class_code}")
            # 組表示名　(日本語) 追加
            class_name = all_classes_dict[class_code].class_name_ja
            ldif_data.append(f"jsFedJaClassName: {class_name}")
        # 出席番号
        student_number = data_dict.get("student_number")
        if student_number:
            ldif_data.append(f"jsFedStudentNumber: {student_number}")
        # 職位
        edu_person_affiliation = "student"
        ldif_data.append(f"eduPersonAffiliation: {edu_person_affiliation}")
        # 権限
        role = "student"
        ldif_data.append(f"jsFedRole: {role}")
        # 登録日時
        ldif_data.append(f"RegDate: {system_time}")
        # Google 連携フラグ
        relationgg = data_dict.get("relationgg")
        ldif_data.append(f"relationgg: {relationgg}")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        ldif_data.append(f"relationwin: {relationwin}")
        # befrelationwin
        befrelationwin = 0
        ldif_data.append(f"befrelationwin: {befrelationwin}")
        # 年度 追加
        fiscal_year = data_dict.get("fiscal_year")
        ldif_data.append(f"jsFedFiscalYear: {fiscal_year}")
        # mextUid
        mextUid = data_dict.get('mextUid')
        ldif_data.append(f"mextUid: {mextUid}")
        # mextOuCode
        mextOuCode = all_schools_dict[organization_code].mextOuCode
        ldif_data.append(f"mextOuCode: {mextOuCode}")
        # userPassword
        user_password = data_dict.get("password")
        ldif_data.append(f"userPassword: {user_password}")
        # パスワード変更フラグ
        password_flg = 0
        ldif_data.append(f"Passwordflg: {password_flg}")
        # 更新日時
        ldif_data.append(f"UpdDate: {system_time}")
        # 固定値
        ldif_data.append(f"jasn: '""'")
        ldif_data.append(f"cn: '""'")
        ldif_data.append(f"pwdAttribute: userPassword")
        ldif_data.append(f"pwdLockout: TRUE")
        ldif_data.append(f"pwdLockoutDuration: 900")
        ldif_data.append(f"pwdMaxFailure: 10")
        ldif_data.append(f"pwdFailureCountInterval: 900")
        ldif_data.append(f"objectClass: top")
        ldif_data.append(f"objectClass: eduPerson")
        ldif_data.append(f"objectClass: eduMember")
        ldif_data.append(f"objectClass: jsFedPerson")
        ldif_data.append(f"objectClass: jaPerson")
        ldif_data.append(f"objectClass: gakuninPerson")
        ldif_data.append(f"objectClass: inetOrgPerson")
        ldif_data.append(f"objectClass: jaOrganization")
        ldif_data.append(f"objectClass: jsOpePerson")
        ldif_data.append(f"objectClass: mext")
        ldif_data.append(f"objectClass: pwdPolicy")
        ldif_data.append(f"\n")

        ldif_student_add_data.extend(ldif_data)
        # 申込情報
        student_add_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="student11",
            target_id=data_dict.get("user_id"),
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF STUDENT ADD ###")

    def edit_ldif_student_mod1(
            self,
            student_mod1_apply_info,
            ldif_student_mod1_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            all_grades_dict,
            all_classes_dict,
            organization_code,
            before_info):
        """
        「児童・生徒進級」のldifファイルを作成
        :param student_mod1_apply_info: 戻り値
        :param ldif_student_mod1_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param all_grades_dict:学年マスタ情報
        :param all_classes_dict:組マスタ情報
        :param organization_code:学校コード
        :param before_info:ユーザー情報

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF STUDENT MOD1 ###")

        ldif_data = []
        before_user_id = "{0}{1}{2}".format(
            organization_code,
            data_dict.get("before_grade_code"),
            data_dict.get("before_user_id"),
        )
        # 文字型（１～256）「学校コード」＋「学年コード」＋「ログインID」等
        user_id = "{0}{1}{2}".format(
            organization_code,
            data_dict.get("grade_code"),
            data_dict.get("user_id"),
        )
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織名(英語)(学校名)
        organization_name = all_schools_dict[organization_code].school_name

        if before_user_id != user_id:
            ldif_data.append(f"dn: uid={before_user_id},ou={organization_name},o={system_organization_name}"
                             f",dc=eop-core,dc=org")
            ldif_data.append(f"changetype: modrdn")
            ldif_data.append(f"newrdn: uid={user_id}")
            ldif_data.append(f"deleteoldrdn: 0")
            ldif_data.append(f"newsuperior: ou={organization_name},o={system_organization_name}"
                             f",dc=eop-core,dc=org")
            ldif_data.append(f"\n")
        ldif_data.append(f"dn: uid={user_id},ou={organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modify")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"replace: sn;lang-ja")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        ldif_data.append(f"-")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"replace: givenName;lang-ja")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        ldif_data.append(f"-")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"replace: displayName;lang-ja")
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        ldif_data.append(f"-")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"replace: gender")
            ldif_data.append(f"gender: {gender}")
            ldif_data.append(f"-")
        if not gender and before_info[before_user_id].gender:
            ldif_data.append(f"delete:gender")
            ldif_data.append(f"-")
        # 年度
        fiscal_year = data_dict.get("fiscal_year")
        ldif_data.append(f"replace: jsFedFiscalYear")
        ldif_data.append(f"jsFedFiscalYear: {fiscal_year}")
        ldif_data.append(f"-")
        # ユーザーID
        if before_user_id != user_id:
            ldif_data.append(f"replace: uid")
            ldif_data.append(f"uid: {user_id}")
            ldif_data.append(f"-")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"replace: mail")
            ldif_data.append(f"mail: {mail}")
            ldif_data.append(f"-")
        if not mail and before_info[before_user_id].mail:
            ldif_data.append(f"delete:mail")
            ldif_data.append(f"-")
        # 下部組織名(日本語)(学校名)
        new_organization_name_ja = all_schools_dict[organization_code].school_name_ja
        ldif_data.append(f"replace: ou;lang-ja")
        ldif_data.append(f"ou;lang-ja: {new_organization_name_ja}")
        ldif_data.append(f"-")
        # 学年コード
        if data_dict.get("before_grade_code") != data_dict.get("grade_code"):
            grade_code = data_dict.get("grade_code")
            ldif_data.append(f"replace: jsFedGrade")
            ldif_data.append(f"jsFedGrade: {grade_code}")
            ldif_data.append(f"-")
            # 学年表示名　(日本語)
            grade_name = all_grades_dict[grade_code].grade_name_ja
            ldif_data.append(f"replace: jsFedJaGradeName")
            ldif_data.append(f"jsFedJaGradeName: {grade_name}")
            ldif_data.append(f"-")
        # 組コード
        class_code = data_dict.get("class_code")
        if class_code:
            ldif_data.append(f"replace: jsFedClass")
            ldif_data.append(f"jsFedClass: {class_code}")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            class_name = all_classes_dict[class_code].class_name_ja
            ldif_data.append(f"replace: jsFedJaClassName")
            ldif_data.append(f"jsFedJaClassName: {class_name}")
            ldif_data.append(f"-")
        if not class_code and before_info[before_user_id].class_code:
            ldif_data.append(f"delete:jsFedClass")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            ldif_data.append(f"delete:jsFedJaClassName")
            ldif_data.append(f"-")

        # 出席番号
        student_number = data_dict.get("student_number")
        if student_number:
            ldif_data.append(f"replace: jsFedStudentNumber")
            ldif_data.append(f"jsFedStudentNumber: {student_number}")
            ldif_data.append(f"-")
        if not student_number and before_info[before_user_id].student_number:
            ldif_data.append(f"delete:jsFedStudentNumber")
            ldif_data.append(f"-")

        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        # befrelationwin
        upd_date = before_info[before_user_id].upd_date
        if upd_date[0:8] != system_time[0:8]:
            ldif_data.append(f"replace: befrelationwin")
            ldif_data.append(f"befrelationwin: {relationwin}")
            ldif_data.append(f"-")
        # 更新日時
        ldif_data.append(f"replace: updDate")
        ldif_data.append(f"updDate: {system_time}")
        ldif_data.append(f"\n")

        ldif_student_mod1_data.extend(ldif_data)
        # 申込情報
        student_mod1_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="student12",
            target_id=data_dict.get("user_id"),
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF STUDENT MOD1 ###")

    def edit_ldif_student_mod2(
            self,
            student_mod2_apply_info,
            ldif_student_mod2_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            all_grades_dict,
            all_classes_dict,
            new_organization_code,
            before_info
    ):
        """
        「児童・生徒進学」のldifファイルを作成
        :param student_mod2_apply_info: 戻り値
        :param ldif_student_mod2_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param all_grades_dict:学年マスタ情報
        :param all_classes_dict:組マスタ情報
        :param new_organization_code:学校コード
        :param before_info:ユーザー情報

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF STUDENT MOD2 ###")

        ldif_data = []
        before_user_id = "{0}{1}{2}".format(
            data_dict.get("before_organization_code"),
            data_dict.get("before_grade_code_transfer"),
            data_dict.get("before_user_id_transfer"),
        )
        # 文字型（１～256）「学校コード」＋「学年コード」＋「ログインID」等
        user_id = "{0}{1}{2}".format(
            new_organization_code,
            data_dict.get("grade_code"),
            data_dict.get("user_id"),
        )
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織名(英語)(学校名)
        new_organization_name = all_schools_dict[new_organization_code].school_name
        # 進学前下部組織コード
        before_organization_code = data_dict.get("before_organization_code")
        # 進学前下部組織名(英語)(学校名)
        before_organization_name = before_info[before_user_id].organization_name

        ldif_data.append(f"dn: uid={before_user_id},ou={before_organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modrdn")
        ldif_data.append(f"newrdn: uid={user_id}")
        ldif_data.append(f"deleteoldrdn: 0")
        ldif_data.append(f"newsuperior: ou={new_organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"\n")
        ldif_data.append(f"dn: uid={user_id},ou={new_organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modify")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"replace: sn;lang-ja")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        ldif_data.append(f"-")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"replace: givenName;lang-ja")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        ldif_data.append(f"-")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"replace: displayName;lang-ja")
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        ldif_data.append(f"-")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"replace: gender")
            ldif_data.append(f"gender: {gender}")
            ldif_data.append(f"-")
        if not gender and before_info[before_user_id].gender:
            ldif_data.append(f"delete:gender")
            ldif_data.append(f"-")
        # 年度
        fiscal_year = data_dict.get("fiscal_year")
        ldif_data.append(f"replace: jsFedFiscalYear")
        ldif_data.append(f"jsFedFiscalYear: {fiscal_year}")
        ldif_data.append(f"-")
        # ユーザーID
        ldif_data.append(f"replace: uid")
        ldif_data.append(f"uid: {user_id}")
        ldif_data.append(f"-")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"replace: mail")
            ldif_data.append(f"mail: {mail}")
            ldif_data.append(f"-")
        if not mail and before_info[before_user_id].mail:
            ldif_data.append(f"delete:mail")
            ldif_data.append(f"-")
        # 下部組織タイプ(学校タイプ)
        new_organization_type = all_schools_dict[new_organization_code].school_type
        ldif_data.append(f"replace: jsFedOuType")
        ldif_data.append(f"jsFedOuType: {new_organization_type}")
        ldif_data.append(f"-")
        # 下部組織名(英語)(学校名)
        ldif_data.append(f"replace: ou")
        ldif_data.append(f"ou: {new_organization_name}")
        ldif_data.append(f"-")
        # 下部組織名(日本語)(学校名)
        new_organization_name_ja = all_schools_dict[new_organization_code].school_name_ja
        ldif_data.append(f"replace: ou;lang-ja")
        ldif_data.append(f"ou;lang-ja: {new_organization_name_ja}")
        ldif_data.append(f"-")
        # 下部組織コード(学校コード)
        ldif_data.append(f"replace: jsFedOu")
        ldif_data.append(f"jsFedOu: {new_organization_code}")
        ldif_data.append(f"-")
        # 異動元下部組織コード(学校コード)
        ldif_data.append(f"replace: jsFedSourceOu")
        ldif_data.append(f"jsFedSourceOu: {before_organization_code}")
        ldif_data.append(f"-")
        # 異動日
        ldif_data.append(f"replace: jsFedTransferDate")
        ldif_data.append(f"jsFedTransferDate: {system_time}")
        ldif_data.append(f"-")
        # 学年コード
        grade_code = data_dict.get("grade_code")
        ldif_data.append(f"replace: jsFedGrade")
        ldif_data.append(f"jsFedGrade: {grade_code}")
        ldif_data.append(f"-")
        # 学年表示名　(日本語)
        grade_name = all_grades_dict[grade_code].grade_name_ja
        ldif_data.append(f"replace: jsFedJaGradeName")
        ldif_data.append(f"jsFedJaGradeName: {grade_name}")
        ldif_data.append(f"-")
        # 組コード
        class_code = data_dict.get("class_code")
        if class_code:
            ldif_data.append(f"replace: jsFedClass")
            ldif_data.append(f"jsFedClass: {class_code}")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            class_name = all_classes_dict[class_code].class_name_ja
            ldif_data.append(f"replace: jsFedJaClassName")
            ldif_data.append(f"jsFedJaClassName: {class_name}")
            ldif_data.append(f"-")
        if not class_code and before_info[before_user_id].class_code:
            ldif_data.append(f"delete:jsFedClass")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            ldif_data.append(f"delete:jsFedJaClassName")
            ldif_data.append(f"-")
        # 出席番号
        student_number = data_dict.get("student_number")
        if student_number:
            ldif_data.append(f"replace: jsFedStudentNumber")
            ldif_data.append(f"jsFedStudentNumber: {student_number}")
            ldif_data.append(f"-")
        if not student_number and before_info[before_user_id].student_number:
            ldif_data.append(f"delete:jsFedStudentNumber")
            ldif_data.append(f"-")
        # 更新日時
        ldif_data.append(f"replace: updDate")
        ldif_data.append(f"updDate: {system_time}")
        ldif_data.append(f"-")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        # befrelationwin
        upd_date = before_info[before_user_id].upd_date
        if upd_date[0:8] != system_time[0:8]:
            ldif_data.append(f"replace: befrelationwin")
            ldif_data.append(f"befrelationwin: {relationwin}")
            ldif_data.append(f"-")
        # mextOuCode
        mextOuCode = all_schools_dict[new_organization_code].mextOuCode
        ldif_data.append(f"replace: mextOuCode")
        ldif_data.append(f"mextOuCode: {mextOuCode}")
        ldif_data.append(f"\n")

        ldif_student_mod2_data.extend(ldif_data)
        # 申込情報
        student_mod2_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="student14",
            target_id=data_dict.get("user_id"),
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=new_organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF STUDENT MOD2 ###")

    def edit_ldif_teacher_mod1(
            self,
            teacher_mod1_apply_info,
            ldif_teacher_mod1_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            all_grades_dict,
            all_classes_dict,
            before_info):
        """
        「教員更新」のldifファイルを作成
        :param teacher_mod1_apply_info: 戻り値
        :param ldif_teacher_mod1_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param all_grades_dict:学年マスタ情報
        :param all_classes_dict:組マスタ情報
        :param before_info:ユーザー情報

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF TEACHER MOD1 ###")

        ldif_data = []

        # user_id
        user_id = data_dict.get("user_id")
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織コード(学校コード)
        organization_code = data_dict.get("organization_code")
        # 下部組織名(英語)(学校名)
        organization_name = all_schools_dict[organization_code].school_name

        ldif_data.append(f"dn: uid={user_id},ou={organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modify")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"replace: sn;lang-ja")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        ldif_data.append(f"-")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"replace: givenName;lang-ja")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        ldif_data.append(f"-")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"replace: displayName;lang-ja")
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        ldif_data.append(f"-")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"replace: gender")
            ldif_data.append(f"gender: {gender}")
            ldif_data.append(f"-")
        if not gender and before_info[user_id].gender:
            ldif_data.append(f"delete:gender")
            ldif_data.append(f"-")
        # 年度
        fiscal_year = data_dict.get("fiscal_year")
        ldif_data.append(f"replace: jsFedFiscalYear")
        ldif_data.append(f"jsFedFiscalYear: {fiscal_year}")
        ldif_data.append(f"-")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"replace: mail")
            ldif_data.append(f"mail: {mail}")
            ldif_data.append(f"-")
        if not mail and before_info[user_id].mail:
            ldif_data.append(f"delete:mail")
            ldif_data.append(f"-")
        # 権限
        role = data_dict.get("role")
        ldif_data.append(f"replace: jsFedRole")
        ldif_data.append(f"jsFedRole: {role}")
        ldif_data.append(f"-")
        # 下部組織名(日本語)(学校名)
        new_organization_name_ja = all_schools_dict[organization_code].school_name_ja
        ldif_data.append(f"replace: ou;lang-ja")
        ldif_data.append(f"ou;lang-ja: {new_organization_name_ja}")
        ldif_data.append(f"-")
        # 教科
        subject_code = data_dict.get("subject_code")
        if subject_code:
            ldif_data.append(f"replace: jsFedSubject")
            ldif_data.append(f"jsFedSubject: {subject_code}")
            ldif_data.append(f"-")
        if not subject_code and before_info[user_id].subject_code:
            ldif_data.append(f"delete:jsFedSubject")
            ldif_data.append(f"-")
        # 学年コード
        grade_code = data_dict.get("grade_code")
        if grade_code:
            ldif_data.append(f"replace: jsFedGrade")
            ldif_data.append(f"jsFedGrade: {grade_code}")
            ldif_data.append(f"-")
            # 学年表示名　(日本語)
            grade_name = all_grades_dict[grade_code].grade_name_ja
            ldif_data.append(f"replace: jsFedJaGradeName")
            ldif_data.append(f"jsFedJaGradeName: {grade_name}")
            ldif_data.append(f"-")
        if not grade_code and before_info[user_id].grade_code:
            ldif_data.append(f"delete:jsFedGrade")
            ldif_data.append(f"-")
            # 学年表示名　(日本語)
            ldif_data.append(f"delete:jsFedJaGradeName")
            ldif_data.append(f"-")
        # 組コード
        class_code = data_dict.get("class_code")
        if class_code:
            ldif_data.append(f"replace: jsFedClass")
            ldif_data.append(f"jsFedClass: {class_code}")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            class_name = all_classes_dict[class_code].class_name_ja
            ldif_data.append(f"replace: jsFedJaClassName")
            ldif_data.append(f"jsFedJaClassName: {class_name}")
            ldif_data.append(f"-")
        if not class_code and before_info[user_id].class_code:
            ldif_data.append(f"delete:jsFedClass")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            ldif_data.append(f"delete:jsFedJaClassName")
            ldif_data.append(f"-")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        # befrelationwin
        upd_date = before_info[user_id].upd_date
        if upd_date[0:8] != system_time[0:8]:
            ldif_data.append(f"replace: befrelationwin")
            ldif_data.append(f"befrelationwin: {relationwin}")
            ldif_data.append(f"-")
        # 更新日時
        ldif_data.append(f"replace: updDate")
        ldif_data.append(f"updDate: {system_time}")
        ldif_data.append(f"\n")

        ldif_teacher_mod1_data.extend(ldif_data)
        # 申込情報
        teacher_mod1_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="teacher12",
            target_id=user_id,
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF TEACHER MOD1 ###")

    def edit_ldif_admin_mod1(
            self,
            admin_mod1_apply_info,
            ldif_admin_mod1_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            before_info):
        """
        「OPE管理者更新」のldifファイルを作成
        :param admin_mod1_apply_info: 戻り値
        :param ldif_admin_mod1_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param before_info:ユーザー情報

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF ADMIN MOD1 ###")

        ldif_data = []

        # user_id
        user_id = data_dict.get("user_id")
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 下部組織コード(学校コード)
        organization_code = data_dict.get("organization_code")
        # 下部組織名(英語)(学校名)
        organization_name = all_schools_dict[organization_code].school_name

        ldif_data.append(f"dn: uid={user_id},ou={organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modify")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"replace: sn;lang-ja")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        ldif_data.append(f"-")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"replace: givenName;lang-ja")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        ldif_data.append(f"-")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"replace: displayName;lang-ja")
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        ldif_data.append(f"-")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"replace: gender")
            ldif_data.append(f"gender: {gender}")
            ldif_data.append(f"-")
        if not gender and before_info[user_id].gender:
            ldif_data.append(f"delete:gender")
            ldif_data.append(f"-")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"replace: mail")
            ldif_data.append(f"mail: {mail}")
            ldif_data.append(f"-")
        if not mail and before_info[user_id].mail:
            ldif_data.append(f"delete:mail")
            ldif_data.append(f"-")
        # 権限
        role = data_dict.get("role")
        ldif_data.append(f"replace: jsFedRole")
        ldif_data.append(f"jsFedRole: {role}")
        ldif_data.append(f"-")
        # 下部組織名(日本語)(学校名)
        new_organization_name_ja = all_schools_dict[organization_code].school_name_ja
        ldif_data.append(f"replace: ou;lang-ja")
        ldif_data.append(f"ou;lang-ja: {new_organization_name_ja}")
        ldif_data.append(f"-")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        # befrelationwin
        upd_date = before_info[user_id].upd_date
        if upd_date[0:8] != system_time[0:8]:
            ldif_data.append(f"replace: befrelationwin")
            ldif_data.append(f"befrelationwin: {relationwin}")
            ldif_data.append(f"-")
        # 更新日時
        ldif_data.append(f"replace: updDate")
        ldif_data.append(f"updDate: {system_time}")
        ldif_data.append(f"\n")

        ldif_admin_mod1_data.extend(ldif_data)
        # 申込情報
        admin_mod1_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="admin12",
            target_id=user_id,
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF ADMIN MOD1 ###")

    def edit_ldif_teacher_mod2(
            self,
            teacher_mod2_apply_info,
            ldif_teacher_mod2_data,
            data_dict,
            system_organization_code,
            system_time,
            all_schools_dict,
            all_grades_dict,
            all_classes_dict,
            before_info):
        """
        「教員更新」のldifファイルを作成
        :param teacher_mod2_apply_info: 戻り値
        :param ldif_teacher_mod2_data: 戻り値
        :param data_dict:ユーザー情報
        :param system_organization_code:組織コード
        :param system_time:システム時間
        :param all_schools_dict:学校マスタ情報
        :param all_grades_dict:学年マスタ情報
        :param all_classes_dict:組マスタ情報
        :param before_info:ユーザー情報

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF TEACHER MOD2 ###")

        ldif_data = []

        # user_id
        user_id = data_dict.get("user_id")
        # 組織名
        system_organization_name = all_schools_dict[system_organization_code].school_name
        # 異動前下部組織コード(学校コード)
        before_organization_code = data_dict.get("before_organization_code")
        # 異動前下部組織名(英語)(学校名)
        before_organization_name = before_info[user_id].organization_name
        # 下部組織コード(学校コード)
        new_organization_code = data_dict.get("organization_code")
        # 下部組織名(英語)(学校名)
        new_organization_name = all_schools_dict[new_organization_code].school_name

        ldif_data.append(f"dn: uid={user_id},ou={before_organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modrdn")
        ldif_data.append(f"newrdn: uid={user_id}")
        ldif_data.append(f"deleteoldrdn: 0")
        ldif_data.append(f"newsuperior: ou={new_organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"\n")
        ldif_data.append(f"dn: uid={user_id},ou={new_organization_name},o={system_organization_name}"
                         f",dc=eop-core,dc=org")
        ldif_data.append(f"changetype: modify")
        # 姓(日本語)
        sur_name = data_dict.get("sur_name")
        ldif_data.append(f"replace: sn;lang-ja")
        ldif_data.append(f"sn;lang-ja: {sur_name}")
        ldif_data.append(f"-")
        # 名(日本語)
        given_name = data_dict.get("given_name")
        ldif_data.append(f"replace: givenName;lang-ja")
        ldif_data.append(f"givenName;lang-ja: {given_name}")
        ldif_data.append(f"-")
        # 表示名
        display_name = f"{sur_name}　{given_name}"
        ldif_data.append(f"replace: displayName;lang-ja")
        ldif_data.append(f"displayName;lang-ja: {display_name}")
        ldif_data.append(f"-")
        # 性別
        gender = data_dict.get("gender")
        if gender:
            ldif_data.append(f"replace: gender")
            ldif_data.append(f"gender: {gender}")
            ldif_data.append(f"-")
        if not gender and before_info[user_id].gender:
            ldif_data.append(f"delete:gender")
            ldif_data.append(f"-")
        # 年度
        fiscal_year = data_dict.get("fiscal_year")
        ldif_data.append(f"replace: jsFedFiscalYear")
        ldif_data.append(f"jsFedFiscalYear: {fiscal_year}")
        ldif_data.append(f"-")
        # ユーザーID
        ldif_data.append(f"replace: uid")
        ldif_data.append(f"uid: {user_id}")
        ldif_data.append(f"-")
        # メールアドレス
        mail = data_dict.get("mail")
        if mail:
            ldif_data.append(f"replace: mail")
            ldif_data.append(f"mail: {mail}")
            ldif_data.append(f"-")
        if not mail and before_info[user_id].mail:
            ldif_data.append(f"delete:mail")
            ldif_data.append(f"-")
        # 権限
        role = data_dict.get("role")
        ldif_data.append(f"replace: jsFedRole")
        ldif_data.append(f"jsFedRole: {role}")
        ldif_data.append(f"-")
        # 下部組織タイプ(学校タイプ)
        new_organization_type = all_schools_dict[new_organization_code].school_type
        ldif_data.append(f"replace: jsFedOuType")
        ldif_data.append(f"jsFedOuType: {new_organization_type}")
        ldif_data.append(f"-")
        # 下部組織名(英語)(学校名)
        ldif_data.append(f"replace: ou")
        ldif_data.append(f"ou: {new_organization_name}")
        ldif_data.append(f"-")
        # 下部組織名(日本語)(学校名)
        new_organization_name_ja = all_schools_dict[new_organization_code].school_name_ja
        ldif_data.append(f"replace: ou;lang-ja")
        ldif_data.append(f"ou;lang-ja: {new_organization_name_ja}")
        ldif_data.append(f"-")
        # 下部組織コード(学校コード)
        ldif_data.append(f"replace: jsFedOu")
        ldif_data.append(f"jsFedOu: {new_organization_code}")
        ldif_data.append(f"-")
        # 異動元下部組織コード(学校コード)
        ldif_data.append(f"replace: jsFedSourceOu")
        ldif_data.append(f"jsFedSourceOu: {before_organization_code}")
        ldif_data.append(f"-")
        # 異動日
        ldif_data.append(f"replace: jsFedTransferDate")
        ldif_data.append(f"jsFedTransferDate: {system_time}")
        ldif_data.append(f"-")
        # 教科
        subject_code = data_dict.get("subject_code")
        if subject_code:
            ldif_data.append(f"replace: jsFedSubject")
            ldif_data.append(f"jsFedSubject: {subject_code}")
            ldif_data.append(f"-")
        if not subject_code and before_info[user_id].subject_code:
            ldif_data.append(f"delete:jsFedSubject")
            ldif_data.append(f"-")
        # 学年コード
        grade_code = data_dict.get("grade_code")
        if grade_code:
            ldif_data.append(f"replace: jsFedGrade")
            ldif_data.append(f"jsFedGrade: {grade_code}")
            ldif_data.append(f"-")
            # 学年表示名　(日本語)
            grade_name = all_grades_dict[grade_code].grade_name_ja
            ldif_data.append(f"replace: jsFedJaGradeName")
            ldif_data.append(f"jsFedJaGradeName: {grade_name}")
            ldif_data.append(f"-")
        if not grade_code and before_info[user_id].grade_code:
            ldif_data.append(f"delete:jsFedGrade")
            ldif_data.append(f"-")
            # 学年表示名　(日本語)
            ldif_data.append(f"delete:jsFedJaGradeName")
            ldif_data.append(f"-")
        # 組コード
        class_code = data_dict.get("class_code")
        if class_code:
            ldif_data.append(f"replace: jsFedClass")
            ldif_data.append(f"jsFedClass: {class_code}")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            class_name = all_classes_dict[class_code].class_name_ja
            ldif_data.append(f"replace: jsFedJaClassName")
            ldif_data.append(f"jsFedJaClassName: {class_name}")
            ldif_data.append(f"-")
        if not class_code and before_info[user_id].class_code:
            ldif_data.append(f"delete:jsFedClass")
            ldif_data.append(f"-")
            # 組表示名　(日本語)
            ldif_data.append(f"delete:jsFedJaClassName")
            ldif_data.append(f"-")
        # 更新日時
        ldif_data.append(f"replace: updDate")
        ldif_data.append(f"updDate: {system_time}")
        ldif_data.append(f"-")
        # Windows連携フラグ
        relationwin = data_dict.get("relationwin")
        # befrelationwin
        upd_date = before_info[user_id].upd_date
        if upd_date[0:8] != system_time[0:8]:
            ldif_data.append(f"replace: befrelationwin")
            ldif_data.append(f"befrelationwin: {relationwin}")
            ldif_data.append(f"-")
        # mextOuCode
        mextOuCode = all_schools_dict[new_organization_code].mextOuCode
        ldif_data.append(f"replace: mextOuCode")
        ldif_data.append(f"mextOuCode: {mextOuCode}")
        ldif_data.append(f"\n")

        ldif_teacher_mod2_data.extend(ldif_data)
        # 申込情報
        teacher_mod2_apply_info[user_id] = ApplyInfo(
            operation_status=3,
            operation_type="teacher14",
            target_id=user_id,
            target_name=display_name,
            target_system_organization_code=self.system_organization_code,
            target_organization_code=new_organization_code,
            remarks="",
            entry_person=os.environ["BATCH_OPERATOR_ID"],
            update_person=os.environ["BATCH_OPERATOR_ID"],
        )

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF TEACHER MOD2 ###")

    def edit_ldif_del(
            self,
            deal_start_time,
            oneroster_directory,
            deal_org_kbn,
    ):
        """
        削除ldifファイルを作成
        :param deal_start_time: 処理開始日時
        :param oneroster_directory: ファイルパス
        :param deal_org_kbn: 組織区分

        """
        self.log_info("### START LDIFFILEMAKE SERVICE EDIT LDIF DEL ###")
        # エラーリスト
        error_list = []
        record_count = 0
        db_retry_count = int(os.environ.get("DB_RETRY_COUNT"))
        ldap_retry_count = int(os.environ.get("LDAP_RETRY_COUNT"))
        specify_filters = [
            "!(UpdDate>=" + deal_start_time + ")"
        ]

        user_model = UserModel(self.ldap_access_object)
        system_organization_name = ""
        organization_names = []
        # RDSのリトライ処理
        for i in range(db_retry_count):
            try:
                self.rds_access_object.begin()
                # 組織情報取得
                if not system_organization_name:
                    system_organization_service = SystemOrganizationService(self.rds_access_object)
                    system_organization = system_organization_service.select_by_code(self.system_organization_code)
                    system_organization_name = system_organization.system_organization_name

                # 学校情報取得
                if deal_org_kbn == "school":
                    school_code = oneroster_directory.split("_")[-1]
                    school = self.crud_model.select(
                        self.system_organization_code,
                        RDS_TABLE.SCHOOL_MASTER,
                        ["school_code", "school_name"],
                        SchoolMaster(school_code=school_code, delete_flag=0)
                    )
                    organization_names = [school[0].school_name]
                break
            except Exception as exception:
                if (i + 1) < db_retry_count:
                    self.log_info(f"RetryError : Retry processing("
                                  f"get_system_organization_data and school_data) for the {i + 1} time.")
                    # 次の試行まで待つ
                    time.sleep(int(os.environ.get("DB_RETRY_INTERVAL")))
                    continue
                else:
                    self.log_error("exception :" + str(exception))
                    self.throw_error("ID_E_0003", None, str(exception))
            finally:
                self.rds_access_object.close()

        # 処理対象組織区分がdistrictの場合
        if deal_org_kbn == "district":
            # LDAPのリトライ処理
            for i in range(ldap_retry_count):
                try:
                    self.ldap_access_object.connect()
                    # 学校情報取得
                    organization_names = user_model.get_organization_names(
                        system_organization_name,
                        self.ldap_access_object,
                        specify_filters
                    )
                    break
                except Exception as exception:
                    if (i + 1) < db_retry_count:
                        self.log_info(f"RetryError : Retry processing(get_organization_names) for the {i + 1} time.")
                        # 次の試行まで待つ
                        time.sleep(int(os.environ.get("LDAP_RETRY_INTERVAL")))
                        continue
                    else:
                        self.log_error('LDAPの検索(get_organization_names) に、最大回数までリトライしても異常終了')
                        self.log_error(traceback.format_exc())
                        self.throw_error("ID_E_0003", None, str(exception))
                finally:
                    self.ldap_access_object.close()

        # attributeをLDAPの名称に変換する
        attributes = csv_roster_setting.ldap_search
        searched_users = []
        success_count = 0
        for organization_name in organization_names:
            # DNを生成
            dn_condition = Oneroster_user(system_organization_name=system_organization_name,
                                          organization_name=organization_name)
            try:
                users = user_model.bulk_delete_select(
                    attributes=attributes,
                    dn_condition=dn_condition,
                    specify_filters=specify_filters
                )
                searched_users.extend(users)
            except Exception as exception:
                if exception.__class__ == LambdaError and 'LDAPNoSuchObjectResult' in str(exception):
                    self.log_error('Ldapの32：DNが見つからない場合(ou不正)エラー発生した')
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": "「一括」モードのLDAPから削除対象ユーザを取得する時、異常が発生しました。"})
                else:
                    self.log_error('LDAPの検索(bulk_delete_select) に、最大回数までリトライしても異常終了')
                    self.log_error(traceback.format_exc())
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": "一括の場合、Ldapから削除対象ユーザが取得失敗しました。"})

        if searched_users:
            record_count = len(searched_users)
            del_ldif_data = []
            delete_apply_info = {}
            delete_user_info = {}
            system_time = self.create_update_date_str()
            # csvファイルをS3から読み込む
            csv_file = self.s3_access_object.im_port(f'{oneroster_directory}/csv/users.csv')
            # csvデータを取得
            csv_reader = csv.reader(io.StringIO(csv_file.strip()))
            not_delete_user = []
            headers = csv_roster_setting.header["users"]
            for each_row in csv_reader:
                csv_dict = {key: val for key, val in zip(headers, each_row)}
                not_delete_user.append(csv_dict["userMasterIdentifier"])

            for user in searched_users:
                # users.csvに存在するユーザが削除対象外
                if user.mextUid in not_delete_user:
                    record_count = record_count - 1
                    continue
                # rootadmin、testadminが削除対象外
                if user.user_id == "rootadmin" or user.user_id == "testadmin":
                    self.log_warning(f"ユーザID：{user.user_id} rootadminやtestadminが削除できません。")
                    record_count = record_count - 1
                    continue
                del_ldif_data.append(f"dn: uid={user.user_id},ou={user.organization_name},o={system_organization_name}"
                                     f",dc=eop-core,dc=org")
                del_ldif_data.append(f"changetype: delete")
                del_ldif_data.append(f"\n")
                if user.role == "student":
                    user_id = user.user_id
                    user_id = user_id.replace(f'{user.organization_code}{user.grade_code}', '')
                    # 申込情報
                    delete_apply_info[user.user_id] = ApplyInfo(
                        operation_status=3,
                        operation_type="student13",
                        target_id=user_id,
                        target_name="",
                        target_system_organization_code=self.system_organization_code,
                        target_organization_code=user.organization_code,
                        remarks="",
                        entry_person=os.environ["BATCH_OPERATOR_ID"],
                        update_person=os.environ["BATCH_OPERATOR_ID"],
                    )
                elif user.role == "admin":
                    # 申込情報
                    delete_apply_info[user.user_id] = ApplyInfo(
                        operation_status=3,
                        operation_type="admin13",
                        target_id=user.user_id,
                        target_name="",
                        target_system_organization_code=self.system_organization_code,
                        target_organization_code=user.organization_code,
                        remarks="",
                        entry_person=os.environ["BATCH_OPERATOR_ID"],
                        update_person=os.environ["BATCH_OPERATOR_ID"],
                    )
                else:
                    # 申込情報
                    delete_apply_info[user.user_id] = ApplyInfo(
                        operation_status=3,
                        operation_type="teacher13",
                        target_id=user.user_id,
                        target_name="",
                        target_system_organization_code=self.system_organization_code,
                        target_organization_code=user.organization_code,
                        remarks="",
                        entry_person=os.environ["BATCH_OPERATOR_ID"],
                        update_person=os.environ["BATCH_OPERATOR_ID"],
                    )
                user.entry_person = os.environ["BATCH_OPERATOR_ID"]
                user.entry_date_time = system_time
                user.update_person = os.environ["BATCH_OPERATOR_ID"]
                user.update_date_time = system_time
                # ユーザ削除情報
                delete_user_info[user.user_id] = user
            if del_ldif_data:
                out_file_path = f'{oneroster_directory}/ldif/delete'
                self.output_ldif_file_to_s3(out_file_path, "delete_user.ldif", del_ldif_data)
                result = self.excute_del_ldif_file(
                    oneroster_directory,
                    delete_apply_info,
                    delete_user_info
                )
                success_count = result["success_count"]
                error_list.extend(result["error_list"])
        if error_list:
            self.export_error_csv_file(error_list, oneroster_directory, deal_start_time)

        self.log_info("### END LDIFFILEMAKE SERVICE EDIT LDIF DEL ###")

        return {
            "success_count": success_count,
            "record_count": record_count
        }

    def excute_ldif_file(
            self,
            file_current,
            file_path,
            student_add_apply_info=[],
            student_mod1_apply_info=[],
            student_mod2_apply_info=[],
            teacher_add_apply_info=[],
            teacher_mod1_apply_info=[],
            teacher_mod2_apply_info=[],
            admin_add_apply_info=[],
            admin_mod1_apply_info=[],
    ):

        """
        ldifファイルの実行

        Returns
        -------

        """

        self.log_info("### START LDIFFILEMAKE SERVICE EXCUTE LDIF ###")
        # SSHクライアントを作成
        ssh = paramiko.SSHClient()
        # know_hostsファイル以外のホストも接続できるようにする
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # クライアント証明書ファイル
        cli_cer_file_name = 'id_rsa'
        # ファイル一時保存ディレクトリ
        tmp_file_dir = "/tmp/"
        # エラーリスト
        error_list = []
        # LDAPユーザー
        ldap_user = os.environ["LDAP_USER"]
        # LDAPパスワード
        ldap_password = os.environ["LDAP_PASSWORD"]
        enc_password = self.decrypt_message(ldap_password)
        # 申込情報エラー
        info_error = False
        # 処理成功件数
        success_count = len(student_add_apply_info) + len(student_mod1_apply_info) + len(student_mod2_apply_info) \
                        + len(teacher_add_apply_info) + len(teacher_mod1_apply_info) + len(teacher_mod2_apply_info) \
                        + len(admin_add_apply_info) + len(admin_mod1_apply_info)

        try:
            # クライアント証明書をとってくる
            with open(tmp_file_dir + cli_cer_file_name, "wb") as cli_cer_file:
                body_cliant_pem = self.s3_access_object.im_port(os.environ["CLIENT_CER_FILE_PATH"])
                # 一時的にサーバ証明書を保存する
                cli_cer_file.write(body_cliant_pem.encode("utf-8"))

            # LDAPサーバを接続する
            self.log_info("LDAPサーバを接続開始します...")
            ssh.connect(hostname=os.environ["LDAP_SERVER_HOST_IP"], port=22,
                        username=os.environ["LDAP_SERVER_USER_NAME"], key_filename=tmp_file_dir + cli_cer_file_name)
            self.log_info("LDAPサーバを接続終了しました。")
            s3_ldif_path = f'{os.environ["S3_BUCKET_NAME"]}/{file_path}/ldif/'
            download_path = '/ldif_file/'

            # ldifファイル実行
            if student_add_apply_info:
                has_error = False
                file_name = f"add_student_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}add/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（add_student_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（add_student_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapadd -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name}'
                    self.log_info("児童・生徒一括登録のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("児童・生徒一括登録のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'adding new entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_add' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_add:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                student_add_apply_info[user_id].operation_status = 4
                                student_add_apply_info[user_id].remarks = error
                                self.log_error(f"児童・生徒一括登録の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"児童・生徒一括登録の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in student_add_apply_info:
                            error_flag = self.db_info_insert(student_add_apply_info[key])
                            if error_flag:
                                self.log_error(f"児童・生徒一括登録の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"児童・生徒一括登録の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"児童・生徒一括登録の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"児童・生徒一括登録の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"児童・生徒一括登録の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"児童・生徒一括登録の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/add/', file_name)

            if student_mod1_apply_info:
                has_error = False
                file_name = f"update_student_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}update/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（update_student_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（update_student_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapmodify -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name} '
                    self.log_info("児童・生徒進級のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("児童・生徒進級のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and ('modifying entry' in res_list[0] or 'modifying rdn of entry' in res_list[0]):
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_modify' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_modify:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                student_mod1_apply_info[user_id].operation_status = 4
                                student_mod1_apply_info[user_id].remarks = error
                                self.log_error(f"児童・生徒進級の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"児童・生徒進級の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in student_mod1_apply_info:
                            error_flag = self.db_info_insert(student_mod1_apply_info[key])
                            if error_flag:
                                self.log_error(f"児童・生徒進級の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"児童・生徒進級の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"児童・生徒進級の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"児童・生徒進級の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"児童・生徒進級の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"児童・生徒進級の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/update/', file_name)

            if student_mod2_apply_info:
                has_error = False
                file_name = f"transfer_student_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}transfer/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（transfer_student_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（transfer_student_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapmodify -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name} '
                    self.log_info("児童・生徒進学のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("児童・生徒進学のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'modifying rdn of entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_modify' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_modify:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                student_mod2_apply_info[user_id].operation_status = 4
                                student_mod2_apply_info[user_id].remarks = error
                                self.log_error(f"児童・生徒進学の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"児童・生徒進学の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in student_mod2_apply_info:
                            error_flag = self.db_info_insert(student_mod2_apply_info[key])
                            if error_flag:
                                self.log_error(f"児童・生徒進学の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"児童・生徒進学の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"児童・生徒進学の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"児童・生徒進学の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"児童・生徒進学の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"児童・生徒進学の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/transfer/', file_name)

            if teacher_add_apply_info:
                has_error = False
                file_name = f"add_teacher_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}add/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（add_teacher_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（add_teacher_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapadd -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name} '
                    self.log_info("教員一括登録のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("教員一括登録のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'adding new entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_add' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_add:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                teacher_add_apply_info[user_id].operation_status = 4
                                teacher_add_apply_info[user_id].remarks = error
                                self.log_error(f"教員一括登録の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"教員一括登録の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in teacher_add_apply_info:
                            error_flag = self.db_info_insert(teacher_add_apply_info[key])
                            if error_flag:
                                self.log_error(f"教員一括登録の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"教員一括登録の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"教員一括登録の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"教員一括登録の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"教員一括登録の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"教員一括登録の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/add/', file_name)

            if teacher_mod1_apply_info:
                has_error = False
                file_name = f"update_teacher_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}update/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（update_teacher_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（update_teacher_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapmodify -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name} '
                    self.log_info("教員一括更新のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("教員一括更新のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'modifying entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_modify' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_modify:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                teacher_mod1_apply_info[user_id].operation_status = 4
                                teacher_mod1_apply_info[user_id].remarks = error
                                self.log_error(f"教員一括更新の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"教員一括更新の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in teacher_mod1_apply_info:
                            error_flag = self.db_info_insert(teacher_mod1_apply_info[key])
                            if error_flag:
                                self.log_error(f"教員一括更新の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"教員一括更新の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"教員一括更新の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"教員一括更新の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"教員一括更新の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"教員一括更新の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/update/', file_name)

            if teacher_mod2_apply_info:
                has_error = False
                file_name = f"transfer_teacher_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}transfer/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（transfer_teacher_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（transfer_teacher_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapmodify -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name}'
                    self.log_info("教員一括異動のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("教員一括異動のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'modifying rdn of entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_modify' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_modify:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                teacher_mod2_apply_info[user_id].operation_status = 4
                                teacher_mod2_apply_info[user_id].remarks = error
                                self.log_error(f"教員一括異動の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"教員一括異動の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in teacher_mod2_apply_info:
                            error_flag = self.db_info_insert(teacher_mod2_apply_info[key])
                            if error_flag:
                                self.log_error(f"教員一括異動の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"教員一括異動の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"教員一括異動の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"教員一括異動の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"教員一括異動の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"教員一括異動の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/transfer/', file_name)

            if admin_add_apply_info:
                has_error = False
                file_name = f"add_admin_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}add/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（add_admin_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（add_admin_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapadd -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name} '
                    self.log_info("OPE管理者一括登録のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("OPE管理者一括登録のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'adding new entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_add' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_add:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                admin_add_apply_info[user_id].operation_status = 4
                                admin_add_apply_info[user_id].remarks = error
                                self.log_error(f"OPE管理者一括登録の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"OPE管理者一括登録の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in admin_add_apply_info:
                            error_flag = self.db_info_insert(admin_add_apply_info[key])
                            if error_flag:
                                self.log_error(f"OPE管理者一括登録の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"OPE管理者一括登録の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"OPE管理者一括登録の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"OPE管理者一括登録の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"OPE管理者一括登録の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"OPE管理者一括登録の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/add/', file_name)

            if admin_mod1_apply_info:
                has_error = False
                file_name = f"update_admin_{file_current}.ldif"
                # ldifファイルダウンロード
                command = f'sudo aws s3 cp s3://{s3_ldif_path}update/{file_name} {download_path}{file_name} --no-verify-ssl'
                self.log_info(f"ldifファイルをS3からダウンロードします。（update_admin_{file_current}.ldif）")
                stdin, stdout, stderr = ssh.exec_command(command)
                self.log_info(f"ldifファイルダウンロードが完了しました。（update_admin_{file_current}.ldif）")
                d_res = stdout.read()
                error = stderr.read().decode()
                if "error" not in error:
                    command = f'sudo ldapmodify -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name} '
                    self.log_info("OPE管理者一括更新のldifファイルを実行開始します。")
                    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                    res = stdout.read()
                    res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                    res_list.pop()
                    if not res_list:
                        self.ssh_retry(res_list, command, ssh)
                    self.log_info("OPE管理者一括更新のldifファイルが実行完了しました。")
                    if len(res_list) > 0 and 'modifying entry' in res_list[0]:
                        for info in res_list:
                            # エラーの場合
                            if 'ldap_modify' in info:
                                success_count = success_count - 1
                                has_error = True
                                match = r"uid=(.*?),ou"
                                err = r"ldap_modify:(.*)"
                                user_id = re.findall(match, info)[0]
                                error = re.findall(err, info)[0]
                                admin_mod1_apply_info[user_id].operation_status = 4
                                admin_mod1_apply_info[user_id].remarks = error
                                self.log_error(f"OPE管理者一括更新の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"OPE管理者一括更新の場合、LDAPのユーザーID<{user_id}>を更新失敗しました。"})
                        for key in admin_mod1_apply_info:
                            error_flag = self.db_info_insert(admin_mod1_apply_info[key])
                            if error_flag:
                                self.log_error(f"OPE管理者一括更新の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"OPE管理者一括更新の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                    else:
                        has_error = True
                        self.log_error(f"OPE管理者一括更新の場合、ldifファイル<{file_name}>を実行失敗しました。command result:<{res}>")
                        error_list.append({"userMasterIdentifier": "なし",
                                           "detail": f"OPE管理者一括更新の場合、ldifファイル<{file_name}>を実行失敗しました。"})
                else:
                    has_error = True
                    self.log_error(f"OPE管理者一括更新の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"OPE管理者一括更新の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
                self.ldif_file_processing(has_error, f'{file_path}/ldif/update/', file_name)

            command = f'sudo rm -f {download_path}{file_name}'
            self.log_info(f"{download_path}{file_name}をLDAPサーバから削除します。")
            ssh.exec_command(command)

        except Exception as exception:
            self.log_error(exception)
            self.log_error(f"一括の場合、ldifファイルの実行に、想定外のエラーが発生しました。")
            error_list.append({"userMasterIdentifier": "なし",
                                "detail": f"一括の場合、ldifファイルの実行に、想定外のエラーが発生しました。"})
            raise exception

        finally:
            if os.path.exists(tmp_file_dir + cli_cer_file_name):
                os.remove(tmp_file_dir + cli_cer_file_name)
            ssh.close()

        self.log_info("### END LDIFFILEMAKE SERVICE EXCUTE LDIF ###")

        return {
            "error_list": error_list,
            "success_count": success_count
        }

    def excute_del_ldif_file(
            self,
            file_path,
            delete_apply_info,
            delete_user_info
    ):

        """
        ldifファイルの実行

        Returns
        -------

        """

        error_list = []

        has_error = False
        # SSHクライアントを作成
        ssh = paramiko.SSHClient()
        # know_hostsファイル以外のホストも接続できるようにする
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # クライアント証明書ファイル
        cli_cer_file_name = 'id_rsa'
        # ファイル一時保存ディレクトリ
        tmp_file_dir = "/tmp/"
        # 処理成功件数
        success_count = len(delete_apply_info)
        ldap_user = os.environ["LDAP_USER"]
        ldap_password = os.environ["LDAP_PASSWORD"]
        enc_password = self.decrypt_message(ldap_password)

        try:
            # クライアント証明書をとってくる
            with open(tmp_file_dir + cli_cer_file_name, "wb") as cli_cer_file:
                body_cliant_pem = self.s3_access_object.im_port(os.environ["CLIENT_CER_FILE_PATH"])
                # 一時的にサーバ証明書を保存する
                cli_cer_file.write(body_cliant_pem.encode("utf-8"))

            # LDAPサーバを接続する
            self.log_info("LDAPサーバを接続開始します...")
            ssh.connect(hostname=os.environ["LDAP_SERVER_HOST_IP"], port=22,
                        username=os.environ["LDAP_SERVER_USER_NAME"], key_filename=tmp_file_dir + cli_cer_file_name)
            self.log_info("LDAPサーバを接続終了しました。")
            s3_ldif_path = f'{os.environ["S3_BUCKET_NAME"]}/{file_path}/ldif/delete/'
            download_path = '/ldif_file/'
            file_name = "delete_user.ldif"
            # ldifファイルダウンロード
            command = f'sudo aws s3 cp s3://{s3_ldif_path}{file_name} {download_path}{file_name} --no-verify-ssl'
            self.log_info(f"ldifファイルをダウンロードします。（delete_user.ldif）")
            stdin, stdout, stderr = ssh.exec_command(command)
            self.log_info(f"ldifファイルダウンロードが完了しました。（delete_user.ldif）")
            d_res = stdout.read()
            error = stderr.read().decode()
            if "error" not in error:
                # ldifファイル実行
                command = f'sudo ldapmodify -x -c -D {ldap_user} -w {enc_password} -f {download_path}{file_name}'
                self.log_info("ユーザー一括削除のldifファイルを実行開始します。")
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                res = stdout.read()
                res_list = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
                res_list.pop()
                not_delete_user = []
                # ldifファイル実行されないので、リトライする
                if not res_list:
                    self.ssh_retry(res_list, command, ssh)
                self.log_info("ユーザー一括削除のldifファイルが実行完了しました。")
                if len(res_list) > 0 and 'deleting entry' in res_list[0]:
                    for info in res_list:
                        # エラーの場合
                        if 'ldap_delete' in info:
                            success_count = success_count - 1
                            has_error = True
                            match = r"uid=(.*?),ou"
                            err = r"ldap_delete:(.*)"
                            user_id = re.findall(match, info)[0]
                            error = re.findall(err, info)[0]
                            # 申込情報にエラー登録
                            delete_apply_info[user_id].operation_status = 4
                            delete_apply_info[user_id].remarks = error
                            self.log_error(f"ユーザー一括削除の場合、LDAPからユーザーID<{user_id}>を削除失敗しました。")
                            error_list.append({"userMasterIdentifier": delete_user_info[user_id].mextUid,
                                               "detail": f"ユーザー一括削除の場合、LDAPからユーザーID<{user_id}>を削除失敗しました。"})
                            # Ldapから削除失敗の場合、ユーザー削除TBLを登録しない
                            delete_user_info[user_id] = None

                    # 申込情報TBLとユーザー削除TBLを登録する
                    for key in delete_apply_info:
                        error_flag = self.db_info_insert(delete_apply_info[key],
                                                         delete_user_info[key],
                                                         True,
                                                         )
                        if error_flag:
                            # ユーザー削除TBLを登録失敗の場合、ユーザー削除TBLを登録するためのcsvをnot_delete_userで出力
                            if delete_user_info[key]:
                                not_delete_user.append(delete_user_info[key])
                                self.log_error(f"ユーザー一括削除の場合、ユーザーID<{key}>のRDSのユーザ削除TBL、申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": delete_user_info[key].mextUid,
                                                   "detail": f"ユーザー一括削除の場合、ユーザーID<{key}>のRDSのユーザ削除TBL、申込情報TBLの登録に異常が発生しました。"})
                            else:
                                self.log_error(f"ユーザー一括削除の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。")
                                error_list.append({"userMasterIdentifier": "なし",
                                                   "detail": f"ユーザー一括削除の場合、ユーザーID<{key}>のRDSの申込情報TBLの登録に異常が発生しました。"})
                else:
                    has_error = True
                    self.log_error(f"ユーザー一括削除の場合、ldifファイル<{file_name}>を実行失敗して、ユーザ削除に異常が発生しました。")
                    error_list.append({"userMasterIdentifier": "なし",
                                       "detail": f"ユーザー一括削除の場合、ldifファイル<{file_name}>を実行失敗して、ユーザ削除に異常が発生しました。"})
                command = f'sudo rm -rf {download_path}'
                self.log_info(f"{download_path}をLDAPサーバから削除します。")
                ssh.exec_command(command)
                # Ldapから削除成功、user削除TBLを登録失敗の場合、ユーザー削除TBLを登録するためのcsvをで出力
                if not_delete_user:
                    not_delete_user_csv = self.create_master_file_contents(
                        not_delete_user,
                        csv_roster_setting.ldap_search,
                        csv_roster_setting.ldap_search
                    )
                    self.log_error(f"Ldap一括削除成功が、ユーザ削除TBLを登録失敗しました。command result:<{res}>"
                                   f"削除されたユーザ情報をファイル{file_path}/error/error_bulk_delete_users.csvに出力しました。")
                    # s3にCSVを配置する
                    self.s3_access_object.export(f'{file_path}/error/error_bulk_delete_users.csv', not_delete_user_csv)
            else:
                has_error = True
                self.log_error(f"ユーザー一括削除の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。command result:<{d_res}>")
                error_list.append({"userMasterIdentifier": "なし",
                                   "detail": f"ユーザー一括削除の場合、ldifファイル<{file_name}>をダウンロード失敗したので、実行されませんでした。"})
            self.ldif_file_processing(has_error, f'{file_path}/ldif/delete/', file_name)
        except Exception as exception:
            raise exception

        finally:
            if os.path.exists(tmp_file_dir + cli_cer_file_name):
                os.remove(tmp_file_dir + cli_cer_file_name)
            # 接続を閉じる
            ssh.close()

        return {
            "error_list": error_list,
            "success_count": success_count,
        }

    def db_info_insert(self, apply_info, delete_user_info=None, delete_flag=False):
        """
        DB情報登録

        Parameters
        apply_info
            申込情報
        file_name
            ldifファイル名
        delete_user_info
            ユーザ削除情報
        delete_flag
            削除フラグ
        ----------

        Returns
        -------

        """
        db_retry_count = int(os.environ.get("DB_RETRY_COUNT"))
        has_error = False
        for i in range(db_retry_count):
            try:
                self.rds_access_object.begin()
                # ユーザ削除テーブルを登録する
                if delete_flag and delete_user_info:
                    # Ldapから取得した属性値（gender、transfer_school_date、from_organization_code）がNoneの場合、""に変更されたので、
                    # ここに""の場合、ユーザ削除TBLにNULLで登録する
                    if delete_user_info.gender == "":
                        delete_user_info.gender = None
                    if delete_user_info.transfer_school_date != "":
                        delete_user_info.transfer_school_date = "{}-{}-{} {}:{}:{}".format(
                            delete_user_info.transfer_school_date[0:4],
                            delete_user_info.transfer_school_date[4:6],
                            delete_user_info.transfer_school_date[6:8],
                            delete_user_info.transfer_school_date[8:10],
                            delete_user_info.transfer_school_date[10:12],
                            delete_user_info.transfer_school_date[12:14],
                        )
                    else:
                        delete_user_info.transfer_school_date = None
                    if delete_user_info.from_organization_code == "":
                        delete_user_info.from_organization_code = None
                    self.crud_model.insert(self.system_organization_code,
                                           RDS_TABLE.DELETE_USER,
                                           delete_user_info)

                # 申込情報登録
                self.crud_model.insert(self.system_organization_code,
                                       RDS_TABLE.APPLY_INFO,
                                       apply_info)
                self.rds_access_object.commit()
                break
            except Exception as exception:
                self.rds_access_object.rollback()
                if (i + 1) < db_retry_count:
                    self.log_info(f"RetryError : Retry processing(ldif_apply_info_insert) for the {i + 1} time.")
                    # 次の試行まで待つ
                    time.sleep(int(os.environ.get("DB_RETRY_INTERVAL")))
                    continue
                else:
                    has_error = True
                    self.log_error("exception :" + str(exception))

            finally:
                self.rds_access_object.close()

        return has_error

    def ldif_file_processing(self, has_error, file_path, file_name):
        """
        ldifファイル処理

        Parameters
        ----------
            :param has_error:エラーあり
            :param file_path:ファイルパス
            :param file_name:ldifファイル名

        Returns
        -------
        """
        s3_resource = boto3.resource('s3')
        bucket_name = os.environ["S3_BUCKET_NAME"]
        file_key = f'{file_path}{file_name}'
        if has_error:
            self.log_info("ldif実行にエラーがあり、ldifファイルをerrorフォルダに移動する")
            # ldifファイル移動
            copy_ldif = {
                'Bucket': bucket_name,
                'Key': file_key
            }
            path = file_path.split("/")
            out_file_key = f'{path[0]}/{path[1]}/error/error_{file_name}'
            s3_resource.meta.client.copy(copy_ldif, bucket_name, out_file_key)

        # ldifファイル削除
        self.log_info(f"delete ldif file : <{file_key}>")
        s3_resource.Object(bucket_name, file_key).delete()

    def export_error_csv_file(self, error_messages, oneroster_directory, deal_start_time):
        """
        エラーメッセージファイルを生成する

        Parameters
        ----------
            :param error_messages:エラーメッセージリスト
            :param oneroster_directory:エラーメッセージリスト
            :param deal_start_time:処理開始日時

        Returns
        -------
        """
        self.log_info("### START EXPORT ERROR CSV FILE ###")

        error_file_directory = oneroster_directory + "/error/"
        csv_file = ""
        out_csv_file_name = "error_messages_" + deal_start_time
        out_csv_file_path = (error_file_directory + out_csv_file_name + ".csv")
        # csvファイルチェック
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(os.environ["S3_BUCKET_NAME"])
        objs = list(bucket.objects.filter(Prefix=out_csv_file_path))
        if len(objs) > 0 and objs[0].key == out_csv_file_path:
            # csvファイルをS3から読み込む
            csv_file = self.s3_access_object.im_port(out_csv_file_path)

        # 同名のエラーファイルが存在している場合、ファイルにエラー内容を追記する（ヘッダー再出力不要）
        if csv_file:
            header_export_flg = False
        else:
            header_export_flg = True

        error_info_csv = self.create_master_file_contents(
            error_messages,
            csv_roster_setting.ERROR_FILE_COLUMN,
            csv_roster_setting.ERROR_FILE_COLUMN,
            header_export_flg
        )

        csv_file += error_info_csv
        # s3にCSVを配置する
        self.s3_access_object.export(out_csv_file_path, csv_file)

        self.log_error(f"エラーが発生しました。エラー内容がファイル{out_csv_file_path}をご参照ください。")
        self.log_info("### END EXPORT ERROR CSV FILE ###")

        return

    def create_master_file_contents(self, out_data, csv_format, headers, header_export_flg=True):
        """
        CSVのファイルを生成する(マスター情報出力)

        Parameters
        ----------
            CSVファイルの内容
            :param csv_format:
            :param out_data:
            :param headers:
            :param header_export_flg:

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES CREATE MASTER FILE CONTENTS ###")

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=csv_format,
                                delimiter=csv_setting.DELIMITER, quoting=csv.QUOTE_ALL,
                                lineterminator=csv_setting.LINETERMINATOR)

        # ヘッダー出力の場合
        if header_export_flg:
            header_dict = {key: val for key, val in zip(csv_format, headers)}
            writer.writerow(header_dict)

        for result in out_data:
            if not isinstance(result, dict):
                result = result.get_dict(allow_empty=True)
                result.pop("entry_date_time")
                result.pop("entry_person")
                result.pop("update_date_time")
                result.pop("update_person")
            writer.writerow(result)
        csv_data = buffer.getvalue()
        buffer.close()
        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CREATE MASTER FILE CONTENTS ###")
        return csv_data

    def ssh_retry(self, res_list, command, ssh_client):
        """
        CSVのファイルを生成する

        Parameters
        ----------
            CSVファイルの内容
            :param res_list:戻り値
            :param command:
            :param ssh_client:

        -------
        """
        self.log_info('execute ldif file retry')
        for i in range(3):
            stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)
            res = stdout.read()
            retry_res = res.decode().replace('\r\n\t', ' ').split('\r\n\r\n')
            retry_res.pop()
            if retry_res:
                res_list.extend(retry_res)
                break
            else:
                time.sleep(10)
