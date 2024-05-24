# 　新規追加
import csv
import io
import logging
import os
import re
import traceback

from common.base import Base
from common.base_service import BaseService
from common.config import csv_setting
from common.s3_access_object import S3AccessObject
from app.config import csv_roster_setting, oneroster_info_setting

logger = logging.getLogger()


class BatchOneRosterTempFileService(BaseService):
    """
     Lambda1にて、連携されたCSV（9個）を一時のファイルに整合し、
    削除データ、学校毎に、分割件数で分割し、分割したファイルをS3に格納する
    """

    def __init__(self):
        """
        Attributes
        ----------
        s3_access_object : S3AccessObject
            S3接続
        """
        self.s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)

    def temp_file_make_service(self, s3_file_key_id):
        """
        Lambda1にて、連携されたCSV（9個）を一時のファイルに整合し、
        削除データ、学校毎に、分割件数で分割し、分割したファイルをS3に格納する

        Parameters
        ----------
        s3_file_key_id: 教育委員会コード または 学校コード

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")

        in_file_row_num = 0
        # file_num：「users_temp_連番.csv」の連番数
        # out_row_num：「users_temp_連番.csv」行数
        file_num = {
            "file_num": 1,
            "out_row_num": 0,
        }

        try:
            # S3 Server CSV PATH
            oneroster_file_path = os.environ["FILE_PATH"]
            file_directory = oneroster_file_path + s3_file_key_id + "/csv/"
            tmp_file_directory = oneroster_file_path + s3_file_key_id + "/tmp/"
            error_file_directory = oneroster_file_path + s3_file_key_id + "/error/"

            # zipファイル名から　教育委員会コード または 学校コード　を取得　例："poc1"
            s3_file_key_id_organization_code = s3_file_key_id.split("_")[-1]

            # 制限行数を取得する
            deal_cnt = os.environ["DEAL_CNT"]
            limit_row = int(deal_cnt)

            # bulk：一括、delta：差分
            deal_mode = ""
            # 組織コード
            system_organization_code = ""
            # システム日時
            deal_start_time = Base.now().strftime("%Y%m%d%H%M%S")
            # エラーリスト
            error_messages = []
            # 戻り値
            return_code = {
                # s3_file_key
                "s3_file_key": "",
                # bulk：一括、delta：差分
                "deal_mode": deal_mode,
                # 組織コード
                "system_organization_code": system_organization_code,
                # keizoku_flag: 0：処理終了、1：処理継続
                "keizoku_flag": 0,
                # 分割ファイルの総件数
                "file_count": 0,
                # カレント処理中のファイルの採番
                "file_current": 0,
                # 処理結果
                "handle_result": [],
                # システム日時
                "deal_start_time": deal_start_time,
                # 処理対象組織区分（"school"、"district"の一つ）
                "deal_org_kbn": ""
            }

            # 2-1.　マッピングデータを取得する。
            # 差分モードまはた一括モードを取得
            try:
                csv_file = self.s3_access_object.im_port(file_directory + csv_roster_setting.CSV_FILE_NAME_MANIFEST)
            except Exception as exception:
                # 「manifest.csv」ファイルが存在しない場合、エラーログを出力し、処理を終了する。
                self.log_error(f"「manifest.csv」ファイルを読み込む時、異常が発生しました。")
                # トレースバック
                self.log_error(traceback.format_exc())
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「manifest.csv」ファイルを読み込む時、異常が発生しました。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 差分モードまはた一括モードを取得 key = 属性名
            manifest_csv = self.csv_dict_create(
                csv_file,
                csv_roster_setting.CSV_FILE_NAME_MANIFEST,
                error_messages
            )
            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in manifest_csv and not manifest_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 「manifest.csv」ファイルにデータが存在しない場合、エラーログを出力し、処理を終了する。
            if len(manifest_csv) == 0:
                self.log_error("「manifest.csv」ファイルにデータが存在しません。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「manifest.csv」ファイルにデータが存在しません。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 「manifest.csv」ファイルにデータが存在しない場合、エラーログを出力し、処理を終了する。
            if "file.users" not in manifest_csv:
                deal_mode = ""
            else:
                deal_mode = manifest_csv["file.users"]["value"]
            if deal_mode != "bulk" and deal_mode != "delta":
                self.log_error("「manifest.csv」ファイルに処理モード不正（「bulk」、「delta」以外）。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「manifest.csv」ファイルに処理モード不正（「bulk」、「delta」以外）。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 学校情報マッピング
            try:
                csv_file = self.s3_access_object.im_port(file_directory + csv_roster_setting.CSV_FILE_NAME_ORGS)
            except Exception as exception:
                # 「orgs.csv」、ファイルが存在しない場合、エラーログを出力し、処理を終了する。
                self.log_error("「orgs.csv」ファイルを読み込む時、異常が発生しました。")
                # トレースバック
                self.log_error(traceback.format_exc())
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「orgs.csv」ファイルを読み込む時、異常が発生しました。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 学校情報マッピング key = ソースID
            r_orgs_csv = self.csv_dict_create(
                csv_file,
                csv_roster_setting.CSV_FILE_NAME_ORGS,
                error_messages
            )
            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in r_orgs_csv and not r_orgs_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 学校情報マッピング：組織種別　 ＝　"school"のデータ
            orgs_csv = r_orgs_csv["data_dict"]
            # 「orgs.csv」、ファイルにデータが存在しない場合、エラーログを出力し、処理を終了する。
            if len(orgs_csv) == 0:
                self.log_error("「orgs.csv」ファイルにデータが存在しません。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「orgs.csv」ファイルにデータが存在しません。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 組織コード：組織種別　 ＝　"district"のデータ
            system_organization_code = r_orgs_csv["system_organization_code"]
            if system_organization_code == "":
                self.log_error("「orgs.csv」ファイルに組織情報が（組織種別がdistrictのデータ）が存在しません。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「orgs.csv」ファイルに組織情報が（組織種別がdistrictのデータ）が存在しません。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 処理対象組織区分の設定
            deal_org_kbn = ""
            # zipファイル名が教育委員会コードの場合、deal_org_kbnが"district"を設定
            if s3_file_key_id_organization_code == system_organization_code:
                deal_org_kbn = "district"
            else:
                # zipファイル名が学校コードの場合、deal_org_kbnが"school"を設定
                deal_org_kbn = "school"

            # ロールデータを取得
            try:
                csv_file = self.s3_access_object.im_port(file_directory + csv_roster_setting.CSV_FILE_NAME_ROLES)
            except Exception as exception:
                # 「roles.csv」ファイルが存在しない場合、エラーログを出力し、処理を終了する。
                self.log_error("「roles.csv」ファイルを読み込む時、異常が発生しました。")
                # トレースバック
                self.log_error(traceback.format_exc())
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「roles.csv」ファイルを読み込む時、異常が発生しました。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # ロールデータを取得 key = ユーザーソースID
            # 取得した情報を下記のロール情報マッピングを保存する。
            roles_csv = self.csv_dict_create(
                csv_file,
                csv_roster_setting.CSV_FILE_NAME_ROLES,
                error_messages
            )
            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in roles_csv and not roles_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 「roles.csv」ファイルにロールタイプが「primary」のデータが存在しない場合、エラーログを出力し、処理を終了する。
            if len(roles_csv) == 0:
                self.log_error("「roles.csv」ファイルにロールタイプが「primary」のデータが存在しません。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「roles.csv」ファイルにロールタイプが「primary」のデータが存在しません。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 年度情報マッピングacademicSessions.csv
            try:
                csv_file = self.s3_access_object.im_port(
                    file_directory + csv_roster_setting.CSV_FILE_NAME_ACADEMIC_SESSIONS)
                # 年度情報マッピング　key = ソースID
                academicsession_csv = self.csv_dict_create(
                    csv_file,
                    csv_roster_setting.CSV_FILE_NAME_ACADEMIC_SESSIONS,
                    error_messages
                )
            except Exception as exception:
                self.log_warning("「academicSessions.csv」ファイルが存在しませんので、年度が今年度となる。")
                academicsession_csv = {}

            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in academicsession_csv and not academicsession_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 所属情報マッピング
            try:
                csv_file = self.s3_access_object.im_port(file_directory + csv_roster_setting.CSV_FILE_NAME_ENROLLMENTS)
                # 所属情報マッピング key = ユーザSourcedId
                enrollment_csv = self.csv_dict_create(
                    csv_file,
                    csv_roster_setting.CSV_FILE_NAME_ENROLLMENTS,
                    error_messages
                )
            except Exception as exception:
                self.log_warning("「enrollments.csv」ファイルが存在しませんので、"
                                 "出席番号、クラスコード、教科コードが設定なし、年度が今年度となる")
                enrollment_csv = {}

            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in enrollment_csv and not enrollment_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # クラス情報マッピング
            try:
                csv_file = self.s3_access_object.im_port(file_directory + csv_roster_setting.CSV_FILE_NAME_CLASSES)
                # クラス情報マッピング key = ソースID
                class_csv = self.csv_dict_create(
                    csv_file,
                    csv_roster_setting.CSV_FILE_NAME_CLASSES,
                    error_messages
                )
            except Exception as exception:
                self.log_warning("「classes.csv」ファイルが存在しませんので、"
                                 "クラスコード、教科コードが設定なし、年度が今年度となる")
                class_csv = {}

            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in class_csv and not class_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 性別情報マッピング
            try:
                csv_file = self.s3_access_object.im_port(
                    file_directory + csv_roster_setting.CSV_FILE_NAME_DEMOGRAPHICS)
                # 性別情報マッピング key = ソースID
                demographics_csv = self.csv_dict_create(
                    csv_file,
                    csv_roster_setting.CSV_FILE_NAME_DEMOGRAPHICS,
                    error_messages
                )
            except Exception as exception:
                self.log_warning("「demographics.csv」ファイルが存在しませんので、性別が設定なし")
                demographics_csv = {}

            # ファイルフォーマット、データチェックにエラーが発生する時、csv_dict_createにてerror_messagesを追加済
            if "is_success" in demographics_csv and not demographics_csv["is_success"]:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # usersデータを取得
            try:
                csv_file = self.s3_access_object.im_port(file_directory + csv_roster_setting.CSV_FILE_NAME_USERS)
            except Exception as exception:
                # 「users.csv」、ファイルが存在しない場合、エラーログを出力し、処理を終了する。
                self.log_error("「users.csv」ファイルを読み込む時、異常が発生しました。")
                # トレースバック
                self.log_error(traceback.format_exc())
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「users.csv」ファイルを読み込む時、異常が発生しました。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            # 2-2.　「users.csv」からユーザー情報を取得する
            # 2-1から取得したマッピングデータを「Users.csv」と結合し、一時ファイル「Users_temp_(日付)_1からの連番.csv」を生成する。
            # 一時ファイルの情報を「1.2_ファイル仕様_一時ファイル」シートを参照
            # csvリーダーに読み込むget_dict
            ret = self.check_csv_and_get_reader(
                csv_file,
                csv_roster_setting.CSV_FILE_NAME_USERS,
                error_messages
            )
            if ret["is_success"] is False:
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            csv_reader = ret["csv_reader"]
            # 「users.csv」ファイルのデータ件数
            in_file_row_num = len(csv_reader)

            # ファイルの件数チェック
            if in_file_row_num == 0:
                self.log_error("「users.csv」ファイルにユーザデータが存在しません。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「users.csv」ファイルにユーザデータが存在しません。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

            capture_users_dict = self.create_temp_csv(
                csv_reader,
                orgs_csv,
                enrollment_csv,
                academicsession_csv,
                class_csv,
                demographics_csv,
                roles_csv,
                deal_org_kbn,
                s3_file_key_id_organization_code,
                deal_mode,
                error_messages)

            # tobedeleted_users_dictのデータがある場合のみ、分割する（全てのデータがエラーで、continueの場合を考える）
            if len(capture_users_dict["tobedeleted_users_dict"]) > 0:
                # 削除データを一時ファイル「users_temp_連番.csv」ファイル出力
                file_num = self.export_temp_csv_file(
                    file_num["out_row_num"],
                    file_num["file_num"],
                    limit_row,
                    capture_users_dict["tobedeleted_users_dict"],
                    tmp_file_directory)

            # active_users_dictのデータがある場合のみ、分割する（全てのデータがエラーで、continueの場合を考える）
            if len(capture_users_dict["active_users_dict"]) > 0:
                # 新規/更新/異動データを一時ファイル「users_temp_連番.csv」ファイル出力
                file_num = self.export_temp_csv_file(
                    file_num["out_row_num"],
                    file_num["file_num"],
                    limit_row,
                    capture_users_dict["active_users_dict"],
                    tmp_file_directory)

            # 対象件数0件（全てのデータがエラー）の場合
            if len(capture_users_dict["tobedeleted_users_dict"]) == 0 \
                    and len(capture_users_dict["active_users_dict"]) == 0:
                self.log_error("「users.csv」ファイルに対象ユーザが存在しません。")
                error_messages.append(
                    {
                        "userMasterIdentifier": "なし",
                        "detail": "「users.csv」ファイルに対象ユーザが存在しません。"
                    }
                )
                self.export_error_csv_file(
                    error_messages,
                    error_file_directory,
                    deal_start_time
                )
                self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
                return_code["keizoku_flag"] = 2
                return return_code

        except Exception as exception:
            # トレースバック
            self.log_error(f"一時ファイル作成する時、想定外のエラー発生：")
            self.log_error(traceback.format_exc())
            error_messages.append({"userMasterIdentifier": "なし",
                                   "detail": f"異常発生：{str(exception)}"})
            return_code["keizoku_flag"] = 2
            return return_code

        # 2-3.戻り値を設定する。
        handle_result = {
            # ユーザ対象件数
            "record_count": in_file_row_num,
            # 処理成功件数
            "success_count": 0
        }

        return_code = {
            # s3_file_key
            "s3_file_key": "",
            # bulk：一括、delta：差分
            "deal_mode": deal_mode,
            # 組織コード
            "system_organization_code": system_organization_code,
            # keizoku_flag: 0：処理終了、1：処理継続
            "keizoku_flag": 1,
            # 分割ファイルの総件数
            "file_count": file_num["file_num"] - 1,
            # カレント処理中のファイルの採番
            "file_current": 1,
            # 処理結果
            "handle_result": handle_result,
            # システム日付（JST）
            "deal_start_time": deal_start_time,
            # 処理対象組織区分（"school"、"district"の一つ）
            "deal_org_kbn": deal_org_kbn
        }

        # 2-4.　エラーファイルの出力
        if len(error_messages) > 0:
            self.export_error_csv_file(error_messages, error_file_directory, deal_start_time)

        self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES TEMP FILE MAKE SERVICES ###")
        return return_code

    def csv_dict_create(self, csv_file, csvName, error_messages):
        """
        CSVの日付（ファイル名）チェック

        Parameters
        ----------
        :param csvName:
        :param csv_file:
        :param error_messages:

        Returns
        -------
        """

        self.log_info("### START BATCH ONEROSTER TEMPFILE SERVICES CSV DICT CREATE ###")
        data_dict = {}
        header_csv_name = csvName.replace(".csv", "")
        headers = csv_roster_setting.header[header_csv_name]
        system_organization_code = ""

        ret = self.check_csv_and_get_reader(csv_file, csvName, error_messages)
        if ret["is_success"] is False:
            return ret

        csv_reader = ret["csv_reader"]
        # ファイルの件数チェック
        if len(csv_reader) == 0:
            if csvName == csv_roster_setting.CSV_FILE_NAME_ORGS:
                return {
                    "data_dict": data_dict,
                    "system_organization_code": system_organization_code
                }
            else:
                return data_dict

        for row in csv_reader:
            csv_dict = {key: val for key, val in zip(headers, row)}
            if csvName == csv_roster_setting.CSV_FILE_NAME_MANIFEST:
                # 「manifest.csv」から処理モード情報を取得する
                data_dict[csv_dict['propertyName']] = csv_dict
            elif csvName == csv_roster_setting.CSV_FILE_NAME_ORGS:
                # 「orgs.csv」から学校情報を取得する
                # Orgs.csv.組織種別 ＝ "school"のデータの場合、取得した情報を下記の学校情報マッピングを保存する。
                if csv_dict["type"] == 'school':
                    user_dict = {
                        'sourcedId': csv_dict["sourcedId"],
                        'identifier': csv_dict["identifier"]
                    }
                    data_dict[user_dict['sourcedId']] = user_dict
                elif csv_dict["type"] == 'district':
                    # Orgs.csv.組織種別　 ＝　"district"のデータを取得する。
                    system_organization_code = csv_dict["identifier"]
                else:
                    continue
            elif csvName == csv_roster_setting.CSV_FILE_NAME_ACADEMIC_SESSIONS:
                # 「academicSession.csv」から年度情報を取得する
                # 取得した情報を下記の年度情報マッピングを保存する。
                user_dict = {
                    'sourcedId': csv_dict["sourcedId"],
                    'schoolYear': csv_dict["schoolYear"]
                }
                data_dict[user_dict['sourcedId']] = user_dict
            elif csvName == csv_roster_setting.CSV_FILE_NAME_CLASSES:
                # 「class.csv」からクラス情報を取得する
                # 取得した情報を下記の年度情報マッピングを保存する。
                user_dict = {
                    'sourcedId': csv_dict["sourcedId"],
                    'title': csv_dict["title"],
                    'classCode': csv_dict["classCode"],
                    'termSourcedIds': csv_dict["termSourcedIds"],
                    'subjectCodes': csv_dict["subjectCodes"]
                }
                data_dict[user_dict['sourcedId']] = user_dict
            elif csvName == csv_roster_setting.CSV_FILE_NAME_DEMOGRAPHICS:
                # 「demographics.csv」からクラス情報を取得する
                # 取得した情報を下記の年度情報マッピングを保存する。
                user_dict = {
                    'sourcedId': csv_dict["sourcedId"],
                    'sex': csv_dict["sex"]
                }
                data_dict[user_dict['sourcedId']] = user_dict
            elif csvName == csv_roster_setting.CSV_FILE_NAME_ENROLLMENTS:
                # 「enrollment.csv」から所属情報を取得する
                user_dict = {
                    'sourcedId': csv_dict["sourcedId"],
                    'classSourcedId': csv_dict["classSourcedId"],
                    'userSourcedId': csv_dict["userSourcedId"],
                    'shussekiNo': csv_dict["metadata.jp.ShussekiNo"]
                }
                # 複数件のためリストを作成
                if user_dict['userSourcedId'] in data_dict:
                    data_dict[user_dict['userSourcedId']].append(user_dict)
                else:
                    capture_user = [user_dict]
                    data_dict[user_dict['userSourcedId']] = capture_user
            elif csvName == csv_roster_setting.CSV_FILE_NAME_ROLES:
                # ロールタイプが「primary」のデータのみ読み込む
                if csv_dict["roleType"] == "primary":
                    # rolesの場合
                    user_dict = {
                        'userSourcedId': csv_dict["userSourcedId"],
                        'role': csv_dict["role"],
                        'orgSourcedId': csv_dict["orgSourcedId"],
                        'roleType': csv_dict["roleType"]
                    }
                    # 複数件のためリストを作成
                    if user_dict['userSourcedId'] in data_dict:
                        data_dict[user_dict['userSourcedId']].append(user_dict)
                    else:
                        capture_user = [user_dict]
                        data_dict[user_dict['userSourcedId']] = capture_user
            else:
                continue
        self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES CSV DICT CREATE ###")
        if csvName == csv_roster_setting.CSV_FILE_NAME_ORGS:
            return {
                "data_dict": data_dict,
                "system_organization_code": system_organization_code
            }
        else:
            return data_dict

    def create_temp_csv(
            self,
            csv_reader,
            orgs_csv,
            enrollment_csv,
            academicsession_csv,
            class_csv,
            demographics_csv,
            roles_csv,
            deal_org_kbn,
            s3_file_key_id_organization_code,
            deal_mode,
            error_messages):
        """
        一時ファイル「users_temp_連番.csv」を生成する。

        Parameters
        ----------
            :param csv_reader: users csv情報
            :param orgs_csv: orgs csv情報
            :param enrollment_csv: enrollment csv情報
            :param academicsession_csv: academicsession csv情報
            :param class_csv: class csv情報
            :param demographics_csv: demographics csv情報
            :param roles_csv: roles csv情報
            :param deal_org_kbn: 処理対象組織区分（"school"、"district"の一つ）
            :param s3_file_key_id_organization_code: 教育委員会コード または 学校コード
            :param deal_mode: bulk：一括、delta：差分
            :param error_messages: error_messages csv情報
        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER TEMPFILE SERVICES CREATE TEMP CSV ###")

        # 現年度を取得
        date_now = Base.now()
        if date_now.month < 4:
            now_year = date_now.year - 1
        else:
            now_year = date_now.year

        # 有効データ
        active_users_dict = {}
        # 削除データ
        tobedeleted_users_dict = {}
        headers = csv_roster_setting.header["users"]

        for row in csv_reader:
            csv_dict = {key: val for key, val in zip(headers, row)}
            # deal_modeにより、ステータス設定
            if deal_mode == "delta":
                status = csv_dict["status"]
            else:
                status = "active"

            # 姓
            familyName = ""
            # 名
            givenName = ""
            if csv_dict.get('preferredFamilyName') and csv_dict.get('preferredGivenName'):
                familyName = csv_dict.get('preferredFamilyName')
                givenName = csv_dict.get('preferredGivenName')
            else:
                familyName = csv_dict["familyName"]
                givenName = csv_dict["givenName"]

            user_dict = {
                # ユーザソースID
                'sourcedId': csv_dict["sourcedId"],
                # ステータス
                'status': status,
                # 名
                'givenName': givenName,
                # 姓
                'familyName': familyName,
                # メールアドレス
                'email': csv_dict["email"],
                # パスワード
                'password': csv_dict["password"],
                # ユーザ名
                'username': csv_dict["username"],
                # ユーザー一意識別子
                'userMasterIdentifier': csv_dict["userMasterIdentifier"],
                # フリガナ名
                'kanaGivenName': "",
                # フリガナ姓
                'kanaFamilyName': "",
                # 出席番号
                'shussekiNo': ''
            }

            # ユーザSourcedId
            sourcedId = csv_dict["sourcedId"]
            username = csv_dict["username"]
            # status = csv_dict["status"]
            userMasterIdentifier = csv_dict["userMasterIdentifier"]

            # ユーザー一意識別子（自治体内ユニークID）が未設定の場合、次のデータを処理続ける
            if not userMasterIdentifier:
                self.log_error(f"＜ユーザー一意識別子:なし＞ "
                               f"ユーザー一意識別子（自治体内ユニークID）が設定されていません。"
                               f"関連CSVファイル：users.csv")
                messages = {
                    "userMasterIdentifier": "なし",
                    "detail": f"ユーザー一意識別子（自治体内ユニークID）が設定されていません。"
                              f"関連CSVファイル：users.csv"
                }
                error_messages.append(messages)
                continue

            # ユーザー一意識別子がUUID4の形式かどうかをチェック
            ret_check = self.check_uuid4(userMasterIdentifier)
            if not ret_check:
                # ユーザー一意識別子がUUID4の形式ではない場合、
                self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                               f"ユーザー一意識別子（自治体内ユニークID）がUUID4の形式ではありません。"
                               f"関連CSVファイル：users.csv")
                messages = {
                    "userMasterIdentifier": userMasterIdentifier,
                    "detail": f"ユーザー一意識別子（自治体内ユニークID）がUUID4の形式ではありません。"
                              f"関連CSVファイル：users.csv"
                }
                error_messages.append(messages)
                continue

            # ユーザ名（ユーザID）が未設定の場合、次のデータを処理続ける
            if not username:
                self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                               f"ユーザ名（ユーザID）が設定されていません。"
                               f"関連CSVファイル：users.csv")
                messages = {
                    "userMasterIdentifier": userMasterIdentifier,
                    "detail": f"ユーザ名（ユーザID）が設定されていません。"
                              f"関連CSVファイル：users.csv"
                }
                error_messages.append(messages)
                continue

            # ステータスが未設定の場合、次のデータを処理続ける
            if not status:
                self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                               f"ステータスが設定されていません。"
                               f"関連CSVファイル：users.csv")
                messages = {
                    "userMasterIdentifier": userMasterIdentifier,
                    "detail": f"ステータスが設定されていません。"
                              f"関連CSVファイル：users.csv"
                }
                error_messages.append(messages)
                continue

            # ロール情報マッピングから　ロール　を取得
            try:
                # 条件：Users.csv.ソースID　＝　ロール情報マッピング.ユーザSourcedId
                # 同件ユーザSourcedIdのrole情報を取得
                role_source_ids = roles_csv[sourcedId]

                if len(role_source_ids) > 1:
                    # ロールタイプがprimaryのデータが複数ある場合
                    self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                   f"ユーザID：{username} roles.csvにユーザに対するロールタイプが「primary」のデータが複数ある。"
                                   f"関連CSVファイル：users.csv、roles.csv")
                    messages = {
                        "userMasterIdentifier": userMasterIdentifier,
                        "detail": f"ユーザID：{username} roles.csvにユーザに対するロールタイプが「primary」のデータが複数ある。"
                                  f"関連CSVファイル：users.csv、roles.csv"
                    }
                    error_messages.append(messages)
                    continue

                # ロールタイプがprimaryのデータが1件しかない場合、該当レコードのロールを利用
                convert_role = ""
                role_dict = role_source_ids[0]
                if role_dict["role"] in oneroster_info_setting.role_convert_rule.keys():
                    convert_role = oneroster_info_setting.role_convert_rule[role_dict["role"]]

                # ロール情報は許容値以外の場合
                if not convert_role:
                    # トレースバック
                    self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                   f"ユーザID：{username} roles.csvにユーザに対するロールタイプが「primary」のロールが不正です。"
                                   f"「districtAdministrator、principal、siteAdministrator、systemAdministrator、student、teacher」のみ連携する。"
                                   f"関連CSVファイル：users.csv、roles.csv")
                    messages = {
                        "userMasterIdentifier": userMasterIdentifier,
                        "detail": f"ユーザID：{username} roles.csvにユーザに対するロールタイプが「primary」のロールが不正です。"
                                  f"「districtAdministrator、principal、siteAdministrator、systemAdministrator、student、teacher」のみ連携する。"
                                  f"関連CSVファイル：users.csv、roles.csv"
                    }
                    error_messages.append(messages)
                    continue

                # ユーザの権限を設定
                user_dict['role'] = convert_role
            except (KeyError, TypeError) as exception:
                # ロール情報マッピングに該当データがない（KeyError）場合
                # トレースバック
                self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                               f"ユーザID：{username} roles.csvにユーザに対するロールタイプが「primary」のデータがありません。"
                               f"関連CSVファイル：users.csv、roles.csv")
                self.log_error(traceback.format_exc())
                messages = {
                    "userMasterIdentifier": userMasterIdentifier,
                    "detail": f"ユーザID：{username} roles.csvにユーザに対するロールタイプが「primary」のデータがありません。"
                              f"関連CSVファイル：users.csv、roles.csv"
                }
                error_messages.append(messages)
                continue

            # 性別情報マッピングから　性別　を取得
            try:
                # 条件：Users.csv.ソースID　＝　性別情報マッピング.ソースID
                sex = demographics_csv[sourcedId]["sex"]
                if sex == "male":
                    # "male"⇒"1"に変換
                    user_dict['sex'] = "1"
                elif sex == "female":
                    # "female"⇒"2"に変換
                    user_dict['sex'] = "2"
                else:
                    # 以外の場合、空白に設定
                    user_dict['sex'] = ""
            except (KeyError, TypeError) as exception:
                # 性別情報マッピングに該当データがない（KeyError）場合、""を設定
                user_dict['sex'] = ''

            # OPE管理者の場合、
            if user_dict['role'] == 'admin':
                if status == "tobedeleted":
                    # rootadmin、testadminが削除対象外
                    if username == "rootadmin" or username == "testadmin":
                        self.log_warning(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                         f"ユーザID：{username} rootadminやtestadminが削除できません。"
                                         f"関連CSVファイル：users.csv")
                        continue
                # ID管理にて、OPE管理者の学校が学校マスタの表示No=0のレコードなので、ここにて、仮値（必ず学校マスタに存在しない値（16桁を超える））を設定、
                # Lambda2にて、学校マスタの表示No=0学校コードで書き込む
                user_dict['schoolCode'] = 'opeadmindummyschoolcode'
                # 学年、有効年度、出席番号、クラスコード、教科コードが入力必要ないので、""で設定
                user_dict['grades'] = ""
                user_dict['schoolYear'] = ""
                user_dict['shussekiNo'] = ""
                user_dict['classCode'] = ""
                user_dict['subjectCodes'] = ""
            else:
                # OPE管理者以外の場合、下記の処理を継続する
                # 学校情報マッピングから　学校コード　を取得
                try:
                    # 条件：ロールタイプが「primary」のデータの組織ソースID　＝　学校情報マッピング.ソースID
                    school_code = orgs_csv[role_dict["orgSourcedId"]]["identifier"]
                except (KeyError, TypeError) as exception:
                    # 学校情報マッピングに該当データがない（KeyError）場合
                    # トレースバック
                    self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                   f"ユーザID：{username} orgs.csvにユーザに対するデータがありません。"
                                   f"関連CSVファイル：users.csv、roles.csv、orgs.csv")
                    self.log_error(traceback.format_exc())
                    messages = {
                        "userMasterIdentifier": userMasterIdentifier,
                        "detail": f"ユーザID：{username} orgs.csvにユーザに対するデータがありません。"
                                  f"関連CSVファイル：users.csv、roles.csv、orgs.csv"
                    }
                    error_messages.append(messages)
                    continue

                # orgs.csvにユーザに対するidentifierが設定されない
                if not school_code:
                    self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                   f"ユーザID：{username} orgs.csvにユーザに対するidentifierが設定されません。"
                                   f"関連CSVファイル：users.csv、roles.csv、orgs.csv")
                    messages = {
                        "userMasterIdentifier": userMasterIdentifier,
                        "detail": f"ユーザID：{username} orgs.csvにユーザに対するidentifierが設定されません。"
                                  f"関連CSVファイル：users.csv、roles.csv、orgs.csv"
                    }
                    error_messages.append(messages)
                    continue

                # zipファイル名が学校コードの場合、繰り返しデータ.学校コード　!=　zipファイル名.学校コードの場合
                if deal_org_kbn == "school" and school_code != s3_file_key_id_organization_code:
                    self.log_warning(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                     f"ユーザID：{username} に対応する学校コードがzipファイル名と不一致のため、対象外です。"
                                     f"関連CSVファイル：users.csv、roles.csv、orgs.csv")
                    continue

                user_dict['schoolCode'] = school_code

                # 繰り返しデータ.学年コードが空の場合
                if csv_dict["grades"] is None or csv_dict["grades"] == "":
                    # 生徒の場合、該当データがエラーデータとして、次のデータを処理し続ける
                    if user_dict['role'] == "student":
                        message_content = {
                            "userMasterIdentifier": userMasterIdentifier,
                            "detail": f"ユーザID：{username} 学年コードが設定されていません。"
                                      f"関連CSVファイル：users.csv"
                        }
                        self.log_error(message_content)
                        error_messages.append(message_content)
                        continue
                    else:
                        # 教員の場合、空のまま設定
                        user_dict['grades'] = csv_dict["grades"]
                elif len(csv_dict["grades"].split(",")) > 1:
                    # 学年コードが複数の場合
                    # 児童生徒の場合、該当データがエラーデータとして、次のデータを処理し続ける
                    if user_dict['role'] == "student":
                        message_content = {
                            "userMasterIdentifier": userMasterIdentifier,
                            "detail": f"ユーザID：{username} 学年コードが複数設定されています（児童生徒の場合）。"
                                      f"関連CSVファイル：users.csv"
                        }
                        self.log_error(message_content)
                        error_messages.append(message_content)
                        continue
                    else:
                        # 教員の場合、空を設定
                        user_dict['grades'] = ""
                else:
                    user_dict['grades'] = csv_dict["grades"]

                # 所属情報マッピングとクラス情報マッピングから　年度、クラスコード、教科コードを取得
                try:
                    # クラス情報マッピングから　クラスコード　を取得
                    # 条件：Users.csv.ソースID　＝　所属情報マッピング.ユーザSourcedId
                    # 所属情報マッピング.クラスSourcedId　＝　クラス情報マッピング.ソースID

                    # 同件ユーザSourcedIdのenrollment情報を取得
                    class_source_ids = enrollment_csv[sourcedId]

                    # 年度
                    school_year = ""
                    year_list = []
                    # クラスコード
                    class_code = ""
                    class_list = []
                    title_list = []
                    # 教科コード
                    subject_list = []
                    # 出席番号
                    shussekiNo_list = []

                    # 同件ユーザSourcedIdのenrollment情報を繰り返す
                    for tmp_id in class_source_ids:
                        # 出席番号
                        tmp_shussekiNo = tmp_id["shussekiNo"]
                        if tmp_shussekiNo is not None and tmp_shussekiNo != "":
                            if tmp_shussekiNo not in shussekiNo_list:
                                # 出席番号が複数件の場合、リストを設定
                                shussekiNo_list.append(tmp_shussekiNo)

                        # クラスコード
                        class_dict = class_csv[tmp_id["classSourcedId"]]

                        # クラスコードの取得
                        tmp_code = class_dict["classCode"]
                        if tmp_code is not None and tmp_code != "":
                            # クラスコードが複数件の場合、リストを設定
                            if tmp_code not in class_list:
                                class_list.append(tmp_code)

                        # クラス名の取得
                        tmp_code = class_dict["title"]
                        if tmp_code is not None and tmp_code != "":
                            # クラスコードが複数件の場合、リストを設定
                            if tmp_code not in title_list:
                                title_list.append(tmp_code)

                        # 教科コードの取得
                        tmp_code = class_dict["subjectCodes"]
                        if tmp_code is not None and tmp_code != "":
                            # 教科コードが複数件の場合、リストを設定
                            if tmp_code not in subject_list:
                                subject_list.append(tmp_code)

                        # 年度の取得
                        for termSourced in class_dict["termSourcedIds"].split(","):
                            try:
                                tmp_year = academicsession_csv[termSourced]["schoolYear"]
                                if tmp_year is not None and tmp_year != "":
                                    # 年度が複数件の場合、リストを設定
                                    if tmp_year not in year_list:
                                        year_list.append(tmp_year)
                            except (KeyError, TypeError) as exception:
                                # 所属情報マッピングに該当データがない（KeyError）場合、次にenrollment情報を処理続ける
                                continue

                    # クラスコードが複数件の場合、空白を設定
                    if len(class_list) == 1:
                        class_code = class_list[0]
                    else:
                        class_code = ""

                    # クラス名が複数件の場合、空白を設定
                    if len(title_list) == 1:
                        title = title_list[0]
                    else:
                        title = ""

                    # 現年度があるの場合
                    if str(now_year) in year_list:
                        school_year = str(now_year)
                    elif str(now_year + 1) in year_list:
                        # 翌年度があるの場合
                        school_year = str(now_year + 1)
                    else:
                        # CSVファイルに有効年度なしの場合、今年度を設定
                        if len(year_list) == 0:
                            school_year = str(now_year)
                        else:
                            # 過去年度があるの場合
                            for s_year in year_list:
                                if s_year < str(now_year):
                                    school_year = str(now_year)
                                    break

                    # 将来年度の場合、エラーメッセージを設定
                    if school_year == "":
                        # 将来年度の場合、エラーメッセージを設定し、データを一時ファイルへ出力しない
                        self.log_error(f"＜ユーザー一意識別子:{userMasterIdentifier}＞ "
                                       f"有効年度は今年度または翌年度のみ入力可能です。"
                                       f"関連CSVファイル：users.csv、enrollments.csv、classes.csv、academicSessions.csv")
                        messages = {
                            "userMasterIdentifier": userMasterIdentifier,
                            "detail": f"有効年度は今年度または翌年度のみ入力可能です。"
                                      f"関連CSVファイル：users.csv、enrollments.csv、classes.csv、academicSessions.csv"
                        }
                        error_messages.append(messages)
                        continue

                    # 年度の設定
                    user_dict['schoolYear'] = school_year

                    # クラスコードの設定
                    # Mappingファイルに定義した転換ルールで転換する
                    if class_code in oneroster_info_setting.class_code_convert_rule.keys():
                        class_code = oneroster_info_setting.class_code_convert_rule[class_code]
                        user_dict['classCode'] = class_code
                    elif title in oneroster_info_setting.class_code_convert_rule.keys():
                        class_code = oneroster_info_setting.class_code_convert_rule[title]
                        user_dict['classCode'] = class_code
                    else:
                        user_dict['classCode'] = ''

                    # 教科コードの設定
                    subject_codes = ""
                    for subject in subject_list:
                        subject_codes += f",{subject}"
                    if subject_codes != "":
                        subject_codes = subject_codes[1:]
                    user_dict['subjectCodes'] = subject_codes

                    # 児童生徒の場合、
                    if user_dict['role'] == "student":
                        # 出席番号が複数件の場合、空白を設定
                        if len(shussekiNo_list) == 1:
                            shussekiNo = shussekiNo_list[0]
                        else:
                            shussekiNo = ""
                        # 出席番号の設定
                        user_dict['shussekiNo'] = shussekiNo

                except (KeyError, TypeError) as exception:
                    # 所属情報マッピング、クラス情報マッピングに該当データがない（KeyError）場合、""を設定
                    user_dict['classCode'] = ''
                    user_dict['subjectCodes'] = ''
                    user_dict['schoolYear'] = str(now_year)
                    user_dict['shussekiNo'] = ''

            # 削除のデータ
            if status == "tobedeleted":
                # 学校コードにより、ファイルを分割する
                if user_dict['schoolCode'] in tobedeleted_users_dict:
                    tobedeleted_users_dict[user_dict['schoolCode']].append(user_dict)
                else:
                    capture_user = [user_dict]
                    tobedeleted_users_dict[user_dict['schoolCode']] = capture_user
            else:
                # 有効のデータ
                # 学校コードにより、ファイルを分割する
                if user_dict['schoolCode'] in active_users_dict:
                    active_users_dict[user_dict['schoolCode']].append(user_dict)
                else:
                    capture_user = [user_dict]
                    active_users_dict[user_dict['schoolCode']] = capture_user

        self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES CREATE TEMP CSV ###")
        return {
            "active_users_dict": active_users_dict,
            "tobedeleted_users_dict": tobedeleted_users_dict
        }

    def export_temp_csv_file(
            self,
            out_row_num,
            file_num,
            limit_row,
            users_dict,
            file_directory):
        """
        一時ファイル「users_temp_(日付).csv」ファイル作成時に1ファイルが
        「環境変数.ファイル分割件数」を超える場合は、CSVファイルを分割する。
        ※ファイル分割時のファイル名は「users_temp_(日付).csv」の場合は、
       「users_temp_(日付)_1.csv」と取得したファイル名の拡張子前に「_連番」とする。

        Parameters
        ----------
            :param out_row_num:一時ファイルの行数
            :param file_num:一時ファイル連番
            :param limit_row:制限行数
            :param users_dict:一時ファイル内容
            :param file_directory:一時ファイル内容パス

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER TEMPFILE SERVICES EXPORT TEMP CSV FILE ###")

        file_name = "users_temp"
        # 学校ごとにファイルを生成
        for key in users_dict:
            split_dict = users_dict[key]
            out_row_num = out_row_num + len(split_dict)
            # 件数のチェック
            if len(split_dict) > limit_row:
                # 最大件数を超える場合、リストを分割する
                for i in range(0, len(split_dict), limit_row):
                    sub_split_dict = split_dict[i:i + limit_row]
                    # csvファイル作成
                    csv_contents = self.create_master_file_contents(
                        sub_split_dict,
                        csv_roster_setting.TEMP_FILE_COLUMN
                    )
                    # 分割したファイルをアプロードする
                    self.s3_access_object.export(
                        "{0}{1}_{2}.csv".format(
                            file_directory,
                            file_name,
                            str(file_num),
                        ),
                        csv_contents,
                    )
                    file_num += 1
            else:
                # csvファイル作成
                csv_contents = self.create_master_file_contents(
                    split_dict,
                    csv_roster_setting.TEMP_FILE_COLUMN
                )
                # 分割したファイルをアプロードする
                self.s3_access_object.export(
                    "{0}{1}_{2}.csv".format(
                        file_directory,
                        file_name,
                        str(file_num),
                    ),
                    csv_contents,
                )
                file_num += 1

        self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES EXPORT TEMP CSV FILE ###")
        return {
            "file_num": file_num,
            "out_row_num": out_row_num,
        }

    def export_error_csv_file(
            self,
            error_messages,
            file_directory,
            deal_start_time):
        """
        エラーメッセージファイルを生成する

        Parameters
        ----------
            :param error_messages:エラーメッセージリスト
            :param file_directory:エラーメッセージパス
            :param deal_start_time:システム時刻

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER TEMPFILE SERVICES EXPORT ERROR CSV FILE ###")

        # csvファイル出力
        out_csv_file_name = "error_messages_" + deal_start_time
        out_csv_file_path = (file_directory + out_csv_file_name + ".csv")

        error_info_csv = self.create_master_file_contents(
            error_messages,
            csv_roster_setting.ERROR_FILE_COLUMN
        )

        # s3にCSVを配置する
        self.s3_access_object.export(out_csv_file_path, error_info_csv)

        self.log_error(f"エラーが発生しました。エラー内容がファイル{out_csv_file_path}をご参照ください。")
        self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES EXPORT ERROR CSV FILE ###")
        return

    def create_master_file_contents(self, csv_dict, header):
        """
        CSVのファイルを生成する(マスター情報出力)

        Parameters
        ----------
            CSVファイルの内容
            :param csv_dict:
            :param header:

        Returns
        -------
        """
        self.log_info("### START BATCH ONEROSTER TEMPFILE SERVICES CREATE MASTER FILE CONTENTS ###")

        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer, fieldnames=header,
            delimiter=csv_setting.DELIMITER, quoting=csv.QUOTE_ALL,
            lineterminator=csv_setting.LINETERMINATOR)

        writer.writeheader()
        csv_data = ""
        for result in csv_dict:
            # csv_school_info = result.get_dict(allow_empty=True)
            writer.writerow(result)
        csv_data = buffer.getvalue()
        buffer.close()

        self.log_info("### END BATCH ONEROSTER TEMPFILE SERVICES CREATE MASTER FILE CONTENTS ###")
        return csv_data

    def check_csv_and_get_reader(self, csv_data, file_name, error_messages):
        """CSVチェックを行い、CSVリーダに読込む

        Parameters
        ----------
        csv_data : str
            文字列のCSVデータ
        file_name : str
            連携CSVファイル名
        error_messages : list
            エラーメッセージ一覧
        Returns
        -------
        ret : dict {
                    "is_success": bool,
                        CSVチェックを行い、CSVリーダに読込む
                    "csv_reader": CSV Reader
                        csvファイルストリーム
                    }
        """
        self.log_info("### START CHECK CSV AND GET READER WITHOUT HEADER FUNCTION ###")
        ret = {}

        csv_data_list: list = []
        # csvリーダーに読み込む
        try:
            csv_reader = csv.reader(io.StringIO(csv_data.strip()))

            # 1行目（ヘッダ）を取得
            title_row = next(csv_reader)
            header_csv_name = file_name.replace(".csv", "")
            headers = csv_roster_setting.header[header_csv_name]
            # BOM付きのファイルを対応
            title_row[0] = title_row[0].replace("\ufeff", "")
            # ヘッダの検証
            if title_row != headers:
                self.log_error(f"連携CSVファイル<{file_name}> 文字コードは「UTF-8」でないか1行目の形式が一致しません")
                messages = {
                    "userMasterIdentifier": "なし",
                    "detail": f"連携CSVファイル<{file_name}> 文字コードは「UTF-8」でないか1行目の形式が一致しません"
                }
                error_messages.append(messages)
                ret["is_success"] = False
                return ret

            for row in csv_reader:
                csv_data_list.append(row)

        except Exception:
            # トレースバック
            self.log_error(f"連携CSVファイル<{file_name}>の形式が不正です")
            self.log_error(traceback.format_exc())
            messages = {
                "userMasterIdentifier": "なし",
                "detail": f"連携CSVファイル<{file_name}>の形式が不正です"
            }
            error_messages.append(messages)
            ret["is_success"] = False
            return ret

        ret["is_success"] = True
        ret["csv_reader"] = csv_data_list

        self.log_info("### END CHECK CSV AND GET READER WITHOUT HEADER FUNCTION ###")
        return ret

    def check_uuid4(self, uuid):
        """
        UUID4形式チェック
        :param uuid:
        :return:
        """
        # UUID4のRegex
        UUID4_REGEX = re.compile(
            # 8桁のhex文字
            '[0-9A-F]{8}-'
            # 4桁のhex文字
            '[0-9A-F]{4}-'
            # 4桁のhex文字
            '[0-9A-F]{4}-'
            # 4桁のhex文字
            '[0-9A-F]{4}-'
            # 12桁のhex文字
            '[0-9A-F]{12}',
            # フラグ
            flags=re.IGNORECASE
        )
        matches = UUID4_REGEX.match(uuid)
        if matches is not None:
            return True
        else:
            return False
