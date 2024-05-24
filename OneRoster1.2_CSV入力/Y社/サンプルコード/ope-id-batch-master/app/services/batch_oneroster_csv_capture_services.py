# 　新規追加
import copy
import csv
import os
import io
import re
import time
import traceback

from collections import namedtuple

import boto3
from common.base_service import BaseService
from common.config import csv_setting
from common.config.static_code import RDS_TABLE
from common.crud_model import CRUDModel
from common.helper_handler import bulk_validate
from common.ldap_access_object import LdapAccessObject
from common.rds_access_object import RdsAccessObject
from common.s3_access_object import S3AccessObject
from common.apply_info import ApplyInfo

from app.config import csv_roster_setting, oneroster_info_setting
from app.entities.user import User
from app.services.batch_oneroster_ldif_make_services import LdifFileMakeService
from app.services.teacher_service import TeacherService
from app.services.student_service import StudentService
from app.services.master_service import MasterService
from app.validations import batch_oneroster_validation


class BatchOnerosterCsvCaptureServices(BaseService):
    """
    OPEID管理用のCSVデータを作成し、
        バリデーションチェックし、マスタデータチェックする
            差分の場合、OPEID管理用のCSVファイルをS3に格納する。格納パス：画面の一括受付前段APIと同一パス
            一括の場合、ldifファイルを作成し、sshコマンドでLdapを更新する

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

        self.rds_access_object = RdsAccessObject(
            os.environ.get("RDS_RESOURCE_ARN"),
            os.environ.get("RDS_SECRET_ARN"),
            os.environ.get("RDS_DATABASE"),
        )

        self.ldap_retry_count = int(os.environ.get("LDAP_RETRY_COUNT"))
        self.ldap_retry_interval = int(os.environ.get("LDAP_RETRY_INTERVAL"))
        self.db_retry_count = int(os.environ.get("DB_RETRY_COUNT"))
        self.db_retry_interval = int(os.environ.get("DB_RETRY_INTERVAL"))

        self.s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
        self.crud_model = CRUDModel(self.rds_access_object)
        self.master_service = MasterService(self.rds_access_object, self.ldap_access_object)

    def csv_matching_service(
            self,
            model,
            s3_file_key_id,
            tmp_file_name,
            system_organization_code,
            deal_org_kbn,
            deal_start_time,
            context
    ):
        """
        バリデーションチェックし、マスタデータチェック

        Parameters
        ----------
        :param model:処理モード(bulk：一括、delta：差分)
        :param s3_file_key_id:教育委員会コード または 学校コード
        :param tmp_file_name:一時ファイル名
        :param system_organization_code:組織コード
        :param deal_org_kbn:処理対象組織区分（"school"、"district"の一つ）
        :param deal_start_time:処理開始日時
        :param context:context
        Returns
        -------
        True
        """

        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")

        aws_request_id = context.aws_request_id
        # 削除データ
        del_teacher = []
        del_student = []
        del_admin = []
        # 新規データ
        add_student = []
        add_teacher = []
        add_admin = []
        # 更新データ
        mod1_student = []
        mod1_teacher = []
        mod1_admin = []
        # 異動データ
        mod2_student = []
        mod2_teacher = []
        before_info = {}

        all_error_messages = []
        del_ldap_datas = []

        csv_file = ""

        master_codes = []
        try:
            # 環境変数からFILE_PATHを取得　例："oneroster/"
            oneroster_file_path = os.environ["FILE_PATH"]

            tmp_file_directory = oneroster_file_path + s3_file_key_id + "/tmp/"
            error_file_directory = oneroster_file_path + s3_file_key_id + "/error/"

            tmp_full_file_name = tmp_file_directory + tmp_file_name
            tmp_err_file_name = error_file_directory + "error_" + tmp_file_name

            # csvファイルをS3から読み込む
            csv_file = self.s3_access_object.im_port(tmp_full_file_name)
            # csvデータを取得
            csv_reader = csv.reader(io.StringIO(csv_file.strip()))
            Row = namedtuple('Row', next(csv_reader))
            csv_data_list: list = []

            for row in csv_reader:
                csv_data_list.append(row)
            data_length = len(csv_data_list)

            # タイムアウトまで設定の残す時間を取得
            # limit_time_1：レコードを受付できるように変換する時の制限時間
            if os.environ.get('LIMIT_TIME'):
                limit_time = int(os.environ.get('LIMIT_TIME')) * 60 * 1000
            else:
                limit_time = 5 * 60 * 1000

            row_number = 0
            is_ldap_connect = False
            unhandled_list: list = []
            limit_flag = False
            # 一時ファイル「users_temp_連番.csv」のデータの件数分、下記処理を繰り返す。
            for each_row in csv_data_list:
                row_info = Row(*each_row)
                row_number += 1

                # タイムアウト回避(Lambdaのタイムアウト回避するため、処理の実際残り時間が不足（環境変数に定義）の場合、タイムアウト回避)
                if context.get_remaining_time_in_millis() < limit_time:
                    if not limit_flag:
                        self.log_info("タイムアウト回避する")
                    unhandled_list.append(row_info)
                    limit_flag = True

                    if row_number == data_length:
                        # 処理できないデータは、カレントファイルに上書きして、保存し、次のファイルの繰り返しにて、処理する
                        self.unhandled_data_upload(tmp_file_directory, tmp_file_name, unhandled_list)
                    continue

                error_messages = []

                # 1件目データの場合、RDSの検索を行う。
                if row_number == 1:
                    # 組織情報、組織の環境情報、学校コード、学年コード、組コード、教科コード情報を取得する。
                    master_codes = self.master_service.select_master_codes(
                        row_info,
                        system_organization_code
                    )

                    # 最大回数までリトライしてもDB操作異常となる場合、エラーログを出力し、分割ファイルの繰り返し処理を終了する。
                    if master_codes["is_retry_last"]:
                        message_content = {"userMasterIdentifier": row_info.userMasterIdentifier,
                                           "detail": f"{tmp_file_name} "
                                                     f"RDSからマスタデータを取得する時、異常が発生しました。"}
                        self.log_error(message_content)
                        self.move_deal_file(tmp_full_file_name, tmp_err_file_name, csv_file)

                        # エラーリストにをエラーメッセージを追加する。
                        all_error_messages.append(message_content)

                        self.export_error_csv_file(all_error_messages, error_file_directory, deal_start_time)
                        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
                        return {
                            "keizoku_flag": 1,
                            "success_count": 0
                        }
                    
                    # 組織情報が取得できない場合、エラーログを出力し、分割ファイルの繰り返し処理を終了する。
                    if master_codes["system_organization"] is None:
                        # エラーログ：組織情報＜組織ID：{上記2-1-1.にて取得した組織コード}＞がOPEIDの組織マスタTBLに存在しません。
                        self.log_error(
                            "組織情報＜組織ID：{0}＞がOPEIDの組織マスタTBLに存在しません。"
                            "関連CSVファイル：users.csv、orgs.csv".format(
                                system_organization_code)
                        )
                        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
                        return {
                            "keizoku_flag": 2,
                            "success_count": 0
                        }

                    # 環境情報が取得できない場合、エラーログを出力し、分割ファイルの繰り返し処理を終了する。
                    if row_info.status != "tobedeleted" and master_codes["environment"] is None:
                        self.log_error(
                            "組織の環境情報＜組織ID：{0}＞がOPEIDの環境情報TBLに存在しません。"
                            "関連CSVファイル：users.csv、orgs.csv".format(
                                system_organization_code)
                        )
                        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
                        return {
                            "keizoku_flag": 2,
                            "success_count": 0
                        }

                    # OPE管理者下部組織情報が取得できない場合、エラーログを出力し、分割ファイルの繰り返し処理を終了する。
                    if master_codes["top_organization"] is None:
                        self.log_error(
                            "OPE管理者の下部組織情報＜組織ID：{0}＞がOPEIDの学校マスタTBLに存在しません。"
                            "関連CSVファイル：users.csv、orgs.csv".format(
                                system_organization_code)
                        )
                        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
                        return {
                            "keizoku_flag": 2,
                            "success_count": 0
                        }

                    if master_codes["school_master"] is None:
                        # 引数.処理対象組織区分が"school"の場合、エラーログを出力し、分割ファイルの繰り返し処理を終了する。
                        if deal_org_kbn == "school":
                            # エラーログ：{上記ファイル名} にあるユーザの学校情報＜組織ID：{上記2-1-1.にて取得した組織コード}、
                            # 学校コード：繰り返しデータ.学校コード＞がOPEIDの学校マスタTBLに存在しません。
                            self.log_error(
                                "{0} にあるユーザの学校情報＜組織ID：{1}、学校コード：{2}＞"
                                "がOPEIDの学校マスタTBLに存在しません。"
                                "関連CSVファイル：users.csv、roles.csv、orgs.csv".format(
                                    tmp_file_name, system_organization_code, row_info.schoolCode)
                            )
                            return {
                                "keizoku_flag": 2,
                                "success_count": 0
                            }
                        else:
                            message_content = {
                                "userMasterIdentifier": row_info.userMasterIdentifier,
                                "detail": "{0} にあるユーザの学校情報＜組織ID：{1}、学校コード：{2}＞が"
                                          "OPEIDの学校マスタTBLに存在しません。"
                                          "関連CSVファイル：users.csv、roles.csv、orgs.csv".format(tmp_file_name,
                                                                                          system_organization_code,
                                                                                          row_info.schoolCode)
                            }
                            self.log_error(message_content)
                            self.move_deal_file(tmp_full_file_name, tmp_err_file_name, csv_file)

                            # エラーリストにをエラーメッセージを追加する。
                            all_error_messages.append(message_content)

                            self.export_error_csv_file(all_error_messages, error_file_directory, deal_start_time)
                            self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
                            return {
                                "keizoku_flag": 1,
                                "success_count": 0
                            }
                # OPE管理者の場合、学校マスタの表示No=0の学校に所属する
                if row_info.role == "admin":
                    row_info = row_info._replace(schoolCode=master_codes["school_master"].school_code)

                # Ldapリトライ処理にて、最大回数までリトライしても例外発生するかのフラグ
                is_data_exception = False

                # Ldapリトライ処理
                for i in range(self.ldap_retry_count):
                    # Ldap接続を閉じるかフラグ（Trueの場合、閉じる）
                    is_close_ldap = False
                    # 最後件目のユーザデータの場合、Ldap接続を閉じる必要
                    if row_number == data_length:
                        is_close_ldap = True

                    try:
                        # 1件目データ、又は、Ldapリトライの時、Ldap再接続する必要
                        if not is_ldap_connect:
                            self.ldap_access_object.connect()
                            is_ldap_connect = True

                        # 「差分」の場合、かつ 繰り返しデータ.ステータス　＝　"tobedeleted"　の場合、削除を行う。
                        if model == "delta" and row_info.status == "tobedeleted":
                            # Ldapの検索を行う。
                            del_ldap_datas = self.master_service.get_del_ldap_datas(
                                master_codes["system_organization"].system_organization_name,
                                row_info
                            )
                            break
                        # 上記以外の場合
                        else:
                            # 繰り返しデータ.ユーザー一意識別子を使用し、LDAPからユーザ情報を取得する。
                            user_ldap = ""

                            # 「繰り返しデータ」.ロールが「student」の場合、繰り返しデータ.学校コード+
                            # 繰り返しデータ.学年コード+繰り返しデータ.ユーザID
                            if row_info.role == "student":
                                user_id = row_info.schoolCode + row_info.grades + row_info.username
                            # 「繰り返しデータ」.ロールが「teacher」、「operator」、adminの場合、ユーザID=繰り返しデータ.ユーザID
                            else:
                                user_id = row_info.username

                            user_datas = self.master_service.get_user_info_by_id(
                                master_codes["system_organization"].system_organization_name,
                                row_info.userMasterIdentifier,
                                user_id
                            )
                            break
                    except Exception as exception:
                        # 異常発生の場合、Ldap接続閉じる必要
                        is_close_ldap = True
                        # Ldapの32：DNが見つからない場合(ou不正)エラーの場合、LDAPリトライしない、次のファイルを継続する
                        if is_ldap_connect and not self.master_service.is_retry:
                            # トレースバック
                            self.log_error('Ldapの32：DNが見つからない場合(ou不正)エラー発生した')
                            self.log_error(traceback.format_exc())
                            self.move_deal_file(tmp_full_file_name, tmp_err_file_name, csv_file)

                            # エラーリストにをエラーメッセージを追加する。
                            all_error_messages.append({"userMasterIdentifier": row_info.userMasterIdentifier,
                                                       "detail": f"{tmp_file_name} "
                                                                 f"にあるユーザの学校情報＜"
                                                                 f"o：{master_codes['system_organization'].system_organization_name}、"
                                                                 f"ou：{master_codes['school_master'].school_name}＞が"
                                                                 f"OPEIDのLDAPに存在しません。"
                                                                 f"関連CSVファイル：users.csv、roles.csv、orgs.csv"})

                            self.export_error_csv_file(all_error_messages, error_file_directory, deal_start_time)
                            self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
                            return {
                                "keizoku_flag": 1,
                                "success_count": 0
                            }

                        # Ldapが32以外のエラーの場合、Ldapリトライする
                        if (i + 1) < self.ldap_retry_count:
                            # Ldapリトライの時、Ldap閉じる必要なので、再接続する必要なため、is_ldap_connect=False
                            is_ldap_connect = False
                            self.log_info(f"RetryError : Retry processing(csv_matching_service) for the {i + 1} time.")
                            # 次の試行まで待つ
                            time.sleep(self.ldap_retry_interval)
                        else:
                            # 最大リトライ回数までできない場合、異常終了
                            # トレースバック
                            self.log_error('Ldapの検索が最大リトライ回数までも異常終了')
                            self.log_error(traceback.format_exc())
                            # 最大リトライ回数までできないため、エラーデータとして、次のデータを処理継続
                            is_data_exception = True
                            # 次のデータを継続するため、次のデータを処理する時、Ldapを再接続する必要
                            is_ldap_connect = False
                            break
                    finally:
                        if is_close_ldap:
                            self.ldap_access_object.close()

                # ユーザのLdap検索に、最大リトライ回数までLdapリトライしても異常の場合、該当データが処理対象外として、次のデータを処理継続
                if is_data_exception:
                    messages = "{0} ユーザID：{1} Ldapを検索する時、異常が発生しました。".format(tmp_file_name, row_info.username)
                    # トレースバック
                    self.log_error(messages)
                    all_error_messages.append({"userMasterIdentifier": row_info.userMasterIdentifier,
                                               "detail": messages})
                    continue

                # 「差分」の場合、かつ 繰り返しデータ.ステータス　＝　"tobedeleted"　の場合、削除を行う。
                if model == "delta" and row_info.status == "tobedeleted":
                    # 繰り返しデータ.ロールが「teacher」、「operator」の場合、
                    if row_info.role == "teacher" or row_info.role == "operator":
                        # 変換方法は、「1.3_教員削除_ファイル仕様」の　「CSV仕様」部分に従う。
                        # チェック処理は、「1.3_教員削除_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                        #  ・項目チェックでエラーがない場合、繰り返し中データを「教員削除データ」に追加する。
                        #  ・項目チェックでエラーがある場合、エラー情報をエラーメッセージリストに追加して、次のデータを処理し続ける
                        messages = self.teacher_del_file_make(
                            row_info,
                            del_teacher,
                            del_ldap_datas,
                            master_codes
                        )
                        error_messages.extend(messages)

                    # 「繰り返しデータ」.ロールが「student」の場合、
                    if row_info.role == "student":
                        # 変換方法は、「1.4_児童・生徒削除_ファイル仕様」の　「CSV仕様」部分に従う。
                        # チェック処理は、「1.4_児童・生徒削除_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                        # ・項目チェックでエラーがない場合、繰り返しデータを「児童・生徒削除データ」に追加する。
                        # ・項目チェックでエラーがある場合、エラー情報をエラーメッセージリストに追加して、次のデータを処理し続ける
                        messages = self.student_del_file_make(
                            row_info,
                            del_student,
                            del_ldap_datas,
                            master_codes
                        )
                        error_messages.extend(messages)

                    # 「繰り返しデータ」.ロールが「admin」の場合、
                    if row_info.role == "admin":
                        messages = self.admin_del_file_make(
                            row_info,
                            del_admin,
                            del_ldap_datas,
                            master_codes
                        )
                        error_messages.extend(messages)
                else:
                    # データ操作フラグ(1：新規登録,2：更新,3：異動)
                    sousa_flg = 0
                    if len(user_datas) == 0:
                        # ・ユーザが取得できない場合、
                        # データ操作フラグ="1：新規登録"
                        sousa_flg = 1
                    elif len(user_datas) == 1:
                        # ・取得した件数が1の場合、
                        user_data = user_datas[0]
                        # 取得したデータ.mextUid=繰り返しデータ.userMasterIdentifier（更新とする）
                        if user_data.mextUid == row_info.userMasterIdentifier:
                            # 取得したデータ.自治体ユニークID=繰り返しデータ.自治体ユニークID かつ、
                            # 取得したデータ.ユーザID=上記Ldap検索条件の{ユーザID}の場合
                            # ※レコードが１つのみあり、かつ両方のmextUuid、自治体ユニークID、ユーザIDが同じので、更新、異動とする
                            if user_data.persistent_uid == row_info.userMasterIdentifier.replace("-", "") and \
                                    user_data.user_id == user_id:
                                user_ldap = user_data
                                # 「繰り返しデータ」.ロールが「teacher」、「operator」の場合、
                                if row_info.role == "teacher" or row_info.role == "operator":
                                    # 繰り返しデータ.学校コード　＝　LDAPからのユーザ情報.下部組織コード　の場合、
                                    if row_info.schoolCode == user_ldap.organization_code:
                                        # データ操作フラグ="2：更新"
                                        sousa_flg = 2
                                    else:
                                        # 上記以外
                                        # データ操作フラグ="3：異動"
                                        sousa_flg = 3
                                else:
                                    # 「繰り返しデータ」.ロールが「student、admin」の場合、ユーザID（学校コード+学年コード詰める）が同じので、
                                    # 学校は必ず変更されないので、データ操作フラグ="2：更新"
                                    sousa_flg = 2
                            elif user_data.persistent_uid == row_info.userMasterIdentifier.replace("-", ""):
                                # ・上記以外、取得したデータ.自治体ユニークID=繰り返しデータ.自治体ユニークIDの場合（ユーザIDが変更された、両方のユーザIDが違う）
                                if row_info.role == "student":
                                    user_ldap = user_data
                                    # 「繰り返しデータ」.ロールが「student」の場合、（ユーザIDが変更された）
                                    # 繰り返しデータ.学校コード　＝　LDAPからのユーザ情報.下部組織コード　の場合、
                                    if row_info.schoolCode == user_ldap.organization_code:
                                        # データ操作フラグ="2：更新"
                                        sousa_flg = 2
                                    else:
                                        # 上記以外
                                        # データ操作フラグ="3：異動"
                                        sousa_flg = 3
                                else:
                                    # 教員、OPE管理者の場合、ユーザIDが変更できないため、Ldapに更新対象のユーザIDが存在しないと判定
                                    error_messages.append(
                                        "ユーザID：{0} 更新対象のユーザID{1}が存在しません。（教員、OPE管理者のユーザIDが更新できません）".format(
                                            row_info.username, row_info.username)
                                    )
                            else:
                                # 上記以外、両方の自治体ユニークIDが違う、自治体ユニークIDが変更できないため、エラーとなる
                                error_messages.append(
                                    "ユーザID：{0} 更新対象の自治体ユニークID{1}が存在しません。（自治体ユニークIDが更新できません）".format(
                                        row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                                )
                        else:
                            # 取得したデータ.mextUid＜＞繰り返しデータ.userMasterIdentifier（新規登録とする）
                            # 新規登録とするため、ldapからデータが取得できた（LdapにユーザIDと自治体ユニークIDの一つ、または両方が一致するレコードがある）ので、エラー
                            if user_data.persistent_uid == row_info.userMasterIdentifier.replace("-", "") and \
                                    user_data.user_id == user_id:
                                # エラーリストに追加し、次のデータを処理し続ける
                                error_messages.append(
                                    "ユーザID：{0} ユーザID{1}、自治体ユニークID{2}がすでに存在しています".format(
                                        row_info.username, row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                                )
                            elif user_data.persistent_uid == row_info.userMasterIdentifier.replace("-", ""):
                                # エラーリストに追加し、次のデータを処理し続ける
                                error_messages.append(
                                    "ユーザID：{0} 自治体ユニークID{1}がすでに存在しています".format(
                                        row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                                )
                            else:
                                # エラーリストに追加し、次のデータを処理し続ける
                                error_messages.append(
                                    "ユーザID：{0} ユーザID{1}がすでに存在しています".format(
                                        row_info.username, row_info.username)
                                )
                    elif len(user_datas) == 2:
                        mextUuid_flg = False
                        persistent_uid_flg = False
                        uid_flg = False
                        # 取得したLdapのデータに、mextUuidとOneRoster側のuserMasterIdentifierが一致するレコードがあるかを判定
                        for tmp_user in user_datas:
                            # mextUuidとOneRoster側のuserMasterIdentifierが一致するレコードがある場合、更新とする
                            if tmp_user.mextUid == row_info.userMasterIdentifier:
                                mextUuid_flg = True
                            else:
                                # mextUuidと一致しないレコードに対して、自治体ユニークIDが同じ
                                if tmp_user.persistent_uid == row_info.userMasterIdentifier.replace("-", ""):
                                    persistent_uid_flg = True
                                # mextUuidと一致しないレコードに対して、ユーザIDが同じ
                                if tmp_user.user_id == user_id:
                                    uid_flg = True

                        # ２つレコードに、mextUuidと一致するレコードがない場合、二つレコードが必ずユーザID、自治体ユニークIDで取得された
                        if not mextUuid_flg:
                            error_messages.append(
                                "ユーザID：{0} ユーザID{1}、自治体ユニークID{2}がすでに存在しています".format(
                                    row_info.username, row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                            )
                        else:
                            # ２つレコードの一つがmextUuidと一致するレコード、他の一つが必ずユーザID、自治体ユニークIDで取得された
                            if persistent_uid_flg and uid_flg:
                                error_messages.append(
                                    "ユーザID：{0} ユーザID{1}、自治体ユニークID{2}がすでに存在しています".format(
                                        row_info.username, row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                                )
                            # 自治体ユニークIDのみ一致
                            elif persistent_uid_flg:
                                error_messages.append(
                                    "ユーザID：{0} 自治体ユニークID{1}がすでに存在しています".format(
                                        row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                                )
                            # ユーザIDのみ一致
                            else:
                                error_messages.append(
                                    "ユーザID：{0} ユーザID{1}がすでに存在しています".format(
                                        row_info.username, row_info.username)
                                )
                    else:
                        # レコードが3件以上の場合、必ず、mextUid、自治体ユニークID、ユーザIDでそれぞれ対応するレコード
                        error_messages.append(
                            "ユーザID：{0} ユーザID{1}、自治体ユニークID{2}がすでに存在しています".format(
                                row_info.username, row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                        )

                    # 「データ操作フラグが1：新規登録」の場合、新規登録を行う。
                    if sousa_flg == 1:
                        # ユーザ削除テーブルの自治体ユニックIDの重複チェック
                        if row_info.userMasterIdentifier.replace("-", "") in master_codes["delete_persistent_uids"]:
                            # エラーメッセージ：「ユーザID：{繰り返しデータ.ユーザ名} 「自治体内ユニークID<{}>がすでに存在しています」
                            # をエラーリストに追加し、次のデータを処理し続ける
                            error_messages.append(
                                "ユーザID：{0} 「自治体内ユニークID<{1}>がすでに存在しています".format(
                                    row_info.username, row_info.userMasterIdentifier.replace("-", ""))
                            )
                        else:
                            # 「繰り返しデータ」.ロールが「teacher」、「operator」の場合、
                            if row_info.role == "teacher" or row_info.role == "operator":
                                # 変換方法は、「1.3_教員登録_ファイル仕様」の　「CSV仕様」部分に従う。
                                # チェック処理は、「1.3_教員登録_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                                messages = self.teacher_add_file_make(
                                    row_info,
                                    add_teacher,
                                    master_codes
                                )
                                error_messages.extend(messages)
                            # 「繰り返しデータ」.ロールが「student」の場合、
                            elif row_info.role == "student":
                                # 変換方法は、「1.4_児童・生徒登録_ファイル仕様」の　「CSV仕様」部分に従う。
                                # チェック処理は、「1.4_児童・生徒登録_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                                messages = self.student_add_file_make(
                                    row_info,
                                    add_student,
                                    master_codes
                                )
                                error_messages.extend(messages)
                            # 「繰り返しデータ」.ロールが「admin」の場合、
                            else:
                                messages = self.admin_add_file_make(
                                    row_info,
                                    add_admin
                                )
                                error_messages.extend(messages)

                    # データ操作フラグ="2：更新"　の場合、更新を行う。
                    if sousa_flg == 2:
                        # 「繰り返しデータ」.ロールが「teacher」、「operator」の場合、
                        if row_info.role == "teacher" or row_info.role == "operator":
                            # ロールがLDAPの値と不一致の場合変更不可
                            if user_ldap.role == "teacher" or user_ldap.role == "operator":
                                # 変換方法は、「1.3_教員更新_ファイル仕様」の　「CSV仕様」部分に従う。
                                # チェック処理は、「1.3_教員更新_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                                messages = self.teacher_mod1_file_make(
                                    row_info,
                                    mod1_teacher,
                                    user_ldap,
                                    master_codes
                                )
                                before_info[user_ldap.user_id] = user_ldap
                                error_messages.extend(messages)
                            else:
                                error_messages.append(
                                    "ユーザID：{0} ロール（権限）が変更できません。CSVファイルの値とLdapの値が不一致です。"
                                    "Ldapのロール：{1}".format(
                                        row_info.username, user_ldap.role)
                                )
                        # 「繰り返しデータ」.ロールが「student」の場合、
                        elif row_info.role == "student":
                            # ロールがLDAPの値と不一致の場合変更不可
                            if user_ldap.role == "student":
                                # 変換方法は、「1.4_児童・生徒更新_ファイル仕様」の　「CSV仕様」部分に従う。
                                # チェック処理は、「1.4_児童・生徒更新_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                                messages = self.student_mod1_file_make(
                                    row_info,
                                    mod1_student,
                                    user_ldap,
                                    master_codes
                                )
                                before_info[user_ldap.user_id] = user_ldap
                                error_messages.extend(messages)
                            else:
                                error_messages.append(
                                    "ユーザID：{0} ロール（権限）が変更できません。CSVファイルの値とLdapの値が不一致です。"
                                    "Ldapのロール：{1}".format(
                                        row_info.username, user_ldap.role)
                                )

                        # 「繰り返しデータ」.ロールが「admin」の場合、
                        else:
                            # ロールがLDAPの値と不一致の場合変更不可
                            if user_ldap.role == "admin":
                                messages = self.admin_mod1_file_make(
                                    row_info,
                                    mod1_admin,
                                    user_ldap
                                )
                                before_info[user_ldap.user_id] = user_ldap
                                error_messages.extend(messages)
                            else:
                                error_messages.append(
                                    "ユーザID：{0} ロール（権限）が変更できません。CSVファイルの値とLdapの値が不一致です。"
                                    "Ldapのロール：{1}".format(
                                        row_info.username, user_ldap.role)
                                )

                    # データ操作フラグ="3：異動"　の場合、異動を行う。
                    if sousa_flg == 3:
                        # 「繰り返しデータ」.ロールが「teacher」、「operator」の場合、
                        if user_ldap.role == "teacher" or user_ldap.role == "operator":
                            # ロールがLDAPの値と不一致の場合変更不可
                            if row_info.role == "teacher" or row_info.role == "operator":
                                # 変換方法は、「1.3_教員異動_ファイル仕様」の　「CSV仕様」部分に従う。
                                # チェック処理は、「1.3_教員異動_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                                messages = self.teacher_mod2_file_make(
                                    row_info,
                                    mod2_teacher,
                                    user_ldap,
                                    master_codes
                                )
                                before_info[user_ldap.user_id] = user_ldap
                                error_messages.extend(messages)
                            else:
                                error_messages.append(
                                    "ユーザID：{0} ロール（権限）が変更できません。CSVファイルの値とLdapの値が不一致です。"
                                    "Ldapのロール：{1}".format(
                                        row_info.username, user_ldap.role)
                                )

                        # 「繰り返しデータ」.ロールが「student」の場合、
                        else:
                            # ロールがLDAPの値と不一致の場合変更不可
                            if row_info.role == "student":
                                # 変換方法は、「1.4_児童・生徒進学_ファイル仕様」の　「CSV仕様」部分に従う。
                                # チェック処理は、「1.4_児童・生徒進学_ファイル仕様」の　「処理No.1　データチェック」部分に従う。
                                messages = self.student_mod2_file_make(
                                    row_info,
                                    mod2_student,
                                    user_ldap,
                                    master_codes
                                )
                                before_info[user_ldap.user_id] = user_ldap
                                error_messages.extend(messages)
                            else:
                                error_messages.append(
                                    "ユーザID：{0} ロール（権限）が変更できません。CSVファイルの値とLdapの値が不一致です。"
                                    "Ldapのロール：{1}".format(
                                        row_info.username, user_ldap.role)
                                )

                # エラーがある場合、エラー情報をエラーメッセージリストに追加して、次のデータを処理し続ける
                if error_messages:
                    for val in error_messages:
                        relation_file = "。関連CSVファイル：users.csv"
                        if "学校コード" in val:
                            relation_file += "、roles.csv、orgs.csv"

                        if "有効年度" in val:
                            relation_file += "、enrollments.csv、classes.csv、academicSessions.csv"

                        if "権限" in val:
                            relation_file += "、roles.csv"

                        if "性別" in val:
                            relation_file += "、demographics.csv"

                        if "組コード" in val or "教科コード" in val:
                            relation_file += "、enrollments.csv、classes.csv"

                        message_content = {
                            "userMasterIdentifier": row_info.userMasterIdentifier,
                            "detail": val + relation_file
                        }

                        self.log_error(message_content)
                        all_error_messages.append(message_content)

        except Exception as exception:
            # トレースバック
            self.log_error('ファイル処理中、想定外のエラーが発生した')
            self.log_error(traceback.format_exc())
            if csv_file:
                self.move_deal_file(tmp_full_file_name, tmp_err_file_name, csv_file)
            if len(all_error_messages) > 0:
                self.export_error_csv_file(all_error_messages, error_file_directory, deal_start_time)

            self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")
            return {
                "keizoku_flag": 1,
                "success_count": 0
            }

        if model == "delta":
            operator_id = os.environ.get("BATCH_OPERATOR_ID")
            # 削除の場合
            if len(del_teacher) > 0:
                operation_type = "teacher13"
                data_columns = csv_roster_setting.bulk_column["teacher13"]
                headers = csv_roster_setting.bulk_header["teacher13"]

                self.export_csv_file(
                    del_teacher,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["top_organization"].school_code,
                    operation_type,
                    aws_request_id
                )

                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["top_organization"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            if len(del_student) > 0:
                operation_type = "student13"
                data_columns = csv_roster_setting.bulk_column["student13"]
                headers = csv_roster_setting.bulk_header["student13"]
                capture_users_dict = {}

                # CSVファイルの学校コードとLdapの学校コードが不一致の可能性があるので、
                # mextUidで削除実行する前に、Ldapの学校により、受付を分ける（児童生徒の場合、受付は学校単位で実行）
                for student in del_student:
                    if student["organization_code"] in capture_users_dict:
                        capture_users_dict[student["organization_code"]].append(student)
                    else:
                        capture_user = [student]
                        capture_users_dict[student["organization_code"]] = capture_user

                # 学校ごとに受付け
                for capture_school in capture_users_dict:
                    self.export_csv_file(
                        capture_users_dict[capture_school],
                        data_columns,
                        headers,
                        system_organization_code,
                        capture_school,
                        operation_type,
                        aws_request_id
                    )

                    self.insert_bulk_status(
                        ApplyInfo(
                            operation_status=3,
                            operation_type=operation_type,
                            target_system_organization_code=system_organization_code,
                            target_organization_code=capture_school,
                            entry_person=operator_id,
                            update_person=operator_id,
                            remarks="ファイル受付完了",
                        )
                    )

            if len(del_admin) > 0:
                operation_type = "admin13"
                data_columns = csv_roster_setting.bulk_column["admin13"]
                headers = csv_roster_setting.bulk_header["admin13"]

                self.export_csv_file(
                    del_admin,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["school_master"].school_code,
                    operation_type,
                    aws_request_id
                )

                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["school_master"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            # 新規の場合
            if len(add_teacher) > 0:
                data_columns = csv_roster_setting.bulk_column["teacher11"]
                headers = csv_roster_setting.bulk_header["teacher11"]
                operation_type = "teacher11"

                self.export_csv_file(
                    add_teacher,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["top_organization"].school_code,
                    operation_type,
                    aws_request_id
                )

                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["top_organization"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            if len(add_student) > 0:
                data_columns = csv_roster_setting.bulk_column["student11"]
                headers = csv_roster_setting.bulk_header["student11"]
                operation_type = "student11"

                self.export_csv_file(
                    add_student,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["school_master"].school_code,
                    operation_type,
                    aws_request_id
                )

                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["school_master"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )
            if len(add_admin) > 0:
                data_columns = csv_roster_setting.bulk_column["admin11"]
                headers = csv_roster_setting.bulk_header["admin11"]
                operation_type = "admin11"

                self.export_csv_file(
                    add_admin,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["school_master"].school_code,
                    operation_type,
                    aws_request_id
                )

                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["school_master"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            # 更新の場合
            if len(mod1_teacher) > 0:
                data_columns = csv_roster_setting.bulk_column["teacher12"]
                headers = csv_roster_setting.bulk_header["teacher12"]
                operation_type = "teacher12"

                self.export_csv_file(
                    mod1_teacher,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["top_organization"].school_code,
                    operation_type,
                    aws_request_id
                )
                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["top_organization"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            if len(mod1_student) > 0:
                data_columns = csv_roster_setting.bulk_column["student12"]
                headers = csv_roster_setting.bulk_header["student12"]
                operation_type = "student12"

                self.export_csv_file(
                    mod1_student,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["school_master"].school_code,
                    operation_type,
                    aws_request_id
                )
                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["school_master"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )
            if len(mod1_admin) > 0:
                data_columns = csv_roster_setting.bulk_column["admin12"]
                headers = csv_roster_setting.bulk_header["admin12"]
                operation_type = "admin12"

                self.export_csv_file(
                    mod1_admin,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["school_master"].school_code,
                    operation_type,
                    aws_request_id
                )
                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["school_master"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            # 異動の場合
            if len(mod2_teacher) > 0:
                data_columns = csv_roster_setting.bulk_column["teacher14"]
                headers = csv_roster_setting.bulk_header["teacher14"]
                operation_type = "teacher14"

                self.export_csv_file(
                    mod2_teacher,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["top_organization"].school_code,
                    operation_type,
                    aws_request_id)
                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["top_organization"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )

            if len(mod2_student) > 0:
                data_columns = csv_roster_setting.bulk_column["student14"]
                headers = csv_roster_setting.bulk_header["student14"]
                operation_type = "student14"

                self.export_csv_file(
                    mod2_student,
                    data_columns,
                    headers,
                    system_organization_code,
                    master_codes["top_organization"].school_code,
                    operation_type,
                    aws_request_id
                )
                self.insert_bulk_status(
                    ApplyInfo(
                        operation_status=3,
                        operation_type=operation_type,
                        target_system_organization_code=system_organization_code,
                        target_organization_code=master_codes["top_organization"].school_code,
                        entry_person=operator_id,
                        update_person=operator_id,
                        remarks="ファイル受付完了",
                    )
                )
            success_count = len(del_teacher) + len(del_student) + len(del_admin) + \
                            len(add_teacher) + len(add_student) + len(add_admin) + \
                            len(mod1_teacher) + len(mod1_student) + len(mod1_admin) + \
                            len(mod2_teacher) + len(mod2_student)

        if model == "bulk":
            data_count = len(del_teacher) + len(del_student) + len(del_admin) + \
                len(add_teacher) + len(add_student) + len(add_admin) + \
                len(mod1_teacher) + len(mod1_student) + len(mod1_admin) + \
                len(mod2_teacher) + len(mod2_student)
            if data_count > 0:
                ldif_file_make_service = LdifFileMakeService(system_organization_code)
                oneroster_directory = oneroster_file_path + s3_file_key_id
                file_current = tmp_file_name.split("_")[-1].replace(".csv", "")
                result = ldif_file_make_service.ldif_file_make(
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
                    file_current)
                all_error_messages.extend(result["error_list"])
                success_count = result["success_count"]
            else:
                success_count = 0

        # エラーメッセージをcsvファイルへ出力
        if len(all_error_messages) > 0:
            self.export_error_csv_file(all_error_messages, error_file_directory, deal_start_time)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CSV MATCHING SERVICES ###")

        return {
            "keizoku_flag": 1,
            "success_count": success_count,
            "limit_flag": limit_flag
        }

    def teacher_del_file_make(self, in_info, out_info, seach_ldap_datas, master_codes):
        """
        教員差分削除メソッド

        Parameters
        -------
            tempCsvファイルから取得したteacher情報
            :param self:
            :param in_info:
            :param out_info:
            :param  seach_ldap_datas:
            :param master_codes:

        Returns
        -------
            error_messages

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER DEL FILE MAKE ###")

        # 学校コード: 一時ファイル.学校コード
        # ユーザID: 一時ファイル.ユーザ名
        teacher_dict = {
            "organization_code": "",
            "user_id": ""
        }
        error_messages = []
        # 教員情報の存在チェックを行う
        if len(seach_ldap_datas) != 1:
            error_messages.append("削除対象のユーザはすでに削除されています")
        else:
            user_data = seach_ldap_datas[0]
            teacher_dict['organization_code'] = user_data.organization_code
            teacher_dict['user_id'] = user_data.user_id
            # Cerberusバリデーションを実施する。
            error_messages = bulk_validate(
                batch_oneroster_validation.teacher_delete_request, teacher_dict
            )

        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]
        if len(row_error_messages) == 0:
            out_info.append(teacher_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER DEL FILE MAKE ###")
        return row_error_messages

    def admin_del_file_make(self, in_info, out_info, seach_ldap_datas, master_codes):
        """
        OPE管理者差分削除メソッド

        Parameters
        -------
            tempCsvファイルから取得したadmin情報
            :param self:
            :param in_info:
            :param out_info:
            :param  seach_ldap_datas:
            :param master_codes:

        Returns
        -------
            error_messages

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES ADMIN DEL FILE MAKE ###")

        # 学校コード: 一時ファイル.学校コード
        # ユーザID: 一時ファイル.ユーザ名
        admin_dict = {
            "organization_code": in_info.schoolCode,
            "user_id": ""
        }

        error_messages = []

        # OPE管理者情報の存在チェックを行う
        if len(seach_ldap_datas) != 1:
            error_messages.append("削除対象のユーザはすでに削除されています")
        else:
            user_data = seach_ldap_datas[0]
            admin_dict['user_id'] = user_data.user_id
            # Cerberusバリデーションを実施する。
            error_messages = bulk_validate(
                batch_oneroster_validation.admin_delete_request, admin_dict
            )

        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]
        if len(row_error_messages) == 0:
            out_info.append(admin_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES ADMIN DEL FILE MAKE ###")
        return row_error_messages

    def teacher_add_file_make(self, in_info, out_info, master_codes):
        """
        教員差分登録メソッド

        Parameters
        -------
            tempCsvファイルから取得したteacher情報
            :param self:
            :param in_info:
            :param out_info:
            :param master_codes:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER ADD FILE MAKE ###")

        relationgg = "0"
        relationwin = "0"
        class_code = int(in_info.classCode) if in_info.classCode else ""

        teacher_dict = {
            "organization_code": in_info.schoolCode,
            "fiscal_year": in_info.schoolYear,
            "role": in_info.role,
            "user_id": in_info.username,
            "persistent_uid": in_info.userMasterIdentifier.replace("-", ""),
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "sur_name_kana": in_info.kanaFamilyName,
            "given_name_kana": in_info.kanaGivenName,
            "password": oneroster_info_setting.DUMMY_PASSWORD,
            "gender": in_info.sex,
            "mail": in_info.email,
            "title_code": "",
            "additional_post_code": "",
            "grade_code": in_info.grades,
            "class_code": class_code,
            "subject_code": in_info.subjectCodes,
            "relationgg": relationgg,
            "relationwin": relationwin,
            "mextUid": in_info.userMasterIdentifier
        }

        # ”teacher11”キーで各変換ルールを適用する。
        teacher_service = TeacherService()
        operation_type = "teacher11"
        teacher_dict_copy = copy.deepcopy(teacher_dict)
        teacher_service.set_rule(teacher_dict_copy, operation_type)

        # 組コードが空の場合はキーを削除する
        if teacher_dict_copy.get("class_code") == "":
            teacher_dict_copy.pop("class_code")
        # userMasterIdentifierが一時ファイル分割の時、チェック済みなので、mextUuidの再チェックが不要
        teacher_dict_copy.pop("mextUid")
        # バリデーション実施
        error_messages = bulk_validate(
            batch_oneroster_validation.teacher_bulk_create_row_request,
            teacher_dict_copy
        )

        # 権限が"operator"でメールアドレスが空である場合、
        if teacher_dict_copy["role"] == "operator":
            if teacher_dict_copy["mail"] == "":
                error_messages.append("管理者にメールアドレスは必須です")

        # 学年コードが空で組コードに値がある場合、
        if teacher_dict_copy.get("grade_code") == "" and teacher_dict_copy.get(
            "class_code"
        ):
            error_messages.append("学年コードが空の場合、組コードは設定できません")

        # マスタ整合性チェック
        teacher_service.check_master_code_integrity(
            teacher_dict,
            master_codes,
            error_messages
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(teacher_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER ADD FILE MAKE ###")
        return row_error_messages

    def admin_add_file_make(self, in_info, out_info):
        """
        OPE管理者差分登録メソッド

        Parameters
        -------
            tempCsvファイルから取得したadmin情報
            :param self:
            :param in_info:
            :param out_info:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES ADMIN ADD FILE MAKE ###")

        relationgg = "0"
        relationwin = "0"

        admin_dict = {
            "organization_code": in_info.schoolCode,
            "role": in_info.role,
            "user_id": in_info.username,
            "persistent_uid": in_info.userMasterIdentifier.replace("-", ""),
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "password": oneroster_info_setting.DUMMY_PASSWORD,
            "gender": in_info.sex,
            "mail": in_info.email,
            "title_code": "0",
            "relationgg": relationgg,
            "relationwin": relationwin,
            "mextUid": in_info.userMasterIdentifier,
        }

        # ”admin11”キーで各変換ルールを適用する。
        teacher_service = TeacherService()
        operation_type = "admin11"
        admin_dict_copy = copy.deepcopy(admin_dict)
        teacher_service.set_rule(admin_dict_copy, operation_type)

        # userMasterIdentifierが一時ファイル分割の時、チェック済みなので、mextUuidの再チェックが不要
        admin_dict_copy.pop("mextUid")
        # OPE管理者のtitle_codeが必ず0なので、再チェックが不要
        admin_dict_copy.pop("title_code")
        # バリデーション実施
        error_messages = bulk_validate(
            batch_oneroster_validation.opeadmin_create_request,
            admin_dict_copy
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(admin_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES ADMIN ADD FILE MAKE ###")
        return row_error_messages

    def teacher_mod1_file_make(self, in_info, out_info, user_ldap: User, master_codes):
        """
        教員差分更新メソッド

        Parameters
        -------
            tempCsvファイルから取得したteacher情報
            :param self:
            :param in_info:
            :param out_info:
            :param user_ldap:
            :param master_codes:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER MOD1 FILE MAKE ###")

        class_code = int(in_info.classCode) if in_info.classCode else ""
        # LDAPの非必須項目が未設定（Noneを取得）の場合、空文字に変換する
        if not user_ldap.sur_name_kana:
            user_ldap.sur_name_kana = ""
        if not user_ldap.given_name_kana:
            user_ldap.given_name_kana = ""
        if not user_ldap.title_code:
            user_ldap.title_code = []
        if not user_ldap.additional_post_code:
            user_ldap.additional_post_code = []

        teacher_dict = {
            "organization_code": in_info.schoolCode,
            "fiscal_year": in_info.schoolYear,
            "role": in_info.role,
            "user_id": in_info.username,
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "sur_name_kana": user_ldap.sur_name_kana,
            "given_name_kana": user_ldap.given_name_kana,
            "password": "",
            "gender": in_info.sex,
            "mail": in_info.email,
            "title_code": ','.join(user_ldap.title_code),
            "additional_post_code": ','.join(user_ldap.additional_post_code),
            "grade_code": in_info.grades,
            "class_code": class_code,
            "subject_code": in_info.subjectCodes,
            "relationgg": user_ldap.relationgg,
            "relationwin": user_ldap.relationwin
        }

        # ”teacher12”キーで各変換ルールを適用する。
        teacher_service = TeacherService()
        operation_type = "teacher12"
        teacher_dict_copy = copy.deepcopy(teacher_dict)
        teacher_service.set_rule(teacher_dict_copy, operation_type)
        # 組コードが空の場合はキーを削除する
        if teacher_dict_copy.get("class_code") == "":
            teacher_dict_copy.pop("class_code")

        # バリデーション実施
        error_messages = bulk_validate(
            batch_oneroster_validation.teacher_bulk_update_row_request,
            teacher_dict_copy
        )

        if teacher_dict_copy["role"] == "operator":
            if teacher_dict_copy["mail"] == "":
                error_messages.append("管理者にメールアドレスは必須です")

        if teacher_dict_copy["grade_code"] == "":
            if teacher_dict_copy["class_code"] != "":
                error_messages.append("学年コードが空の場合、組コードは設定できません")

        # マスタ整合性チェック
        teacher_service.check_master_code_integrity(
            teacher_dict,
            master_codes,
            error_messages
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(teacher_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER MOD1 FILE MAKE ###")
        return row_error_messages

    def admin_mod1_file_make(self, in_info, out_info, user_ldap: User):
        """
        OPE管理者差分更新メソッド

        Parameters
        -------
            tempCsvファイルから取得したadmin情報
            :param self:
            :param in_info:
            :param out_info:
            :param user_ldap:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES ADMIN MOD1 FILE MAKE ###")

        admin_dict = {
            "organization_code": in_info.schoolCode,
            "role": in_info.role,
            "user_id": in_info.username,
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "password": "",
            "gender": in_info.sex,
            "mail": in_info.email,
            "relationgg": user_ldap.relationgg,
            "relationwin": user_ldap.relationwin
        }

        # ”admin12”キーで各変換ルールを適用する。
        teacher_service = TeacherService()
        operation_type = "admin12"
        admin_dict_copy = copy.deepcopy(admin_dict)
        teacher_service.set_rule(admin_dict_copy, operation_type)

        # バリデーション実施
        error_messages = bulk_validate(
            batch_oneroster_validation.opeadmin_update_request,
            admin_dict_copy
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(admin_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES ADMIN MOD1 FILE MAKE ###")
        return row_error_messages

    def teacher_mod2_file_make(self, in_info, out_info, user_ldap: User, master_codes):
        """
        教員差分異動メソッド

        Parameters
        -------
            tempCsvファイルから取得したteacher情報
            :param self:
            :param in_info:
            :param out_info:
            :param user_ldap:
            :param master_codes:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER MOD2 FILE MAKE ###")

        class_code = int(in_info.classCode) if in_info.classCode else ""
        # LDAPの非必須項目が未設定（Noneを取得）の場合、空文字に変換する
        if not user_ldap.sur_name_kana:
            user_ldap.sur_name_kana = ""
        if not user_ldap.given_name_kana:
            user_ldap.given_name_kana = ""
        if not user_ldap.title_code:
            user_ldap.title_code = []
        if not user_ldap.additional_post_code:
            user_ldap.additional_post_code = []

        teacher_dict = {
            "before_organization_code": user_ldap.organization_code,
            "organization_code": in_info.schoolCode,
            "fiscal_year": in_info.schoolYear,
            "role": in_info.role,
            "user_id": in_info.username,
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "sur_name_kana": user_ldap.sur_name_kana,
            "given_name_kana": user_ldap.given_name_kana,
            "password": "",
            "gender": in_info.sex,
            "mail": in_info.email,
            "title_code": ','.join(user_ldap.title_code),
            "additional_post_code": ','.join(user_ldap.additional_post_code),
            "grade_code": in_info.grades,
            "class_code": class_code,
            "subject_code": in_info.subjectCodes,
            "relationgg": user_ldap.relationgg,
            "relationwin": user_ldap.relationwin
        }

        # ”teacher14”キーで各変換ルールを適用する。
        teacher_service = TeacherService()
        operation_type = "teacher14"
        teacher_dict_copy = teacher_dict.copy()
        teacher_service.set_rule(teacher_dict_copy, operation_type)

        # 組コードが空の場合はキーを削除する
        if teacher_dict_copy.get("class_code") == "":
            teacher_dict_copy.pop("class_code")

        # バリデーション実施
        error_messages = bulk_validate(
            batch_oneroster_validation.teacher_bulk_transfer_row_request,
            teacher_dict_copy
        )

        if teacher_dict_copy["role"] == "operator":
            if teacher_dict_copy["mail"] == "":
                error_messages.append("管理者にメールアドレスは必須です")

        if teacher_dict_copy["grade_code"] == "":
            if teacher_dict_copy["class_code"] != "":
                error_messages.append("学年コードが空の場合、組コードは設定できません")

        # マスタ整合性チェック
        teacher_service.check_master_code_integrity(
            teacher_dict,
            master_codes,
            error_messages
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(teacher_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES TEACHER MOD2 FILE MAKE ###")
        return row_error_messages

    def student_del_file_make(self, in_info, out_info, seach_ldap_datas, master_codes):
        """
        児童・生徒差分削除メソッド

        Parameters
        -------
            tempCsvファイルから取得したstudent情報
            :param self:
            :param in_info:
            :param out_info:
            :param seach_ldap_datas:
            :param master_codes:

        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT DEL FILE MAKE ###")

        # 学校コード  : 一時ファイル.学校コード
        # ユーザID  　: 一時ファイル.学校コード＋一時ファイル.学年＋一時ファイル.ユーザ名
        # 学年コード  : 一時ファイル.学年
        student_dict = {
            "organization_code": '',
            "user_id": '',
            "grade_code": ''
        }

        error_messages = []

        # LDAP.mextUuid = users.csvのuserMasterIdentifierが存在するかを判定
        if len(seach_ldap_datas) != 1:
            error_messages.append("削除対象のユーザはすでに削除されています")
        else:
            user_data = seach_ldap_datas[0]
            student_dict['organization_code'] = user_data.organization_code
            student_dict['user_id'] = user_data.user_id
            student_dict['grade_code'] = user_data.grade_code
            # Cerberusバリデーションを実施する。
            error_messages = bulk_validate(
                batch_oneroster_validation.student_delete_request,
                student_dict
            )

        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(student_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT DEL FILE MAKE ###")
        return row_error_messages

    def student_add_file_make(self, in_info, out_info, master_codes):
        """
        児童生徒差分登録メソッド

        Parameters
        -------
            tempCsvファイルから取得したstudent情報
            :param self:
            :param in_info:
            :param out_info:
            :param master_codes:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT ADD FILE MAKE ###")

        relationgg = "0"
        relationwin = "0"
        class_code = int(in_info.classCode) if in_info.classCode else ""

        student_dict = {
            "fiscal_year": in_info.schoolYear,
            "user_id": in_info.username,
            "persistent_uid": in_info.userMasterIdentifier.replace("-", ""),
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "sur_name_kana": in_info.kanaFamilyName,
            "given_name_kana": in_info.kanaGivenName,
            "password": oneroster_info_setting.DUMMY_PASSWORD,
            "gender": in_info.sex,
            "mail": in_info.email,
            "grade_code": in_info.grades,
            "class_code": class_code,
            "student_number": in_info.shussekiNo,
            "relationgg": relationgg,
            "relationwin": relationwin,
            "mextUid": in_info.userMasterIdentifier
        }

        # "student11"キーで各変換ルールを適用する。
        operation_type = "student11"
        student_service = StudentService()
        student_dict_copy = copy.deepcopy(student_dict)
        student_service.set_rule(student_dict_copy, operation_type)
        student_dict_copy["organization_code"] = in_info.schoolCode

        # 組コードが空の場合はキーを削除する
        if student_dict_copy.get("class_code") == "":
            student_dict_copy.pop("class_code")
        # userMasterIdentifierが一時ファイル分割の時、チェック済みなので、mextUuidの再チェックが不要
        student_dict_copy.pop("mextUid")

        error_messages = bulk_validate(
            batch_oneroster_validation.student_bulk_create_row_request,
            student_dict_copy
        )

        # マスタ整合性チェック
        student_service.check_master_code_integrity(
            student_dict,
            master_codes,
            error_messages
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(student_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT ADD FILE MAKE ###")
        return row_error_messages

    def student_mod1_file_make(self, in_info, out_info, user_ldap: User, master_codes):
        """
        児童生徒差分更新メソッド

        Parameters
        -------
            tempCsvファイルから取得したstudent情報
            :param self:
            :param in_info:
            :param out_info:
            :param user_ldap:
            :param master_codes:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT MOD1 FILE MAKE ###")

        replace_str = f"^{user_ldap.organization_code}{user_ldap.grade_code}"
        user_id = re.sub(replace_str, "", user_ldap.user_id, 1).strip()

        class_code = int(in_info.classCode) if in_info.classCode else ""
        if not user_ldap.sur_name_kana:
            user_ldap.sur_name_kana = ""
        if not user_ldap.given_name_kana:
            user_ldap.given_name_kana = ""

        student_dict = {
            "before_user_id": user_id,
            "before_grade_code": user_ldap.grade_code,
            "fiscal_year": in_info.schoolYear,
            "user_id": in_info.username,
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "sur_name_kana": user_ldap.sur_name_kana,
            "given_name_kana": user_ldap.given_name_kana,
            "password": "",
            "gender": in_info.sex,
            "mail": in_info.email,
            "grade_code": in_info.grades,
            "class_code": class_code,
            "student_number": in_info.shussekiNo,
            "relationgg": user_ldap.relationgg,
            "relationwin": user_ldap.relationwin
        }

        # "student12"キーで各変換ルールを適用する。
        operation_type = "student12"
        student_service = StudentService()
        student_dict_copy = copy.deepcopy(student_dict)
        student_service.set_rule(student_dict_copy, operation_type)
        student_dict_copy["organization_code"] = in_info.schoolCode

        # 組コードが空の場合はキーを削除する
        if student_dict_copy.get("class_code") == "":
            student_dict_copy.pop("class_code")

        error_messages = bulk_validate(
            batch_oneroster_validation.student_bulk_update_row_request,
            student_dict_copy
        )

        # マスタ整合性チェック
        student_service.check_master_code_integrity(
            student_dict,
            master_codes,
            error_messages
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(student_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT MOD1 FILE MAKE ###")
        return error_messages

    def student_mod2_file_make(self, in_info, out_info, user_ldap: User, master_codes):
        """
        児童生徒差分異動メソッド

        Parameters
        -------
            tempCsvファイルから取得したstudent情報
            :param self:
            :param in_info:
            :param out_info:
            :param user_ldap:
            :param master_codes:
        Returns
        -------
            out_info

        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT MOD2 FILE MAKE ###")

        replace_str = f"^{user_ldap.organization_code}{user_ldap.grade_code}"
        user_id = re.sub(replace_str, "", user_ldap.user_id, 1).strip()

        class_code = int(in_info.classCode) if in_info.classCode else ""
        if not user_ldap.sur_name_kana:
            user_ldap.sur_name_kana = ""
        if not user_ldap.given_name_kana:
            user_ldap.given_name_kana = ""

        student_dict = {
            "before_organization_code": user_ldap.organization_code,
            "before_user_id_transfer": user_id,
            "before_grade_code_transfer": user_ldap.grade_code,
            "organization_code": in_info.schoolCode,
            "fiscal_year": in_info.schoolYear,
            "user_id": in_info.username,
            "sur_name": in_info.familyName,
            "given_name": in_info.givenName,
            "sur_name_kana": user_ldap.sur_name_kana,
            "given_name_kana": user_ldap.given_name_kana,
            "password": "",
            "gender": in_info.sex,
            "mail": in_info.email,
            "grade_code": in_info.grades,
            "class_code": class_code,
            "student_number": in_info.shussekiNo,
            "relationgg": user_ldap.relationgg,
            "relationwin": user_ldap.relationwin
        }

        # "student14"キーで各変換ルールを適用する。
        operation_type = "student14"
        student_service = StudentService()
        student_dict_copy = copy.deepcopy(student_dict)
        student_service.set_rule(student_dict_copy, operation_type)

        # 組コードが空の場合はキーを削除する
        if student_dict_copy.get("class_code") == "":
            student_dict_copy.pop("class_code")

        error_messages = bulk_validate(
            batch_oneroster_validation.student_bulk_transfer_row_request,
            student_dict_copy
        )

        # マスタ整合性チェック
        student_service.check_master_code_integrity(
            student_dict,
            master_codes,
            error_messages
        )

        # エラーメッセージが空ではない場合、定型バリデーション、コードチェックは配列でメッセージをエラーメッセージリストに設定する。
        # エラーメッセージ：ユーザID：{繰り返しデータ.ユーザ名} {エラーメッセージ}
        row_error_messages = [
            f"ユーザID：{in_info.username} {val}" for val in error_messages
        ]

        if len(row_error_messages) == 0:
            out_info.append(student_dict)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES STUDENT MOD2 FILE MAKE ###")
        return row_error_messages

    def export_csv_file(
            self,
            out_data,
            data_columns,
            headers,
            system_organization_code,
            orgnization_code,
            operation_type,
            aws_request_id
    ):
        """
        新規/更新/異動/削除csvファイルを出力

        Parameters
        ----------
            :param out_data:
            :param data_columns:
            :param system_organization_code:
            :param orgnization_code:
            :param operation_type:
            :param aws_request_id:

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES EXPORT CSV FILE ###")

        # 児童生徒削除と教員削除の場合、受付ファイルにヘッダー出力されない
        header_export_flg = True
        if operation_type in ("student13", "teacher13", "admin13"):
            header_export_flg = False

        # csvファイル作成
        csv_contents = self.create_master_file_contents(
            out_data,
            data_columns,
            headers,
            header_export_flg
        )

        self.s3_access_object.export(
            "{0}/{1}/{2}/{3}/{4}_{5}_bulk_oneroster.csv".format(
                "user",
                system_organization_code,
                orgnization_code,
                operation_type,
                os.environ.get("BATCH_OPERATOR_ID"),
                aws_request_id,
            ),
            csv_contents,
        )

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES EXPORT CSV FILE ###")
        return

    def export_error_csv_file(self, error_messages, error_file_directory, deal_start_time):
        """
        エラーメッセージファイルを生成する

        Parameters
        ----------
            :param error_messages:エラーメッセージリスト
            :param error_file_directory:エラーメッセージリスト
            :param deal_start_time:処理開始日時

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES EXPORT ERROR CSV FILE ###")

        # csvファイル出力
        out_csv_file_name = "error_messages_" + deal_start_time
        out_csv_file_path = (error_file_directory + out_csv_file_name + ".csv")

        csv_file = ""
        file_list = self.s3_access_object.get_file_list(error_file_directory)
        # 指定パスにエラーファイルがある場合
        for file_ls_name in file_list:
            if file_ls_name.split("/")[-1] == out_csv_file_name + ".csv":
                # 他の分割ファイルのエラーデータを取得
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
        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES EXPORT ERROR CSV FILE ###")
        return

    def move_deal_file(self, from_file_name, to_file_name, csv_file_content):
        """
        処理エラーファイルをエラーフォルダに移動して、元ファイルを削除する
        :param from_file_name:
        :param to_file_name:
        :param csv_file_content:
        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES MOVE DEAL FILE ###")

        # csvファイルをS3から読み込む
        self.s3_access_object.export(to_file_name, csv_file_content)
        # 元パスのファイルを削除する
        self.s3_access_object.del_file(from_file_name)

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES MOVE DEAL FILE ###")

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
            # csv_school_info = result.get_dict(allow_empty=True)
            writer.writerow(result)
        csv_data = buffer.getvalue()
        buffer.close()
        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES CREATE MASTER FILE CONTENTS ###")
        return csv_data

    def insert_bulk_status(self, apply_info):
        """一括登録時のファイル受付情報を申込履歴テーブルに登録する
        ユーザ個別の申込履歴ではなく、ファイル処理開始、終了時の案内を登録する
        Parameters
        ----------
        apply_info : ApplyInfo
            申込情報に登録する情報
        Returns
        -------
        return : None
        """
        self.log_info("申込情報登録 , Operator : -" + f" , Input : {apply_info}")

        crud_model = CRUDModel(self.rds_access_object)
        for i in range(self.db_retry_count):
            try:
                self.rds_access_object.begin()
                crud_model.insert(apply_info.target_system_organization_code,
                                  RDS_TABLE.APPLY_INFO,
                                  apply_info)
                self.rds_access_object.commit()
                break
            except Exception as exception:
                self.log_info("処理異常 , Operator : - , Output : -")
                self.rds_access_object.rollback()
                if (i + 1) < self.db_retry_count:
                    self.log_info(f"RetryError : Retry processing(insert_bulk_status) for the {i + 1} time.")
                    # 次の試行まで待つ
                    time.sleep(self.db_retry_interval)
                    continue
                else:
                    # トレースバック
                    self.log_error('申込情報登録時、最大回数までリトライしても異常終了')
                    self.log_error(traceback.format_exc())
            finally:
                self.rds_access_object.close()
        self.log_info(
            "申込情報コミット , Operator : - , Output : -")

    def send_email(self, handle_result):
        """
        SNSを利用して、処理結果のメールを送信する

        Parameters
        ----------
        handle_result : dict
            実行結果（処理件数）

        Returns
        -------
        is_success: bool
            実行結果
        """
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES SEND EMAIL BY SNS ###")
        sub = "SNS OneRoster CSV 入力バッチ結果通知 メッセージ"
        msg = """
    この電子メール メッセージは、OneRoster CSV 入力バッチ中に、SNS から自動送信されたものです。

    このメールに返信されても、返信内容の確認およびご返答ができません。

    ------------------------------------------------------------------------------------
    処理結果:
    ------------------------------------------------------------------------------------
                """

        file_name = "    users.csv"
        success_count = handle_result["success_count"]
        failed_count = handle_result["record_count"] - success_count

        msg += "\n" + file_name + " : " + "\n"
        msg += "      受付成功件数：" + str(success_count) + "件" + "\n"
        msg += "      受付失敗件数：" + str(failed_count) + "件" + "\n"

        msg += """

    ------------------------------------------------------------------------------------

                """

        topic_arn = os.environ.get("SNS_ARN")

        try:
            sns = boto3.client("sns")
            sns.publish(
                TopicArn=topic_arn,
                Message=msg,
                Subject=sub
            )
        except Exception as exception:
            # トレースバック
            self.log_error('SNS送信処理中、想定外のエラーが発生した')
            self.log_error(traceback.format_exc())
            return False

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES SEND EMAIL BY SNS ###")
        return True

    def unhandled_data_upload(self, file_path, file_name, data_content=[]):
        """
        未取込データ（失敗データも含む）をCSVファイルに出力し、作成のCSVファイルをS3へアップロード

        Parameters
        ----------
        file_name : str
            連携CSVファイル名
        data_content : list
            アップロードファイルの内容（リスト）

        Returns
        -------
        """

        # S3へアップロードするデータは未取込／取込失敗の区分
        self.log_info("### START BATCH ONEROSTER CSV CAPTURE SERVICES UNHANDLED DATA UPLOAD ###")
        headers = csv_roster_setting.TEMP_FILE_COLUMN
        data_content_list = data_content

        try:
            # CSVのファイルを生成する
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=headers,
                                    delimiter=",", quoting=csv.QUOTE_ALL,
                                    lineterminator="\n")
            writer.writeheader()
            # CSV内容出力
            for file_content in data_content_list:
                temp_dict = {key: val for key, val in zip(csv_roster_setting.TEMP_FILE_COLUMN, file_content)}
                writer.writerow(temp_dict)
            unhandled_data = buffer.getvalue()

            # 作成したファイルをアプロードする
            self.s3_access_object.export(
                "{0}{1}".format(file_path, file_name),
                unhandled_data,
            )

            del unhandled_data

        except Exception as exception:
            self.log_error(f"連携CSVファイル<{file_name}> 取込失敗データをCSVファイルに出力する際にエラーが発生しました。")
            # トレースバック
            self.log_error(traceback.format_exc())
        finally:
            buffer.close()

        self.log_info("### END BATCH ONEROSTER CSV CAPTURE SERVICES UNHANDLED DATA UPLOAD ###")
