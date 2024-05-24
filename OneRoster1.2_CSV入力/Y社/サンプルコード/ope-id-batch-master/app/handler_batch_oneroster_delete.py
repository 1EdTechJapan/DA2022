# 　新規追加
import logging
import os

from app.services.batch_oneroster_ldif_make_services import LdifFileMakeService
from app.services.batch_oneroster_csv_capture_services import BatchOnerosterCsvCaptureServices

from common.s3_access_object import S3AccessObject


logger = logging.getLogger()


def batch_oneroster_delete_handler(event, context, body=None):
    """
    教員/児童・生徒一括削除

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報

    Returns
    -------

    """

    # ユーザ対象件数
    record_count = event["handle_result"]["record_count"]
    # ファイルパス
    s3_file_key = event["s3_file_key"]
    oneroster_directory = s3_file_key.split("/")[-1].replace('.zip', '')
    oneroster_directory = os.environ["FILE_PATH"] + oneroster_directory
    if record_count:
        deal_mode = event["deal_mode"]
        if deal_mode == "bulk":
            # 組織コード
            system_organization_code = event["system_organization_code"]
            # 処理開始日時
            deal_start_time = event["deal_start_time"]
            # 処理対象組織区分
            deal_org_kbn = event["deal_org_kbn"]
            ldif_file_make_service = LdifFileMakeService(system_organization_code)
            result = ldif_file_make_service.edit_ldif_del(deal_start_time, oneroster_directory, deal_org_kbn)
            # 処理成功件数
            event["handle_result"]["record_count"] = event["handle_result"]["record_count"] + result["record_count"]
            event["handle_result"]["success_count"] = event["handle_result"]["success_count"] + result["success_count"]
        # SNSでメール送信する。
        # 処理完了すると、メール送信する
        batch_user_info_capture_service = BatchOnerosterCsvCaptureServices()
        batch_user_info_capture_service.send_email(event["handle_result"])

    # 中間CSVファイルを削除する
    # S3 の CSV パス
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    # zipから解凍したCSVファイルの格納パス
    csv_file_directory = oneroster_directory + "/csv"
    # 一時ファイルパス
    tmp_file_directory = oneroster_directory + "/tmp"

    # 一時ファイルパスにあるCSVファイルを削除する
    csv_file_list = s3_access_object.get_file_list(tmp_file_directory)
    for tmp_del_file in csv_file_list:
        s3_access_object.del_file(tmp_del_file)

    # zipから解凍したCSVファイルの格納パスにあるCSVファイルを削除する
    csv_file_list = s3_access_object.get_file_list(csv_file_directory)
    for tmp_del_file in csv_file_list:
        s3_access_object.del_file(tmp_del_file)

    return event

