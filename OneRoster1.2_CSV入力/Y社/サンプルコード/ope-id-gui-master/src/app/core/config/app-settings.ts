import { environment } from '../../../environments/environment';

/** システム定数クラス */
export namespace AppSetings {
  export const eop_core_url = environment.base_url + "/V2/eopacs.json";
  export const ecp_session_url = environment.ecp_session_base_url;
  export const opeadmin = {
    // OPE管理者情報取得APIのURLのリソースID
    list_resource_id: '50001',
    // OPE管理者情報登録受付PIのリソースID
    create_resource_id: '50002',
    // OPE管理者情報更新受付APIのリソースID
    update_resource_id: '50003',
    // OPE管理者情報削除受付APIのリソースID
    delete_resource_id: '50005',
    // OPE管理者パスワード更新APIのリソースID
    password_update_resource_id: '50004'
  }
  export const teacher = {
    // 教員報検索APIのURLのリソースID
    list_resource_id: '50010',
    // 教員報登録受付APIのリソースID
    create_resource_id: '50011',
    // 教員報更新受付APIのリソースID
    update_resource_id: '50012',
    // 教員削除受付APIのリソースID
    delete_resource_id: '50013',
    // 教員再登録ユーザ受付APIのリソースID
    delete_list_resource_id: '50015',
    // 教員再登録受付APIのリソースID
    recreate_resource_id: '50016',
    // 教員一括登録受付APIのリソースID
    bulk_create_resource_id: '50052',
    // 教員一括更新受付APIのリソースID
    bulk_update_resource_id: '50057',
    // 　新規追加（教員一括削除追加）　START
    // 教員一括削除受付APIのリソースID
    bulk_delete_resource_id: '50058',
    // 　新規追加（教員一括削除追加）　END
    // 　新規追加（教員一括異動追加）　START
    // 教員一括異動受付APIのリソースID 
    bulk_transfer_resource_id: '50059',
    // 　新規追加（教員一括異動追加）　END
    // 教員転入・転出受付APIのリソースID
    transfer_resource_id: '50012',
  }
  export const student = {
    // 児童・生徒検索APIのURLのリソースID
    list_resource_id: '50020',
    // 児童・生徒登録受付APIのリソースID
    create_resource_id: '50021',
    // 児童・生徒更新受付APIのリソースID
    update_resource_id: '50022',
    // 児童・生徒削除受付APIのリソースID
    delete_resource_id: '50023',
    // 児童・生徒一括登録受付APIのリソースID
    bulk_create_resource_id: '50050',
    // 児童・生徒進級受付APIのリソースID
    bulk_update_resource_id: '50053',
    // 児童・生徒無効ユーザ検索APIのリソースID
    delete_list_resource_id: '50026',
    // 児童・生徒再登録受付APIのリソースID
    recreate_resource_id: '50027',
    // 児童・生徒転入・転出受付APIのリソースID
    transfer_resource_id: '50022',
    // 児童・生徒進学受付のAPIのリソースID
    bulk_transfer_resource_id: '50056',
    // 児童・生徒一括削除受付APIのリソースID
    bulk_delete_resource_id: '50054',
  }
  export const master = {
    // マスター参照APIのURLのリソースID
    list_resource_id: '50014',
  }
  export const school = {
    // 学校検索APIのURLのリソースID
    list_resource_id: '50030',
    // 学校登録APIのURLのリソースID
    create_resource_id: '50031',
    // 学校更新APIのURLのリソースID
    update_resource_id: '50032',
    // 学校削除APIのURLのリソースID
    delete_resource_id: '50033',
    // 学校一括登録受付APIのリソースID
    bulk_create_resource_id: '50051'
  }
  export const grade = {
    // 学年検索APIのURLのリソースID
    list_resource_id: '50035',
    // 学年登録APIのURLのリソースID
    create_resource_id: '50036',
    // 学年更新APIのURLのリソースID
    update_resource_id: '50037',
    // 学年削除APIのURLのリソースID
    delete_resource_id: '50038'
  }
  export const kumi = {
    // 組検索APIのURLのリソースID
    list_resource_id: '50040',
    // 組登録APIのURLのリソースID
    create_resource_id: '50041',
    // 組更新APIのURLのリソースID
    update_resource_id: '50042',
    // 組削除APIのURLのリソースID
    delete_resource_id: '50043'
  }
  export const subject = {
    // 教科検索APIのURLのリソースID
    list_resource_id: '50045',
    // 教科登録APIのURLのリソースID
    create_resource_id: '50046',
    // 教科更新APIのURLのリソースID
    update_resource_id: '50047',
    // 教科削除APIのURLのリソースID
    delete_resource_id: '50048'
  }
  export const auto_generator = {
    // 自動払い出しAPIのURLのリソースID
    auto_generator_resource_id: '50055'
  }
  export const apply_list_resource_id = '50024';
  export const start_up_resource_id = '50025';
  export const db_over_time_out_count = 4;
  export const school_types = [
    { type: 2, name: "小学校" },
    { type: 3, name: "中学校" },
    { type: 4, name: "高校" },
    { type: 5, name: "義務教育学校" },
    { type: 6, name: "特別支援学校" },
    { type: 7, name: "小中一貫校" },
    { type: 8, name: "中高一貫校" }
  ];
  // 　新規追加（マルチテナント化対応）　START
  export const school_types_kg = [
    { type: 98, name: "企業" }
  ];
  // 　新規追加（マルチテナント化対応）　END
  // 　新規追加（文科省標準の学校コード追加）　START
  export const mextOuCode_prefixs = [
    { type: "S", name: "S：学校" },
    { type: "B", name: "B：自治体" },
    { type: "P", name: "P：都道府県" }
  ];
  // 　新規追加（文科省標準の学校コード追加）　END
  export const class_type = [
    { name: "クラス", value: 1 },
    { name: "専科", value: 2 },
    { name: "任意", value: 3 }
  ];
  export const operation_type = [
    { code: "admin01", name: "OPE管理者登録" },
    { code: "admin02", name: "OPE管理者更新" },
    // 　新規追加（案件８．OPE管理者の削除）　START
    { code: "admin03", name: "OPE管理者削除" },
    // 　新規追加（案件８．OPE管理者の削除）　END
    # ↓OneRosterCSV項目取り込みバッチ連携時には以下は必須です
    // 　新規追加（OneRoster対応）　START
    { code: "admin11", name: "OPE管理者登録(一括)" },
    { code: "admin12", name: "OPE管理者更新(一括)" },
    { code: "admin13", name: "OPE管理者削除(一括)" },
    // 　新規追加（OneRoster対応）　END
    # ↑ここまで
    { code: "teacher01", name: "教員登録(個別)" },
    { code: "teacher02", name: "教員更新(個別)" },
    { code: "teacher03", name: "教員削除(個別)" },
    { code: "teacher04", name: "教員再登録(個別)" },
    { code: "teacher05", name: "教員異動" },
    { code: "teacher11", name: "教員登録(一括)" },
    { code: "teacher12", name: "教員更新(一括)" },
    // 　新規追加（教員一括削除追加）　START
    { code: "teacher13", name: "教員削除(一括)" },
    // 　新規追加（教員一括削除追加）　END
    // 　新規追加（教員一括異動追加）　START
    { code: "teacher14", name: "教員異動(一括)" },
    // 　新規追加（教員一括異動追加）　END
    { code: "student01", name: "児童・生徒登録(個別)" },
    { code: "student02", name: "児童・生徒更新(個別)" },
    { code: "student03", name: "児童・生徒削除(個別)" },
    { code: "student04", name: "児童・生徒再登録(個別)" },
    { code: "student05", name: "児童・生徒転入・転出" },
    { code: "student11", name: "児童・生徒登録(一括)" },
    { code: "student12", name: "児童・生徒進級" },
    { code: "student13", name: "児童・生徒削除(一括)" },
    { code: "student14", name: "児童・生徒進学" },
    { code: "school11", name: "学校一括登録" },
    { code: "autog11", name: "自動払い出し" }
  ];
  export const operation_status = [
    { code: "1", name: "申込中" },
    { code: "2", name: "処理中" },
    { code: "3", name: "完了" },
    { code: "4", name: "処理失敗" },
    { code: "7", name: "完了（通知成功)" },
    { code: "8", name: "完了（通知失敗)" },
    { code: "9", name: "エラー" }
  ];
  export const relation_win_label ={
    no_relation_win_label:"Azure ADアカウントの連携を行わない ",
    no_relation_win_label_sync:"Azure ADアカウントを削除する",
    new_relation_win_label:"Azure ADアカウントの新規作成を行う",
    exit_relation_win_label:"既存Azure ADアカウントと紐づける",
    relation_win_sync_upd_label:"Azure ADアカウントの同期を維持する",
    relation_win_sync_del_label:"Azure ADアカウントを削除する",
  }
  export const csv_setting = {
    // 児童・生徒一括登録件数上限
    bulk_add_number_limit: 5000,
    // 学校一括登録件数上限
    school_bulk_add_number_limit: 300,
    // 　改修（第三者CDI指摘対応）　START
    // 児童・生徒一括登録ファイルサイズ上限
    bulk_add_file_size_limit: 3670016,
    // 　改修（第三者CDI指摘対応）　END
    // 児童・生徒一括登録固定文字列
    bulk_add_Fixed_str: '有効年度',
    // 児童・生徒進級件数上限
    bulk_update_number_limit: 5000,
    // 　改修（第三者CDI指摘対応）　START
    // 児童・生徒進級ファイルサイズ上限
    bulk_update_file_size_limit: 3670016,
    // 　改修（第三者CDI指摘対応）　END
    // 児童・生徒進級固定文字列
    bulk_update_Fixed_str: '(進級前)ユーザID',
    // 学校マスタ一括登録固定文字列
    // 　改修（文科省標準の学校コード追加）　START
    school_bulk_add_Fixed_str: '学習eポータル組織コード(接頭子)',
    // 　改修（文科省標準の学校コード追加）　END
    // 児童・生徒進学固定文字列
    bulk_transfer_Fixed_str: '(進学前)学校コード',
    // 児童・生徒進学件数上限
    bulk_transfer_number_limit: 5000,
    // 　改修（第三者CDI指摘対応）　START
    // 児童・生徒進学ファイルサイズ上限
    bulk_transfer_file_size_limit: 3670016,
    // 　改修（第三者CDI指摘対応）　END
    // 教員一括登録固定文字列
    teacher_bulk_add_Fixed_str: '学校コード',
    // 教員一括登録件数上限
    teacher_bulk_add_number_limit: 3000,
    // 自動払い出し固定文字列
    auto_generator_add_Fixed_str: 'No',
    // 自動払い出し登録件数上限
    auto_generator_add_number_limit: 200,
    // 　新規追加（教員一括異動追加）　START
    // 教員一括異動固定文字列 
    teacher_bulk_transfer_Fixed_str: '(異動前)学校コード',
    // 　新規追加（教員一括異動追加）　END
  }
  export const output_csv_setting = {
    // 児童・生徒一括登録件数上限
    student: {
      //csvに出力する値を設定する
      csv_column_set: ["fiscal_year", "user_id", "persistent_uid", "sur_name", "given_name", "sur_name_kana", "given_name_kana", "password", "gender", "mail", "grade_code", "class_code", "student_number", "relationgg","relationwin"],
      csv_header_set: '"有効年度","ユーザID","自治体内ユニークID","姓","名","姓(ふりがな)","名(ふりがな)","パスワード","性別","メールアドレス","学年コード","組コード","出席番号","Googleアカウント作成有無","AzureADアカウント作成有無"',
      limit: 5000
    },
    teacher: {
      //csvに出力する値を設定する
      csv_column_set: ["organization_code","fiscal_year","role","user_id", "persistent_uid", "sur_name", "given_name","sur_name_kana","given_name_kana", "password", "gender", "mail", "title_code","additional_post_code","grade_code", "class_code", "subject_code", "relationgg","relationwin"],
      csv_header_set: '"学校コード","有効年度","権限","ユーザID","自治体内ユニークID","姓","名","姓(ふりがな)","名(ふりがな)","パスワード","性別","メールアドレス","職階コード","兼務コード","学年コード","組コード","教科コード","Googleアカウント作成有無","AzureADアカウント作成有無"',
      limit: 1000
    }
  }
}
