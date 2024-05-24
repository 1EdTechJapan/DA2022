# coding: utf-8
import logging
import json
import os
import time
from common.http_access_object import HttpAccessObject
from common.secrets_manager_access_object import SecretsManagerAccessObject
from common.base_service import BaseService

logger = logging.getLogger()


class BatchOneRosterAuthService(BaseService):
    """
    Secrets Managerから認証情報を取得し、OneRoster Rest APIの認証APIをコールする
    """
    def __init__(self):
        self.http_access_object = HttpAccessObject()
        self.secrets_manager_access_object = SecretsManagerAccessObject()

    def get_access_token(self, secret_arn):
        """
        OneRoster Rest APIのアクセストークンを取得するサービスメソッド

        Parameters
        ----------
        secret_arn : str
            Secrets ManagerのARN

        Returns
        -------
        access_token
        """
        logger.info('### START BATCH SERVICE GET ACCESS TOKEN ###')
        # Secrets ManagerのARN取得
        try:
            secret_string = self.secrets_manager_access_object.get_secret_string(secret_arn)

        except Exception as exception:
            self.log_critical(json.dumps({"exception": exception}))
            raise exception

        client_id = secret_string['client_id']
        client_secret = secret_string['client_secret']
        scope = 'https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly ' \
                'https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly ' \
                'https://purl.imsglobal.org/spec/or/v1p2/scope/roster-demographics.readonly'
        grant_type = 'client_credentials'
        url = 'https://www.imsglobal.org/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'client_id': client_id,
            'scope': scope,
            'client_secret': client_secret,
            'grant_type': grant_type
        }

        # OneRoster Rest APIの認証
        api_retry_count = int(os.environ.get("API_RETRY_COUNT"))

        for i in range(api_retry_count):
            try:
                res = self.http_access_object.post_urlencode(url, payload, headers)

                # レスポンスステータスコードが「200(正常)」以外の場合
                if res.status != 200:
                    raise Exception(json.loads(res.data.decode('utf-8')))
                break
            except Exception as exception:
                if (i + 1) < api_retry_count:
                    self.log_info(f"RetryError : Retry processing(get_access_token) for the {i + 1} time.")
                    # 次の試行まで待つ
                    time.sleep(int(os.environ.get("API_RETRY_INTERVAL")))
                    continue
                else:
                    self.log_error("exception :" + str(exception))
                    raise exception
        logger.info("### END BATCH SERVICE GET ACCESS TOKEN ###")
        return json.loads(res.data.decode('utf-8'))['access_token']
