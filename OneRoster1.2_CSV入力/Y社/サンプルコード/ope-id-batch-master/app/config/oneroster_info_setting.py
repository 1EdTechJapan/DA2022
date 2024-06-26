# coding: utf-8
# 　新規追加
"""
onerosterみバッチ用情報
"""
# Dummyのパスワード（登録用）
DUMMY_PASSWORD = "123456Aa"

# 組変換ルール
class_code_convert_rule = {
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "A": "9",
    "B": "10",
    "い": "11",
    "ろ": "12",
    "は": "13",
    "ひかり": "14",
    "ゆめ": "15",
    "あい": "16",
    "にじ": "17",
    "未来": "18",
    "空": "19",
    "星": "20",
    "風": "21",
    "緑": "22",
    "太陽": "23",
    "大地": "24",
    "99": "99",
    "１年１組": "101",
    "１年２組": "102",
    "１年３組": "103",
    "１年４組": "104",
    "１年５組": "105",
    "１年６組": "106",
    "１年７組": "107",
    "１年８組": "108",
    "１年９組": "109",
    "１年１０組": "110",
    "１年１１組": "111",
    "１年１２組": "112",
    "１年１３組": "113",
    "１年１４組": "114",
    "１年１５組": "115",
    "１年１６組": "116",
    "１年１７組": "117",
    "１年１８組": "118",
    "１年１９組": "119",
    "１年２０組": "120",
    "１年A組": "101",
    "Chem101-Mr Rogers": "101",
}

# 権限変換ルール
role_convert_rule = {
    "student": "student",
    "teacher": "teacher",
    "principal": "teacher",
    "districtAdministrator": "admin",
    "siteAdministrator": "operator",
    "systemAdministrator": "admin"
}

