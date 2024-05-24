# coding: utf-8
import copy
import csv
import io
import logging
import os
from collections import namedtuple

from common.helper_handler_scim import decorate_scim_handler
from common.lambda_error import LambdaError
from common.s3_access_object import S3AccessObject

logger = logging.getLogger()


@decorate_scim_handler
def scim_demographics_get_handler(event, context, body=None, query=None):
    """
    デモグラフィックデータを検索する

    Parameters
    ----------
    event : dict
        Httpのヘッダ、ボディー情報
    context : LambdaContext
        AWS Lambda情報
    body : dict
        デコレータにより抜き出され、dictに変換されたデータ
    query: dict
        デコレータより抜き出されたパラメータストリングのデータ

    Returns
    -------
    return : dict
        SCIMレスポンスのbody値
    """
    logger.info("### START SCIM demographics HANDLER SEARCH ###")
    logger.info(f"event: {event}")

    queryStringParameters = event['queryStringParameters']
    limit = int(queryStringParameters['limit'])
    offset = int(queryStringParameters['offset'])
    search_filters = []
    if 'filter' in queryStringParameters:
        filters = queryStringParameters['filter']
        search_filters = filters.split(' AND ')

    start_time = ''
    end_time = ''
    for condition in search_filters:
        if ">=" in condition:
            start_time = condition.split(">=")[1].replace("'", "")
        elif "<" in condition:
            end_time = condition.split("<")[1].replace("'", "")

    # csvファイルをS3から読み込む
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    # ファイル名からデータを取得
    file_path = "{0}/{1}".format(
            os.environ["CSV_FILE_PATH"],
            "demographics.csv"
        )
    csv_data = s3_access_object.im_port(file_path)

    # csvリーダーに読み込む
    try:
        csv_reader = csv.reader(io.StringIO(csv_data.strip()))
    except Exception as exception:
        raise exception

    columns = next(csv_reader)

    Row = namedtuple('Row', columns)
    csv_data_list = []

    for row in csv_reader:
        row_info = Row(*row)
        if 'filter' in queryStringParameters:
            if start_time <= str(row_info.dateLastModified) < end_time:
                csv_data_list.append(row_info)
        else:
            csv_data_list.append(row_info)

    csv_data_list.sort(
        key=lambda x: (
            x.sourcedId if x.sourcedId is not None else "",
        )
    )

    return_datas = []
    row_number = 0
    for row in csv_data_list:
        row_number += 1
        if row_number < offset + 1:
            continue

        # CSV行をdictに変換
        data_dict = {key: val for key, val in zip(columns, row)}
        return_datas.append(data_dict)

        if len(return_datas) == limit:
            break

    # SCIMレスポンスを生成
    scim_search_return = {
        "demographics": return_datas
    }
    logger.info("### END SCIM demographics HANDLER SEARCH ###")
    # 返りのデータは1つでも複数扱いで返す
    return scim_search_return
