# 　新規追加
import logging
import os
import traceback
import zipfile
import boto3

from app.config import csv_roster_setting
from app.services.batch_oneroster_split_tempfile_service import BatchOneRosterTempFileService
from app.validations import batch_oneroster_csv_split_validation
from common.helper_handler import validate
from common.s3_access_object import S3AccessObject
from common.validation_error import ValidationError

logger = logging.getLogger()


def batch_oneroster_split_tempfile_handler(event, context, body=None):
    """
    Lambda1にて、連携されたCSV（9個）を一時のファイルに整合し、
    削除データ、学校毎に、分割件数で分割し、分割したファイルをS3に格納する

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報
    body:

    Returns
    -------
    True
    """
    logger.info("### START BATCH ONEROSTER SPLIT TEMPFILE HANDLER ###")
    try:
        validate(batch_oneroster_csv_split_validation.batch_request_param, event)
        # s3_file_keyを取得：例："oneroster/zip/RO_20220101_poc1.zip"
        s3_file_key = event["s3_file_key"]

        # フォルダー名を取得：例："RO_20220101_poc1"
        s3_file_key_id = s3_file_key.split("/")[-1].replace(".zip", "")

        # zipファイル名をチェックする
        request_file = {"s3_file_key": s3_file_key.split("/")[-1]}
        validate(batch_oneroster_csv_split_validation.batch_user_info_file_name, request_file)

        # zipファイル解凍して、S3にファイルをアップロードする
        ret = unzip_file(s3_file_key)
        if not ret:
            logger.error("zipファイル解凍失敗")
            return {"keizoku_flag": 2}

    except ValidationError:
        # バリデーションエラーの場合
        logger.error("指定パスから取得した連携ファイルのファイル名は想定の形式ではないです")
        return {"keizoku_flag": 2}
    except Exception as exception:
        logger.error(f"指定パスから連携ファイル取得でエラー発生：")
        # トレースバック
        logger.error(traceback.format_exc())
        return {"keizoku_flag": 2}

    # Servicesを呼び出す
    temp_file_service = BatchOneRosterTempFileService()
    temp_file_make_return_code = temp_file_service.temp_file_make_service(
        s3_file_key_id
    )

    temp_file_make_return_code["s3_file_key"] = event["s3_file_key"]

    logger.info("### END BATCH ONEROSTER SPLIT TEMPFILE HANDLER ###")

    return temp_file_make_return_code


def unzip_file(s3_file_key):
    """
    zipファイルを解凍して、CSVファイルをS3にアップロードする
    :param s3_file_key:
    """

    # フォルダー名を取得：例："RO_20220101_poc1"
    s3_file_key_id = s3_file_key.split("/")[-1].replace(".zip", "")

    # ファイル一時保存ディレクトリ
    tmp_file_dir = "/tmp/"

    unzip_dir_path = tmp_file_dir + s3_file_key_id + "/"
    if os.path.exists(unzip_dir_path):
        # 解凍先パスにて、既存ファイルがあれば、ファイルを削除
        del_file(unzip_dir_path)
    else:
        # 解凍先パスを作成
        os.makedirs(unzip_dir_path)

    zip_file_name = s3_file_key.split("/")[-1]
    zip_save_path = unzip_dir_path + zip_file_name

    s3 = boto3.resource('s3')
    s3.meta.client.download_file(os.environ["S3_BUCKET_NAME"], s3_file_key, zip_save_path)

    file_list = []
    # ファイルを解凍する
    with zipfile.ZipFile(zip_save_path) as zf:
        for info in zf.infolist():
            info.filename = info.filename.encode('cp437').decode('shift_jis')
            file_name = info.filename
            if not file_name.endswith('/'):
                file_list.append(unzip_dir_path + file_name)
            zf.extract(info, path=unzip_dir_path)

    logger.info(file_list)

    if len(file_list) == 0:
        logger.error('zipファイルにCSVファイルがありません。')
        return False
    else:
        # 解凍したファイルの存在をチェックする
        f_name = unzip_dir_path + csv_roster_setting.CSV_FILE_NAME_MANIFEST
        if f_name not in file_list:
            logger.error('zipファイルに{0}ファイルがありません。'.format(csv_roster_setting.CSV_FILE_NAME_MANIFEST))
            return False

        f_name = unzip_dir_path + csv_roster_setting.CSV_FILE_NAME_ORGS
        if f_name not in file_list:
            logger.error('zipファイルに{0}ファイルがありません。'.format(csv_roster_setting.CSV_FILE_NAME_ORGS))
            return False

        f_name = unzip_dir_path + csv_roster_setting.CSV_FILE_NAME_USERS
        if f_name not in file_list:
            logger.error('zipファイルに{0}ファイルがありません。'.format(csv_roster_setting.CSV_FILE_NAME_USERS))
            return False

        f_name = unzip_dir_path + csv_roster_setting.CSV_FILE_NAME_ROLES
        if f_name not in file_list:
            logger.error('zipファイルに{0}ファイルがありません。'.format(csv_roster_setting.CSV_FILE_NAME_ROLES))
            return False

    # 解凍したファイルをS3にアップロードする
    oneroster_file_path = os.environ["FILE_PATH"]
    file_directory = oneroster_file_path + s3_file_key_id + "/csv/"
    for file in file_list:
        file_name = file.replace(unzip_dir_path, '')
        s3_key = file_directory + file_name
        s3.meta.client.upload_file(file, os.environ["S3_BUCKET_NAME"], s3_key)

    return True


def del_file(path):
    """
    ファイル削除
    :param path:
    """
    ls = os.listdir(path)
    for file in ls:
        c_path = os.path.join(path, file)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
