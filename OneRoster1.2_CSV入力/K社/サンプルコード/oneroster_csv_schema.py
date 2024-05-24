import pandera as pa
import utils_for_pandera_check as pc_utils
'''
OneRoster仕様の参照元 https://www.imsglobal.org/spec/oneroster/v1p2/bind/csv/#csv-format
panderaのcheck の参考 https://pandera.readthedocs.io/en/stable/reference/generated/pandera.checks.Check.html
NOTE:Checkの中は期待値 期待値から外れるとエラーとなる
'''

# ファイル単体のスキームを定義し、バリデーション時に"check"パラメータ内のチェックが入る
df_schema = {
    'manifest': pa.DataFrameSchema({
        'manifest.version' : pa.Column(str,checks=[pa.Check.equal_to(['1.0'],error='OneRosterErrorCode:ib9003')]),
        'oneroster.version' : pa.Column(str,checks=[pa.Check.equal_to(['1.2'],error='OneRosterErrorCode:ib9006')]),
        'file.academicSessions' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.categories' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.classResources' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.classes' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.courseResources' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.courses' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.demographics' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.enrollments' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.lineItemLearningObjectiveIds' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.lineItemScoreScales' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.lineItems' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.orgs' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.resources' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.resultLearningObjectiveIds' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.resultScoreScales' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.results' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.roles' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.scoreScales' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.userProfiles' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.userResources' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'file.users' : pa.Column(str,checks=[pa.Check.isin(['absent','bulk','delta'],error='OneRosterErrorCode:ib9009')]),
        'source.systemName' : pa.Column(str),
        'source.systemCode' : pa.Column(str),
    }),
    'academicSessions': pa.DataFrameSchema({
        'sourcedId': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0009'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1061')
            ]),
        'status': pa.Column(str, checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1001')]),
        'dateLastModified': pa.Column(str, checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1002')]),
        'title': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0010'),
            pc_utils.is_JP_profile_FY_pc(errorString = 'OneRosterErrorCode:ib1062')
            ]),
        'type': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0011'),
            pa.Check.isin(['schoolYear'],error='OneRosterErrorCode:ib1003')
            # pa.Check.isin(['gradingPeriod','semester','schoolYear','term'],error='OneRosterErrorCode:ib1003')
            ]),
        'startDate': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0012'),
            pc_utils.is_ISO_timeformat_pc(errorString = 'OneRosterErrorCode:ib1004')
            ]),
        'endDate': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0013'),
            pc_utils.is_ISO_timeformat_pc(errorString = 'OneRosterErrorCode:ib1005')
            ]),
        'parentSourcedId': pa.Column(str),
        'schoolYear': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0014'),
            pc_utils.is_YYYY_format_pc(errorString= 'OneRosterErrorCode:ib1006')
            ])
    }),
    'classes': pa.DataFrameSchema({
        'sourcedId': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0015'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1063')
            ]),
        'status': pa.Column(str, checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1007')]),
        'dateLastModified': pa.Column(str, checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1008')]),
        'title': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0016'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1064')
            ]),
        'grades': pa.Column(str, checks=[pc_utils.is_in_APPLIC_GRADES_W_NONE_list_pc('OneRosterErrorCode:ib1065')]),
        'courseSourcedId': pa.Column(str, checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0017')]),
        'classCode': pa.Column(str, checks=[]),
        'classType': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0018'),
            pa.Check.isin(['homeroom','scheduled'],error='OneRosterErrorCode:ib1009')
            ]),
        'location': pa.Column(str, checks=[pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1066')]),
        'schoolSourcedId': pa.Column(str, checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0019')]),
        'termSourcedIds': pa.Column(str, checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0020')]),
        'subjects': pa.Column(str, checks=[]),
        'subjectCodes': pa.Column(str, checks=[pc_utils.is_in_APPLIC_SUBJECTS_W_NONE_list_pc(errorString='OneRosterErrorCode:ib1068')]),
        'periods': pa.Column(str, checks=[]),
        'metadata.jp.specialNeeds': pa.Column(str, checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1067')]),
    }),
    'courses': pa.DataFrameSchema({
        'sourcedId':pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0021'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1070')
            ]),
        'status':pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1010')]),
        'dateLastModified':pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1011')]),
        'schoolYearSourcedId':pa.Column(str,checks=[]),
        'title':pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0022'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1077'),
            pc_utils.is_JP_profile_course_title_pc(errorString = 'OneRosterErrorCode:ib1078')
            ]),
        'courseCode':pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1080')]),
        'grades':pa.Column(str,checks=[pa.Check.isin(pc_utils.APPLIC_GRADES_W_NONE,error='OneRosterErrorCode:ib1079')]),
        'orgSourcedId':pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0054')]),
        'subjects':pa.Column(str,checks=[]),
        'subjectCodes':pa.Column(str,checks=[pc_utils.is_in_APPLIC_SUBJECTS_W_NONE_list_pc(errorString='OneRosterErrorCode:ib1069')]),
    }),
    'demographics': pa.DataFrameSchema({
        'sourcedId': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0023')]),
        'status': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1012')]),
        'dateLastModified': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1013')]),
        'birthDate': pa.Column(str,checks=[pc_utils.is_ISO_timeformat_option_pc(errorString = 'OneRosterErrorCode:ib1014')]),
        'sex': pa.Column(str,checks=[pa.Check.isin(['','male','female','unspecified','other'],error='OneRosterErrorCode:ib1015')]),
        'americanIndianOrAlaskaNative': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1016')]),
        'asian': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1017')]),
        'blackOrAfricanAmerican': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1018')]),
        'nativeHawaiianOrOtherPacificIslander': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1019')]),
        'white': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1020')]),
        'demographicRaceTwoOrMoreRaces': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1021')]),
        'hispanicOrLatinoEthnicity': pa.Column(str,checks=[pa.Check.isin(['','true','false'],error='OneRosterErrorCode:ib1022')]),
        'countryOfBirthCode': pa.Column(str,checks=[]),
        'stateOfBirthAbbreviation': pa.Column(str,checks=[]),
        'cityOfBirth': pa.Column(str,checks=[]),
        'publicSchoolResidenceStatus': pa.Column(str,checks=[]),
    }),
    'enrollments': pa.DataFrameSchema({
        'sourcedId': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0024'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1071')
            ]),
        'status': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1023')]),
        'dateLastModified': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1024')]),
        'classSourcedId': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0025')]),
        'schoolSourcedId': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0026')]),
        'userSourcedId': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0027')]),
        'role': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0028'),
            pa.Check.isin(['administrator','proctor','student','teacher'],error='OneRosterErrorCode:ib1025')
            ]),
        'primary': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0048'),
            pa.Check.isin(['true','false'],error='OneRosterErrorCode:ib1026')
            ]),
        'beginDate': pa.Column(str,checks=[pc_utils.is_ISO_timeformat_option_pc(errorString = 'OneRosterErrorCode:ib1027')]),
        'endDate': pa.Column(str,checks=[pc_utils.is_ISO_timeformat_option_pc(errorString = 'OneRosterErrorCode:ib1028')]),
    }),
    'users': pa.DataFrameSchema({
        'sourcedId': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0029'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1072')
            ]),
        'status': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1029')]),
        'dateLastModified': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1030')]),
        'enabledUser': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0030'),
            pa.Check.isin(['true','false'],error='OneRosterErrorCode:ib1031')
            ]),
        'username': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0031')]),
        'userIds': pa.Column(str,checks=[pc_utils.is_correct_userIds_list_option_list(errorString = 'OneRosterErrorCode:ib1032')]),
        'givenName': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0032'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1083')
            ]),
        'familyName': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0033'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1084')
            ]),
        'middleName': pa.Column(str,checks=[pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1085')]),
        'identifier': pa.Column(str,checks=[]),
        'email': pa.Column(str,checks=[]),
        'sms': pa.Column(str,checks=[]),
        'phone': pa.Column(str,checks=[]),
        'agentSourcedIds': pa.Column(str,checks=[]),
        'grades': pa.Column(str,checks=[pa.Check.isin(pc_utils.APPLIC_GRADES_W_NONE,error='OneRosterErrorCode:ib1092')]),
        'password': pa.Column(str,checks=[]),
        'userMasterIdentifier': pa.Column(str,checks=[pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1073')]),# eポタ標準仕様でrequired 学習eポータルUUIDを使用する とあるけど現実UUIDの発行者やフローとか固まっていないし入ってこないかも デジ庁テストケースにもないから一旦Pass
        'resourceSourcedIds': pa.Column(str,checks=[]),
        'preferredGivenName': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0049'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1086')
            ]),
        'preferredFamilyName': pa.Column(str,checks=[
                pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0050'),
                pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1087')
                ]),
        'preferredMiddleName': pa.Column(str,checks=[pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1088')]),
        'primaryOrgSourcedId': pa.Column(str,checks=[]),
        'pronouns': pa.Column(str,checks=[]),
        'metadata.jp.kanaGivenName': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0051'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1089')
            ]),
        'metadata.jp.kanaFamilyName': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0052'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1090')
            ]),
        'metadata.jp.kanaMiddleName': pa.Column(str,checks=[pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1091')]),
        'metadata.jp.homeClass': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0053')]),
    }),
    'orgs': pa.DataFrameSchema({
        'sourcedId': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0034'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1074')
            ]),
        'status': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1033')]),
        'dateLastModified': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1034')]),
        'name': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0035'),
            pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1090')
            ]),
        'type': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0036'),
            pa.Check.isin(['department','school','district','local','state','national'],error='OneRosterErrorCode:ib1035')
            ]),
        'identifier': pa.Column(str),
        'parentSourcedId': pa.Column(str,checks=[]),
        }),
    'roles': pa.DataFrameSchema({
        'sourcedId': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0037'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1075')
            ]),
        'status': pa.Column(str, checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1036')]),
        'dateLastModified': pa.Column(str, checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1037')]),
        'userSourcedId': pa.Column(str, checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0038')]),
        'roleType': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0039'),
            pa.Check.isin(['primary','secondary'],error='OneRosterErrorCode:ib1038')
            ]),
        'role': pa.Column(str, checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0040'),
            pa.Check.isin(['districtAdministrator','guardian','principal','siteAdministrator','student','teacher'],error='OneRosterErrorCode:ib1039')
            # pa.Check.isin(['aide','counselor','districtAdministrator','guardian','parent','principal','proctor','relative','siteAdministrator','student','systemAdministrator','teacher'],error='OneRosterErrorCode:ib1039')
            ]),
        'beginDate': pa.Column(str, checks=[pc_utils.is_ISO_timeformat_option_pc(errorString = 'OneRosterErrorCode:ib1040')]),
        'endDate': pa.Column(str, checks=[pc_utils.is_ISO_timeformat_option_pc(errorString = 'OneRosterErrorCode:ib1041')]),
        'orgSourcedId': pa.Column(str, checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0041')]),
        'userProfileSourcedId': pa.Column(str, checks=[]),
        }),
    'userProfiles': pa.DataFrameSchema({
        'sourcedId': pa.Column(str,checks=[
            pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0042'),
            pc_utils.is_uuid_v4_pc(errorString = 'OneRosterErrorCode:ib1076')
            ]),
        'status': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1042')]),
        'dateLastModified': pa.Column(str,checks=[pc_utils.is_missing_pc(errorString = 'OneRosterErrorCode:ib1043')]),
        'userSourcedId': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0043')]),
        'profileType': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0044')]),
        'vendorId': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0045')]),
        'applicationId': pa.Column(str,checks=[]),
        'description': pa.Column(str,checks=[pc_utils.is_not_include_half_katakana_pc(errorString = 'OneRosterErrorCode:ib1100')]),
        'credentialType': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0046')]),
        'username': pa.Column(str,checks=[pc_utils.is_exists_pc(errorString = 'OneRosterErrorCode:ib0047')]),
        'password': pa.Column(str,checks=[]),
        }),
}

def validate_academicSessions_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs['sourcedId'].unique().tolist()
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    orgs_sourceIds.append('')# Not Requiredなので空文字込み
    check_ref_schema = pa.DataFrameSchema({
        'parentSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1044')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['academicSessions'])

def validate_classes_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_courses = bulk_dataframe_list['courses']
    courses_sourceIds = df_courses['sourcedId'].unique().tolist()
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs.query('type == "school"')['sourcedId'].unique().tolist()
    df_academicSessions = bulk_dataframe_list['academicSessions']
    # MEMO:ここtype == term で絞る方が正しそう 仕様に明確に書いてないけど
    academicSessions_sourceIds = df_academicSessions['sourcedId'].unique().tolist()
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'courseSourcedId': pa.Column(str,checks=[pa.Check.isin(courses_sourceIds,error='OneRosterErrorCode:ib1045')]),
        'schoolSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1046')]),
        'termSourcedIds': pa.Column(str,checks=[pa.Check.isin(academicSessions_sourceIds,error='OneRosterErrorCode:ib1047')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['classes'])
    
def validate_courses_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs['sourcedId'].unique().tolist()
    df_academicSessions = bulk_dataframe_list['academicSessions']
    academicSessions_sourceIds = df_academicSessions.query('type == schoolYear')['sourcedId'].unique().tolist()
    academicSessions_sourceIds.append('')# Not Requiredなので空文字込み
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'orgSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1048')]),
        'schoolYearSourcedId': pa.Column(str,checks=[pa.Check.isin(academicSessions_sourceIds,error='OneRosterErrorCode:ib1049')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['courses'])

def validate_enrollments_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_classes = bulk_dataframe_list['classes']
    classes_sourceIds = df_classes['sourcedId'].unique().tolist()
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs.query('type == "school"')['sourcedId'].unique().tolist()
    df_users = bulk_dataframe_list['users']
    users_sourceIds = df_users['sourcedId'].unique().tolist()
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'classSourcedId': pa.Column(str,checks=[pa.Check.isin(classes_sourceIds,error='OneRosterErrorCode:ib1050')]),
        'schoolSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1051')]),
        'userSourcedId': pa.Column(str,checks=[pa.Check.isin(users_sourceIds,error='OneRosterErrorCode:ib1052')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['enrollments'])

def validate_users_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs['sourcedId'].unique().tolist()
    if bool(bulk_dataframe_list.get('resources')):
        df_resources = bulk_dataframe_list['resources']
        resources_sourceIds = df_resources['sourcedId'].unique().tolist()
    else:
        resources_sourceIds = ['']
    df_users = bulk_dataframe_list['users']
    users_sourceIds = df_users['sourcedId'].unique().tolist()
    df_classes = bulk_dataframe_list['classes']
    classes_sourceIds = df_classes['sourcedId'].unique().tolist()
    orgs_sourceIds.append('')# Not Requiredなので空文字込み
    users_sourceIds.append('')# Not Requiredなので空文字込み
    resources_sourceIds.append('')# Not Requiredなので空文字込み
    classes_sourceIds.append('')# Not Requiredなので空文字込み
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'agentSourcedIds': pa.Column(str,checks=[pa.Check.isin(users_sourceIds,error='OneRosterErrorCode:ib1053')]),
        'resourceSourcedIds': pa.Column(str,checks=[pa.Check.isin(resources_sourceIds,error='OneRosterErrorCode:ib1054')]),
        'primaryOrgSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1055')]),
        'metadata.jp.homeClass': pa.Column(str,checks=[pa.Check.isin(classes_sourceIds,error='OneRosterErrorCode:ib1094')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['users'])
    
def validate_orgs_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs['sourcedId'].unique().tolist()
    orgs_sourceIds.append('')# Not Requiredなので空文字込み
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'parentSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1056')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['orgs'])
    
def validate_roles_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_orgs = bulk_dataframe_list['orgs']
    orgs_sourceIds = df_orgs['sourcedId'].unique().tolist()
    df_users = bulk_dataframe_list['users']
    users_sourceIds = df_users['sourcedId'].unique().tolist()
    # userProfilesはabsentが想定されているため
    # TODO:改善 特別対応ではなくて、プロセス的に対応できるように
    if 'userProfiles' in bulk_dataframe_list.keys():
        df_userProfiles = bulk_dataframe_list['userProfiles']
        userProfiles_sourceIds = df_userProfiles['sourcedId'].unique().tolist()
        userProfiles_sourceIds.append('')# Not Requiredなので空文字込み
    else:
        userProfiles_sourceIds = ['']# userProfilesがないので参照なし状態を正
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'userSourcedId': pa.Column(str,checks=[pa.Check.isin(users_sourceIds,error='OneRosterErrorCode:ib1057')]),
        'userProfileSourcedId': pa.Column(str,checks=[pa.Check.isin(userProfiles_sourceIds,error='OneRosterErrorCode:ib1058')]),
        'orgSourcedId': pa.Column(str,checks=[pa.Check.isin(orgs_sourceIds,error='OneRosterErrorCode:ib1059')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['roles'])
    
def validate_userProfiles_ref(bulk_dataframe_list):
    # 参照先dataframeからユニークなIDリストを取ってくる
    df_users = bulk_dataframe_list['users']
    users_sourceIds = df_users['sourcedId'].unique().tolist()
    # pa.DataFrameSchemaで該当Colだけisinでチェック
    check_ref_schema = pa.DataFrameSchema({
        'userSourcedId': pa.Column(str,checks=[pa.Check.isin(users_sourceIds,error='OneRosterErrorCode:ib1060')]),
    })
    check_ref_schema.validate(bulk_dataframe_list['userProfiles'])
    
def validate_demographics_ref(bulk_dataframe_list):
    # userProfilesはabsentが想定されているため
    # TODO:改善 特別対応ではなくて、プロセス的に対応できるように
    if 'demographics' in bulk_dataframe_list.keys():
        # 参照先dataframeからユニークなIDリストを取ってくる
        df_users = bulk_dataframe_list['users']
        users_sourceIds = df_users['sourcedId'].unique().tolist()
        # pa.DataFrameSchemaで該当Colだけisinでチェック
        check_ref_schema = pa.DataFrameSchema({
            'sourcedId': pa.Column(str,checks=[pa.Check.isin(users_sourceIds,error='OneRosterErrorCode:ib1081')]),
        })
        check_ref_schema.validate(bulk_dataframe_list['demographics'])

# その他のルール系 組み合わせ等々
def validate_users_other_rules(bulk_dataframe_list):
    df_users = bulk_dataframe_list['users']
    if df_users['userMasterIdentifier'].nunique() != len(df_users):
        raise Exception('OneRosterErrorCode:ib1093')

def validate_enrollments_other_rules(bulk_dataframe_list):
    df_enrollment = bulk_dataframe_list['enrollments']
    for index, row in df_enrollment.iterrows():
        if row['role'] == 'student' and row['primary'] == 'true':
            raise Exception('OneRosterErrorCode:ib1082')

def validate_orgs_other_rules(bulk_dataframe_list):
    df_orgs = bulk_dataframe_list['orgs']
    for index, row in df_orgs.iterrows():
        # 教育委員会なのに親組織がいるケースはJP Profile v1.2では未考慮&弾く
        if row['type'] == 'district':
            if row['parentSourcedId'] != '':
                raise Exception('OneRosterErrorCode:ib1095')
            if not pc_utils.is_mext_kyouikuiinkai_code_option(row['identifier']):
                raise Exception('OneRosterErrorCode:ib1102')
        if row['type'] == 'school':
            if not pc_utils.is_mext_school_code_option(row['identifier']):
                raise Exception('OneRosterErrorCode:ib1098')

def validate_roles_other_rules(bulk_dataframe_list):
    df_roles = bulk_dataframe_list['roles']
    primary_sourcedIds = df_roles.query('roleType == "primary"')['userSourcedId'].unique().tolist()
    secondary_sourcedIds = df_roles.query('roleType == "secondary"')['userSourcedId'].unique().tolist()
    # 十分条件として、A＆Bの個数とB単体の個数が同じ時にA->BでOK 違う数でNG
    if not(len( set(primary_sourcedIds)&set(secondary_sourcedIds) ) == len(secondary_sourcedIds)):
        raise Exception('OneRosterErrorCode:ib1099')

# ヘッダー順
ACADEMICSESSIONS_HEADERS = ['sourcedId','status','dateLastModified','title','type','startDate','endDate','parentSourcedId','schoolYear']
CLASSS_HEADERS = ['sourcedId','status','dateLastModified','title','grades','courseSourcedId','classCode','classType','location','schoolSourcedId','termSourcedIds','subjects','subjectCodes','periods','metadata.jp.specialNeeds']
COURSES_HEADERS = ['sourcedId','status','dateLastModified','schoolYearSourcedId','title','courseCode','grades','orgSourcedId','subjects','subjectCodes']
DEMOGRAPHICS_HEADERS = ['sourcedId','status','dateLastModified','birthDate','sex','americanIndianOrAlaskaNative','asian','blackOrAfricanAmerican','nativeHawaiianOrOtherPacificIslander','white','demographicRaceTwoOrMoreRaces','hispanicOrLatinoEthnicity','countryOfBirthCode','stateOfBirthAbbreviation','cityOfBirth','publicSchoolResidenceStatus']
ENROLLMENTS_HEADERS = ['sourcedId','status','dateLastModified','classSourcedId','schoolSourcedId','userSourcedId','role','primary','beginDate','endDate', 'metadata.jp.ShussekiNo', 'metadata.jp.PublicFlg']
USERS_HEADERS = ['sourcedId','status','dateLastModified','enabledUser','username','userIds','givenName','familyName','middleName','identifier','email','sms','phone','agentSourcedIds','grades','password','userMasterIdentifier','resourceSourcedIds','preferredGivenName','preferredMiddleName','preferredFamilyName','primaryOrgSourcedId','pronouns','metadata.jp.kanaGivenName','metadata.jp.kanaFamilyName','metadata.jp.kanaMiddleName','metadata.jp.homeClass']
ORGS_HEADERS = ['sourcedId','status','dateLastModified','name','type','identifier','parentSourcedId']
ROLES_HEADERS = ['sourcedId','status','dateLastModified','userSourcedId','roleType','role','beginDate','endDate','orgSourcedId','userProfileSourcedId']
USERPROFILES_HEADERS = ['sourcedId','status','dateLastModified','userSourcedId','profileType','vendorId','applicationId','description','credentialType','username','password']

def validate_academicSessions_order_rules(df_academicSessions):
    heders = df_academicSessions.columns.tolist()
    if heders != ACADEMICSESSIONS_HEADERS:
        raise Exception('OneRosterErrorCode:ib2000')
def validate_classes_order_rules(df_classes):
    heders = df_classes.columns.tolist()
    if heders != CLASSS_HEADERS:
        raise Exception('OneRosterErrorCode:ib2001')
def validate_courses_order_rules(df_courses):
    heders = df_courses.columns.tolist()
    if heders != COURSES_HEADERS:
        raise Exception('OneRosterErrorCode:ib2002')
def validate_demographics_order_rules(df_demographics):
    heders = df_demographics.columns.tolist()
    if heders != DEMOGRAPHICS_HEADERS:
        raise Exception('OneRosterErrorCode:ib2003')
def validate_enrollments_order_rules(df_enrollments):
    heders = df_enrollments.columns.tolist()
    if heders != ENROLLMENTS_HEADERS:
        raise Exception('OneRosterErrorCode:ib2004')
def validate_users_order_rules(df_users):
    heders = df_users.columns.tolist()
    if heders != USERS_HEADERS:
        raise Exception('OneRosterErrorCode:ib2005')
def validate_orgs_order_rules(df_orgs):
    heders = df_orgs.columns.tolist()
    if heders != ORGS_HEADERS:
        raise Exception('OneRosterErrorCode:ib2006')
def validate_roles_order_rules(df_roles):
    heders = df_roles.columns.tolist()
    if heders != ROLES_HEADERS:
        raise Exception('OneRosterErrorCode:ib2007')
def validate_userProfiles_order_rules(df_userProfiles):
    heders = df_userProfiles.columns.tolist()
    if heders != USERPROFILES_HEADERS:
        raise Exception('OneRosterErrorCode:ib2008')

def pass_func(bulk_dataframe_list):
    pass
ref_validate = {
    'academicSessions': validate_academicSessions_ref,
    'classes': validate_classes_ref,
    'courses': validate_courses_ref,
    'enrollments': validate_enrollments_ref,
    'users': validate_users_ref,
    'orgs': validate_orgs_ref,
    'roles': validate_roles_ref,
    'userProfiles': validate_userProfiles_ref,    
    'demographics': validate_demographics_ref,    
}

order_rules = {
    'academicSessions': validate_academicSessions_order_rules,
    'classes': validate_classes_order_rules,
    'courses': validate_courses_order_rules,
    'enrollments': validate_enrollments_order_rules,
    'users': validate_users_order_rules,
    'orgs': validate_orgs_order_rules,
    'roles': validate_roles_order_rules,
    'userProfiles': validate_userProfiles_order_rules,    
    'demographics': validate_demographics_order_rules,    
}

other_rules = {
    # TODO:一部float方であるかのチェックしていない
    # TODO:startDate,endDateのInclusive,Exclusive系のチェックもしていない
    'academicSessions': pass_func,
    'classes': pass_func,
    'courses': pass_func,
    'enrollments': validate_enrollments_other_rules,
    'users': validate_users_other_rules,
    'orgs': validate_orgs_other_rules,
    'roles': validate_roles_other_rules,
    'userProfiles': pass_func,    
    'demographics': pass_func,    
}
