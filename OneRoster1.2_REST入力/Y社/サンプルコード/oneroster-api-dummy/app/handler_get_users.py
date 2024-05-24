# coding: utf-8
import copy
import csv
import io
import logging
import os
from collections import namedtuple

from common.helper_handler_scim import decorate_scim_handler
from common.s3_access_object import S3AccessObject

logger = logging.getLogger()


@decorate_scim_handler
def scim_users_get_handler(event, context, body=None, query=None):
    """
    教員、児童生徒データを検索する

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
    logger.info("### START SCIM USERS HANDLER SEARCH ###")
    logger.info(f"event: {event}")

    search_conditons = []
    queryStringParameters = event['queryStringParameters']
    resource = event['resource']
    limit = int(queryStringParameters['limit'])
    offset = int(queryStringParameters['offset'])
    # sort = queryStringParameters['sort']
    # orderBy = queryStringParameters['orderBy']
    search_filters = []
    if 'filter' in queryStringParameters:
        filters = queryStringParameters['filter']
        search_filters = filters.split(' AND ')
    for condition in search_filters:
        kigo = ""
        if ">=" in condition:
            item_value = condition.split(">=")
            kigo = ">="
        elif "<=" in condition:
            item_value = condition.split("<=")
            kigo = "<="
        elif "<" in condition:
            item_value = condition.split("<")
            kigo = "<"
        elif ">" in condition:
            item_value = condition.split(">")
            kigo = ">="
        elif "=" in condition:
            item_value = condition.split("=")
            kigo = ">="
        else:
            logger.error("条件不正")
            continue
        con_dict = {
            item_value[0]:
                {
                    "value": item_value[1].replace("'", ''),
                    "kigo": kigo
                 }
            }
        search_conditons.append(con_dict)

    # csvファイルをS3から読み込む
    s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
    role_path = "{0}/{1}".format(
            os.environ["CSV_FILE_PATH"],
            'roles.csv'
        )
    role_csv_data = s3_access_object.im_port(role_path)
    # csvリーダーに読み込む
    try:
        role_csv_reader = csv.reader(io.StringIO(role_csv_data.strip()))
    except Exception as exception:
        raise exception

    role_columns = next(role_csv_reader)
    role_datas = {}
    for row in role_csv_reader:
        # CSV行をdictに変換
        data_dict = {key: val for key, val in zip(role_columns, row)}
        if data_dict['userSourcedId'] not in role_datas:
            role_datas[data_dict['userSourcedId']] = [data_dict]
        else:
            roles = role_datas[data_dict['userSourcedId']]
            roles.append(data_dict)
            role_datas[data_dict['userSourcedId']] = roles

    # ファイル名からデータを取得
    file_path = "{0}/{1}".format(
            os.environ["CSV_FILE_PATH"],
            "users.csv"
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
        csv_data_list.append(row_info)
    # data_length = len(csv_data_list)

    csv_data_list.sort(
        key=lambda x: (
            x.primaryOrgSourcedId if x.primaryOrgSourcedId is not None else "",
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

        is_ok_data = []
        for con in search_conditons:
            keys = con.keys()
            for key in keys:
                if key not in data_dict:
                    continue

                con_item = key
                con_value = con[con_item]['value']
                kigo = con[con_item]['kigo']
                if kigo == '>=' and data_dict[con_item] >= con_value:
                    is_ok_data.append('true')
                if kigo == '<=' and data_dict[con_item] <= con_value:
                    is_ok_data.append('true')
                if kigo == '>' and data_dict[con_item] > con_value:
                    is_ok_data.append('true')
                if kigo == '<' and data_dict[con_item] < con_value:
                    is_ok_data.append('true')
                if kigo == '=' and data_dict[con_item] == con_value:
                    is_ok_data.append('true')

        if len(is_ok_data) == len(search_conditons):
            roles = []
            if data_dict['sourcedId'] in role_datas:
                roles = role_datas[data_dict['sourcedId']]

            user_roles = []
            for role in roles:
                tmp_role = {
                    "roleType": role['roleType'],
                    "role": role['role'],
                    "org": {
                        "href": "",
                        "sourcedId": role['orgSourcedId'],
                        "type": "",
                    },
                    "userProfile": role['userProfileSourcedId'],
                    "beginDate": role['beginDate'],
                    "endDate": role['endDate'],
                }
                user_roles.append(tmp_role)
            data_dict['roles'] = user_roles

            tmp_metadata = {
                "jp.kanaGivenName": "jp.kanaGivenName",
                "jp.kanaFamilyName": "jp.kanaFamilyName",
                "jp.kanaMiddleName": "jp.kanaMiddleName",
                "jp.homeClass": "jp.homeClass"
            }
            data_dict["metadata"] = tmp_metadata
            tmp_userIds = []
            userIds = data_dict["userIds"].split(",")
            for user_Id in userIds:
                userId = {
                        "type" : "..NormalizedString..",
                        "identifier" : user_Id
                    }
                tmp_userIds.append(userId)
                
            data_dict['userIds'] = tmp_userIds
            grades = data_dict['grades'].split(",")
            data_dict['grades'] = grades
            tmp_primaryOrg = {
                "href" : "URI",
                "sourcedId" : data_dict["primaryOrgSourcedId"],
                "type" : "org"
            }
            data_dict["primaryOrg"] = tmp_primaryOrg
            tmp_agents = []
            agentSourcedIds = data_dict["agentSourcedIds"].split(",")
            for source_id in agentSourcedIds:
                agent = {
                    "href" : "URI",
                    "sourcedId" : source_id,
                    "type" : ""
                    }
                tmp_agents.append(agent)

            data_dict["agents"] = tmp_agents
            tmp_resources = []
            resourceSourcedIds = data_dict["resourceSourcedIds"].split(",")
            for source_id in resourceSourcedIds:
                resource = {
                        "href" : "URI",
                        "sourcedId" : source_id,
                        "type" : "user"
                    }
                tmp_resources.append(resource)
            data_dict["resources"] = tmp_resources
            data_dict["preferredFirstName"] = data_dict["preferredGivenName"]
            data_dict["preferredLastName"] = data_dict["preferredFamilyName"]

            return_datas.append(data_dict)

        if len(return_datas) == limit:
            break

    # SCIMレスポンスを生成
    scim_search_return = {
        "users": return_datas
    }
    logger.info("### END SCIM USER HANDLER SEARCH ###")
    # 返りのデータは1つでも複数扱いで返す
    return scim_search_return
