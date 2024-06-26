# coding: utf-8
import logging
import os
import io
import csv
import copy
from common.helper_handler import decorate_responce_handler
from common.config import csv_bulk_setting
from app.config import csv_oneroster_setting
from common.s3_access_object import S3AccessObject
from common.apply_info import ApplyInfo
from common.base import Base
from app.services.apply_info_service import ApplyInfoService
from app.services.bulk_register_teacher_service import (
    BulkRegisterTeacherService,
)
from common.config.static_code import APPLICATION_ID
from common.environment_service import EnvironmentService
from common.master_entities.environment import Environment
from common.config.static_code import ENVIRONMENT_NAME

logger = logging.getLogger()


@decorate_responce_handler
def register_bulk_insert_teacher_handler(event, context, body=None):
    """教員一括登録CSVの受付登録を行う
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
    logger.info("### START TEACHER BULK CREATE REGESTER HANDLER ###")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    #  改修 (マルチテナント化対応) START
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    #  改修 (マルチテナント化対応) END
    entry_person_id = file_path.split("/")[-1].split("_")[0]
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    oneroster_kbn = file_path.split("/")[-1].split("_")[-1]
    # 命令に対応したカラム情報を取得
    if oneroster_kbn == "oneroster.csv":
        columns = csv_oneroster_setting.column[operation_type]
    else:
        columns = csv_bulk_setting.column[operation_type]
	# ↑ここまで
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    #  新規追加(マルチテナント化対応) START
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
    #  新規追加(マルチテナント化対応) END

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # ヘッダを飛ばす
    next(csv_reader)
    # 内部処理開始を申込履歴テーブルに登録
    #  改修(マルチテナント化対応) START
    apply_info_service = ApplyInfoService(queue_url)
    #  改修(マルチテナント化対応) END
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        #  新規追加(マルチテナント化対応) START
        target_system_organization_code=system_organization_code,
        #  新規追加(マルチテナント化対応) END
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_teacher_service = BulkRegisterTeacherService()
    row_number = 1
    for row in csv_reader:
        row_number = row_number + 1
        # CSV行をdictに変換
        teacher_dict = {key: val for key, val in zip(columns, row)}
        #  新規追加(マルチテナント化対応) START
        teacher_dict["system_organization_code"] = system_organization_code
        #  新規追加(マルチテナント化対応) END
        # 登録申込情報の準備(児童生徒の場合ユーザIDが修正されるため参照を切る)
        apply_info.target_id = copy.copy(teacher_dict["user_id"])
        apply_info.target_name = "{0}　{1}".format(
            teacher_dict["sur_name"], teacher_dict["given_name"]
        )
        apply_info.target_organization_code = teacher_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        #  改修(マルチテナント化対応) START
        teacher_dict = bulk_register_teacher_service.processing_insert_teacher(
            teacher_dict, google_cooperation_flag
        )
        #  改修(マルチテナント化対応) END
        # 申込情報登録
        try:
            apply_info_service.register_reception(teacher_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    logger.info("### END BULK REGESTER HANDLER ###")
    return {}


@decorate_responce_handler
def register_bulk_update_teacher_handler(event, context, body=None):
    """教員一括更新CSVの受付登録を行う
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
    logger.info("教員一括更新 CSV受付 開始 , Operator : -" + f" , Input : {body}")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    #  改修 (マルチテナント化対応) START
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    #  改修 (マルチテナント化対応) END
    entry_person_id = file_path.split("/")[-1].split("_")[0]
    # 命令に対応したカラム情報を取得
    columns = csv_bulk_setting.column[operation_type]
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    #  新規追加(マルチテナント化対応) START
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

        log_massage = Base.log_create_output("", "教員一括更新 CSV受付 終了", "", "")
        logger.info("END " + log_massage)
        return {}
    #  新規追加(マルチテナント化対応) END

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # ヘッダを飛ばす
    next(csv_reader)
    # 内部処理開始を申込履歴テーブルに登録
    #  改修(マルチテナント化対応) START
    apply_info_service = ApplyInfoService(queue_url)
    #  改修(マルチテナント化対応) END
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        #  新規追加(マルチテナント化対応) START
        target_system_organization_code=system_organization_code,
        #  新規追加(マルチテナント化対応) END
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_teacher_service = BulkRegisterTeacherService()
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
        #  改修(マルチテナント化対応) START
        teacher_dict = {
            'user_id': user_id,
            'organization_code': organization_code,
            'user': user_dict,
            "system_organization_code": system_organization_code
        }
        #  改修(マルチテナント化対応) END
        # 登録申込情報の準備
        apply_info.target_id = copy.copy(teacher_dict["user_id"])
        apply_info.target_name = "{0}　{1}".format(
            teacher_dict["user"]["sur_name"], teacher_dict["user"]["given_name"]
        )
        apply_info.target_organization_code = teacher_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        #  改修 (マルチテナント化対応) START
        teacher_dict = bulk_register_teacher_service.processing_update_teacher(
            teacher_dict, google_cooperation_flag
        )
        #  改修 (マルチテナント化対応) END
        # 申込情報登録
        try:
            apply_info_service.register_reception(teacher_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    log_massage = Base.log_create_output("", "教員一括更新 CSV受付 終了", "", "")
    logger.info("END " + log_massage)
    return {}


# 　新規追加
@decorate_responce_handler
def register_bulk_transfer_teacher_handler(event, context, body=None):
    """
    教員一括異動CSVの受付登録を行う
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
    logger.info("教員一括異動 CSV受付 開始 , Operator : -" + f" , Input : {body}")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    #  改修 (マルチテナント化対応) START
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    #  改修 (マルチテナント化対応) END
    entry_person_id = file_path.split("/")[-1].split("_")[0]
    # 命令に対応したカラム情報を取得
    columns = csv_bulk_setting.column[operation_type]
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    #  新規追加(マルチテナント化対応) START
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

        log_massage = Base.log_create_output("", "教員一括異動 CSV受付 終了", "", "")
        logger.info("END " + log_massage)
        return {}
    #  新規追加(マルチテナント化対応) END

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # ヘッダを飛ばす
    next(csv_reader)
    # 内部処理開始を申込履歴テーブルに登録
    #  改修(マルチテナント化対応) START
    apply_info_service = ApplyInfoService(queue_url)
    #  改修(マルチテナント化対応) END
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        #  新規追加 (マルチテナント化対応) START
        target_system_organization_code=system_organization_code,
        #  新規追加 (マルチテナント化対応) END
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_teacher_service = BulkRegisterTeacherService()
    row_number = 1
    for row in csv_reader:
        row_number = row_number + 1
        # CSV行をdictに変換
        user_dict = {key: val for key, val in zip(columns, row)}
        if user_dict['password'] == "":
            user_dict.pop('password')
        user_dict['password_flg'] = 1
        # 更新リクエスト用に生成
        user_id = user_dict.get('user_id')
        organization_code = user_dict.get('before_organization_code')
        new_organization_code = user_dict.get('organization_code')
        user_dict.pop('user_id')
        user_dict.pop('organization_code')
        user_dict.pop('before_organization_code')
        #  改修(マルチテナント化対応) START
        teacher_dict = {
            'user_id': user_id,
            'organization_code': organization_code,
            'new_organization_code': new_organization_code,
            'user': user_dict,
            "system_organization_code": system_organization_code
        }
        #  改修 (マルチテナント化対応) END
        # 登録申込情報の準備
        apply_info.target_id = copy.copy(teacher_dict["user_id"])
        apply_info.target_name = "{0}　{1}".format(
            teacher_dict["user"]["sur_name"], teacher_dict["user"]["given_name"]
        )
        apply_info.target_organization_code = teacher_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        #  改修 (マルチテナント化対応) START
        teacher_dict = bulk_register_teacher_service.processing_transfer_teacher(
            teacher_dict, google_cooperation_flag
        )
        #  改修 (マルチテナント化対応) END
        # 申込情報登録
        try:
            apply_info_service.register_reception(teacher_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    log_massage = Base.log_create_output("", "教員一括異動 CSV受付 終了", "", "")
    logger.info("END " + log_massage)
    return {}


# 　新規追加
@decorate_responce_handler
def register_bulk_delete_teacher_handler(event, context, body=None):
    """
    教員一括削除CSVの受付登録を行う
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
    logger.info("### START TEACHER BULK DELETE REGESTER HANDLER ###")

    # ファイル名からデータを取得
    file_path = event["Records"][0]["s3"]["object"]["key"]
    #  改修(マルチテナント化対応) START
    system_organization_code = file_path.split("/")[1]
    organization_code = file_path.split("/")[2]
    operation_type = file_path.split("/")[3]
    #  改修(マルチテナント化対応) END
    entry_person_id = file_path.split("/")[-1].split("_")[0]
    # 命令に対応したカラム情報を取得
    columns = csv_bulk_setting.column[operation_type]
    # apply_info_service流用解決、ヘッダー補完
    event["headers"] = {"X-OPEID-SS-User-Id": entry_person_id}

    #  新規追加(マルチテナント化対応) START
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

        logger.info("### END TEACHER BULK DELETE REGESTER HANDLER ###")
        return {}
    #  新規追加(マルチテナント化対応) END

    # csvファイルをS3から読み込む
    # ファイル名は{学校コード}/{操作者ID}_{lambdaリクエストID:36桁}_bulk.csv
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    csv_file = s3_access_object.im_port(file_path)
    # csvリーダーに読み込む
    csv_reader = csv.reader(io.StringIO(csv_file.strip()))
    # 内部処理開始を申込履歴テーブルに登録
    #  改修(マルチテナント化対応) START
    apply_info_service = ApplyInfoService(queue_url)
    #  改修(マルチテナント化対応) END
    apply_info = ApplyInfo(
        operation_status=3,
        operation_type=operation_type,
        #  新規追加(マルチテナント化対応) START
        target_system_organization_code=system_organization_code,
        #  新規追加(マルチテナント化対応) END
        target_organization_code=organization_code,
        entry_person=entry_person_id,
        update_person=entry_person_id,
        remarks="ファイル内部処理開始",
    )
    apply_info_service.insert_bulk_status(apply_info)
    apply_info.remarks = ""
    apply_info.operation_status = None
    # CSV処理開始
    bulk_register_teacher_service = BulkRegisterTeacherService()
    row_number = 1
    for row in csv_reader:
        row_number = row_number + 1
        # CSV行をdictに変換
        teacher_dict = {key: val for key, val in zip(columns, row)}
        teacher_dict["operator_id"] = entry_person_id
        #  新規追加(マルチテナント化対応) START
        teacher_dict["system_organization_code"] = system_organization_code
        #  新規追加(マルチテナント化対応) END
        # 登録申込情報の準備(教員の場合ユーザIDが修正されるため参照を切る)
        apply_info.target_id = copy.copy(teacher_dict["user_id"])
        apply_info.target_organization_code = teacher_dict["organization_code"]
        # バリデーションと補完をサービスメソッドに委譲
        #  改修 (マルチテナント化対応) START
        teacher_dict = bulk_register_teacher_service.processing_delete_teacher(
            teacher_dict, google_cooperation_flag
        )
        #  改修 (マルチテナント化対応) END
        # 申込情報登録
        try:
            apply_info_service.register_reception(teacher_dict, apply_info)
        except Exception as exception:
            apply_info_service.throw_error("ID_E_0001", exception)

    logger.info("### END TEACHER BULK DELETE REGESTER HANDLER ###")
    return {}
