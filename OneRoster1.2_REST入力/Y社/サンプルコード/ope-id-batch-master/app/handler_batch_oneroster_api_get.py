import logging
import traceback

from app.entities.api_search_date import Api_search_date
from app.services.batch_oneroster_api_get_service import OneRosterApiService
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()


def batch_oneroster_api_get_handler(event, context, body=None):
    """
    OneRoster Rest APIで、ユーザ情報を取得してCSVファイルをS3に配置する

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報

    Returns
    -------
    True
    """
    logger.info("### START BATCH EXPORT USER CHANGE HISTORY INFO HANDLER ###")
    try:
        export_type = event['export_type']
        oneroster_api_host = event["oneroster_api_host"]
        offset = event['offset']
        if 'export_term' in event:
            export_term = event['export_term']
        else:
            export_term = 24
        if 'hours_ago' in event:
            hours_ago = event['hours_ago']
        else:
            hours_ago = 26
        system_organization_code = event['system_organization_code']
        api_search_date = Api_search_date(export_type=export_type,
                                          offset=offset,
                                          export_term=export_term,
                                          hours_ago=hours_ago,
                                          oneroster_api_host=oneroster_api_host)
        api_search_date.system_organization_code = system_organization_code
        # 出力するデータの開始時間と終了時間の取得 (差分出力のみ)
        if export_type == "delta":
            if api_search_date.export_term is not None and api_search_date.hours_ago is not None:
                JST = timezone(timedelta(hours=+9), 'JST')
                date = datetime.now(JST).replace(minute=0, second=0, microsecond=0)
                start_time = date - timedelta(hours=event['hours_ago'])
                end_time = start_time + timedelta(hours=event['export_term'])
                api_search_date.start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                api_search_date.end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S.999Z')

        batch_oneroster_api_service = OneRosterApiService(event)
        ret_value = batch_oneroster_api_service.export(api_search_date)
    except Exception as ex:
        # トレースバック
        logger.error(f"想定外のエラーが発生しました: {ex}")
        logger.error(traceback.format_exc())
        return {"keizoku_flag": 0}

    logger.info("### END BATCH BATCH EXPORT USER HISTORY INFO HANDLER ###")

    return ret_value
