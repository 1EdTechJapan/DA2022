# -*- coding: utf-8 -*-
import convert_csv_to_tomolinks
import validate_oneroster_csv
from error_code import ErrorCode
import csv
import sys
import os

#CSV_FILE_PATH = 'C:/oneroster_test/OneRoster CSV入力_接続テスト項目書.csv'
# CSV_FILE_PATH = 'C:/oneroster_test/OneRoster CSV入力_接続テスト項目書_20230124.csv'
# CSV_FILE_PATH = 'C:/oneroster_test/OneRoster CSV入力_接続テスト項目書_20230201.csv'
CSV_FILE_PATH = 'C:/oneroster_test/OneRoster CSV入力_接続テスト項目書_20230216.csv'
#ONE_ROSTER_FILE_FOLDER = 'C:/oneroster_test/OneRosterTestCSV_2023010601/'
# ONE_ROSTER_FILE_FOLDER = 'C:/oneroster_test/OneRosterTestCSV_2023012401/'
# ONE_ROSTER_FILE_FOLDER = 'C:/oneroster_test/OneRosterTestCSV_2023020801/'
ONE_ROSTER_FILE_FOLDER = 'C:/oneroster_test/OneRosterTestCSV_2023021601/'
TOMOLINKS_FILE_PATH = 'C:/oneroster_test/tomolinks.zip'

if len(sys.argv) == 2:
    TEST_MODE = sys.argv[1]
else:
    TEST_MODE = 'Valid'

print('Test Case is '+ TEST_MODE)
mitsukaranai_list = []
with open(CSV_FILE_PATH, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        testdatas = [row for row in reader]

for testcase in testdatas:
    if TEST_MODE == 'Valid' and testcase['カテゴリ'] == '正常系':
        print("正常系テスト : " + testcase['Test ID'] + ':' + testcase['テスト内容'])
    elif TEST_MODE == 'Invalid' and testcase['カテゴリ'] != '正常系':
        print('================================')
        print("異常系テスト : " + testcase['Test ID'] + ':' + testcase['テスト内容'])
        # if testcase['テスト対象'] == '全体':
        #     print('なぜか全体のテストファイルがないのでスキップ')
        #     continue
    else:
        continue

    if testcase['テスト対象'].split('.')[0] == '全体':
        testfile = ONE_ROSTER_FILE_FOLDER + 'manifest' + '/' + testcase['ファイル名'] 
    else:
        testfile = ONE_ROSTER_FILE_FOLDER + testcase['テスト対象'].split('.')[0] + '/' + testcase['ファイル名'] 
    output_folder = 'result\\' + testcase['Test ID']

    if os.path.exists('result\\') != True:
        os.mkdir('result\\')
    if os.path.exists(output_folder) != True:
        os.mkdir(output_folder)

    if os.path.isfile(testfile):
        validation_result = validate_oneroster_csv.validateBulk(testfile)
        if not validation_result['is_success']:
            result_str = '\033[31m'+'変換失敗 : ' + str(validation_result['error_code']) + ' reason : ' + validation_result['error_message']+'\033[0m'
            print(result_str)
        else:
            ret_code, excuse_list = convert_csv_to_tomolinks.convert_csv(testfile,TOMOLINKS_FILE_PATH,output_folder)
            if ret_code == ErrorCode.convert_success:
                show_str = '\033[32m' + '変換に成功しました。tomoLinksへインポートしてください。\n' + '\033[0m'
                for excuse in excuse_list:
                    show_str = show_str + excuse + '\n'
                print(show_str)
            else:
                result_str = '変換失敗 : ' + str(ret_code) + ' reason : ' + ErrorCode.get_error_reason(ErrorCode, code = ret_code)
                print(result_str)
    else:
        print('This file does not found ' + testfile)
    continue
