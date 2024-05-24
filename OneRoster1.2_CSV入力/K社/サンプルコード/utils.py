# -*- coding: utf-8 -*-

import os
import sys

dict_gradename_tomolinks = {
    '01':'小学1年',
    '02':'小学2年',
    '03':'小学3年',
    '04':'小学4年',
    '05':'小学5年',
    '06':'小学6年',
    '07':'中学1年',
    '08':'中学2年',
    '09':'中学3年',
}

dict_rolename_tomolinks = {
    'student'   : '児童生徒',
    'guardian'  : '保護者',
    'teacher'   : '一般教員',
    'principal' : '管理職教員',
    'siteAdministrator' : '管理職教員',
    'systemAdministrator' : 'システム管理者',
    'districtAdministrator' : 'システム管理者',
}

def convert_gradename_to_tomolinks(grade_name):
    '''
    整数型の学年情報からのtomoLinks型学年情報に変換する
    '''
    if grade_name in dict_gradename_tomolinks:
        return dict_gradename_tomolinks[grade_name]
    else:
        return -1

def convert_gradename_from_tomolinks(tomolinks_grade_name):
    '''
    tomoLinks型の学年情報からの整数型学年情報に変換する
    '''
    if tomolinks_grade_name in dict_gradename_tomolinks.values():
        keys = [k for k, v in dict_gradename_tomolinks.items() if v == tomolinks_grade_name]
        return keys
    else:
        return -1

def convert_role_to_tomolinks(role_name):
    '''
    OneRosterのrole名からtomoLinksのrole名に変換する
    見つからなかった場合、Noneを返す
    '''
    if role_name in dict_rolename_tomolinks:
        return dict_rolename_tomolinks[role_name]
    else:
        print("Unknows role name : " + role_name)
        return None


def get_resource_path(resource_filename):
    '''
    resourceファイル名から実際のパスを取得する
    pyinstallerやcx_freeze等複数の方法でのexe化をサポートする
    見つからなかった場合にはNoneを返す
    '''
    resource_path = None
    resource_dirs = [
        "",
        "resources",
        os.path.dirname(__file__),
        os.path.join(os.path.dirname(__file__), "resources"),
    ]
    # for pyinstaller
    try:
        resource_dirs.append(sys._MEIPASS)
        d = os.path.join(sys._MEIPASS, "resources")
        resource_dirs.append(d)
    except Exception:
        pass

    # for cx_freeze
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
        resource_dirs.append(datadir)
        resource_dirs.append(os.path.join(datadir, "resources"))

    for d in resource_dirs:
        if os.path.exists(os.path.join(d, resource_filename)):
            resource_path = os.path.join(d, resource_filename)
            break

    return resource_path
