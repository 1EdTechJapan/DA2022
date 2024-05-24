import csv
import uuid
from datetime import datetime, timedelta, timezone

import boto3
import os
import io
import copy
import traceback
import zipfile

from app.models.batch_oneroster_api_model import BatchOneRosterApiModel
from common.base_service import BaseService
from common.s3_access_object import S3AccessObject

from app.config import csv_roster_setting


class OneRosterApiService(BaseService):
    """Rest api でデータ取得とCSV出力

    Attributes
    ----------
    event : event
    """

    def __init__(self, event):
        self.s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
        self.out_file_path = os.environ["OUTPUT_FILE_PATH"]
        self.event = event
        # アクセストークン
        self.access_token = event['access_token']
        # 同期処理モデルを取得する
        self.batch_oneroster_api_model = BatchOneRosterApiModel(self.event)

        # システム日時
        JST = timezone(timedelta(hours=+9), 'JST')
        date = datetime.now(JST).replace(minute=0, second=0, microsecond=0)
        self.deal_start_time = date.strftime("%Y%m%d")
        self.local_file_path = f"/tmp/RO_{self.deal_start_time}/"

    def export(self, api_search_date):
        """
        CSVデータ取得と整合

        Parameters
        ----------
        :param api_search_date:
        Returns
        -------
        True
        """
        self.log_info("### START BATCH ONE ROSTER REST API SERVICES ###")

        deal_cnt = int(os.environ.get('DEAL_CNT'))
        # 1回目該当Lambdaを実行する時、
        offset = api_search_date.offset
        if offset == 0:
            # CSV出力先のフォルダパスにあるファイルを削除する
            self.del_file(self.local_file_path)
        ret_value = {}
        # ユーザ情報を取得する
        if 'user_data_length' not in self.event or self.event['user_data_length'] != 0:
            user_value = self.create_users_csv(api_search_date)
            user_data_length = user_value['user_data_length']
            ret_value['user_data_length'] = user_data_length
        else:
            ret_value['user_data_length'] = 0
            user_data_length = 0

        # 初回対象ユーザデータがない場合、バッチを終了する
        if user_data_length == 0 and offset == 0:
            ret_value['offset'] = offset
            ret_value['keizoku_flag'] = 0
            return ret_value

        # ユーザの組織、所属、クラス、年度、ロール情報を取得する
        if 'orgs_data_length' not in self.event or self.event['orgs_data_length'] != 0:
            orgs_value = self.create_org_csv(api_search_date)
            orgs_data_length = orgs_value['orgs_data_length']
            ret_value['orgs_data_length'] = orgs_data_length
        else:
            ret_value['orgs_data_length'] = 0
            orgs_data_length = 0

        if 'academicSessions_data_length' not in self.event or self.event['academicSessions_data_length'] != 0:
            academicSessions_value = self.create_academicSession_csv(api_search_date)
            academicSessions_data_length = academicSessions_value['academicSessions_data_length']
            ret_value['academicSessions_data_length'] = academicSessions_data_length
        else:
            ret_value['academicSessions_data_length'] = 0
            academicSessions_data_length = 0

        if 'enrollments_data_length' not in self.event or self.event['enrollments_data_length'] != 0:
            enrollments_value = self.create_enrollment_csv(api_search_date)
            enrollments_data_length = enrollments_value['enrollments_data_length']
            ret_value['enrollments_data_length'] = enrollments_data_length
        else:
            ret_value['enrollments_data_length'] = 0
            enrollments_data_length = 0

        if 'classes_data_length' not in self.event or self.event['classes_data_length'] != 0:
            classes_value = self.create_class_csv(api_search_date)
            classes_data_length = classes_value['classes_data_length']
            ret_value['classes_data_length'] = classes_data_length
        else:
            ret_value['classes_data_length'] = 0
            classes_data_length = 0

        if  'demographics_data_length' not in self.event or self.event['demographics_data_length'] != 0:
            demographics_value = self.create_demographics_csv(api_search_date)
            demographics_data_length = demographics_value['demographics_data_length']
            ret_value['demographics_data_length'] = demographics_data_length
        else:
            ret_value['demographics_data_length'] = 0
            demographics_data_length = 0

        # すべてのデータが取得完了した場合、処理を終了する
        if user_data_length < deal_cnt \
                and orgs_data_length < deal_cnt \
                and academicSessions_data_length < deal_cnt \
                and enrollments_data_length < deal_cnt\
                and classes_data_length < deal_cnt\
                and demographics_data_length < deal_cnt:
            # manifest.csvファイルを作成
            self.create_manifest_csv()

            # 処理を終了する前に、CSVファイルをzipに圧縮する
            system_organization_code = api_search_date.system_organization_code
            self.zip_file(self.local_file_path, system_organization_code)

            # CSV出力先のフォルダパスにあるファイルを削除する
            self.del_file(self.local_file_path)

            s3_access_object = S3AccessObject(os.environ["S3_BUCKET_NAME"], None)
            # CSVファイルの格納パス
            csv_file_directory = self.out_file_path + "csv"

            # CSVファイルの格納パスにあるCSVファイルを削除する
            csv_file_list = s3_access_object.get_file_list(csv_file_directory)
            for tmp_del_file in csv_file_list:
                s3_access_object.del_file(tmp_del_file)

            ret_value['offset'] = offset
            ret_value['keizoku_flag'] = 0
            return ret_value

        self.log_info("### END BATCH ONE ROSTER REST API SERVICES ###")

        ret_value['offset'] = offset + deal_cnt
        ret_value['keizoku_flag'] = 1
        ret_value['oneroster_api_host'] = api_search_date.oneroster_api_host
        ret_value['export_type'] = api_search_date.export_type
        ret_value['export_term'] = api_search_date.export_term
        ret_value['hours_ago'] = api_search_date.hours_ago
        ret_value['system_organization_code'] = api_search_date.system_organization_code
        ret_value['access_token'] = self.access_token

        return ret_value

    def request_data(self, api_path, api_search_date):
        """
        インターフェースを呼び出す
        :param api_search_date:
        :param api_path:
        :return:
        """

        self.log_info("### START REQUEST API ###")
        # アクセストークンもマスクする
        error_event = copy.deepcopy(self.event)
        if self.event.get('access_token') is not None:
            error_event['access_token'] = '*************'

        limit = os.environ.get('DEAL_CNT')
        offset = api_search_date.offset
        param = "limit={0}&offset={1}".format(limit, offset)
        if api_search_date.export_type == "delta"\
                and api_path in ["getAllUsers", "getAllEnrollments", "getAllDemographics"]:
            param += f"&filter=dateLastModified<'{api_search_date.end_time}'" \
                     f" AND dateLastModified>='{api_search_date.start_time}'"

        if api_path == "getAllOrgs":
            param += "&sort=identifier&orderBy=asc"
            param += f"&filter=identifier='{api_search_date.system_organization_code}'"
        else:
            param += "&sort=sourcedId&orderBy=asc"

        req = self.batch_oneroster_api_model.get_api(error_event, api_path, param)
        self.log_info("### END REQUEST API ###")
        return req

    def create_org_csv(self, api_search_date):
        """
        orgs情報
        :param api_search_date:
        :return:
        """

        self.log_info("### START CREATE ORGS CSV ###")

        response = self.request_data("getAllOrgs", api_search_date)
        data = response['orgs']

        headers = csv_roster_setting.header["orgs"]
        temp_io = io.StringIO()
        temp_csv_writer = csv.DictWriter(temp_io, fieldnames=headers)
        orgs_value = ''
        if api_search_date.offset == 0:
            temp_csv_writer.writeheader()
        else:
            orgs_value = self.s3_access_object.im_port(self.out_file_path + 'csv/orgs.csv')
        for value in data:
            temp_row = {}
            temp_row[headers[0]] = value['sourcedId']
            if api_search_date.export_type == 'delta':
                temp_row[headers[1]] = value['status']
                temp_row[headers[2]] = value['dateLastModified']
            else:
                temp_row[headers[1]] = ''
                temp_row[headers[2]] = ''

            temp_row[headers[3]] = value['name']
            temp_row[headers[4]] = value['type']
            temp_row[headers[5]] = value['identifier']
            temp_row[headers[6]] = value['parent']['sourcedId']
            temp_csv_writer.writerow(temp_row)

        # データがない場合、終了
        if len(data) == 0:
            ret_value = {'orgs_data_length': 0}
            self.log_info(ret_value)
            return ret_value
        else:
            ret_value = {'orgs_data_length': len(data)}
            self.log_info(ret_value)

        # "orgs.csv"
        csv_value = orgs_value + temp_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_ORGS,
                                csv_value)
        self.log_info("### END CREATE ORGS CSV ###")
        return ret_value

    def create_academicSession_csv(self, api_search_date):
        """
        academicSession_csv
        :param api_search_date:
        :return:
        """

        self.log_info("### START CREATE ACADEMIC_SESSIONS CSV ###")
        response = self.request_data("getAllAcademicSessions", api_search_date)
        data = response['academicSessions']

        headers = csv_roster_setting.header["academicSessions"]
        temp_io = io.StringIO()
        temp_csv_writer = csv.DictWriter(temp_io, fieldnames=headers)
        academicSessions_value = ''
        if api_search_date.offset == 0:
            temp_csv_writer.writeheader()
        else:
            academicSessions_value = self.s3_access_object.im_port(self.out_file_path + 'csv/academicSessions.csv')
        for value in data:
            temp_row = {}
            temp_row[headers[0]] = value['sourcedId']
            if api_search_date.export_type == 'delta':
                temp_row[headers[1]] = value['status']
                temp_row[headers[2]] = value['dateLastModified']
            else:
                temp_row[headers[1]] = ''
                temp_row[headers[2]] = ''
            temp_row[headers[3]] = value['title']
            temp_row[headers[4]] = value['type']
            temp_row[headers[5]] = value['startDate']
            temp_row[headers[6]] = value['endDate']
            temp_row[headers[7]] = value['parent']['sourcedId']
            temp_row[headers[8]] = value['schoolYear']
            temp_csv_writer.writerow(temp_row)

        # データがない場合、終了
        if len(data) == 0:
            ret_value = {'academicSessions_data_length': 0}
            self.log_info(ret_value)
            return ret_value
        else:
            ret_value = {'academicSessions_data_length': len(data)}
            self.log_info(ret_value)

        # "academicSessions.csv"
        csv_value = academicSessions_value + temp_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_ACADEMIC_SESSIONS,
                                csv_value)
        self.log_info("### END CREATE ACADEMIC_SESSIONS CSV ###")
        return ret_value

    def create_enrollment_csv(self, api_search_date):
        """
        enrollment_csv
        :param api_search_date:
        :return:
        """

        self.log_info("### START CREATE ENROLLMENTS CSV ###")
        response = self.request_data("getAllEnrollments", api_search_date)
        data = response['enrollments']

        headers = csv_roster_setting.header["enrollments"]
        temp_io = io.StringIO()
        temp_csv_writer = csv.DictWriter(temp_io, fieldnames=headers)
        enrollments_value = ''
        if api_search_date.offset == 0:
            temp_csv_writer.writeheader()
        else:
            enrollments_value = self.s3_access_object.im_port(self.out_file_path + 'csv/enrollments.csv')
        for value in data:
            temp_row = {}
            temp_row[headers[0]] = value['sourcedId']
            if api_search_date.export_type == 'delta':
                temp_row[headers[1]] = value['status']
                temp_row[headers[2]] = value['dateLastModified']
            else:
                temp_row[headers[1]] = ''
                temp_row[headers[2]] = ''
            temp_row[headers[3]] = value['class']['sourcedId']
            temp_row[headers[4]] = value['school']['sourcedId']
            temp_row[headers[5]] = value['user']['sourcedId']
            temp_row[headers[6]] = value['role']
            temp_row[headers[7]] = value['primary']
            temp_row[headers[8]] = value['beginDate']
            temp_row[headers[9]] = value['endDate']
            temp_row[headers[10]] = value['metadata']["jp.ShussekiNo"]
            temp_row[headers[11]] = value['metadata']["jp.PublicFlg"]
            temp_csv_writer.writerow(temp_row)

        # データがない場合、終了
        if len(data) == 0:
            ret_value = {'enrollments_data_length': 0}
            self.log_info(ret_value)
            return ret_value
        else:
            ret_value = {'enrollments_data_length': len(data)}
            self.log_info(ret_value)

        # "enrollments.csv"
        csv_value = enrollments_value + temp_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_ENROLLMENTS,
                                csv_value)
        self.log_info("### END CREATE ENROLLMENTS CSV ###")
        return ret_value

    def create_class_csv(self, api_search_date):
        """
        class_csv
        :param api_search_date:
        :return:
        """

        self.log_info("### START CREATE CLASSES CSV ###")
        response = self.request_data("getAllClasses", api_search_date)
        data = response['classes']

        headers = csv_roster_setting.header["classes"]
        temp_io = io.StringIO()
        temp_csv_writer = csv.DictWriter(temp_io, fieldnames=headers)
        classes_value = ''
        if api_search_date.offset == 0:
            temp_csv_writer.writeheader()
        else:
            classes_value = self.s3_access_object.im_port(self.out_file_path + 'csv/classes.csv')
        for value in data:
            temp_row = {}
            temp_row[headers[0]] = value['sourcedId']
            if api_search_date.export_type == 'delta':
                temp_row[headers[1]] = value['status']
                temp_row[headers[2]] = value['dateLastModified']
            else:
                temp_row[headers[1]] = ''
                temp_row[headers[2]] = ''
            temp_row[headers[3]] = value['title']
            temp_row[headers[4]] = ','.join(value['grades'])
            temp_row[headers[5]] = value['course']['sourcedId']
            temp_row[headers[6]] = value['classCode']
            temp_row[headers[7]] = value['classType']
            temp_row[headers[8]] = value['location']
            temp_row[headers[9]] = value['school']['sourcedId']
            termSourcedIds = []
            for term in value['terms']:
                termSourcedIds.append(term['sourcedId'])
            temp_row[headers[10]] = ','.join(termSourcedIds)
            temp_row[headers[11]] = ','.join(value['subjects'])
            temp_row[headers[12]] = ','.join(value['subjectCodes'])
            temp_row[headers[13]] = ','.join(value['periods'])
            temp_row[headers[14]] = value['metadata']["jp.specialNeeds"]
            temp_csv_writer.writerow(temp_row)

        # データがない場合、終了
        if len(data) == 0:
            ret_value = {'classes_data_length': 0}
            self.log_info(ret_value)
            return ret_value
        else:
            ret_value = {'classes_data_length': len(data)}
            self.log_info(ret_value)

        # "classes.csv"
        csv_value = classes_value + temp_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_CLASSES,
                                csv_value)
        self.log_info("### END CREATE CLASSES CSV ###")
        return ret_value

    def create_demographics_csv(self, api_search_date):
        """
        demographics_csv
        :param api_search_date:
        :return:
        """

        self.log_info("### START CREATE DEMOGRAPHICS CSV ###")
        response = self.request_data("getAllDemographics", api_search_date)
        data = response['demographics']

        headers = csv_roster_setting.header["demographics"]
        temp_io = io.StringIO()
        temp_csv_writer = csv.DictWriter(temp_io, fieldnames=headers)
        demographics_value = ''
        if api_search_date.offset == 0:
            temp_csv_writer.writeheader()
        else:
            demographics_value = self.s3_access_object.im_port(self.out_file_path + 'csv/demographics.csv')
        for value in data:
            temp_row = {}
            temp_row[headers[0]] = value['sourcedId']
            if api_search_date.export_type == 'delta':
                temp_row[headers[1]] = value['status']
                temp_row[headers[2]] = value['dateLastModified']
            else:
                temp_row[headers[1]] = ''
                temp_row[headers[2]] = ''
            temp_row[headers[3]] = value['birthDate']
            temp_row[headers[4]] = value['sex']
            temp_row[headers[5]] = value['americanIndianOrAlaskaNative']
            temp_row[headers[6]] = value['asian']
            temp_row[headers[7]] = value['blackOrAfricanAmerican']
            temp_row[headers[8]] = value['nativeHawaiianOrOtherPacificIslander']
            temp_row[headers[9]] = value['white']
            temp_row[headers[10]] = value['demographicRaceTwoOrMoreRaces']
            temp_row[headers[11]] = value['hispanicOrLatinoEthnicity']
            temp_row[headers[12]] = value['countryOfBirthCode']
            temp_row[headers[13]] = value['stateOfBirthAbbreviation']
            temp_row[headers[14]] = value['cityOfBirth']
            temp_row[headers[15]] = value['publicSchoolResidenceStatus']
            temp_csv_writer.writerow(temp_row)

        # データがない場合、終了
        if len(data) == 0:
            ret_value = {'demographics_data_length': 0}
            self.log_info(ret_value)
            return ret_value
        else:
            ret_value = {'demographics_data_length': len(data)}
            self.log_info(ret_value)

        # "demographics.csv"
        csv_value = demographics_value + temp_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_DEMOGRAPHICS,
                                csv_value)
        self.log_info("### END CREATE DEMOGRAPHICS CSV ###")
        return ret_value

    def create_users_csv(self, api_search_date):
        """
        users_csv
        :param api_search_date:
        :return:
        """

        self.log_info("### START CREATE USERS CSV ###")
        ret_value = {"keizoku_flag": 1}
        user_data = []
        # ユーザ取得
        response = self.request_data("getAllUsers", api_search_date)

        user_data = response['users']

        # ユーザがない場合、バッチ終了
        if len(user_data) == 0:
            ret_value['user_data_length'] = 0
            self.log_info(ret_value)
            return ret_value

        user_headers = csv_roster_setting.header["users"]
        temp_user_io = io.StringIO()
        temp_user_csv_writer = csv.DictWriter(temp_user_io, fieldnames=user_headers)
        users_value = ''
        if api_search_date.offset == 0:
            temp_user_csv_writer.writeheader()
        else:
            users_value = self.s3_access_object.im_port(self.out_file_path + 'csv/users.csv')
            
        role_headers = csv_roster_setting.header["roles"]
        temp_role_io = io.StringIO()
        temp_role_csv_writer = csv.DictWriter(temp_role_io, fieldnames=role_headers)
        roles_value = ''
        if api_search_date.offset == 0:
            temp_role_csv_writer.writeheader()
        else:
            roles_value = self.s3_access_object.im_port(self.out_file_path + 'csv/roles.csv')

        for value in user_data:
            temp_row = {}
            temp_row[user_headers[0]] = value['sourcedId']
            if api_search_date.export_type == 'delta':
                temp_row[user_headers[1]] = value['status']
                temp_row[user_headers[2]] = value['dateLastModified']
            else:
                temp_row[user_headers[1]] = ''
                temp_row[user_headers[2]] = ''
            temp_row[user_headers[3]] = value['enabledUser']
            temp_row[user_headers[4]] = value['username']
            userIds = []
            for userId in value['userIds']:
                userIds.append(userId['identifier'])
            temp_row[user_headers[5]] = ','.join(userIds)
            temp_row[user_headers[6]] = value['givenName']
            temp_row[user_headers[7]] = value['familyName']
            temp_row[user_headers[8]] = value['middleName']
            temp_row[user_headers[9]] = value['identifier']
            temp_row[user_headers[10]] = value['email']
            temp_row[user_headers[11]] = value['sms']
            temp_row[user_headers[12]] = value['phone']
            agentSourcedIds = []
            for agent in value['agents']:
                agentSourcedIds.append(agent['sourcedId'])
            temp_row[user_headers[13]] = ','.join(agentSourcedIds)
            temp_row[user_headers[14]] = ','.join(value['grades'])
            temp_row[user_headers[15]] = value['password']
            temp_row[user_headers[16]] = value['userMasterIdentifier']
            resourceSourcedIds = []
            for resource in value['resources']:
                resourceSourcedIds.append(resource['sourcedId'])
            temp_row[user_headers[17]] = ','.join(resourceSourcedIds)
            temp_row[user_headers[18]] = value['preferredFirstName']
            temp_row[user_headers[19]] = value['preferredMiddleName']
            temp_row[user_headers[20]] = value['preferredLastName']
            temp_row[user_headers[21]] = value['primaryOrg']['sourcedId']
            temp_row[user_headers[22]] = value['pronouns']
            temp_row[user_headers[23]] = value['metadata']["jp.kanaGivenName"]
            temp_row[user_headers[24]] = value['metadata']["jp.kanaFamilyName"]
            temp_row[user_headers[25]] = value['metadata']["jp.kanaMiddleName"]
            temp_row[user_headers[26]] = value['metadata']["jp.homeClass"]
            temp_user_csv_writer.writerow(temp_row)

            user_roles = value['roles']
            for role in user_roles:
                role_row = {}
                role_row[role_headers[0]] = str(uuid.uuid4())
                if api_search_date.export_type == 'delta':
                    role_row[role_headers[1]] = value['status']
                    role_row[role_headers[2]] = value['dateLastModified']
                else:
                    role_row[role_headers[1]] = ''
                    role_row[role_headers[2]] = ''
                role_row[role_headers[3]] = value['sourcedId']
                role_row[role_headers[4]] = role['roleType']
                role_row[role_headers[5]] = role['role']
                role_row[role_headers[6]] = role['beginDate']
                role_row[role_headers[7]] = role['endDate']
                role_row[role_headers[8]] = role['org']['sourcedId']
                role_row[role_headers[9]] = role['userProfile']
                temp_role_csv_writer.writerow(role_row)

        # "users.csv"
        csv_value = users_value + temp_user_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_USERS,
                                csv_value)

        # "roles.csv"
        csv_value = roles_value + temp_role_io.getvalue()
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_ROLES,
                                csv_value)

        ret_value['user_data_length'] = len(user_data)
        self.log_info(ret_value)
        self.log_info("### END CREATE USERS CSV ###")
        return ret_value

    def write_tmp_csv_file(self, filename, csv_content):
        """
        CSVファイルを作成
        :param csv_content:
        :param filename:
        """

        self.log_info("### START WRITE CSV ###")
        self.log_info(filename)
        self.s3_access_object.export(self.out_file_path + 'csv/' + filename, csv_content)
        # 出力フォルダがない場合、作成する
        if not os.path.exists(self.local_file_path):
            os.makedirs(self.local_file_path)

        try:
            file_path = f"{self.local_file_path}{filename}"
            with open(file_path, "w") as csv_file:
                for line in csv_content.split("\r"):
                    csv_file.write(line)
        except Exception as ex:
            # トレースバック
            self.log_error(traceback.format_exc())
            raise ex
        self.log_info("### END WRITE CSV ###")

    def del_file(self, path):
        """
        ファイル削除
        :param path:
        """

        self.log_info("### START DELETE CSV ###")
        if not os.path.exists(path):
            self.log_info("パスがない")
            self.log_info("### END DELETE CSV ###")
            return

        ls = os.listdir(path)
        # フォルダにファイルがない場合、フォルダを削除
        if len(ls) == 0:
            self.log_info("パスにファイルがない")
            self.log_info("### END DELETE CSV ###")
            return

        # フォルダにファイルがある場合、削除
        for file in ls:
            c_path = os.path.join(path, file)
            if os.path.isdir(c_path):
                self.del_file(c_path)
            else:
                self.log_info(c_path)
                os.remove(c_path)
        self.log_info("### END DELETE CSV ###")

    def zip_file(self, src_dir, system_organization_code):
        """
        CSVファイルをzipに圧縮する
        :param system_organization_code:
        :param src_dir:
        """

        self.log_info("### START ZIP CSV ###")

        zip_file_name = f"RO_{self.deal_start_time}_{system_organization_code}"

        manifest_file_path = f"{self.local_file_path}{csv_roster_setting.CSV_FILE_NAME_MANIFEST}"
        if not os.path.exists(manifest_file_path):
            self.log_info('ユーザデータがないため、zipファイルが作成されませんでした')
            return

        zip_name = src_dir + zip_file_name + '.zip'

        zf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

        for dir_path, dir_names, filenames in os.walk(src_dir):
            fpath = dir_path.replace(src_dir, '')
            fpath = fpath and fpath + os.sep or ''

            for filename in filenames:
                self.log_info(filename)
                if filename == zip_file_name + '.zip':
                    continue
                zf.write(os.path.join(dir_path, filename), fpath + filename)

        zf.close()

        # zipファイルをS3にアップロードする
        s3 = boto3.resource('s3')
        s3_key = self.out_file_path + 'zip/' + zip_file_name + ".zip"
        s3.meta.client.upload_file(zip_name, os.environ["S3_BUCKET_NAME"], s3_key)

        self.log_info("### END ZIP CSV ###")

    def create_manifest_csv(self):
        """
        manifest.csv
        """
        self.log_info("### START CREATE MANIFEST CSV ###")
        headers = csv_roster_setting.header["manifest"]
        temp_io = io.StringIO()
        temp_csv_writer = csv.DictWriter(temp_io, fieldnames=headers)
        temp_csv_writer.writeheader()

        # CSV出力内容
        export_type = self.event['export_type']
        content_list = [
            {
                'propertyName': "manifest.version",
                'value': "1.0"
            },
            {
                'propertyName': "oneroster.version",
                'value': "1.2"
            },
            {
                'propertyName': "file.academicSessions",
                'value': export_type
            },
            {
                'propertyName': "file.categories",
                'value': "absent"
            },
            {
                'propertyName': "file.classes",
                'value': export_type
            },
            {
                'propertyName': "file.classResources",
                'value': "absent"
            },
            {
                'propertyName': "file.courses",
                'value': "absent"
            },
            {
                'propertyName': "file.courseResources",
                'value': "absent"
            },
            {
                'propertyName': "file.demographics",
                'value': export_type
            },
            {
                'propertyName': "file.enrollments",
                'value': export_type
            },
            {
                'propertyName': "file.lineItemLearningObjectiveIds",
                'value': "absent"
            },
            {
                'propertyName': "file.lineItems",
                'value': "absent"
            },
            {
                'propertyName': "file.lineItemScoreScales",
                'value': "absent"
            },
            {
                'propertyName': "file.orgs",
                'value': export_type
            },
            {
                'propertyName': "file.resources",
                'value': "absent"
            },
            {
                'propertyName': "file.resultLearningObjectiveIds",
                'value': "absent"
            },
            {
                'propertyName': "file.results",
                'value': "absent"
            },
            {
                'propertyName': "file.resultScoreScales",
                'value': "absent"
            },
            {
                'propertyName': "file.roles",
                'value': export_type
            },
            {
                'propertyName': "file.scoreScales",
                'value': "absent"
            },
            {
                'propertyName': "file.userProfiles",
                'value': "absent"
            },
            {
                'propertyName': "file.userResources",
                'value': "absent"
            },
            {
                'propertyName': "file.users",
                'value': export_type
            },
            {
                'propertyName': "file.systemName",
                'value': "absent"
            },
            {
                'propertyName': "file.systemCode",
                'value': "absent"
            }
        ]
        for temp_row in content_list:
            temp_csv_writer.writerow(temp_row)

        # "manifest.csv"
        self.write_tmp_csv_file(csv_roster_setting.CSV_FILE_NAME_MANIFEST,
                                temp_io.getvalue())

        self.log_info("### END CREATE MANIFEST CSV ###")
