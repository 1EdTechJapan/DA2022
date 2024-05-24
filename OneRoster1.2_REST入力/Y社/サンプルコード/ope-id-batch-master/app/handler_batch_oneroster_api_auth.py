# coding: utf-8
import logging
import os
import traceback
import time

from app.services.batch_oneroster_api_auth_service import BatchOneRosterAuthService
from common.environment_service import EnvironmentService
from common.lambda_error import LambdaError
from common.master_entities.environment import Environment
from common.config.static_code import APPLICATION_ID, ENVIRONMENT_NAME
from app.validations import batch_oneroster_api_validation
from common.helper_handler import validate
from common.base import Base

logger = logging.getLogger()


def batch_oneroster_api_auth_handler(event, context):
    """
    OneRoster Rest APIのアクセストークンを取得する

    Parameters
    ----------
    event : dict
        secret_arn情報
    context : LambdaContext
        AWS Lambda情報

    Returns
    -------
    access_token
    """
    logger.info("### START BATCH ONE ROSTER AUTH HANDLER ###")
    logger.info(event)
    try:
        # バリデーション実施
        validate(batch_oneroster_api_validation.batch_oneroster_api_validation_request, event)

        batch_oneroster_auth_service = BatchOneRosterAuthService()
        access_token = batch_oneroster_auth_service.get_access_token(event["secret_arn"])
        # 環境情報取得
        environment_service = EnvironmentService()
        db_retry_count = int(os.environ.get("DB_RETRY_COUNT"))
        for i in range(db_retry_count):
            try:
                oneroster_api_host = environment_service.select_by_key(Environment(
                    system_organization_code=event["system_organization_code"],
                    application_id=APPLICATION_ID.Common.value,
                    environment_name=ENVIRONMENT_NAME.ONEROSTER_API_HOST.value,
                    delete_flag=0))
                break
            except Exception as exception:
                # 環境情報取得できない場合、リトライ処理が行わない
                if exception.__class__ == LambdaError and exception.error_code == 'ID_E_0020':
                    raise exception
                else:
                    if (i + 1) < db_retry_count:
                        logger.info(f"RetryError : Retry processing(get_api_host) for the {i + 1} time.")
                        # 次の試行まで待つ
                        time.sleep(int(os.environ.get("DB_RETRY_INTERVAL")))
                        continue
                    else:
                        logger.error("exception :" + str(exception))
                        Base.throw_error("ID_E_0003", exception)

        ret_value = {
            "access_token": access_token,
            "oneroster_api_host": oneroster_api_host,
            "offset": 0,
            "keizoku_flag": 1
        }
        ret_value.update(event)
        logger.info("### END BATCH ONE ROSTER AUTH HANDLER ###")
        return ret_value
    except Exception:
        logger.error('想定外のエラーが発生しました。')
        logger.error(traceback.format_exc())
        ret_value = {
            "keizoku_flag": 0
        }
        return ret_value
