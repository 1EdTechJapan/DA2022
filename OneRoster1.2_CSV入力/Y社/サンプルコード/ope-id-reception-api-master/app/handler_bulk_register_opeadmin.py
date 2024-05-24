# coding: utf-8
import logging
import os
import io
import csv
import copy

from app.services.bulk_register_opeadmin_service import BulkRegisterOpeadminService
from app.config import csv_oneroster_setting
from common.helper_handler import decorate_responce_handler
from common.s3_access_object import S3AccessObject
from common.apply_info import ApplyInfo
from common.base import Base
from app.services.apply_info_service import ApplyInfoService
from common.config.static_code import APPLICATION_ID
from common.environment_service import EnvironmentService
from common.master_entities.environment import Environment
from common.config.static_code import ENVIRONMENT_NAME
from common.system_organization_service import SystemOrganizationService

logger = logging.getLogger()


@decorate_responce_handler
def register_bulk_insert_admin_handler(event, context, body=None):
    """OPE管理者一括登録CSVの受付登録を行う
    S3PUTイベントをトリガーに実行される

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報
    body : dict
        デコレータにより抜き出され、dictに変換されたデータ

    Returns
    -------
    なし(エラー時にエラー情報を返却)
    """
    logger.info("### START OPEADMIN BULK CREATE REGESTER HANDLER ###")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    entry_person_id = file_path.split("/")[-1].split("_")[0]
    # 命令に対応したカラム情報を取得
    columns = csv_oneroster_setting.column[operation_type]
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    # 環境情報取得
    environment_service = EnvironmentService()
    environments = environment_service.select(Environment(system_organization_code=system_organization_code,
                                                          application_id=APPLICATION_ID.Common.value,
                                                          delete_flag=0))
    google_cooperation_flag = environment_service.get_environment_value(environments,
                                                                        ENVIRONMENT_NAME.GOOGLE_COOPERATION_FLAG.value)
    try:
        queue_url = environment_service.get_environment_value(environments, ENVIRONMENT_NAME.QUEUE_URL.value)
    except Exception:
        apply_info_service_err = ApplyInfoService()
        apply_info_err = ApplyInfo(
            operation_status=4,
            operation_type=operation_type,
            target_system_organization_code=system_organization_code,
            target_organization_code=organization_code,
            entry_person=entry_person_id,
            update_person=entry_person_id,
            remarks="ファイル内部処理失敗",
        )
        apply_info_service_err.insert_bulk_status(apply_info_err)

        logger.info("### END BULK REGESTER HANDLER ###")
        return {}

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # ヘッダを飛ばす
    next(csv_reader)
    # 内部処理開始を申込履歴テーブルに登録
    apply_info_service = ApplyInfoService(queue_url)
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        target_system_organization_code=system_organization_code,
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_admin_service = BulkRegisterOpeadminService()
    row_number = 1
    for row in csv_reader:
        row_number = row_number + 1
        # CSV行をdictに変換
        admin_dict = {key: val for key, val in zip(columns, row)}
        admin_dict["system_organization_code"] = system_organization_code
        admin_dict['password_flg'] = 0
        # 登録申込情報の準備(児童生徒の場合ユーザIDが修正されるため参照を切る)
        apply_info.target_id = copy.copy(admin_dict["user_id"])
        apply_info.target_name = "{0}　{1}".format(
            admin_dict["sur_name"], admin_dict["given_name"]
        )
        apply_info.target_organization_code = admin_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        admin_dict = bulk_register_admin_service.processing_insert_admin(
            admin_dict, google_cooperation_flag
        )
        # 申込情報登録
        try:
            apply_info_service.register_reception(admin_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    logger.info("### END BULK REGESTER HANDLER ###")
    return {}


@decorate_responce_handler
def register_bulk_update_admin_handler(event, context, body=None):
    """OPE管理者一括更新CSVの受付登録を行う
    S3PUTイベントをトリガーに実行される

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報
    body : dict
        デコレータにより抜き出され、dictに変換されたデータ

    Returns
    -------
    なし(エラー時にエラー情報を返却)
    """
    logger.info("OPE管理者一括更新 CSV受付 開始 , Operator : -" + f" , Input : {body}")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    entry_person_id = file_path.split("/")[-1].split("_")[0]
    # 命令に対応したカラム情報を取得
    columns = csv_oneroster_setting.column[operation_type]
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    # 環境情報取得
    environment_service = EnvironmentService()
    environments = environment_service.select(Environment(system_organization_code=system_organization_code,
                                                          application_id=APPLICATION_ID.Common.value,
                                                          delete_flag=0))
    google_cooperation_flag = environment_service.get_environment_value(environments,
                                                                        ENVIRONMENT_NAME.GOOGLE_COOPERATION_FLAG.value)
    try:
        queue_url = environment_service.get_environment_value(environments, ENVIRONMENT_NAME.QUEUE_URL.value)
    except Exception:
        apply_info_service_err = ApplyInfoService()
        apply_info_err = ApplyInfo(
            operation_status=4,
            operation_type=operation_type,
            target_system_organization_code=system_organization_code,
            target_organization_code=organization_code,
            entry_person=entry_person_id,
            update_person=entry_person_id,
            remarks="ファイル内部処理失敗",
        )
        apply_info_service_err.insert_bulk_status(apply_info_err)

        log_massage = Base.log_create_output("", "OPE管理者一括更新 CSV受付 終了", "", "")
        logger.info("END " + log_massage)
        return {}

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # ヘッダを飛ばす
    next(csv_reader)
    # 内部処理開始を申込履歴テーブルに登録
    apply_info_service = ApplyInfoService(queue_url)
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        target_system_organization_code=system_organization_code,
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_admin_service = BulkRegisterOpeadminService()
    row_number = 1
    for row in csv_reader:
        row_number = row_number + 1
        # CSV行をdictに変換
        user_dict = {key: val for key, val in zip(columns, row)}
        if (user_dict['password'] == ""):
            user_dict.pop('password')
        user_dict['password_flg'] = 1
        # 更新リクエスト用に生成
        user_id = user_dict.get('user_id')
        organization_code = user_dict.get('organization_code')
        user_dict.pop('user_id')
        user_dict.pop('organization_code')
        admin_dict = {
            'user_id': user_id,
            'organization_code': organization_code,
            'user': user_dict,
            "system_organization_code": system_organization_code
        }
        # 登録申込情報の準備
        apply_info.target_id = copy.copy(admin_dict["user_id"])
        apply_info.target_name = "{0}　{1}".format(
            admin_dict["user"]["sur_name"], admin_dict["user"]["given_name"]
        )
        apply_info.target_organization_code = admin_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        admin_dict = bulk_register_admin_service.processing_update_admin(
            admin_dict, google_cooperation_flag
        )
        # 申込情報登録
        try:
            apply_info_service.register_reception(admin_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    log_massage = Base.log_create_output("", "OPE管理者一括更新 CSV受付 終了", "", "")
    logger.info("END " + log_massage)
    return {}


@decorate_responce_handler
def register_bulk_delete_admin_handler(event, context, body=None):
    """
    OPE管理者一括削除CSVの受付登録を行う
    S3PUTイベントをトリガーに実行される

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報
    body : dict
        デコレータにより抜き出され、dictに変換されたデータ

    Returns
    -------
    なし(エラー時にエラー情報を返却)
    """
    logger.info("### START OPEADMIN BULK DELETE REGESTER HANDLER ###")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    entry_person_id = file_path.split("/")[-1].split("_")[0]
    # 命令に対応したカラム情報を取得
    columns = csv_oneroster_setting.column[operation_type]
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    # OPE管理者下部組織情報取得
    system_organization_service = SystemOrganizationService()
    system_organization = system_organization_service.select_by_code(system_organization_code)
    system_organization_name = system_organization.system_organization_name
    top_organization = system_organization_service.select_top_organization(system_organization_code)
    school_name = top_organization.school_name

    # 環境情報取得
    environment_service = EnvironmentService()
    environments = environment_service.select(Environment(system_organization_code=system_organization_code,
                                                          application_id=APPLICATION_ID.Common.value,
                                                          delete_flag=0))
    google_cooperation_flag = environment_service.get_environment_value(environments,
                                                                        ENVIRONMENT_NAME.GOOGLE_COOPERATION_FLAG.value)
    try:
        queue_url = environment_service.get_environment_value(environments, ENVIRONMENT_NAME.QUEUE_URL.value)
    except Exception:
        apply_info_service_err = ApplyInfoService()
        apply_info_err = ApplyInfo(
            operation_status=4,
            operation_type=operation_type,
            target_system_organization_code=system_organization_code,
            target_organization_code=organization_code,
            entry_person=entry_person_id,
            update_person=entry_person_id,
            remarks="ファイル内部処理失敗",
        )
        apply_info_service_err.insert_bulk_status(apply_info_err)

        logger.info("### END OPEADMIN BULK DELETE REGESTER HANDLER ###")
        return {}

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # 内部処理開始を申込履歴テーブルに登録
    apply_info_service = ApplyInfoService(queue_url)
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        target_system_organization_code=system_organization_code,
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_admin_service = BulkRegisterOpeadminService()
    row_number = 1
    for row in csv_reader:
        row_number = row_number + 1
        # CSV行をdictに変換
        admin_dict = {key: val for key, val in zip(columns, row)}
        admin_dict["operator_id"] = entry_person_id
        admin_dict["system_organization_code"] = system_organization_code
        admin_dict["system_organization_name"] = system_organization_name
        admin_dict["organization_name"] = school_name
        # 登録申込情報の準備(OPE管理者の場合ユーザIDが修正されるため参照を切る)
        apply_info.target_id = copy.copy(admin_dict["user_id"])
        apply_info.target_organization_code = admin_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        admin_dict = bulk_register_admin_service.processing_delete_admin(
            admin_dict, google_cooperation_flag
        )
        # 申込情報登録
        try:
            apply_info_service.register_reception(admin_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    logger.info("### END OPEADMIN BULK DELETE REGESTER HANDLER ###")
    return {}
