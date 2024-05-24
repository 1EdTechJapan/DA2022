# -*- coding: utf-8 -*-

dict_gradename_applic_tomolinks = {
    'P1':'小学1年',
    'P2':'小学2年',
    'P3':'小学3年',
    'P4':'小学4年',
    'P5':'小学5年',
    'P6':'小学6年',
    'J1':'中学1年',
    'J2':'中学2年',
    'J3':'中学3年',
}

dict_gradename_applic_integer = {
    'P1':1,
    'P2':2,
    'P3':3,
    'P4':4,
    'P5':5,
    'P6':6,
    'J1':7,
    'J2':8,
    'J3':9,
}

def convert_gradename_to_tomolinks(applic_grade_name):
    '''
    applic型の学年情報からtomoLinks型の学年情報に変換する
    '''
    if applic_grade_name in dict_gradename_applic_tomolinks:
        return dict_gradename_applic_tomolinks[applic_grade_name]
    else:
        return None

def convert_gradename_from_tomolinks(tomolinks_grade_name):
    '''
    tomoLinks型の学年情報からのapplic型学年情報に変換する
    '''
    if tomolinks_grade_name in dict_gradename_applic_tomolinks.values():
        keys = [k for k, v in dict_gradename_applic_tomolinks.items() if v == tomolinks_grade_name]
        return keys
    else:
        return None

def convert_gradename_to_integer(applic_grade_name):
    '''
    applic型の学年情報から整数型の学年情報に変換する
    '''
    if applic_grade_name in dict_gradename_applic_integer:
        return dict_gradename_applic_integer[applic_grade_name]
    else:
        return None
