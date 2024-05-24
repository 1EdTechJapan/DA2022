# coding: utf-8
import importlib
import logging
from common.config import handler_mappings
from common.helper_handler import create_error_response
from common.lambda_error import LambdaError

logger = logging.getLogger()

api_resource_mappings = {
    "/getAllAcademicSessions": {
        "module": "app.handler_get_academicSessions",
        "handler": "scim_academicSessions_get_handler",
    },
    "/getAllClasses": {
        "module": "app.handler_get_class",
        "handler": "scim_class_get_handler",
    },
    "/getAllDemographics": {
        "module": "app.handler_get_demographics",
        "handler": "scim_demographics_get_handler",
    },
    "/getAllEnrollments": {
        "module": "app.handler_get_enrollments",
        "handler": "scim_enrollments_get_handler",
    },
    "/getAllOrgs": {
        "module": "app.handler_get_orgs",
        "handler": "scim_orgs_get_handler",
    },
    "/getAllUsers": {
        "module": "app.handler_get_users",
        "handler": "scim_users_get_handler",
    },
}


def resource_mapping_handler(event, context):
    """
    リクエストリソースとハンドラーをマッピングする

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報

    Returns
    -------
    res : dict
        レスポンスのBODYとして返される情報
        各呼び出し先ハンドラーの結果をそのまま返す
    """
    logger.info("### START MAPPING HANDLER ###")
    try:
        logger.info(f"event: {event}")
        # httpリクエストのurlのresourceでマッピング先データを取得
        resource = event['resource']
        resource_mapping = api_resource_mappings[
            resource
        ]
        # 設定ファイルが指定するファイルをimportする
        mod = importlib.import_module(resource_mapping['module'])
        # 設定ファイルが指定するハンドラーを実行する
        res = getattr(mod, resource_mapping['handler'])(event, context)
    except LambdaError as lambda_error:
        # キャッチ済み例外
        res = create_error_response(lambda_error)
    except Exception:
        # リクエストリソースが不正のエラー
        lambda_error = LambdaError()
        lambda_error.error_code = 'ID_E_0009'
        lambda_error.format_error_message = event['resource']
        res = create_error_response(lambda_error)
    # エラーがなければマッピング先のハンドラーメソッドの返り値をそのまま返す
    return res
