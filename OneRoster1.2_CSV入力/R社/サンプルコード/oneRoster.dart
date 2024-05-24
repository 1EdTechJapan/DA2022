import 'dart:convert';

import 'package:archive/archive.dart';
import 'package:csv/csv.dart';

class OneRoster {
  Map<String, List<List<dynamic>>> main;
  Map<String, String> fileType = {};
  OneRoster(this.main);

  // この値をfalseにするとjapanProfileではない国際標準のcsvファイルを読み込める。
  bool japanProfile = true;

  static checkZip(Iterable<dynamic> zipFile, Function ok, Function ng) {
    OneRoster? or;
    try {
      var ar = ZipDecoder().decodeBuffer(InputStream(zipFile));
      Map<String, List<List<dynamic>>> map = {};
      for (var f in ar.files) {
        if (f.isFile) {
          f.decompress();
          String s = utf8.decode(f.content);

          var crlf = s.contains("\r\n");

          // ファイルの改行コードに応じて外部ライブラリへ改行コードを切り替えている。
          // imsglobalで提供されているテストファイルと、japan profileのテストファイルとで
          // 使用している改行コードが異なっているため。

          var l = CsvToListConverter()
              .convert(s, shouldParseNumbers: false, eol: crlf ? "\r\n" : "\n");

          map[f.name] = l;
        }
      }

      or = OneRoster(map);
      or.check();

      // ここで or にエラーチェックが完了したデータが格納されているので、内部DBへの登録関数を呼び出す。
      // データにエラーが発生した場合はthrowされここは呼ばれない。
      // 本ソースコードでは省略

      ok();
    } catch (e) {
      ng("${or?.base ?? 'base'} $e");
    }
  }

  Map<String, dynamic> property(List<List<dynamic>> x) {
    Map<String, dynamic> m = {};
    var h = x[0];
    if (h[0] != "propertyName") error("no propertyName");
    if (h[1] != "value") error("no value");
    for (int i = 1; i < x.length; i++) {
      h = x[i];
      if (h.length >= 2) {
        m[h[0]] = h[1];
      }
    }
    return m;
  }

  List<Map<String, dynamic>> listMap(List<List<dynamic>> x) {
    List<Map<String, dynamic>> l = [];
    if (x.length < 2) error("invalid list");
    List<dynamic> names = x[0];
    for (int i = 1; i < x.length; i++) {
      List<dynamic> ll = x[i];
      Map<String, dynamic> m = {};
      for (int j = 0; j < names.length; j++) {
        if (j < ll.length) {
          var xx = ll[j];
          if (xx == '""') xx = "";
          m[names[j]] = xx;
        }
      }
      l.add(m);
    }

    return l;
  }

  Map<String, Map<String, dynamic>> keySourceId(List<Map<String, dynamic>> m) {
    Map<String, Map<String, dynamic>> map = {};
    for (var k in m) {
      var id = k["sourcedId"];
      if (id == null) error("no sourcedId");
      map[id] = k;
    }
    return map;
  }

  error(String mes) {
    throw (mes);
  }

  String base = "";
  check() {
    checkHankaku();

    checkManifest();
    checkAcademicSessions();
    checkClasses();
    checkCourses();
    checkDemographics();
    checkEnrollments();
    checkUsers();
    checkOrgs();
    checkRoles();
    checkUserProfiles();

    checkReferences();
  }

  //  関数命名規則
  //   checkXXXX : 直接呼ばれる関数。フォーマット違反の場合はthrowされる。
  //   ckXXXXX   : 間接的に呼ばれる関数。

  checkHankaku() {
    // 半角カナチェック
    var fn = main.keys.iterator;
    var hkana = RegExp(r'[ｦ-ﾟ]');
    while (fn.moveNext()) {
      var x = main[fn.current];
      var i = x!.iterator;
      while (i.moveNext()) {
        var j = i.current.iterator;
        while (j.moveNext()) {
          var s = j.current;
          if (hkana.hasMatch(s)) {
            base = fn.current;
            error("hankaku kana $s");
          }
        }
      }
    }
  }

  checkManifest() {
    // manifestのチェック
    base = "manifest.csv";
    var x = main[base];
    if (x == null) error("no manifest");

    var p = property(x!);

    if (p["manifest.version"] != "1.0") error("invalid manifest version");
    if (p["oneroster.version"] != "1.2") error("invalid oneroster version");

    for (var v in p.keys) {
      if (v.startsWith("file.")) {
        var fn = v.replaceAll("file.", "") + ".csv";
        var vv = p[v];
        if (vv == "absent") {
          if (main[fn] != null) error("exist $fn but manifest shows absent");
        }
        if (vv == "bulk") {
          if (main[fn] == null) error("absent $fn but manifest shows bulk");
        }
        if (vv == "delta") {
          if (main[fn] == null) error("absent $fn but manifest shows delta");
        }
        fileType[fn] = vv;
//        debugPrint("$v ${p[v]}");
      }
    }
//    debugPrint("$p");
  }

  nock(String? v, String mes) {
    // 値がnullか""以外はエラー
    if (v == null || v == "") error(mes);
  }

  noheader(Map<String, dynamic> m, String fname) {
    // fname という名前のheaderがない場合エラー
    if (m[fname] == null) error("no header $fname");
  }

  ckRegExp(String? x, RegExp rex, String mes) {
    // 値が正規表現rexであるかどうか。違う場合はエラー
    if (!rex.hasMatch(x ?? "")) {
      error(mes);
    }
  }

  ckUUID(String? x, String mes) {
    // 簡易的な uuid v4のチェック
    ckRegExp(x, RegExp(r'^........-....-4...-....-............$'), mes);
  }

  ckList(String? x, Function fn) {
    // リストの各要素に対して関数fnでチェックする。
    if (x == null || x == "") return;
    var a = x.split(',');
    var itr = a.iterator;
    while (itr.moveNext()) {
      var c = itr.current;
      if (c != "") {
        fn(c);
      }
    }
  }

  ckSubjectCodes(String? x, String mes) {
    // サブジェクトコードが正しいかどうか
    ckList(x, (c) => ckRegExp(c, RegExp(r'^[PJ][01][0-9]0$'), mes));
  }

  ckSchoolCode(String? x, String mes) {
    // 学校コードが正しいかどうか
    if (x == null || x == "") return;
    ckRegExp(x, RegExp(r'^[A-H][0-9]{12}$'), mes);
  }

  ckDiscrictCode(String? x, String mes) {
    // 自治体コードが正しいかどうか
    if (x == null || x == "") return;
    ckRegExp(x, RegExp(r'^[0-9]{6}$'), mes);
  }

  ckUserIds(String? x, String mes) {
    // 外部認証プロバイダーのuseridのチェック
    ckList(x, (c) => ckRegExp(c, RegExp(r'\{.*:.*\}'), mes));
  }

  ckHeader(Map<String, dynamic> m, List<String> hd) {
    // csvのheaderチェック
    for (var h in hd) {
      noheader(m, h);
    }
  }

  ckSelect(String? v, List<String> l, String mes) {
    // 値が空か、リストlのどれかと一致しているかのチェック
    // 値が空でなく、リストのどの要素とも一致しなければエラー
    if (v == null) error(mes);
    if (v == "" || l.contains(v)) return;
    error(mes);
  }

  ckBool(String? v, String mes) {
    // 真偽値かどうかのチェック
    ckSelect(v, ["true", "false"], mes);
  }

  ckGrades(String? v, String mes) {
    // 学年コードかどうかのチェック
    ckList(
        v,
        (c) => ckSelect(
            c,
            [
              "P1",
              "P2",
              "P3",
              "P4",
              "P5",
              "P6",
              "J1",
              "J2",
              "J3",
              "H1",
              "H2",
              "H3",
              "E1",
              "E2",
              "E3"
            ],
            mes));
  }

  ckDate(String? v, String mes) {
    // 日付のフォーマットかどうかのチェック
    try {
      if (v != null) {
        if (v != "") {
          var dt = DateTime.parse(v);
        }
      }
    } catch (e) {
      error(mes);
    }
  }

  ckstatus(String? v, String mes) {
    // deltaの場合のステータスかどうか
    ckSelect(v, ["active", "tobedeleted"], mes);
  }

  ckYear(String? v) {
    // 年のフォーマットかどうか
    // 2000より大きく3000よりちいさいとしている。
    try {
      if (v == "" || v == null) return;
      var i = int.parse(v);
      if (i < 2000 && i > 3000) error("invalid year");
    } catch (e) {
      error("invalid year");
    }
  }

  ckDuplicate(List<Map<String, dynamic>> data, String fieldName, String mes) {
    // 辞書のリストの各要素で、fieldNameの値が同じ場合があればエラー
    Set id = {};
    for (var l in data) {
      var x = l[fieldName];
      if (id.contains(x)) error(mes);
      id.add(x);
    }
  }

  ckPrimarySecondary(List<Map<String, dynamic>> data, String mes) {
    // districtAdmin, siteAdmin, principalは主ロールになれない
    // 主ロールをteacherとして、それらを副ロールにする

    Map<String, Map<String, dynamic>> userRoles = {};
    for (var l in data) {
      var usi = l["userSourcedId"];
      var role = l["role"];
      var roleType = l["roleType"];
      if (!userRoles.containsKey(usi)) {
        userRoles[usi] = {};
      }
      userRoles[usi]![role] = roleType;
    }
    for (var usi in userRoles.keys) {
      var m = userRoles[usi]!;

      ckPrimary(String r) {
        if (m[r] == "primary") error("$r can not primary");
        if (m[r] == "secondary" && m["teacher"] != "primary")
          error("$r must have the role of teacher as primary");
      }

      ckPrimary("districtAdministrator");
      ckPrimary("siteAdministrator");
      ckPrimary("principal");
    }
  }

  checkAcademicSessions() {
    // academinsession.csvのチェック

    base = "academicSessions.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);

    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "title",
        "type",
        "startDate",
        "endDate",
        "parentSourcedId",
        "schoolYear"
      ]);

      nock(p["sourcedId"], "no sourcedId");
      nock(p["title"], "no title");
      nock(p["type"], "no type");
      nock(p["startDate"], "no startDate");
      nock(p["endDate"], "no endDate");
      nock(p["schoolYear"], "no schoolYear");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");
      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckSelect(
          p["type"],
          ["gradingPeriod", "schoolYear", "semester", "term", "ext:quarter"],
          "invalid type");
      ckDate(p["startDate"], "invalid startDate");
      ckDate(p["endDate"], "invalid endDate");
      ckYear(p["schoolYear"]);

      if (japanProfile) {
        // japanprofileに特化したチェック

        ckRegExp(p["title"], RegExp(r'^....年度$'), "invalid title format");
        ckUUID(p["sourcedId"], "invalid sourcedId format");

        ckSelect(
            p["parentSourcedId"], ["NULL"], "invalid parentSourcedId value");
        nock(p["parentSourcedId"], "no parentSourcedId");

        if (p["type"] == "semester") error("invalid value type (semester)");
      }
    }
  }

  checkClasses() {
    // クラスのチェック
    base = "classes.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "title",
        "grades",
        "courseSourcedId",
        "classCode",
        "classType",
        "location",
        "schoolSourcedId",
        "termSourcedIds",
        "subjects",
        "subjectCodes",
        "periods"
      ]);

      nock(p["sourcedId"], "no sourcedId");
      nock(p["title"], "no title");
      nock(p["courseSourcedId"], "no courseSourcedId");
      nock(p["classType"], "no classType");
      nock(p["schoolSourcedId"], "no schoolSourcedId");
      nock(p["termSourcedIds"], "no termSourcedIds");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");
      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckSelect(p["classType"], ["homeroom", "scheduled", "ext:special"],
          "invalid classType");

      if (japanProfile) {
        // japanProfileに特化したチェック

        ckGrades(p["grades"], "invalid grades");

        ckHeader(p, [
          "sourcedId",
          "status",
          "dateLastModified",
          "title",
          "grades",
          "courseSourcedId",
          "classCode",
          "classType",
          "location",
          "schoolSourcedId",
          "termSourcedIds",
          "subjects",
          "subjectCodes",
          "periods",
          "metadata.jp.specialNeeds"
        ]);
        ckBool(p["metadata.jp.specialNeeds"], "invalid specialNeeds");
        ckSubjectCodes(p["subjectCodes"], "invalid subjectCodes");
      }
    }
  }

  checkCourses() {
    // coursesのチェック
    base = "courses.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "schoolYearSourcedId",
        "title",
        "courseCode",
        "grades",
        "orgSourcedId",
        "subjects",
        "subjectCodes"
      ]);

      nock(p["sourcedId"], "no sourcedId");
      nock(p["title"], "no title");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");
      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }
      if (japanProfile) {
        // japanProfileに特化したチェック

        ckRegExp(p["title"], RegExp(r'^....年度'), "invalid title format");
        if (p["courseCode"] != "") {
          ckRegExp(p["courseCode"], RegExp(r'^[0..1A..Za..z]'),
              "invalid courseCode");
        }
        ckGrades(p["grades"], "invalid grade");
        nock(p["orgSourcedId"], "no orgSourcedId");
        ckSubjectCodes(p["subjectCodes"], "invalid subjectCodes");
      }
    }
  }

  checkDemographics() {
    // demographicsのチェック

    base = "demographics.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "birthDate",
        "sex",
        "americanIndianOrAlaskaNative",
        "asian",
        "blackOrAfricanAmerican",
        "nativeHawaiianOrOtherPacificIslander",
        "white",
        "demographicRaceTwoOrMoreRaces",
        "hispanicOrLatinoEthnicity",
        "countryOfBirthCode",
        "stateOfBirthAbbreviation",
        "cityOfBirth",
        "publicSchoolResidenceStatus"
      ]);

      nock(p["sourcedId"], "no sourcedId");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");

      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckDate(p["birthDate"], "invalid birthDate");

      ckSelect(p["sex"], ["male", "female", "unspecified", "other", "ext:NB"],
          "invalid sex");

      ckBool(p["americanIndianOrAlaskaNative"], "invalid americanIndian..");
      ckBool(p["asian"], "invalid asian");
      ckBool(p["blackOrAfricanAmerican"], "invalid blackOrAfrican..");
      ckBool(p["nativeHawaiianOrOtherPacificIslander"],
          "invalid nativeHawaiian..");
      ckBool(p["white"], "invalid white");
      ckBool(p["demographicRaceTwoOrMoreRaces"], "invalid twoOrMoreRaces");
      ckBool(p["hispanicOrLatinoEthnicity"], "invalid hispanic");
    }
  }

  checkEnrollments() {
    // enrollmentのチェック

    base = "enrollments.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "classSourcedId",
        "schoolSourcedId",
        "userSourcedId",
        "role",
        "primary",
        "beginDate",
        "endDate"
      ]);

      nock(p["sourcedId"], "no sourcedId");
      nock(p["classSourcedId"], "no classSourcedId");
      nock(p["schoolSourcedId"], "no schoolSourcedId");
      nock(p["userSourcedId"], "no userSourcedId");
      nock(p["role"], "no role");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");

      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckDate(p["beginDate"], "invalid beginDate");
      ckDate(p["endDate"], "invalid endDate");

      ckSelect(
          p["role"],
          [
            "student",
            "teacher",
            "administrator",
            "guardian",
            "ext:demonstrator"
          ],
          "invalid role");

      ckBool(p["primary"], "invalid primary");

      if (japanProfile) {
        // japan profileに限定したチェック

        ckUUID(p["sourcedId"], "invalid UUID format sourcedId");
        if (p["role"] == "student" && p["primary"] == "true")
          error("primary==true for student");

        // headerが増えているので再度チェックしている
        ckHeader(p, [
          "sourcedId",
          "status",
          "dateLastModified",
          "classSourcedId",
          "schoolSourcedId",
          "userSourcedId",
          "role",
          "primary",
          "beginDate",
          "endDate",
          "metadata.jp.ShussekiNo",
          "metadata.jp.PublicFlg"
        ]);
        nock(p["primary"], "empty primary");
      }
    }
  }

  checkUsers() {
    // users のチェック
    base = "users.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "enabledUser",
        "username",
        "userIds",
        "givenName",
        "familyName",
        "middleName",
        "identifier",
        "email",
        "sms",
        "phone",
        "agentSourcedIds",
        "grades",
        "password",
        "userMasterIdentifier",
        "resourceSourcedIds",
        "preferredGivenName",
        "preferredMiddleName",
        "preferredFamilyName",
        "primaryOrgSourcedId",
        "pronouns"
      ]);
      nock(p["sourcedId"], "no sourcedId");
      nock(p["enabledUser"], "no enabledUser");
      nock(p["username"], "no username");
      nock(p["givenName"], "no givenName");
      nock(p["familyName"], "no familyName");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");

      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckBool(p["enabledUser"], "invalid enabledUser");

      if (japanProfile) {
        // japanprofileに特化したチェック

        ckHeader(p, [
          "sourcedId",
          "status",
          "dateLastModified",
          "enabledUser",
          "username",
          "userIds",
          "givenName",
          "familyName",
          "middleName",
          "identifier",
          "email",
          "sms",
          "phone",
          "agentSourcedIds",
          "grades",
          "password",
          "userMasterIdentifier",
          "resourceSourcedIds",
          "preferredGivenName",
          "preferredMiddleName",
          "preferredFamilyName",
          "primaryOrgSourcedId",
          "pronouns",
          "metadata.jp.kanaGivenName",
          "metadata.jp.kanaFamilyName",
          "metadata.jp.kanaMiddleName",
          "metadata.jp.homeClass"
        ]);
        nock(p["preferredGivenName"], "no preferredGivenName");
        nock(p["preferredFamilyName"], "no preferredFamilyName");
        nock(p["metadata.jp.kanaGivenName"], "no metadata.jp.kanaGivenName");
        nock(p["metadata.jp.kanaFamilyName"], "no metadata.jp.kanaFamilyName");
        nock(p["metadata.jp.homeClass"], "no metadata.jp.homeClass");
        ckGrades(p["grades"], "invalid grades");
        ckUUID(p["userMasterIdentifier"], "invalid userMasterIdentifire");
        ckUserIds(p["userIds"], "invalid UserIds format");
      }
    }
    if (japanProfile) {
      ckDuplicate(l, "userMasterIdentifier", "duplicate userMasterIdentifier");
    }
  }

  checkOrgs() {
    // orgsのチェック
    base = "orgs.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "name",
        "type",
        "identifier",
        "parentSourcedId"
      ]);

      nock(p["sourcedId"], "no sourcedId");
      nock(p["name"], "no name");
      nock(p["type"], "no type");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");

      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckSelect(
          p["type"],
          [
            "department",
            "district",
            "local",
            "national",
            "school",
            "state",
            "ext:technicalCollege"
          ],
          "invalid type");
      if (japanProfile) {
        // japanprofileに特化したチェック

        if (p["type"] == "district") {
          ckSelect(
              p["parentSourcedId"], ["NULL"], "parentSourcedId is not empty");
        }

        if (p["type"] == "school")
          ckSchoolCode(p["identifier"], "invalid school code");
        if (p["type"] == "district")
          ckDiscrictCode(p["identifier"], "invalid district code");
      }
    }
  }

  checkRoles() {
    // rolesのチェック

    base = "roles.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      nock(p["sourcedId"], "no sourcedId");
      nock(p["userSourcedId"], "no userSourcedId");
      nock(p["roleType"], "no roleType");
      nock(p["role"], "no role");
      nock(p["orgSourcedId"], "no orgSourcedId");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");

      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }

      ckSelect(p["roleType"], ["primary", "secondary"], "invalid roleType");
      ckSelect(
          p["role"],
          [
            "aide",
            "counseior",
            "districtAdministrator",
            "guardian",
            "parent",
            "principal",
            "proctor",
            "relative",
            "siteAdministrator",
            "student",
            "systemAdministrator",
            "teacher",
            "administrator",
            "ext:prefect"
          ],
          "invalid role");

      ckDate(p["beginDate"], "invalid beginDate");
      ckDate(p["endDate"], "invalid endDate");
      if (japanProfile) {
        // japan profileに特化したチェック
        ckUUID(p["sourcedId"], "invalid sourcedId UUID");
        ckSelect(
            p["role"],
            [
              "districtAdministrator",
              "guardian",
              "principal",
              "proctor",
              "siteAdministrator",
              "student",
              "systemAdministrator",
              "teacher",
            ],
            "invalid role");
      }
    }
    if (japanProfile) {
      ckPrimarySecondary(l, "invalid ruletype primary/secondary");
    }
  }

  checkUserProfiles() {
    // userprofilesのチェック
    base = "userProfiles.csv";
    var x = main[base];
    if (x == null) return;
    var l = listMap(x);
    for (var p in l) {
      ckHeader(p, [
        "sourcedId",
        "status",
        "dateLastModified",
        "userSourcedId",
        "profileType",
        "vendorId",
        "applicationId",
        "description",
        "credentialType",
        "username",
        "password"
      ]);

      nock(p["sourcedId"], "no sourcedId");
      nock(p["userSourcedId"], "no userSourcedId");
      nock(p["profileType"], "no profileType");
      nock(p["vendorId"], "no vendorId");
      nock(p["credentialType"], "no credentialType");
      nock(p["username"], "no username");

      ckstatus(p["status"], "invalid status");
      ckDate(p["dateLastModified"], "invalid dateLastModified");

      if (fileType[base] == "delta") {
        nock(p["status"], "no status");
        nock(p["dateLastModified"], "no dateLastModified");
      }
      if (japanProfile) {
        ckUUID(p["sourcedId"], "invalid sourcedId");
      }
    }
  }

  // 複数のDBに跨った関係をチェックする関数。参照先のデータが存在するかどうか。
  ckRef(var dbmain, String dbfrom, String fname, String dbto, [Function? cnd]) {
    var m = dbmain[dbfrom];
    if (m != null) {
      var m2 = dbmain[dbto];
      for (var kk in m.keys) {
        Map<String, dynamic> p = m[kk]!;
        var k = p[fname];
        if (k == "") return;
        if (k == "NULL") return;
        if (m2 == null) error("no db $dbto $fname");
        if (dbmain[dbto][k] == null) error("no link $dbfrom $fname");
        if (cnd != null) {
          cnd(dbmain[dbto][k]);
        }
      }
    }
  }

  checkReferences() {
    // 複数のdbに跨った関係をチェックする。

    base = "references";

    Map<String, Map<String, Map<String, dynamic>>> dbmain = {};
    var acs = "academicSessions";
    var cls = "classes";
    var clsr = "classResources";
    var crs = "courses";
    var crsr = "courseResources";
    var org = "orgs";
    var rsc = "resources";
    var usrr = "userResources";
    var usr = "users";
    var userp = "userProfiles";
    var role = "roles";
    var enr = "enrollments";
    var demo = "demographics";

    var dbname = [
      acs,
      cls,
      clsr,
      crs,
      crsr,
      org,
      rsc,
      usrr,
      usr,
      enr,
      demo,
      role,
      userp
    ];

    // 全てのファイル(DB)に対して
    for (var db in dbname) {
      var d = main["$db.csv"];
      if (d != null) {
        // sourcedIdをキーとするmapを作り登録する。
        var m = keySourceId(listMap(d));
        dbmain[db] = m;
      }
    }

    // cls(classes)の"courseSourcedId”に書かれているIdが crs(courses)のsourcedIdとしてあるかをチェックしている。
    ckRef(dbmain, cls, "courseSourcedId", crs);

    //以下同じ。
    ckRef(dbmain, cls, "schoolSourcedId", org);
    ckRef(dbmain, cls, "termSourcedIds", acs);

    ckRef(dbmain, crs, "orgSourcedId", org);
    ckRef(dbmain, crs, "schoolYearSourcedId", acs);

    ckRef(dbmain, enr, "classSourcedId", cls);
    ckRef(dbmain, enr, "schoolSourcedId", org);
    ckRef(dbmain, enr, "userSourcedId", usr);

    ckRef(dbmain, usr, "primaryOrgSourcedId", org);

    ckRef(dbmain, usr, "agentSourcedIds", usr);

    ckRef(dbmain, org, "parentSourcedId", org);

    ckRef(dbmain, role, "userSourcedId", usr);
    ckRef(dbmain, role, "userProfileSourcedId", userp);
    ckRef(dbmain, role, "orgSourcedId", org);

    ckRef(dbmain, userp, "userSourcedId", usr);

    if (japanProfile) {
      // japan Profileに特化したチェック。より複雑なロジックもチェックしている。

      // enr(enrollments)のschoolSourcedIdがorgにあるかどうか。
      // さらに見つかった場合はそのエントリーのtypeがschoolじゃなければエラー
      ckRef(dbmain, enr, "schoolSourcedId", org, (x) {
        if (x["type"] != "school") {
          error("enrollment schoolSourcedId refer non school org");
        }
      });

      // cls(classes)のschoolSourcedIdがorgにあるかどうか。
      // さらに見つかった場合はそのエントリーがtypeがschoolじゃなければエラー
      ckRef(dbmain, cls, "schoolSourcedId", org, (x) {
        if (x["type"] != "school") {
          error("classes schoolSourcedId refer non school org");
        }
      });

      ckRef(dbmain, demo, "sourcedId", usr);
      ckRef(dbmain, usr, "metadata.jp.homeClass", cls);
    }
  }
}
