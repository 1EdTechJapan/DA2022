# coding: utf-8
"""
CSV一括登録データの列定義、データ型定義
"""
# CSVの列情報
column = {
    "student_bulk_update": [
        "persistent_uid",
        "new_class_code",
        "new_student_number"
    ],
    "student_bulk_transfer": [
        "persistent_uid",
        "new_school_code",
        "new_class_code",
        "new_student_number"
    ],
    "student_bulk_insert": [
        # "organization_code",
        "fiscal_year",
        "user_id",
        "persistent_uid",
        "sur_name",
        "given_name",
        "sur_name_kana",
        "given_name_kana",
        "password",
        "gender",
        "mail",
        "grade_code",
        "class_code",
        "student_number",
        "relationgg",
        "relationwin"
    ],
}
# CSVのヘッダ情報
header = {
    "student_bulk_update": [
        "自治体ユニークID",
        "変更後の組コード",
        "変更後の出席番号",
    ],
    "student_bulk_transfer": [
        "自治体ユニークID",
        "異動後の中学校コード",
        "変更後の組コード",
        "変更後の出席番号",
    ],
    "student_bulk_insert": [
        # "学校コード",
        "有効年度",
        "ユーザID",
        "自治体内ユニークID",
        "姓",
        "名",
        "姓(ふりがな)",
        "名(ふりがな)",
        "パスワード",
        "性別",
        "メールアドレス",
        "学年コード",
        "組コード",
        "出席番号",
        "Googleアカウント作成有無",
        "AzureADアカウント作成有無",
    ],
}
# 数字として扱うルール
numeric_rules = {
    "student_bulk_update": ["class_code", "relationgg", "relationwin", "fiscal_year"],
    "student_bulk_transfer": ["class_code", "relationgg", "relationwin", "fiscal_year"],
    "student_bulk_insert": ["gender", "fiscal_year", "student_number", "relationgg", "relationwin"],
}
# 配列として扱うルール
list_splitter = ","
list_rules = {
    "student_bulk_update": ["title_code", "additional_post_code", "subject_code"],
    "student_bulk_transfer": ["title_code", "additional_post_code", "subject_code"],
    "student_bulk_insert": [],
}

# 学校コード+1への変換ルール
GRADE_CODE_CONVERT_RULE = {
    "P1": "P2",
    "P2": "P3",
    "P3": "P4",
    "P4": "P5",
    "P5": "P6",
    "P6": "J1",
    "J1": "J2",
    "J2": "J3",
}

LDAP_SEARCH_ATTRIBUTES = [
        "organization_name",
        "organization_name_ja",
        "organization_type",
        "organization_code",
        "user_id",
        "opaque_id",
        "mextUid",
        "persistent_uid",
        "sur_name",
        "given_name",
        "sur_name_kana",
        "given_name_kana",
        "display_name",
        "mail",
        "person_affiliation_code",
        "title_code",
        "role",
        "additional_post_code",
        "subject_code",
        "grade_code",
        "grade_name",
        "class_code",
        "class_name",
        "password_flg",
        "reg_date",
        "upd_date",
        "student_number",
        "gender",
        "relationgg",
        "relationwin",
        "befrelationwin",
        "fiscal_year",
        "mextOuCode",
    ]


# 操作内容(申込情報)
OPERATION_TYPE = {
    "admin01": "OPE管理者登録",
    "admin02": "OPE管理者更新",
    "admin03": "OPE管理者削除",
	# ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    "admin11": "OPE管理者登録(一括)",
    "admin12": "OPE管理者更新(一括)",
    "admin13": "OPE管理者削除(一括)",
	# ↑ここまで
    "teacher01": "教員登録(個別)",
    "teacher02": "教員更新(個別)",
    "teacher03": "教員削除(個別)",
    "teacher04": "教員再登録(個別)",
    "teacher05": "教員異動",
    "teacher11": "教員登録(一括)",
    "teacher12": "教員更新(一括)",
    "teacher13": "教員削除(一括)",
    "teacher14": "教員異動(一括)",
    "teacher15": "教員登録(一括)大阪市バッチ専用",
    "teacher16": "教員更新(一括)大阪市バッチ専用",
    "student01": "児童・生徒登録(個別)",
    "student02": "児童・生徒更新(個別)",
    "student03": "児童・生徒削除(個別)",
    "student04": "児童・生徒再登録(個別)",
    "student05": "児童・生徒転入・転出",
    "student11": "児童・生徒登録(一括)",
    "student12": "児童・生徒進級",
    "student13": "児童・生徒削除(一括)",
    "student14": "児童・生徒進学",
    "school11": "学校一括登録",
    "autog11": "自動払い出し"
}
# ステータス(申込情報)
OPERATION_STATUS = {
    "1": "申込中",
    "2": "処理中",
    "3": "完了",
    "4": "処理失敗",
    "7": "完了（通知成功)",
    "8": "完了（通知失敗)",
    "9": "エラー"
}