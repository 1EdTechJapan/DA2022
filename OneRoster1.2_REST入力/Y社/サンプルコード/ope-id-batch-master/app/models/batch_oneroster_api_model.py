# coding: utf-8
import json
import os
import time
from common.base_model import BaseModel
from common.http_access_object import HttpAccessObject


class BatchOneRosterApiModel(BaseModel):
    """
    OneRosterRestAPIモデルクラス
    """

    def __init__(self, event):
        super().__init__()
        self.access_token = event["access_token"]
        self.http_access_object = HttpAccessObject()
        # self.url = 'https://imsglobal.org/ims/oneroster/rostering/v1p2/'
        self.url = event["oneroster_api_host"]
        self.headers = {
            'content-type': 'application/json',
            'authorization': 'Bearer ' + self.access_token
        }

    def get_api(self, error_event, api_path, param):
        """
        Onerosterデータ情報を取得する

        Parameters
        ----------
        error_event : error_event
        api_path : api_path
        param : param
        
        Returns
        -------
        """
        self.log_info('### START GET API MODEL  ###')
        self.log_info(f"url: {self.url}, api: {api_path}, param: {param}")
        api_retry_count = int(os.environ.get("API_RETRY_COUNT"))
        for i in range(api_retry_count):
            is_try_exception = False
            res = None
            try:
                request_url = "{0}{1}?{2}".format(self.url, str(api_path), param)
                self.log_info(f"request_url: {request_url}")
                res = self.http_access_object.get(request_url, self.headers)
                self.log_info(f"res.status: {res.status}")
                if res.status != 200:
                    # レスポンスステータスコードが429の場合
                    if res.status == 429:
                        is_try_exception = True
                        raise Exception(json.loads(res.data.decode('utf-8')))
                    else:
                        is_try_exception = False
                        raise Exception(json.loads(res.data.decode('utf-8')))
                break
            except Exception as exception:
                if is_try_exception and (i + 1) < api_retry_count:
                    self.log_info(f"RetryError : Retry processing(get api) for the {i + 1} time.")
                    # 次の試行まで待つ
                    time.sleep(int(os.environ.get("API_RETRY_INTERVAL")))
                    continue
                else:
                    self.log_error(
                        f"event': {error_event}, 'request': {request_url}, "
                        f"'response': {res}, 'exception': {exception}")
                    raise exception

        self.log_info('### END GET API MODEL  ###')
        return json.loads(res.data.decode('utf-8'))
