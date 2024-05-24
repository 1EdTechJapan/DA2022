# -*- coding: utf-8 -*-
import string
import secrets
import zipfile
import csv
import io
import copy
import convert_applic_to_tomolinks
import utils
from error_code import ErrorCode

class tomolinks_class:
    def __init__(self,fiscal_year,school_name,grade_name,class_name):
        self.fiscal_year = fiscal_year
        self.school_name = school_name
        self.grade_name = grade_name
        self.class_name = class_name

class tomolinks_account:
    '''
    tomoLinksのアカウントで必要となるデータをまとめたもの
    '''
    def __init__(self,name,user_id,school_name,grade_name,fiscal_year,class_name,user_role,password):
        self.name = name
        self.user_id = user_id
        self.school_name = school_name
        self.grade_name = grade_name
        self.fiscal_year = fiscal_year
        self.class_name = class_name
        self.user_role = user_role
        self.password = password

class OnerosterClass:
    '''
    OneRosterのすべてのユーザーデータから、クラスと学年を紐づける辞書を作成しておくクラス
    教員アカウントの場合、クラスには所属するが、学年情報が不明になるため、
    そのクラスに所属する別のアカウントの学年情報を保持する
    '''
    __class_dict = dict()
    def __init__(self):
        __class_dict = dict()
    def set(self, class_id, grade):
        if grade == None:
            return
        if class_id not in self.__class_dict:
            self.__class_dict[class_id] = grade
        else:
            if self.__class_dict[class_id] != grade:
                print('doubt class grade prev :' + self.__class_dict[class_id] + 'after ' + str(grade))
    def get_grade_by_class_id(self, class_id):
        if class_id in self.__class_dict:
            return self.__class_dict[class_id]
        else:
            return None

class SchoolCodeGenerator:
    '''
    OneRosterCsvConverterでアカウントを払い出すときに使う学校コードを生成する
    '''
    __counter = 0
    def __init__(self):
        self.__counter = 0
    def reset(self, initial_value = 1):
        self.__counter = initial_value
    def get_id(self):
        ret = str(self.__counter).zfill(3)
        self.__counter = self.__counter + 1
        return ret

class UserSerialNumberGenerator:
    '''
    OneRosterCsvConverterでアカウントを払い出すときに使う通し番号を生成する
    '''
    __counter = 0
    def __init__(self):
        self.__counter = 0
    def reset(self, initial_value = 1):
        self.__counter = initial_value
    def get_id(self):
        ret = str(self.__counter).zfill(3)
        self.__counter = self.__counter + 1
        return ret
        
class ExcuseList:
    '''
    CSV変換時に特殊な対応をしたときに、ユーザーに通知する文字列を格納する
    '''
    __excuse_list = []
    def __init__(self):
        self.__excuse_list = []
    def set(self, excuse):
        self.__excuse_list.append(excuse)
    def get(self):
        return self.__excuse_list
    def reset(self):
        self.__excuse_list = []

oneroster_filelist = []
tomolinks_filelist = []

manifest_filename = 'manifest.csv'

school_code_generator = SchoolCodeGenerator()
user_serial_number_generator = UserSerialNumberGenerator()
excuse_list = ExcuseList()

def validate_oneroster(zf):
    '''
    OneRosterCsvファイルの簡易チェックを行う
    '''
    global oneroster_filelist
    # manifestファイルがあるかどうかを確認する
    filelists = zf.namelist()
    if manifest_filename not in filelists:
        return ErrorCode.not_found_manifest
    
    manifest = read_csvfile_in_zipfile(zf, manifest_filename)
    for row in manifest:
        items = row['propertyName'].split('.') 
        if items[0] == 'file':
            if row['value'] != 'absent':
                oneroster_filelist.append(items[1]+'.csv')

    oneroster_filelist_for_check = copy.copy(oneroster_filelist)
    for file in zf.namelist():
        if file in oneroster_filelist_for_check:
            oneroster_filelist_for_check.remove(file)
    if len(oneroster_filelist_for_check):
        return False
    else:
        return True

def validate_tomolinks(zf):
    '''
    tomoLinksCsvファイルの簡易チェックを行う
    非公開
    '''
    return True

def generate_password(size=128):
    '''
    OneRosterCsvConverterがパスワードを生成するときに使用する
    非公開
    '''
    return 'password'

def get_grade_applic(course, or_class, user = None):
    '''
    userの学年情報をapplic型で返す
    学年情報が見つからない場合 Not Foundを返す
    '''
    if user != None and len(user['grades']):
        grade = user['grades']
    elif len(or_class['grades']):
        grade = or_class['grades']
    elif len(course['grades']):
        grade = course['grades']
    else:
        # 学年情報が見つからない場合、同じクラスに属している児童生徒の学年から学年情報を補完する
        grade = 'Not Found'
    return grade.split(',')[0]

def get_grade_tomolinks(course, or_class, user = None):
    '''
    userの学年情報をtomoLinks型で返す
    学年情報が見つからない場合 Not Foundを返す
    '''
    grade = get_grade_applic(course, or_class, user)
    return convert_applic_to_tomolinks.convert_gradename_to_tomolinks(grade)

def get_grade_integer(course, or_class, user = None):
    '''
    userの学年情報を整数型で返す
    小学1年が1、中学1年は7となる
    '''
    grade = get_grade_applic(course, or_class, user)
    return convert_applic_to_tomolinks.convert_gradename_to_integer(grade)


def get_grade_tomolinks_by_oneroster_class(or_class, oneroster_class):
    '''
    classの学年情報を整数型で返す
    '''
    return oneroster_class.get_grade_by_class_id(or_class['courseSourcedId'])

def get_role(oneroster_data, user):
    for role in oneroster_data['roles.csv']:
        if role['userSourcedId'] == user['sourcedId']:
            return role
    return None

def get_org(oneroster_data, user):
    role = get_role(oneroster_data, user)
    if len(user['primaryOrgSourcedId']):
        org_source_id = user['primaryOrgSourcedId']
    else:
        or_class = get_class(oneroster_data, user)
        if len(or_class['schoolSourcedId']):
            org_source_id = or_class['schoolSourcedId']
        else:
            role = get_role(oneroster_data, user)
            org_source_id = role['orgSourcedId']
    for org in oneroster_data['orgs.csv']:
        if org['sourcedId'] == org_source_id:
            return org
    return None

def get_enrollment(oneroster_data, user):
    for enrollment in oneroster_data['enrollments.csv']:
        if enrollment['userSourcedId'] == user['sourcedId']:
            return enrollment
    return None

def get_class(oneroster_data, user):
    enrollment = get_enrollment(oneroster_data, user)
    for or_class in oneroster_data['classes.csv']:
        if or_class['sourcedId'] == enrollment['classSourcedId']:
            return or_class
    return None

def get_course(oneroster_data, user):
    or_class = get_class(oneroster_data, user)
    for course in oneroster_data['courses.csv']:
        if course['sourcedId'] == or_class['courseSourcedId']:
            return course
    return None

def get_academic_session(oneroster_data, user):
    or_class = get_class(oneroster_data, user)
    for academic_session in oneroster_data['academicSessions.csv']:
        if academic_session['sourcedId'] == or_class['termSourcedIds']:
            return academic_session
    return None

def get_userprofile(oneroster_data, user):
    for user_profile in oneroster_data['userProfiles.csv']:
        if user_profile['userSourcedId'] == user['sourcedId']:
            return user_profile
    return None

def get_org_by_class(oneroster_data, or_class):
    for org in oneroster_data['orgs.csv']:
        if org['sourcedId'] == or_class['schoolSourcedId']:
            return org
    return None

def get_academic_session_by_class(oneroster_data, or_class):
    for academic_session in oneroster_data['academicSessions.csv']:
        if academic_session['sourcedId'] == or_class['termSourcedIds']:
            return academic_session
    return None

def get_course_by_class(oneroster_data, or_class):
    for course in oneroster_data['courses.csv']:
        if course['sourcedId'] == or_class['courseSourcedId']:
            return course
    return None

def get_tomolinks_id(oneroster_data, user):
    '''
    tomoLinksのIDをOneRosterから取得する関数
    tomoLinks側は自治体内部でユニークである必要がある
    '''
    return user['username']

def read_csvfile_in_zipfile(zf, csv_file_name):
    with zf.open(csv_file_name, 'r') as z:
        r = z.read().decode('utf_8_sig')
        f = io.StringIO()
        f.write(r)
        f.seek(0)
        reader = csv.DictReader(f, delimiter=',')
        data = [row for row in reader]
        return data

def create_tomolinks_class(oneroster_data, or_class, oneroster_class):
    '''
    OneRosterのデータから、tomoLinksのClass情報を生成・返答する
    '''
    org = get_org_by_class(oneroster_data, or_class)
    academic_session = get_academic_session_by_class(oneroster_data, or_class)
    course = get_course_by_class(oneroster_data, or_class)
    fiscal_year = academic_session['schoolYear']
    school_name = org['name']
    grade_name = get_grade_tomolinks(course=course, or_class=or_class)
    if grade_name == None:
        grade_name = get_grade_tomolinks_by_oneroster_class(or_class, oneroster_class)
        if grade_name == None:
            grade_name = get_default_grade(school_name)

    class_name = or_class['title']
    return tomolinks_class(fiscal_year,school_name,grade_name,class_name)

def create_tomolinks_account(oneroster_data, user, oneroster_class):
    '''
    OneRosterのデータから、tomoLinksのaccount情報を生成・返答する
    '''
    role = get_role(oneroster_data, user)
    org = get_org(oneroster_data, user = user)
    enrollment = get_enrollment(oneroster_data, user)
    or_class = get_class(oneroster_data, user)
    course = get_course(oneroster_data, user)
    academic_session = get_academic_session(oneroster_data, user)

    user_id = create_tomolinks_id(oneroster_data, user)
    if len(user['preferredGivenName']) == 0 and len(user['preferredFamilyName']) == 0:
        name = user_id
    else:
        name = user['preferredGivenName'] + ' ' + user['preferredFamilyName']

    school_name = org['name']
    grade_name = get_grade_tomolinks(course, or_class, user)
    if grade_name == None:
        grade_name = get_grade_tomolinks_by_oneroster_class(or_class, oneroster_class)
        if grade_name == None:
            grade_name = get_default_grade(school_name)
            excuse = user_id + 'の学年が見つからないため、' + grade_name + 'に設定しました。'
            excuse_list.set(excuse)

    fiscal_year = academic_session['schoolYear']
    class_name = or_class['title']
    user_role = utils.convert_role_to_tomolinks(role['role'])

    if len(user['password']) == 0:
        password = generate_password()
    else:
        password = user['password']
    return tomolinks_account(name,user_id,school_name,grade_name,fiscal_year,class_name,user_role,password)

def create_school_code():
    return school_code_generator.get_id()

def create_user_serial_number():
    return user_serial_number_generator.get_id()

def get_school_code(school_name):
    with open('school_mapping_data.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        data = [row for row in reader]
        for s in data:
            if s['school_name'] == school_name:
                return s['school_code']
        return create_school_code()
    return create_school_code()

def get_default_grade(school_name):
    '''
    各学校のデフォルト学年を外部設定ファイルから取得する
    '''
    with open('school_mapping_data.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        data = [row for row in reader]
        for s in data:
            if s['school_name'] == school_name:
                return convert_applic_to_tomolinks.convert_gradename_to_tomolinks(s['default_grade'])
        return '小学1年'
    return '小学1年'

def get_entrance_year(oneroster_data, user):
    '''
    児童生徒の学年と現在年度から入学年度の下２桁を文字列で返す
    '''
    academic_session = get_academic_session(oneroster_data, user)
    school_year = int(academic_session['schoolYear'])
    grade_integer = get_grade_integer(get_course(oneroster_data, user), get_class(oneroster_data, user), user)
    if grade_integer == None:
        grade_integer = 1
    entrance_year = school_year - grade_integer + 1
    return str(entrance_year % 100).zfill(2)

def create_tomolinks_id(oneroster_data, user):
    '''
    非公開
    '''
    return 'tomolinks'

tomolinks_class_csv_header = [
    '年度',
    '学校',
    '学年',
    'クラス名',
]
def generate_class_csv_file_for_tomolinks(filename, tl_classes):
    with open(filename, "w", encoding="utf_8_sig") as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(tomolinks_class_csv_header)
        for a in tl_classes:
            writer.writerow([a.fiscal_year, a.school_name, a.grade_name, a.class_name])
    f.close()

tomolinks_account_csv_header = [
    '表示名',
    'ユーザーID',
    '学校',
    '学年',
    '年度',
    'クラス',
    'ユーザー種別',
    'パスワード',
]

def generate_account_csv_file_for_tomolinks(filename,tl_accounts):
    with open(filename, "w", encoding="utf_8_sig") as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(tomolinks_account_csv_header)
        for a in tl_accounts:
            writer.writerow([a.name, a.user_id, a.school_name, a.grade_name, a.fiscal_year, a.class_name, a.user_role, a.password])
    f.close()

def convert_csv(oneroster_file, tomolinks_file, output_folder, mode = None):
    '''
    OneRosterCSVファイルからtomoLinksのCSVファイルを生成するメイン関数
    '''
    global oneroster_filelist
    oneroster_filelist = []
    tomolinks_filelist = []
    
    tomolinks_account_original = []
    tomolinks_accounts_for_register = []
    tomolinks_accounts_for_edit = []
    tomolinks_accounts_for_delete = []
    tomolinks_classes_for_register = []

    school_code_generator.reset()
    user_serial_number_generator.reset()
    excuse_list.reset()

    try:
        with zipfile.ZipFile(oneroster_file, 'r') as zf_or, zipfile.ZipFile(tomolinks_file, 'r') as zf_tl:
            ## ファイルが期待通りかチェックする
            ret_code = validate_oneroster(zf_or)
            if ret_code != True:
                return ret_code
            ret_code = validate_tomolinks(zf_tl)
            if ret_code != True:
                return ret_code
            
            ## OneRosterのCSVファイルをメモリに展開する
            oneroster_data = dict()
            for oneroster_file in oneroster_filelist:
                oneroster_data[oneroster_file] = read_csvfile_in_zipfile(zf_or, oneroster_file)

            ## tomoLinksのCSVファイルをメモリに展開する
            tomolinks_data = dict()
            for tomolinks_file in zf_tl.infolist():
                tomolinks_filelist.append(tomolinks_file.filename)
                tomolinks_data[tomolinks_file.filename] = read_csvfile_in_zipfile(zf_tl, tomolinks_file.filename)

                for row in tomolinks_data[tomolinks_file.filename]:
                    # 保護者ロールは対象外
                    if(row['ユーザー種別'] == '保護者'):
                        continue
                    name = row['表示名']
                    user_id = row['ユーザーID']
                    school_name = row['学校']
                    grade_name = row['学年']
                    fiscal_year = int(row['年度'])
                    class_name = row['クラス']
                    user_role = row['ユーザー種別']
                    password = row['パスワード']

                    account = tomolinks_account(name,user_id,school_name,grade_name,fiscal_year,class_name,user_role,password)
                    tomolinks_account_original.append(account)

            ## OneRosterの各クラスの学年を取得する
            oneroster_class = OnerosterClass()
            if 'users.csv' in oneroster_filelist:
                for user in oneroster_data['users.csv']:
                    role = get_role(oneroster_data, user)
                    if role['role'] == 'guardian':
                        # 保護者アカウントはtomoLinksでは児童生徒に紐づくものなのでスキップする
                        continue
                    or_class = get_class(oneroster_data, user)
                    if or_class != None:
                        course = get_course(oneroster_data, user)
                        if course != None:
                            grade_name = get_grade_tomolinks(course, or_class, user)
                            if grade_name != None:
                                oneroster_class.set(or_class['courseSourcedId'], grade_name)
            
            ## OneRosterのユーザーリストでループ
            if 'users.csv' in oneroster_filelist:
                for user in oneroster_data['users.csv']:
                    role = get_role(oneroster_data, user)
                    if role['role'] == 'guardian':
                        # 保護者アカウントはtomoLinksでは児童生徒に紐づくものなのでスキップする
                        continue
                    for tl_account in tomolinks_account_original:
                        is_found = False
                        if tl_account.user_id == get_tomolinks_id(oneroster_data, user):
                            ## 存在したので編集対象アカウント
                            tomolinks_accounts_for_edit.append(create_tomolinks_account(oneroster_data, user, oneroster_class))
                            tomolinks_account_original.remove(tl_account)
                            is_found = True
                            break
                    ## 存在しない場合、新規登録
                    if is_found == False:
                        tomolinks_accounts_for_register.append(create_tomolinks_account(oneroster_data, user, oneroster_class))
            ## この時点でマッチングが取れていないtomoLinksIDは削除する
            for tl_account in tomolinks_account_original:
                tomolinks_accounts_for_delete.append(tl_account)

            # クラス登録が必要なものを探す
            if 'classes.csv' in oneroster_filelist:
                for or_class in oneroster_data['classes.csv']:
                    tomolinks_classes_for_register.append(create_tomolinks_class(oneroster_data, or_class, oneroster_class))

            ## CSV生成フェーズ
            #print('クラス登録のCSV作成')
            if len(tomolinks_classes_for_register):
                filename = output_folder + '/class_register.csv'
                generate_class_csv_file_for_tomolinks(filename,tomolinks_classes_for_register)

            #print('新規登録のCSV作成')
            if len(tomolinks_accounts_for_register):
                filename = output_folder + '/account_register.csv'
                generate_account_csv_file_for_tomolinks(filename,tomolinks_accounts_for_register)

            #print('編集のCSV作成')
            if len(tomolinks_accounts_for_edit):
                filename = output_folder + '/account_edit.csv'
                generate_account_csv_file_for_tomolinks(filename,tomolinks_accounts_for_edit)

            #print('削除のCSV作成')
            if len(tomolinks_accounts_for_delete):
                filename = output_folder + '/account_delete.csv'
                generate_account_csv_file_for_tomolinks(filename,tomolinks_accounts_for_delete)

    except zipfile.BadZipFile:
        return -1
    return 0, excuse_list.get()