# -*- coding: utf-8 -*-
module ImportOneRosterDataHelper

  MANIFEST_VERSION = "1.0"
  ONEROSTER_VERSION = "1.2"

  require 'nkf'

  #====ImportOneRosterDataHelper.import_csv()
  #
  #メイン処理 (1)エラーチェックと取込ファイル記録
  #
  # dir_path      ・・ファイルパス
  # tenant_id     ・・テナントID（マルチテナント構成であり、テナントを指定するためのID）
  # tenant_prefix ・・テナント識別子
  # target_db     ・・取込先のデータベース
  #
  def self.import_csv(dir_path, tenant_id, tenant_prefix, target_db)

    logger = Logger.new('log/one_roster.log')
    logger.info("========== OneRoster V1.2 (CSV形式）取り込み処理開始 ==========")

    begin

    #[ 取込ファイル記録 ]
    ro_processing_id = nil
    ActiveRecord::Base.connected_to(database: target_db.to_sym) do
      ro = RoProcessing.new(xtype: 1, input_path: dir_path)
      ro.save
      ro_processing_id = ro.id
    end

    #manifestファイル
    logger.info("- manifest 取り込み")
    manifests = {}
    file_path = [dir_path, "manifest.csv"].join(File::SEPARATOR)
    logger.info("   取込ファイル：#{file_path}")
    raise "manifestファイルがありません。" unless File.exist?(file_path)

    #manifest文字コードチェック
    encoding_err = ImportOneRosterDataHelper.check_encoding(file_path, true)
    raise encoding_err if encoding_err.present? 

    #manifestヘッダーチェック
    header_err = ImportOneRosterDataHelper.check_header(dir_path, "manifest.csv")
    raise header_err if header_err.present? 

    manifest_err = ""
    CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
      #manifest[ レコードエラーチェックと取込ファイル記録 ]"
      err_msg = ImportOneRosterDataHelper.validate_manifest(row, MANIFEST_VERSION, ONEROSTER_VERSION)
      ImportOneRosterDataHelper.insert_ro_manifests(target_db, ro_processing_id, row, err_msg)
      manifest_err += err_msg if err_msg.present?
      manifests[row["propertyName"]] = row["value"]
    end
    raise "manifestファイルにエラーがあります。#{manifest_err}" if manifest_err.present?
    raise "manifestファイルにmanifestバージョン情報が明記されていません。" if manifests["manifest.version"].blank?
    raise "manifestファイルにonerosterバージョン情報が明記されていません。" if manifests["oneroster.version"].blank?
    logger.info("manifest.version : #{manifests["manifest.version"]}")
    logger.info("oneroster.version : #{manifests["oneroster.version"]}")

    #manifestの内容と実際のファイルの内容が一致しているか確認。各ファイルの文字コードチェックとヘッダーチェックもおこなう。
    csv_err = ImportOneRosterDataHelper.check_csv_files(dir_path, manifests)
    raise csv_err if csv_err.present? 

    #Academic Session（年度情報）
    school_years = {}
    file_path = [dir_path, "academicSessions.csv"].join(File::SEPARATOR)
    if manifests["file.academicSessions"] == "bulk" && File.exist?(file_path)
      logger.info("- Academic Session（年度情報）取り込み")
      logger.info("   取込ファイル：#{file_path}")
      err_cnt = 0
      ok_cnt = 0
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_academic_session(row)
        ImportOneRosterDataHelper.insert_ro_academic_sessions(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        ok_cnt += 1
        school_years[row["sourcedId"]] = {"status" => row["status"],
                                          "dateLastModified" => row["dateLastModified"],
                                          "fiscal_year" => row["schoolYear"],
                                          "start_date" => row["startDate"],
                                          "end_date" => row["endDate"]}
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    #Org（学校情報）
    districts = {}   #教育委員会
    schools = {}     #学校
    file_path = [dir_path, "orgs.csv"].join(File::SEPARATOR)
    if manifests["file.orgs"] == "bulk" && File.exist?(file_path)
      logger.info("- Org（学校情報）取り込み")
      logger.info("   取込ファイル：#{file_path}")
      #教育委員会チェック用
      district_sourced_ids = []
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
        next if row["type"] == "school"
        district_sourced_ids.push(row["sourcedId"])
      end
      err_cnt = 0
      ok_cnt = 0
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_org(row, district_sourced_ids)
        ImportOneRosterDataHelper.insert_ro_orgs(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        ok_cnt += 1

        if row["type"] == "school"
          schools[row["sourcedId"]] = {"mext_school_code" => row["identifier"],
                                       "name" => row["name"],
                                       "parent" => (row["parentSourcedId"]=="NULL" ? "" : row["parentSourcedId"]),
                                       "type" => row["type"]}
        else
          districts[row["sourcedId"]] = {"name" => row["name"],
                                         "type" => row["type"]}
        end
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    org_sourced_ids = schools.merge(districts)

    #Courses(学籍クラス/教科クラス情報の上位モデル)
    courses = {}    #学校別 コース
    file_path = [dir_path, "courses.csv"].join(File::SEPARATOR)
    if manifests["file.courses"] == "bulk" && File.exist?(file_path)
      logger.info("- Courses(コース情報)取り込み")
      logger.info("   取込ファイル：#{file_path}" )
      err_cnt = 0
      ok_cnt = 0
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_course(row, org_sourced_ids, school_years)
        ImportOneRosterDataHelper.insert_ro_courses(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        ok_cnt += 1

        if districts[row["orgSourcedId"]].present?
          #教育委員会で作成されていたらparentSourcedId配下またはparentSourcedIdが空白の学校全てで作成
          schools.each do |school_sourced_id, val|
            next if val["parent"].present? && val["parent"] != "NULL" && val["parent"] != row["orgSourcedId"]
            courses[school_sourced_id] = {} if courses[school_sourced_id].blank?
            courses[school_sourced_id][row["sourcedId"]] = {
                                                          "fiscal_year_sourcedId" => row["schoolYearSourcedId"],
                                                          "title" => row["title"],
                                                          "grades" => OneRosterHelper.convert_grades(row["grades"]),
                                                          "subjects" => OneRosterHelper.convert_to_array(row["subjects"]),
                                                          "subjectCodes" => OneRosterHelper.convert_to_array(row["subjectCodes"])}
          end
        else
          courses[row["orgSourcedId"]] = {} if courses[row["orgSourcedId"]].blank?
          courses[row["orgSourcedId"]][row["sourcedId"]] = {
                                                          "fiscal_year_sourcedId" => row["schoolYearSourcedId"],
                                                          "title" => row["title"],
                                                          "grades" => OneRosterHelper.convert_grades(row["grades"]),
                                                          "subjects" => OneRosterHelper.convert_to_array(row["subjects"]),
                                                          "subjectCodes" => OneRosterHelper.convert_to_array(row["subjectCodes"])}
        end
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    #Class(学籍クラス/教科クラス情報)
    class_homerooms = {}   #学校別 学籍クラス
    class_subjects = {}    #学校別 教科クラス
    file_path = [dir_path, "classes.csv"].join(File::SEPARATOR)
    if manifests["file.classes"] == "bulk" && File.exist?(file_path)
      logger.info("- Class(学籍クラス/教科クラス情報)取り込み")
      logger.info("   取込ファイル：#{file_path}")
      err_cnt = 0
      ok_cnt = 0
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_class(row, org_sourced_ids, school_years, courses)
        ImportOneRosterDataHelper.insert_ro_classes(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        ok_cnt += 1

        #class.gradesが無い場合はcoursesから取得
        grades = OneRosterHelper.convert_grades(row["grades"])
        if grades.blank?
          if courses[row["schoolSourcedId"]].present? && courses[row["schoolSourcedId"]][row["courseSourcedId"]].present? && courses[row["schoolSourcedId"]][row["courseSourcedId"]]["grades"].present?
            grades = courses[row["schoolSourcedId"]][row["courseSourcedId"]]["grades"]
          end
        end

        if row["classType"] == "homeroom"
          class_homerooms[row["schoolSourcedId"]] = {} if class_homerooms[row["schoolSourcedId"]].blank?
          class_homerooms[row["schoolSourcedId"]][row["sourcedId"]] = {
                                                       "title" => row["title"],
                                                       "grades" => grades,
                                                       "courseSourcedId" => row["courseSourcedId"],
                                                       "classCode" => row["classCode"],
                                                       "specialNeeds" => row["metadata.jp.specialNeeds"],
                                                       "termSourcedIds" => OneRosterHelper.convert_to_array(row["termSourcedIds"])}
        else
          class_subjects[row["schoolSourcedId"]] = {} if class_subjects[row["schoolSourcedId"]].blank?
          class_subjects[row["schoolSourcedId"]][row["sourcedId"]] = {
                                                       "title" => row["title"],
                                                       "grades" => grades,
                                                       "courseSourcedId" => row["courseSourcedId"],
                                                       "classCode" => row["classCode"],
                                                       "subjectCodes" => OneRosterHelper.convert_to_array(row["subjectCodes"]),
                                                       "subjects" => OneRosterHelper.convert_to_array(row["subjects"]),
                                                       "specialNeeds" => row["metadata.jp.specialNeeds"],
                                                       "termSourcedIds" => OneRosterHelper.convert_to_array(row["termSourcedIds"])}
        end
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    #User(児童・生徒、教員、保護者)
    users = {}
    file_path = [dir_path, "users.csv"].join(File::SEPARATOR)
    if manifests["file.users"] == "bulk" && File.exist?(file_path)
      logger.info("- User(児童・生徒、教員、保護者)取り込み")
      logger.info("   取込ファイル：#{file_path}")
      err_cnt = 0
      ok_cnt = 0
      user_master_identifiers = []   #重複チェック用
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_user(row, org_sourced_ids, class_homerooms, class_subjects, user_master_identifiers)
        ImportOneRosterDataHelper.insert_ro_users(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        user_master_identifiers.push(row["userMasterIdentifier"])
        ok_cnt += 1

        fullname = row["familyName"].to_s
        fullname += " " + row["middleName"].to_s if row["middleName"].present?
        fullname += " " + row["givenName"].to_s if row["givenName"].present?
        fullname = row["preferredGivenName"].to_s if fullname.blank? && row["preferredGivenName"].present?
        fullname += " " + row["preferredmiddleName"].to_s if row["preferredmiddleName"].present?
        fullname += " " + row["preferredgivenName"].to_s if row["preferredgivenName"].present?
        fullname_kana = row["metadata.jp.kanaFamilyName"].to_s
        fullname_kana += " " + row["metadata.jp.kanaMiddleName"].to_s if row["metadata.jp.kanaMiddleName"].present?
        fullname_kana += " " + row["metadata.jp.kanaGivenName"].to_s if row["metadata.jp.kanaGivenName"].present?
        users[row["sourcedId"]] = {"fullname" => fullname,
                                   "fullname_kana" => fullname_kana,
                                   "userIds" => row["userIds"],
                                   "userMasterIdentifier" => row["userMasterIdentifier"],
                                   "schoolSourcedId" => row["primaryOrgSourcedId"],
                                   "classSourcedId" => row["metadata.jp.homeClass"],
                                   "grades" => OneRosterHelper.convert_grades(row["grades"])}
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    #Demographics(生徒デモグラフィック属性（誕生日、性別）) ※1.2では未使用
    file_path = [dir_path, "demographics.csv"].join(File::SEPARATOR)
    if manifests["file.demographics"] == "bulk"
      logger.info("- Demographics(生徒デモグラフィック属性（誕生日、性別）)取り込み")
      logger.info("    ※Demographicsは処理対象外です。")
    end

    #Enrollment(UserとClassの関連情報)
    teacher_classes = {}    #教員学籍クラス
    teacher_subjects = {}   #教員教科担当
    student_classes = {}    #生徒学籍クラス
    student_subjects = {}   #生徒教科クラス
    file_path = [dir_path, "enrollments.csv"].join(File::SEPARATOR)
    if manifests["file.enrollments"] == "bulk" && File.exist?(file_path)
      logger.info("- Enrollment(UserとClassの関連情報)取り込み")
      logger.info("   取込ファイル：#{file_path}")
      err_cnt = 0
      ok_cnt = 0
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_enrollment(row, org_sourced_ids, users, class_homerooms, class_subjects)
        ImportOneRosterDataHelper.insert_ro_enrollments(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        ok_cnt += 1

        if row["role"] == "teacher" && class_homerooms[row["schoolSourcedId"]].present? && class_homerooms[row["schoolSourcedId"]][row["classSourcedId"]].present?
             #教員学籍クラス
          teacher_classes[row["userSourcedId"]] = {} if teacher_classes[row["userSourcedId"]].blank?
          teacher_classes[row["userSourcedId"]][row["classSourcedId"]] = {"schoolSourcedId" => row["schoolSourcedId"],
                                                                          "begin_date" => row["beginDate"],
                                                                          "end_date" => row["endDate"],
                                                                          "primary" => row["primary"]}
        elsif row["role"] == "teacher" && class_subjects[row["schoolSourcedId"]].present? && class_subjects[row["schoolSourcedId"]][row["classSourcedId"]].present?
             #教員教科担当
          teacher_subjects[row["userSourcedId"]] = {} if teacher_subjects[row["userSourcedId"]].blank?
          teacher_subjects[row["userSourcedId"]][row["classSourcedId"]] = {"schoolSourcedId" => row["schoolSourcedId"],
                                                                           "begin_date" => row["beginDate"],
                                                                           "end_date" => row["endDate"],
                                                                           "primary" => row["primary"]}
        elsif row["role"] == "student" && class_homerooms[row["schoolSourcedId"]].present? && class_homerooms[row["schoolSourcedId"]][row["classSourcedId"]].present?
             #生徒学籍クラス
          student_classes[row["userSourcedId"]] = {} if student_classes[row["userSourcedId"]].blank?
          student_classes[row["userSourcedId"]][row["classSourcedId"]] = {"schoolSourcedId" => row["schoolSourcedId"],
                                                                          "begin_date" => row["beginDate"],
                                                                          "end_date" => row["endDate"],
                                                                          "hr_no" => row["metadata.jp.ShussekiNo"]}
        elsif row["role"] == "student" && class_subjects[row["schoolSourcedId"]].present? && class_subjects[row["schoolSourcedId"]][row["classSourcedId"]].present?
             #生徒教科クラス
          student_subjects[row["userSourcedId"]] = {} if student_subjects[row["userSourcedId"]].blank?
          student_subjects[row["userSourcedId"]][row["classSourcedId"]] = {"schoolSourcedId" => row["schoolSourcedId"],
                                                                           "begin_date" => row["beginDate"],
                                                                           "end_date" => row["endDate"],
                                                                           "hr_no" => row["metadata.jp.ShussekiNo"]}
        end
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    #Roles(学校所属情報)
    deployments = {}    #教員所属
    move_in_outs = {}   #生徒在籍 学校別
    roles = {}          #その他ロール
    file_path = [dir_path, "roles.csv"].join(File::SEPARATOR)
    if manifests["file.roles"] == "bulk" && File.exist?(file_path)
      logger.info("- Roles(学校所属情報)取り込み")
      logger.info("   取込ファイル：#{file_path}")
      primary_user_sourced_ids = []   #primaryが必ず含まれるかチェック用
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
        primary_user_sourced_ids.push(row["userSourcedId"]) if row["roleType"]=="primary"
      end
      err_cnt = 0
      ok_cnt = 0
      CSV.foreach(file_path, :headers=> true, :encoding => "utf-8") do |row|
          #- 各値チェックと取込ファイル記録への登録
        err_msg = ImportOneRosterDataHelper.validate_ro_role(row, org_sourced_ids, users, primary_user_sourced_ids)
        ImportOneRosterDataHelper.insert_ro_roles(target_db, ro_processing_id, row, err_msg)
        if err_msg.present?
          err_cnt += 1
          next
        end
        ok_cnt += 1

        if row["role"] == "teacher" && (schools[row["orgSourcedId"]].present? || districts[row["orgSourcedId"]].present?)
             #教員所属(学校 or 教育委員会)
          deployments[row["userSourcedId"]] = [] if deployments[row["userSourcedId"]].blank?
          deployments[row["userSourcedId"]] << {"schoolSourcedId" => row["orgSourcedId"],
                                                "roleType" => row["roleType"],
                                                "begin_date" => row["beginDate"],
                                                "end_date" => row["endDate"]}
        elsif row["role"] == "student" && schools[row["orgSourcedId"]].present?
             #生徒在籍
          move_in_outs[row["userSourcedId"]] = {} if move_in_outs[row["userSourcedId"]].blank?
          move_in_outs[row["userSourcedId"]][row["orgSourcedId"]] = {
                                                 "begin_date" => row["beginDate"],
                                                 "end_date" => row["endDate"]}
        else
            #その他ロール（管理職（教育委員会）「districtAdministrator」管理職（学校）「siteAdministrator」）
          roles[row["userSourcedId"]] = [] if roles[row["userSourcedId"]].blank?
          roles[row["userSourcedId"]] << {"schoolSourcedId" => row["orgSourcedId"],
                                          "role" => row["role"],
                                          "roleType" => row["roleType"],
                                          "begin_date" => row["beginDate"],
                                          "end_date" => row["endDate"]}
        end
      end
      logger.info("   取込件数：#{ok_cnt} エラー件数：#{err_cnt}")
    end

    #userProfiles ※1.2では未使用
    file_path = [dir_path, "userProfiles.csv"].join(File::SEPARATOR)
    if manifests["file.userProfiles"] == "bulk"
      logger.info("- userProfiles取り込み")
      logger.info("    ※userProfilesは処理対象外です。")
    end

    logger.info("- 学習eポータルDB登録")
    import_db(tenant_id, tenant_prefix, target_db,
              manifests,
              school_years,districts,
              schools,courses,
              class_homerooms,class_subjects,users,
              teacher_classes,teacher_subjects,student_classes,student_subjects,
              deployments,
              move_in_outs,
              roles,
              logger)

    logger.info("========== 処理終了 ==========")

    rescue=>e
      logger.error(e.message)
      #[ 取込ファイル記録 ]
      if ro_processing_id.present?
        ActiveRecord::Base.connected_to(database: target_db.to_sym) do
          ro = RoProcessing.where(:id => ro_processing_id).first
          if ro.present?
            ro.err_msg = e.message
            ro.save
          end
        end
      end
      logger.error("========== エラー終了 ==========")
    end
  end

  #====ImportOneRosterDataHelper.import_db()
  #
  #メイン処理 (2) 学習eポータルDB登録
  # 
  # tenant_id       ・・テナントID（マルチテナント構成であり、テナントを指定するためのID）
  # tenant_prefix   ・・テナント識別子
  # manifests       ・・manifests
  # school_years    ・・学校年度
  # districts       ・・教育委員会
  # schools         ・・学校
  # courses         ・・コース
  # class_homerooms ・・ホームルームクラス
  # class_subjects  ・・クラス教科
  # users           ・・ユーザ情報
  # teacher_classes ・・クラス担任
  # teacher_subjects・・教科担当
  # student_classes ・・生徒クラス在籍情報
  # student_subjects・・生徒履修教科情報
  # deployments     ・・教職員異動情報
  # move_in_outs    ・・生徒在籍情報
  # roles           ・・ロール
  # logger          ・・ログ
  #
  def self.import_db(tenant_id, tenant_prefix, target_db,
                     manifests,
                     school_years,districts,
                     schools,courses,
                     class_homerooms,class_subjects,users,
                     teacher_classes,teacher_subjects,student_classes,student_subjects,
                     deployments,
                     move_in_outs,
                     roles,
                     logger)
    error_info = []
    ActiveRecord::Base.transaction do
      ActiveRecord::Base.connected_to(database: target_db.to_sym) do

        #学校マスタ取り込み

        #教育委員会取込

        #学年・組マスタ取り込み

        #児童生徒取り込み（学籍クラスに在籍しているユーザーを対象）

        #教職員取り込み（学校に所属しているユーザーを対象）
        #異動情報取込
        #担任取込
       
      end
    end
  end


  #====ImportOneRosterDataHelper.check_csv_files()
  #
  #manifestの内容と実際のファイルの内容が一致しているか確認
  #
  # dir_path        ・・ディレクトリパス
  # manifests       ・・manifests
  #
  def self.check_csv_files(dir_path, manifests)
    err_msg = ""
    dir_names = dir_path.split(File::SEPARATOR)
    file_names = []
    Dir.foreach(dir_path) do |w_path|
      w_file_name = File.basename(w_path)
      next if w_file_name=="." || w_file_name==".." || w_file_name==dir_names[-1] || w_file_name=="manifest.csv"
      file_names << w_file_name
      next if manifests["file.academicSessions"]=="bulk" && w_file_name=="academicSessions.csv"
      next if manifests["file.orgs"]=="bulk" && w_file_name=="orgs.csv"
      next if manifests["file.courses"]=="bulk" && w_file_name=="courses.csv"
      next if manifests["file.classes"]=="bulk" && w_file_name=="classes.csv"
      next if manifests["file.users"]=="bulk" && w_file_name=="users.csv"
      next if manifests["file.demographics"]=="bulk" && w_file_name=="demographics.csv"
      next if manifests["file.enrollments"]=="bulk" && w_file_name=="enrollments.csv"
      next if manifests["file.roles"]=="bulk" && w_file_name=="roles.csv"
      next if manifests["file.userProfiles"]=="bulk" && w_file_name=="userProfiles.csv"
      err_msg += "manifestファイルの内容と実際のファイルが一致しません。または不明なファイルが存在します。(#{w_file_name})"
    end
    err_msg += "academicSessions.csvファイルがありません。" if manifests["file.academicSessions"]=="bulk" && !file_names.include?("academicSessions.csv")
    err_msg += "orgs.csvファイルがありません。" if manifests["file.orgs"]=="bulk" && !file_names.include?("orgs.csv")
    err_msg += "courses.csvファイルがありません。" if manifests["file.courses"]=="bulk" && !file_names.include?("courses.csv")
    err_msg += "classes.csvファイルがありません。" if manifests["file.classes"]=="bulk" && !file_names.include?("classes.csv")
    err_msg += "users.csvファイルがありません。" if manifests["file.users"]=="bulk" && !file_names.include?("users.csv")
    err_msg += "demographics.csvファイルがありません。" if manifests["file.demographics"]=="bulk" && !file_names.include?("demographics.csv")
    err_msg += "enrollments.csvファイルがありません。" if manifests["file.enrollments"]=="bulk" && !file_names.include?("enrollments.csv")
    err_msg += "roles.csvファイルがありません。" if manifests["file.roles"]=="bulk" && !file_names.include?("roles.csv")
    err_msg += "userProfiles.csvファイルがありません。" if manifests["file.userProfiles"]=="bulk" && !file_names.include?("userProfiles.csv")

    #文字コードチェックとヘッダーチェック
    if manifests["file.academicSessions"]=="bulk" && file_names.include?("academicSessions.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "academicSessions.csv"].join(File::SEPARATOR))
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "academicSessions.csv")
        err_msg += header_err if header_err.present? 
      end
      #※「"」で囲まれていなくても問題なく取り込めるためチェックなしとする
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "academicSessions.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.orgs"]=="bulk" && file_names.include?("orgs.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "orgs.csv"].join(File::SEPARATOR))
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "orgs.csv")
        err_msg += header_err if header_err.present? 
      end
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "orgs.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.courses"]=="bulk" && file_names.include?("courses.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "courses.csv"].join(File::SEPARATOR))
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "courses.csv")
        err_msg += header_err if header_err.present? 
      end
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "courses.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.classes"]=="bulk" && file_names.include?("classes.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "classes.csv"].join(File::SEPARATOR))
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "classes.csv")
        err_msg += header_err if header_err.present? 
      end
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "classes.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.users"]=="bulk" && file_names.include?("users.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "users.csv"].join(File::SEPARATOR))
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "users.csv")
        err_msg += header_err if header_err.present? 
      end
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "users.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.demographics"]=="bulk" && file_names.include?("demographics.csv")
      #文字コードチェックなし
      #ヘッダーチェックなし
    end
    if manifests["file.enrollments"]=="bulk" && file_names.include?("enrollments.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "enrollments.csv"].join(File::SEPARATOR), true)
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "enrollments.csv")
        err_msg += header_err if header_err.present? 
      end
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "enrollments.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.roles"]=="bulk" && file_names.include?("roles.csv")
      encoding_err = ImportOneRosterDataHelper.check_encoding([dir_path, "roles.csv"].join(File::SEPARATOR), true)
      if encoding_err.present?
        err_msg += encoding_err
      else
        header_err = ImportOneRosterDataHelper.check_header(dir_path, "roles.csv")
        err_msg += header_err if header_err.present? 
      end
      quote_err = ImportOneRosterDataHelper.check_d_quote(dir_path, "roles.csv")
      err_msg += quote_err if quote_err.present? 
    end
    if manifests["file.userProfiles"]=="bulk" && file_names.include?("userProfiles.csv")
      #文字コードチェックなし
      #ヘッダーチェックなし
    end
    return err_msg
  end


  #====ImportOneRosterDataHelper.check_encoding()
  #
  #文字コードチェック
  #
  # file_path       ・・ファイルパス
  # ascii_char_only ・・ASCII文字のみかどうか（デフォルトfalse）
  #
  def self.check_encoding(file_path, ascii_char_only=false)
    err_msg = ""
    begin
      File.open(file_path, "r:utf-8") do |f|
        f.each_line do |l|
          if l.index("\uFEFF", 0)==0
            err_msg = "#{file_path}がBOM付ファイルとなっています。"
          end  
          break
        end
      end
    rescue
      err_msg = "#{file_path}の読み込みに失敗しました。"
    end
    return err_msg
  end
  

  #====ImportOneRosterDataHelper.get_xxxx()
  #
  #各種CSVファイルヘッダー取得
  #
  def self.get_manifest_header
    return ["propertyName","value"]
  end

  def self.get_academic_session_header
    return ["sourcedId","status","dateLastModified","title","type","startDate","endDate","parentSourcedId","schoolYear"]
  end

  def self.get_org_header
    return ["sourcedId","status","dateLastModified","name","type","identifier","parentSourcedId"]
  end

  def self.get_course_header
    return ["sourcedId","status","dateLastModified","schoolYearSourcedId","title","courseCode","grades","orgSourcedId","subjects","subjectCodes"]
  end

  def self.get_class_header
    return ["sourcedId","status","dateLastModified","title","grades","courseSourcedId","classCode","classType","location","schoolSourcedId","termSourcedIds","subjects","subjectCodes","periods","metadata.jp.specialNeeds"]
  end

  def self.get_user_header
    return ["sourcedId","status","dateLastModified","enabledUser","username","userIds","givenName","familyName","middleName","identifier","email","sms","phone","agentSourcedIds","grades","password","userMasterIdentifier","resourceSourcedIds","preferredGivenName","preferredMiddleName","preferredFamilyName","primaryOrgSourcedId","pronouns","metadata.jp.kanaGivenName","metadata.jp.kanaFamilyName","metadata.jp.kanaMiddleName","metadata.jp.homeClass"]
  end

  def self.get_enrollment_header
    return ["sourcedId","status","dateLastModified","classSourcedId","schoolSourcedId","userSourcedId","role","primary","beginDate","endDate","metadata.jp.ShussekiNo","metadata.jp.PublicFlg"]
  end

  def self.get_role_header
    return ["sourcedId","status","dateLastModified","userSourcedId","roleType","role","beginDate","endDate","orgSourcedId","userProfileSourcedId"]
  end


  #====ImportOneRosterDataHelper.check_header()
  #
  #CSVファイルヘッダーチェック
  # dir_path ・・ディレクトリパス
  # csv_name ・・CSVファイル名
  #
  def self.check_header(dir_path, csv_name)
    file_path = [dir_path, csv_name].join(File::SEPARATOR)
    err_msg = ""
    CSV.foreach(file_path, :headers=> false, :encoding => "utf-8") do |row|
      if csv_name=="manifest.csv"
        err_msg = ImportOneRosterDataHelper.check_header_manifest(row)
      elsif csv_name=="academicSessions.csv"
        err_msg = ImportOneRosterDataHelper.check_header_academic_session(row)
      elsif csv_name=="orgs.csv"
        err_msg = ImportOneRosterDataHelper.check_header_org(row)
      elsif csv_name=="courses.csv"
        err_msg = ImportOneRosterDataHelper.check_header_course(row)
      elsif csv_name=="classes.csv"
        err_msg = ImportOneRosterDataHelper.check_header_class(row)
      elsif csv_name=="users.csv"
        err_msg = ImportOneRosterDataHelper.check_header_user(row)
      elsif csv_name=="enrollments.csv"
        err_msg = ImportOneRosterDataHelper.check_header_enrollment(row)
      elsif csv_name=="roles.csv"
        err_msg = ImportOneRosterDataHelper.check_header_role(row)
      end
      break
    end
    err_msg = "CSVファイル(#{File.basename(file_path)})のヘッダー" + err_msg if err_msg.present?
    return err_msg
  end


  #====ImportOneRosterDataHelper.check_header_xxx()
  #
  #各種ヘッダーチェック
  # header_row ・・行レコード
  #
  def self.check_header_manifest(header_row)
    get_manifest_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_manifest_header
    return ""
  end

  def self.check_header_academic_session(header_row)
    get_academic_session_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_academic_session_header
    return ""
  end

  def self.check_header_org(header_row)
    get_org_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_org_header
    return ""
  end

  def self.check_header_course(header_row)
    get_course_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_course_header
    return ""
  end

  def self.check_header_class(header_row)
    get_class_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_class_header
    return ""
  end

  def self.check_header_user(header_row)
    get_user_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_user_header
    return ""
  end

  def self.check_header_enrollment(header_row)
    get_enrollment_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_enrollment_header
    return ""
  end

  def self.check_header_role(header_row)
    get_role_header.each do |h_name|
      return "に「#{h_name}」がありません。" unless header_row.include?(h_name)
    end
    return "の並び順が不正です。" if header_row != get_role_header
    return ""
  end


  #====ImportOneRosterDataHelper.check_d_quote()
  #
  # ダブルクォーテーションで囲まれているかチェック
  #  dir_path ・・ディレクトリパス
  #  csv_name ・・CSVファイル名
  #
  def self.check_d_quote(dir_path, csv_name)
    file_path = [dir_path, csv_name].join(File::SEPARATOR)
    err_msg = ""
    line_no = 0
    File.foreach(file_path){|line|
      line_no += 1
      next if line_no==1   #ヘッダーは除く

      #「","」で区切って項目数が正しいかチェックする
      line_num = line.split('","').length
      if csv_name=="manifest.csv"
        err_msg = "#{line_no} " if line_num < get_manifest_header.length
      elsif csv_name=="academicSessions.csv"
        err_msg = "#{line_no} " if line_num < get_academic_session_header.length
      elsif csv_name=="orgs.csv"
        err_msg = "#{line_no} " if line_num < get_org_header.length
      elsif csv_name=="courses.csv"
        err_msg = "#{line_no} " if line_num < get_course_header.length
      elsif csv_name=="classes.csv"
        err_msg = "#{line_no} " if line_num < get_class_header.length
      elsif csv_name=="users.csv"
        err_msg = "#{line_no} " if line_num < get_user_header.length
      elsif csv_name=="enrollments.csv"
        err_msg = "#{line_no} " if line_num < get_enrollment_header.length
      elsif csv_name=="roles.csv"
        err_msg = "#{line_no} " if line_num < get_role_header.length
      end
      break if err_msg.present?
     }
    return (err_msg.presence ? "#{file_path}:#{err_msg}行目 ダブルクォーテーションで囲まれていない項目が存在します。" : "")
  end


  #====ImportOneRosterDataHelper.validate_manifest()
  #
  #manifestエラーチェック
  #
  # row                ・・行データ
  # manifest_version   ・・manifest_version
  # oneroster_version  ・・oneroster_version
  #
  def self.validate_manifest(row, manifest_version, oneroster_version)
    err_msg = ""
    err_msg += "manifestバージョンが違います。" if row["propertyName"] == "manifest.version" && row["value"] != manifest_version
    err_msg += "onerosterバージョンが違います。" if row["propertyName"] == "oneroster.version" && row["value"] != oneroster_version
    #※1.2では「absent」or「bulk」のみ
    err_msg += "bulkデータのみ指定可能です。" if row["propertyName"].present? && row["propertyName"].slice(0,5) == "file." && row["value"] != "bulk" && row["value"] != "absent"
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_academic_session()
  #
  #academic_sessionエラーチェック
  #
  # row                ・・行データ
  #
  def self.validate_ro_academic_session(row)
    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "titleに値なし。" if row["title"].blank?
    err_msg += "typeが不正。" if row["type"] != "schoolYear"
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "startDateに値なし。" if row["startDate"].blank?
    err_msg += "startDateが不正。" unless check_date(row["startDate"])
    err_msg += "endDateに値なし。" if row["endDate"].blank?
    err_msg += "endDateが不正。" unless check_date(row["endDate"])
    #parentSourcedId:固定値「NULL」
    err_msg += "parentSourcedIdが不正。" if row["parentSourcedId"] != "NULL"
    err_msg += "schoolYearに値なし。" if row["schoolYear"].blank?
    err_msg += "schoolYearが不正。" if row["schoolYear"].present? && (row["schoolYear"].length != 4 || !check_int(row["schoolYear"]))
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_org()
  #
  #orgエラーチェック
  #
  # row                  ・・行データ
  # district_sourced_ids ・・教育委員会sourced_idリスト
  #
  def self.validate_ro_org(row, district_sourced_ids={})
    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "nameに値なし。" if row["name"].blank?
    err_msg += "nameが不正（半角カタカナが存在）。"  if row["name"].present? && !check_han_katakana(row["name"])
    err_msg += "nameが30文字以上。" if row["name"].present? && row["name"].length > 30
    err_msg += "typeが不正。" if row["type"] != "district" && row["type"] != "school"
    #err_msg += "identifierに値なし。" if row["identifier"].blank?  #identifier(=mext_school_code)
    err_msg += "identifierが20文字以上。" if row["identifier"].present? && row["identifier"].length > 20
    #parentSourcedId:学校でも必須ではない。教育委員会は固定値「NULL」。
    #err_msg += "parentSourcedIdに値なし(type:school)。" if row["parentSourcedId"].blank? && row["type"] == "school"
    err_msg += "parentSourcedIdがNULL以外(type:district)。" if (row["parentSourcedId"].present? && row["parentSourcedId"] != "NULL") && row["type"] == "district"
    err_msg += "parentSourcedIdが不正(orgs-districtに定義がありません)。" if (row["parentSourcedId"].present? && row["parentSourcedId"] != "NULL" && district_sourced_ids.blank?) || (row["parentSourcedId"].present? && row["parentSourcedId"] != "NULL" && district_sourced_ids.present? && !district_sourced_ids.include?(row["parentSourcedId"]))
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_course()
  #
  #courseエラーチェック
  #
  # row                     ・・行データ
  # org_sourced_ids         ・・組織sourced_idリスト
  # school_year_sourced_ids ・・学校年度sourced_idリスト
  #
  def self.validate_ro_course(row, org_sourced_ids={}, school_year_sourced_ids={})
    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "schoolYearSourcedIdが不正(academicSessionsファイルに定義がありません)。" if (row["schoolYearSourcedId"].present? && school_year_sourced_ids.blank?) || (row["schoolYearSourcedId"].present? && school_year_sourced_ids.present? && school_year_sourced_ids[row["schoolYearSourcedId"]].blank?)
    err_msg += "titleに値なし。" if row["title"].blank?
    err_msg += "titleが不正（半角カタカナが存在）。"  if row["title"].present? && !check_han_katakana(row["title"])
    err_msg += "courseCodeが空白以外。" if row["courseCode"].present?   #courseCodeは空白以外許可しない
    if row["grades"].present?
      row["grades"].split(",").each do |g|
        next if g.blank?
        grade_cd = RoConversion.get_grade(g)
        if grade_cd.blank?
          err_msg += "gradesが不正。"
          break
        end
      end
    end
    err_msg += "orgSourcedIdに値なし。" if row["orgSourcedId"].blank?
    err_msg += "orgSourcedIdが不正(orgsファイルに定義がありません)。" if (row["orgSourcedId"].present? && org_sourced_ids.blank?) || (row["orgSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["orgSourcedId"]].blank?)
    err_msg += "subjectsが不正（半角カタカナが存在）。"  if row["subjects"].present? && !check_han_katakana(row["subjects"])
    if row["subjectCodes"].present?
      row["subjectCodes"].split(",").each do |c|
        next if c.blank?
        subject_name = RoConversion.get_subject_name(c)
        if subject_name.blank?
          err_msg += "subjectCodesが不正。"
          break
        end
      end
    end
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_class()
  #
  #classエラーチェック
  #
  # row                     ・・行データ
  # org_sourced_ids         ・・組織sourced_idリスト
  # school_year_sourced_ids ・・学校年度sourced_idリスト
  # course_sourced_ids      ・・コースsourced_idリスト
  #
  def self.validate_ro_class(row, org_sourced_ids={}, school_year_sourced_ids={}, course_sourced_ids={})
    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "titleに値なし。"  if row["title"].blank?
    err_msg += "titleが不正（半角カタカナが存在）。"  if row["title"].present? && !check_han_katakana(row["title"])
    if row["grades"].present?
      row["grades"].split(",").each do |g|
        next if g.blank?
        grade_cd = RoConversion.get_grade(g)
        if grade_cd.blank?
          err_msg += "gradesが不正。"
          break
        end
      end
    end
    err_msg += "schoolSourcedIdに値なし。"  if row["schoolSourcedId"].blank?
    err_msg += "schoolSourcedIdが不正(orgsファイルに定義がありません)。" if (row["schoolSourcedId"].present? && org_sourced_ids.blank?) || (row["schoolSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["schoolSourcedId"]].blank?)
    err_msg += "schoolSourcedIdが不正(schoolではない)。" if row["schoolSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["schoolSourcedId"]].present? && org_sourced_ids[row["schoolSourcedId"]]["type"] != "school"
    err_msg += "courseSourcedIdに値なし。"  if row["courseSourcedId"].blank?
    err_msg += "courseSourcedIdが不正(coursesファイルに定義がありません)。" if (row["schoolSourcedId"].present? && row["courseSourcedId"].present? && course_sourced_ids.blank?) || (row["schoolSourcedId"].present? && row["courseSourcedId"].present? && course_sourced_ids.present? && (course_sourced_ids[row["schoolSourcedId"]].blank? || (course_sourced_ids[row["schoolSourcedId"]].present? && course_sourced_ids[row["schoolSourcedId"]][row["courseSourcedId"]].blank?)))
    #err_msg += "classCodeに値なし(homeroom)。"  if row["classCode"].blank? && row["classType"] == "homeroom"
    err_msg += "classCodeが不正。" if row["classCode"].present? && row["classType"] == "homeroom" && RoConversion.get_class_code(row["classCode"]).blank?
    err_msg += "classTypeが不正。" if row["classType"] != "homeroom" && row["classType"] != "scheduled"
    err_msg += "locationが不正（半角カタカナが存在）。"  if row["location"].present? && !check_han_katakana(row["location"])
    err_msg += "termSourcedIdsに値なし。"  if row["termSourcedIds"].blank?
    if row["termSourcedIds"].present? && school_year_sourced_ids.present?
      row["termSourcedIds"].split(",").each do |school_year|
        if school_year.present? && school_year_sourced_ids[school_year].blank?
          err_msg += "termSourcedIdsが不正(academicSessionsファイルに定義がありません)。"
          break
        end
      end
    elsif row["termSourcedIds"].present? && school_year_sourced_ids.blank?
      err_msg += "termSourcedIdsが不正(academicSessionsファイルに定義がありません)。"
    end
    err_msg += "subjectsが不正（半角カタカナが存在）。"  if row["subjects"].present? && !check_han_katakana(row["subjects"])
    if row["subjectCodes"].present?
      row["subjectCodes"].split(",").each do |c|
        next if c.blank?
        subject_name = RoConversion.get_subject_name(c)
        if subject_name.blank?
          err_msg += "subjectCodesが不正。"
          break
        end
      end
    end
    #periods
    #err_msg += "specialNeedsに値なし。" if row["metadata.jp.specialNeeds"].blank?
    err_msg += "specialNeedsが不正。" if row["metadata.jp.specialNeeds"].present? && row["metadata.jp.specialNeeds"].downcase != "true" && row["metadata.jp.specialNeeds"].downcase != "false"
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_user()
  #
  #userエラーチェック
  #
  # row                        ・・行データ
  # org_sourced_ids            ・・組織sourced_idリスト
  # class_homeroom_sourced_ids ・・ホームルームクラスsourced_idリスト
  # class_subject_sourced_ids  ・・クラス教科sourced_idリスト
  # user_master_identifiers    ・・ユーザ識別子リスト（UUID）
  #
  def self.validate_ro_user(row, org_sourced_ids={}, class_homeroom_sourced_ids = {}, class_subject_sourced_ids = {}, user_master_identifiers=[])
    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "enabledUserに値なし。" if row["enabledUser"].blank?
    err_msg += "enabledUserが不正。" if row["enabledUser"].present? && row["enabledUser"].downcase != "true"
    err_msg += "usernameに値なし。" if row["username"].blank?
    err_msg += "userIdsが不正。" unless check_userids(row["userIds"])
    err_msg += "givenNameに値なし。" if row["givenName"].blank?
    err_msg += "givenNameが不正（半角カタカナが存在）。"  if row["givenName"].present? && !check_han_katakana(row["givenName"])
    err_msg += "familyNameに値なし。" if row["familyName"].blank?
    err_msg += "familyNameが不正（半角カタカナが存在）。"  if row["familyName"].present? && !check_han_katakana(row["familyName"])
    err_msg += "middleNameが不正（半角カタカナが存在）。"  if row["middleName"].present? && !check_han_katakana(row["middleName"])
    len1 = (row["givenName"].presence ? row["givenName"].length : 0)
    len1 += row["familyName"].length if row["familyName"].present?
    len1 += row["middleName"].length if row["middleName"].present?
    err_msg += "Nameが200文字以上。" if len1 > 200
    #identifier
    #email
    #sms
    #phone
    #agentSourcedIds
    if row["grades"].present?
      row["grades"].split(",").each do |g|
        next if g.blank?
        grade_cd = RoConversion.get_grade(g)
        if grade_cd.blank?
          err_msg += "gradesが不正。"
          break
        end
      end
    end
    #password
    err_msg += "userMasterIdentifierに値なし。" if row["userMasterIdentifier"].blank?
    err_msg += "userMasterIdentifierがUUIDv4形式ではありません。" if row["userMasterIdentifier"].present? && !check_uuid_v4(row["userMasterIdentifier"])
    #userMasterIdentifier重複チェック
    err_msg += "userMasterIdentifierが重複。" if user_master_identifiers.include?(row["userMasterIdentifier"])
    #resourceSourcedIds
    err_msg += "preferredGivenNameに値なし。" if row["preferredGivenName"].blank?
    err_msg += "preferredGivenNameが不正（半角カタカナが存在）。"  if row["preferredGivenName"].present? && !check_han_katakana(row["preferredGivenName"])
    err_msg += "preferredFamilyNameに値なし。" if row["preferredFamilyName"].blank?
    err_msg += "preferredFamilyNameが不正（半角カタカナが存在）。"  if row["preferredFamilyName"].present? && !check_han_katakana(row["preferredFamilyName"])
    err_msg += "preferredMiddleNameが不正（半角カタカナが存在）。"  if row["preferredMiddleName"].present? && !check_han_katakana(row["preferredMiddleName"])
    len2 = (row["preferredGivenName"].presence ? row["preferredGivenName"].length : 0)
    len2 += row["preferredMiddleName"].length if row["preferredMiddleName"].present?
    len2 += row["preferredFamilyName"].length if row["preferredFamilyName"].present?
    err_msg += "preferredNameが200文字以上。" if len2 > 200
    err_msg += "primaryOrgSourcedIdが不正(orgsファイルに定義がありません)。" if row["primaryOrgSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["primaryOrgSourcedId"]].blank?
    #pronouns
    err_msg += "metadata.jp.kanaGivenNameに値なし。" if row["metadata.jp.kanaGivenName"].blank?
    err_msg += "metadata.jp.kanaFamilyNameに値なし。" if row["metadata.jp.kanaFamilyName"].blank?
    err_msg += "metadata.jp.kanaGivenNameが不正（全角カタカナでない）。" unless check_zen_katakana(row["metadata.jp.kanaGivenName"])
    err_msg += "metadata.jp.kanaFamilyNameが不正（全角カタカナでない）。" unless check_zen_katakana(row["metadata.jp.kanaFamilyName"])
    err_msg += "metadata.jp.kanaMiddleNameが不正（全角カタカナでない）。" unless check_zen_katakana(row["metadata.jp.kanaMiddleName"])
    len3 = (row["metadata.jp.kanaGivenName"].presence ? row["metadata.jp.kanaGivenName"].length : 0)
    len3 += row["metadata.jp.kanaFamilyName"].length if row["metadata.jp.kanaFamilyName"].present?
    len3 += row["metadata.jp.kanaMiddleName"].length if row["metadata.jp.kanaMiddleName"].present?
    err_msg += "kanaNameが200文字以上。" if len3 > 200
    err_msg += "metadata.jp.homeClassに値なし。" if row["metadata.jp.homeClass"].blank?
    class_sourced_ids = {}
    class_homeroom_sourced_ids.each do |schoolSourcedId, val|
       class_sourced_ids.merge!(val)
    end
    class_subject_sourced_ids.each do |schoolSourcedId, val|
       class_sourced_ids.merge!(val)
    end
    err_msg += "metadata.jp.homeClassが不正(classesファイルに定義がありません)。" if (row["metadata.jp.homeClass"].present? && class_sourced_ids.blank?) || (row["metadata.jp.homeClass"].present? && class_sourced_ids.present? && class_sourced_ids[row["metadata.jp.homeClass"]].blank?)
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_enrollment()
  #
  #enrollmentエラーチェック
  #
  # row                        ・・行データ
  # org_sourced_ids            ・・組織sourced_idリスト
  # user_sourced_ids           ・・ユーザsourced_idリスト
  # class_homeroom_sourced_ids ・・ホームルームクラスsourced_idリスト
  # class_subject_sourced_ids  ・・クラス教科sourced_idリスト
  #
  def self.validate_ro_enrollment(row, org_sourced_ids={}, user_sourced_ids = {}, class_homeroom_sourced_ids = {}, class_subject_sourced_ids = {})

    class_sourced_ids = Marshal.load(Marshal.dump(class_homeroom_sourced_ids[row["schoolSourcedId"]]))
    class_sourced_ids = {} if class_sourced_ids.blank?
    class_sourced_ids.merge!(class_subject_sourced_ids[row["schoolSourcedId"]]) if class_subject_sourced_ids[row["schoolSourcedId"]].present?

    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "schoolSourcedIdに値なし。" if row["schoolSourcedId"].blank?
    err_msg += "schoolSourcedIdが不正(orgsファイルに定義がありません)。" if (row["schoolSourcedId"].present? && org_sourced_ids.blank?) || (row["schoolSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["schoolSourcedId"]].blank?)
    err_msg += "schoolSourcedIdが不正(schoolではない)。" if row["schoolSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["schoolSourcedId"]].present? && org_sourced_ids[row["schoolSourcedId"]]["type"] != "school"
    err_msg += "classSourcedIdに値なし。"  if row["classSourcedId"].blank?
    err_msg += "classSourcedIdが不正(classesファイルに定義がありません)。" if (row["classSourcedId"].present? && class_sourced_ids.blank?) || (row["classSourcedId"].present? && class_sourced_ids.present? && class_sourced_ids[row["classSourcedId"]].blank?)
    err_msg += "userSourcedIdに値なし。" if row["userSourcedId"].blank?
    err_msg += "userSourcedIdが不正(usersファイルに定義がありません)。" if (row["userSourcedId"].present? && user_sourced_ids.blank?) || (row["userSourcedId"].present? && user_sourced_ids.present? && user_sourced_ids[row["userSourcedId"]].blank?)
    err_msg += "roleに値なし。" if row["role"].blank?
    err_msg += "roleが不正。" if row["role"].present? && row["role"]!="teacher" && row["role"]!="student" && row["role"]!="administrator" && row["role"]!="proctor"
    err_msg += "primaryに値なし。" if row["primary"].blank?
    err_msg += "primaryが不正。" if row["role"]=="student" && row["primary"].present? && row["primary"].downcase != "false"
    err_msg += "primaryが不正。" if row["role"]=="teacher" && row["primary"].present? && row["primary"].downcase != "true" && row["primary"].downcase != "false"
    err_msg += "beginDateが不正。" unless check_date(row["beginDate"])
    err_msg += "endDateが不正。" unless check_date(row["endDate"])
    err_msg += "ShussekiNoが不正。" unless check_int(row["metadata.jp.ShussekiNo"])
    err_msg += "PublicFlgが不正。" if row["metadata.jp.PublicFlg"].present? && row["metadata.jp.PublicFlg"].downcase != "true" && row["metadata.jp.PublicFlg"].downcase != "false"
    return err_msg
  end


  #====ImportOneRosterDataHelper.validate_ro_role()
  #
  #roleエラーチェック
  #
  # row                        ・・行データ
  # org_sourced_ids            ・・組織sourced_idリスト
  # user_sourced_ids           ・・ユーザsourced_idリスト
  # primary_user_sourced_ids   ・・roleがprimaryのsourced_idリスト
  #
  def self.validate_ro_role(row, org_sourced_ids={}, user_sourced_ids={}, primary_user_sourced_ids={})
    err_msg = ""
    err_msg += "sourcedIdに値なし。" if row["sourcedId"].blank?
    err_msg += "sourcedIdがUUID形式ではありません。" if row["sourcedId"].present? && !check_uuid(row["sourcedId"])
    err_msg += "statusが不正。" unless check_status(row["status"])
    err_msg += "dateLastModifiedが不正。" unless check_datetime(row["dateLastModified"])
    err_msg += "userSourcedIdに値なし。" if row["userSourcedId"].blank?
    err_msg += "userSourcedIdが不正(usersファイルに定義がありません)。" if (row["userSourcedId"].present? && user_sourced_ids.blank?) || (row["userSourcedId"].present? && user_sourced_ids.present? && user_sourced_ids[row["userSourcedId"]].blank?)
    err_msg += "roleTypeに値なし。" if row["roleType"].blank?
    err_msg += "roleTypeが不正。" if row["roleType"].present? && row["roleType"] != "primary" && row["roleType"] != "secondary"
    err_msg += "roleType:primaryデータなし。" if row["userSourcedId"].present? && row["roleType"] == "secondary" && !primary_user_sourced_ids.include?(row["userSourcedId"])
    err_msg += "roleに値なし。" if row["role"].blank?
    err_msg += "beginDateが不正。" unless check_date(row["beginDate"])
    err_msg += "endDateが不正。" unless check_date(row["endDate"])
    err_msg += "orgSourcedIdに値なし。" if row["orgSourcedId"].blank?
    err_msg += "orgSourcedIdが不正(orgsファイルに定義がありません)。" if (row["orgSourcedId"].present? && org_sourced_ids.blank?) || (row["orgSourcedId"].present? && org_sourced_ids.present? && org_sourced_ids[row["orgSourcedId"]].blank?)
    #userProfileSourcedId
    return err_msg
  end


  #====ImportOneRosterDataHelper.check_uuid()
  #
  #UUID形式チェック
  # str  ・・ 文字列
  #
  def self.check_uuid(str)
    w_str = str.downcase   #大文字は小文字にしてチェック（大文字でもOK）
    return !(w_str !~ /([0-9a-f]{8})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{4})-([0-9a-f]{12})/)
  end


  #====ImportOneRosterDataHelper.check_uuid_v4()
  #
  #UUIDv4形式チェック
  # str  ・・ 文字列
  #
  def self.check_uuid_v4(str)
    w_str = str.downcase   #大文字は小文字にしてチェック（大文字でもOK）
    return !(w_str !~ /([0-9a-f]{8})-([0-9a-f]{4})-(4[0-9a-f]{3})-([0-9a-f]{4})-([0-9a-f]{12})/)
  end


  #====ImportOneRosterDataHelper.check_status()
  #
  #statusチェック
  # str  ・・ 文字列
  #
  def self.check_status(str)
    return true if str.blank? || str == "active" || str == "tobedeleted"
    return false
  end


  #====ImportOneRosterDataHelper.check_date()
  #
  #日付形式チェック
  # str  ・・ 文字列
  #
  def self.check_date(str)
    return true if str.blank?
    return true if OneRosterHelper.date_strptime(str).present?
    return false
  end


  #====ImportOneRosterDataHelper.check_datetime()
  #
  #日付時間形式チェック
  # str  ・・ 文字列
  #
  def self.check_datetime(str)
    return true if str.blank?
    return true if OneRosterHelper.utc_datetime_strptime(str).present?
    return false
  end


  #====ImportOneRosterDataHelper.check_int()
  #
  #整数チェック
  # str  ・・ 文字列
  #
  def self.check_int(str)
    return true if str.blank?
    begin
      i = str.to_i
    rescue => e
      return false
    end
    return true
  end


  #====ImportOneRosterDataHelper.check_zen_katakana()
  #
  #全角カタカナチェック
  # str  ・・ 文字列
  #
  def self.check_zen_katakana(str)
    return true if str.blank?
    str2 = str.gsub(" ","")
    return !(str2 !~ /\A[ァ-ヶー]+\z/)
  end


  #====ImportOneRosterDataHelper.check_han_katakana()
  #
  #半角カタカナチェック
  # str  ・・ 文字列
  #
  def self.check_han_katakana(str)
    return true if str.blank?
    ["ｱ","ｲ","ｳ","ｴ","ｵ","ｶ","ｷ","ｸ","ｹ","ｺ","ｻ","ｼ","ｽ","ｾ","ｿ","ﾀ","ﾁ","ﾂ","ﾃ","ﾄ","ﾅ","ﾆ","ﾇ","ﾈ","ﾉ",
     "ﾊ","ﾋ","ﾌ","ﾍ","ﾎ","ﾏ","ﾐ","ﾑ","ﾒ","ﾓ","ﾔ","ﾕ","ﾖ","ﾗ","ﾘ","ﾙ","ﾚ","ﾛ","ﾜ","ｦ","ﾝ",
     "ｧ","ｨ","ｩ","ｪ","ｫ","ｯ","ｬ","ｭ","ｮ","ｰ","ｶﾞ","ｷﾞ","ｸﾞ","ｹﾞ","ｺﾞ","ｻﾞ","ｼﾞ","ｽﾞ","ｾﾞ","ｿﾞ",
     "ﾀﾞ","ﾁﾞ","ﾂﾞ","ﾃﾞ","ﾄﾞ","ﾊﾞ","ﾋﾞ","ﾌﾞ","ﾍﾞ","ﾎﾞ","ﾊﾟ","ﾋﾟ","ﾌﾟ","ﾍﾟ","ﾎﾟ","ｳﾞ"].each do |c|
      if str.include?(c)
        return false
        break
       end
    end 
    return true
  end


  #====ImportOneRosterDataHelper.check_userids()
  #
  #userid形式チェック  "{koumu:Id},{MS:Id},{Google:Id}"
  # user_ids  ・・ 文字列
  #
  def self.check_userids(user_ids)
    return true if user_ids.blank?
    user_ids.split(",").each do |val|
      return false if val !~ /{.+:.+}/
    end
    return true
  end

end
