# 　新規追加
import logging
import traceback

from app.services.batch_oneroster_csv_capture_services import BatchOnerosterCsvCaptureServices

logger = logging.getLogger()


def batch_oneroster_csv_capture_handler(event, context, body=None):
    """
    分割したファイル毎に、Lambda2を実行する
        Lambda2にて、連携ファイルデータごとに、OPEID管理用のCSVデータを作成し、
        バリデーションチェックし、マスタデータチェックする
            差分の場合、OPEID管理用のCSVファイルをS3に格納する。格納パス：画面の一括受付前段APIと同一パス
            一括の場合、ldifファイルを作成し、sshコマンドでLdapを更新する

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
    logger.info("### START BATCH ONEROSTER CSV CAPTURE HANDLER ###")
    return_code = {"keizoku_flag": 0}
    try:
        # モード
        model = event["deal_mode"]
        # 組織コード
        system_organization_code = event["system_organization_code"]
        # s3_file_keyを取得：例："oneroster/zip/RO_20220101_poc1.zip"
        s3_file_key = event["s3_file_key"]
        # フォルダー名を取得：例："RO_20220101_poc1"
        s3_file_key_id = s3_file_key.split("/")[-1].replace(".zip", "")
        # 一時ファイルパス
        tmp_file_name = "{0}_{1}.csv".format("users_temp", event["file_current"])
        # 処理対象組織区分（"school"、"district"の一つ）
        deal_org_kbn = event["deal_org_kbn"]
        # 処理開始日時
        deal_start_time = event["deal_start_time"]

        # Servicesを呼び出す
        csv_matching_service = BatchOnerosterCsvCaptureServices()
        return_code = csv_matching_service.csv_matching_service(
            model,
            s3_file_key_id,
            tmp_file_name,
            system_organization_code,
            deal_org_kbn,
            deal_start_time,
            context)

        # 戻り値を設定
        # 処理成功件数
        event["handle_result"]["success_count"] = \
            event["handle_result"]["success_count"] + return_code["success_count"]

        # カレント処理中のファイルの採番
        if not ("limit_flag" in return_code and return_code['limit_flag']):
            event["file_current"] += 1

    except Exception as exception:
        # トレースバック
        logger.error("一時ファイル処理の時、想定外のエラーが発生しました。")
        logger.error(traceback.format_exc())
        event["file_current"] += 1

    # 継続フラグ:0：処理終了、1：処理継続
    if return_code["keizoku_flag"] != 2:
        # カレント処理中のファイルの採番 > 分割ファイルの総件数 の場合
        if event["file_current"] > event["file_count"]:
            # 継続フラグ = 0
            event["keizoku_flag"] = 0
        else:
            # 継続フラグ = 1
            event["keizoku_flag"] = return_code["keizoku_flag"]
    else:
        event["keizoku_flag"] = return_code["keizoku_flag"]

    logger.info("### END BATCH ONEROSTER CSV CAPTURE HANDLER ###")
    return event



