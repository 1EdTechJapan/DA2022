import pandas as pd
import pandera as pa
import zipfile
import csv
import json
import utils
import re

import oneroster_csv_schema

with open(utils.get_resource_path('invalidErrorConfig.json'), mode="rt", encoding="utf-8") as f:
  ORE = json.load(f)

# oneRoster Error
class OneRosterManifestError(Exception):
  pass

class OneRosterFileSetError(Exception):
  def __init__(self, code, message):
    self.code = code
    self.message = message

def makeErrorResult(code, omessage = ''):
  errorResult = {}
  errorResult['error_code'] = code
  errorResult['error_message'] = ORE[code].format(omessage)
  errorResult['is_success'] = False
  return errorResult

# NOTE:「column XXX not in dataframe」を拾うために必要
r_colum_lack = r'column\S*notindataframe\S*'

# NOTE:チェック中のファイル名を拾ってExceptionでメッセージ出すために必要
target_file_name = ''

def validateBulk(oneroster_file):
  '''OneRoster Bulkのバリデーションチェックを行う.
  
  参考にした仕様は1Edtech OneRoster v1p2, JP profile v.1.2, 学習eポータル標準仕様 v3.0.0α版

  Args:
    oneroster_file: zip file path about oneRoster
    
  Returns:
    result: include below params.
      error_code
      error_message
      is_success
  '''
  result = {}
  result['is_success'] = True
  try:
    # manifestファイルの有無チェック＆OKならその中身をDataFrameで返す
    df_manifest = read_manifest_to_df(oneroster_file)

    global target_file_name
    target_file_name = 'manifest'
    # manifestfileのバリデーション
    if df_manifest.index.name != "propertyName":
      raise OneRosterManifestError('ib9004')
    if df_manifest.columns.values[0] != "value":
      raise OneRosterManifestError('ib9005')
    oneroster_csv_schema.df_schema['manifest'].validate(df_manifest.transpose())

    # manifestファイルにBulkで記載あがるファイル名のリストを返す absentも同様
    # prefixのfile.も除く
    bulk_file_name_list = [s.replace('file.','') for s in  df_manifest[df_manifest['value']=='bulk'].index.to_list()]
    absent_file_name_list = [s.replace('file.','') for s in  df_manifest[df_manifest['value']=='absent'].index.to_list()]
    # XX->XX.csvにする
    bulk_file_list = [s + '.csv' for s in bulk_file_name_list]
    absent_file_list = [s + '.csv' for s in absent_file_name_list]

    # manifestファイルでのBulk記載のCSVファイルの有無チェック
    validate_file_set(oneroster_file,bulk_file_list,absent_file_list)
    
    # CSVファイルのフォーマットのチェック
    bulk_dataframe_list = validate_csv_format(oneroster_file,bulk_file_name_list)

    # Reference系のチェック
    validate_csv_reference_format(bulk_dataframe_list)

    # その他仕様のチェック 並び順, 禁則,組み合わせ条件など
    validate_other_rules(bulk_dataframe_list)

  # 以下バリデーションで投げられた例外を元にエラー処理
  except OneRosterManifestError as e:
    code = e.args[0]
    result = makeErrorResult(code)
  except OneRosterFileSetError as e:
    result = makeErrorResult(e.code, e.message)
  except UnicodeDecodeError as e:
    result = makeErrorResult('ib1101')
  except Exception as e:
    # NOTE:いろんな例外がくる中で、pandera.checkで出てきた「OneRosterErrorCode」を拾う
    # pandera.checkのExceptionをカスタムにできないけど、errorの指定で文字列カスタムできるのでそれをキャッチ
    tmp_str = e.args[0]
    tmp_index = tmp_str.find('OneRosterErrorCode') if type(tmp_str) is str else False
    if tmp_index > -1:
      code = e.args[0][tmp_index+19:tmp_index+25]#OneRosterErrorCode:(19)ibXXXX(25)
      result = makeErrorResult(code)

    # NOTE:Field headerが無い系のエラーを拾うところ
    # pandera checkでColumnsが無い系はカスタムエラー飛ばせないので無理矢理ここで拾う
    elif bool(re.fullmatch(r_colum_lack,tmp_str.replace('\n','').replace(' ',''))):
      result = makeErrorResult('ib9002', target_file_name + 'ファイルに' + tmp_str[tmp_str.find('column \'')+8:tmp_str.find('\' not in dataframe')])
    else:
      code = 'ib9999'
      result = makeErrorResult(code)
      print(target_file_name)
      print('不明なエラー:')
      print(e)

  if result['is_success']:
    print('\033[32m'+'Invalid case validate is pass'+'\033[0m')
  return result

def read_manifest_to_df(oneroster_file):
  with zipfile.ZipFile(oneroster_file, 'r') as zf_or:
    filelists = zf_or.namelist()
    manifest_filename = 'manifest.csv'
    if manifest_filename not in filelists:
      raise OneRosterManifestError('ib9001')
    return pd.read_csv(zf_or.open(manifest_filename), index_col=0)

def validate_file_set(oneroster_file,bulk_file_list,absent_file_list):
  with zipfile.ZipFile(oneroster_file, 'r') as zf_or:
    filelists = zf_or.namelist()
    for bulk_file in bulk_file_list:
      if bulk_file not in filelists:
        raise OneRosterFileSetError('ib9008',bulk_file)
    for absent_file in absent_file_list:
      if absent_file in filelists:
        raise OneRosterFileSetError('ib9007',absent_file)

def validate_csv_format(oneroster_file,bulk_file_name_list):
  bulk_dataframe_list = {}
  with zipfile.ZipFile(oneroster_file, 'r') as zf_or:
    for bulk_file_name in bulk_file_name_list:
      global target_file_name
      target_file_name = bulk_file_name
      # 空文字で埋める Bulk CSVという仮定のもとすべて文字列に
      df_target = pd.read_csv(zf_or.open(bulk_file_name+'.csv'), dtype='str').fillna('')
      oneroster_csv_schema.df_schema[bulk_file_name].validate(df_target)
      bulk_dataframe_list[target_file_name] = df_target
    return bulk_dataframe_list

def validate_csv_reference_format(bulk_dataframe_list):
  for bulk_file_name in bulk_dataframe_list.keys():
    oneroster_csv_schema.ref_validate[bulk_file_name](bulk_dataframe_list)

def validate_other_rules(bulk_dataframe_list):
  for bulk_file_name in bulk_dataframe_list.keys():
    oneroster_csv_schema.order_rules[bulk_file_name](bulk_dataframe_list[bulk_file_name])
    oneroster_csv_schema.other_rules[bulk_file_name](bulk_dataframe_list)