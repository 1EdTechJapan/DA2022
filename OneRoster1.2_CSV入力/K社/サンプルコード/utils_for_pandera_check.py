import pandera as pa
from datetime import datetime
import re

# util funcs
# pc means pandera check
def is_exists_pc(errorString):
    return pa.Check(lambda s: s.str.len()>0 ,error = errorString )
def is_missing_pc(errorString):
    return pa.Check(lambda s: s.str.len()==0 ,error = errorString )

def is_ISO_timeformat(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except:
        return False
    return True
def is_ISO_timeformat_pc(errorString):
    return pa.Check(lambda s: s.map(is_ISO_timeformat) ,error = errorString )
def is_ISO_timeformat_option(dt_str):
    if len(dt_str) == 0:
        return True    
    try:
        datetime.fromisoformat(dt_str)
    except:
        return False
    return True
def is_ISO_timeformat_option_pc(errorString):
    return pa.Check(lambda s: s.map(is_ISO_timeformat_option) ,error = errorString )

def is_YYYY_format(str):
    return bool(re.fullmatch(r'[0-9]{4}',str))
def is_YYYY_format_pc(errorString):
    return pa.Check(lambda s: s.map(is_YYYY_format),error = errorString)

def is_uuid_v4(str):
    return bool(re.fullmatch(r'[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}',str.lower()))
def is_uuid_v4_pc(errorString):
    return pa.Check(lambda s: s.map(is_uuid_v4),error = errorString)
def is_uuid_v4_option(str):
    if len(str) == 0:
        return True
    return bool(re.fullmatch(r'[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}',str.lower()))
def is_uuid_v4_option_pc(errorString):
    return pa.Check(lambda s: s.map(is_uuid_v4_option),error = errorString)

def is_JP_profile_FY(str):
    return bool(re.fullmatch(r'[0-9]{4}年度',str))
def is_JP_profile_FY_pc(errorString):
    return pa.Check(lambda s: s.map(is_JP_profile_FY),error = errorString)

def is_JP_profile_course_title(str):
    return bool(re.fullmatch(r'[0-9]{4}年度[\s\S]*',str))
def is_JP_profile_course_title_pc(errorString):
    return pa.Check(lambda s: s.map(is_JP_profile_course_title),error = errorString)

def is_not_include_half_katakana(str):
    return not bool(re.findall(r'[ｦ-ﾟ]',str))
def is_not_include_half_katakana_pc(errorString):
    return pa.Check(lambda s: s.map(is_not_include_half_katakana),error = errorString)

def is_mext_school_code_option(str):
    if len(str) == 0:
        return True
    # https://www.mext.go.jp/content/20210128-mxt_chousa01-000011635_01.pdf
    return bool(re.fullmatch(r'[ABCDEFGH][12][0-4][0-9][123][0-9]{7}[0-9]',str))
def is_mext_school_code_pc_option(errorString):
    return pa.Check(lambda s: s.map(is_mext_school_code_option),error = errorString)

def is_mext_kyouikuiinkai_code_option(str):
    if len(str) == 0:
        return True
    # https://www.mext.go.jp/content/20210128-mxt_chousa01-000011635_01.pdf
    return bool(re.fullmatch(r'[0-4][0-9]{5}',str))

def is_in_APPLIC_GRADES_W_NONE_list(str):
    grade_list = str.split(',')
    for grade_str in grade_list:
        if not (grade_str in APPLIC_GRADES_W_NONE):
            return False
    return True
def is_in_APPLIC_GRADES_W_NONE_list_pc(errorString):
    return pa.Check(lambda s: s.map(is_in_APPLIC_GRADES_W_NONE_list),error = errorString)

def is_in_APPLIC_SUBJECTS_W_NONE_list(str):
    subject_list = str.split(',')
    for subject_str in subject_list:
        if not (subject_str in APPLIC_SUBJECTS_W_NONE):
            return False
    return True
def is_in_APPLIC_SUBJECTS_W_NONE_list_pc(errorString):
    return pa.Check(lambda s: s.map(is_in_APPLIC_SUBJECTS_W_NONE_list),error = errorString)

def is_correct_userIds_list_option(userIdsStr):
    userIds = userIdsStr.split(',')
    for userId in userIds:
        if len(userId) != 0:
            # optionalなので文字長0は許容
            # 文字列入っていて、かつそれが規定にUnmatchで弾く
            if not bool(re.fullmatch(r'\{\S*:\S*\}',userIdsStr)):#https://www.imsglobal.org/spec/oneroster/v1p2/bind/csv/#users-csv:~:text=User%20name.-,userIds,-No
                return False
    return True
def is_correct_userIds_list_option_list(errorString):
    return pa.Check(lambda s: s.map(is_correct_userIds_list_option),error = errorString)

APPLIC_GRADES = ['P1','P2','P3','P4','P5','P6','J1','J2','J3']
APPLIC_GRADES_W_NONE = APPLIC_GRADES + ['']

APPLIC_SUBJECTS = ['P010','P020','P030','P040','P050','P060','P070','P080','P090','P100','J010','J020','J030','J040','J050','J060','J070','J080','J090']
APPLIC_SUBJECTS_W_NONE = APPLIC_SUBJECTS + ['']