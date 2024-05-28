# DA2022
Digital Agency project in 2022 for exchange educational data by 1EdTech standards

## 概要
DA2022は[デジタル庁実証調査研究支援プロジェクト](https://www.digital.go.jp/news/dcdf7f73-55ba-44b3-a482-fd892e0cbaff/)の略称になります。
DA2022プロジェクト内にて[1EdTech](https://www.1edtechjapan.org/technical-standard)標準である[Learning Tools Interoperability version 1.3 (LTI1.3)](https://www.1edtechjapan.org/_files/ugd/0c34cf_af01fc64edc24ad6b664d0d0dd4daa27.pdf)/[OneRoster version 1.2](https://www.1edtechjapan.org/_files/ugd/0c34cf_1b8475cb3a124cd6a80d0dcd4adaa752.pdf)・学習経験データを保持するための標準規格である[xAPI](https://www.gingerapp.co.jp/service/xapi_lrs.html)のソースコードが作成されております。
本リポジトリでは作成されたソースコードについて再利用を目的として公開しています。

## GitHub構成
それぞれのソースコードは規格・事業者別にディレクトリを作成し管理しています。

## 規格
* LTI1.3 Tools
* LTI1.3 Platform
* OneRoster1.2 REST 入力
* OneRoster1.2 REST 出力
* OneRoster1.2 CSV 入力
* OneRoster1.2 CSV 出力
* xAPI 出力

## 構成要素
表に規格・事業者別にそれぞれのソースコードの構成要素を記載します。

### LTI1.3

 | 事業者名 | 規格 | ソースコード言語 | フレームワーク | 基にしたLTIライブラリ | ライセンス | DeepLinkingの対応 | AGSの対応 | NRPSの対応 |
 | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
 | A社 | LTI1.3 Tools | Ruby | Ruby on Rails | 記載なし | MIT | × | × | × |
 | B社 | LTI1.3 Tools | PHP | Laravel | 1EdTech/lti-1-3-php-library | MIT | 〇 | 〇 | 〇 |
 | D社 | LTI1.3 Tools | Java , PHP | なし | LTI com.auth0 java-jwt 4.2.1 、java.security | MIT | × | × | × |
 | F社 | LTI1.3 Tools | PHP | Laravel | 1EdTech/lti-1-3-php-library | MIT | × | × | × |
 | H社 | LTI1.3 Tools | Python | Flask | dmitry-viskov/pylti1.3 | MIT | × | × | × |
 | I社 | LTI1.3 Tools | Java | Spring Boot | Unicon/tool13demo | MIT | × | × | × |
 | J社 | LTI1.3 Tools | Ruby，Haskell | Ruby on Rails，Servant | 記載なし | MIT | × | × | × |
 | M社 | LTI1.3 Tools | Java | なし | java-jwt / fusionauth-jwt | MIT | × | × | × |
 | N社 | LTI1.3 Tools | Ruby | Ruby on Rails | 1EdTech/lti-1-3-php-library / dmitry-viskov/pylti1.3 / Cvmcosta/ltijs / omniauth_openid_connect | MIT | × | × | × |
 | O社 | LTI1.3 Tools | PHP | なし | 1EdTech/lti-1-3-php-library | MIT | × | × | × |
 | P社 | LTI1.3 Tools | Python | Flask | PyLTI1p3 | MIT | 〇 | × | × |
 | Q社 | LTI1.3 Tools | JavaScript , Node.js |  Express.js | Cvmcosta/ltijs | MIT | × | × | × |
 | R社 | LTI1.3 Tools | JavaScript , Node.js |  Express.js | Cvmcosta/ltijs | MIT | × | × | × |
 | T社 | LTI1.3 Tools | Java | Sprint | spring-security-lti13 | Apache License | × | × | × |
 | U社 | LTI1.3 Tools | Java | Spring Boot | Unicon/tool13demo | MIT | × | × | × |
 | V社 | LTI1.3 Tools | PHP | Laravel | 1EdTech/lti-1-3-php-library | MIT | × | × | × |
 | W社 | LTI1.3 Tools | Java | Spring Boot | 記載なし | MIT | × | × | × |
 | X社 | LTI1.3 Tools | Java | Spring Boot | spring-security-lti13 | Apache License | × | × | 〇 |
 | Z社 | LTI1.3 Tools | Java | なし | Jjwt 0.9.1 / nimbus-jose-jwt 9.0.1 / guava 31.1 | MIT | × | × | × |
 | E社 | LTI1.3 Platform | Ruby，Haskell | Ruby on Rails，Servant | 記載なし | MIT | × | × | × |
 | X社 | LTI1.3 Platform | PHP | Yii | 記載なし | AGPL | 〇 | 〇 | 〇 |
 | Y社 | LTI1.3 Platform | Java | Spring Framework | net.shibboleth.oidc.common / net.shibboleth.idp.plugin.oidc.op | MIT | × | × | × |
 | AA社 | LTI1.3 Platform | PHP | CakePHP | 1EdTech/lti-1-3-php-library | MIT | 〇 | × | × |
 | C社 | LTI1.3 Platform | PHP | CakePHP | 1EdTech/lti-1-3-php-library | MIT | 〇 | 〇 | × |

### OneRoster1.2

 | 事業者名 | 規格 | ソースコード言語 | フレームワーク | 基になっているOneRosterライブラリ | ライセンス | 出力（入力）しているcsvファイル | 実装されているエンドポイント | 
 | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
 | X社 | OneRoster1.2 CSV出力 | JavaScript | Node.js ,  Express.js | 記載なし | MIT | manifest , academicSessions , classes , courses , enrollments , orgs , users , roles , demographics , userProfiles | - | 
 | G社 | OneRoster1.2 CSV出力 | C# | ASP.NET(.NET Framework 4.8) | 記載なし | MIT | academicSessions ,  classes ,  courses ,  demographics ,  enrollments ,  orgs ,  roles ,  users | - | 
 | L社 | OneRoster1.2 CSV出力 | Bat ,  SQL | なし | 記載なし | MIT | manifest ,  orgs ,  roles ,  users ,  academicSessions ,  classes ,  courses ,  enrollments | - | 
 | X社 | OneRoster1.2 CSV出力 | Windows PowerShell | なし | 記載なし | MIT | academicSessions ,  classes ,  courses ,  enrollments ,  orgs ,  users ,  manifest ,  userProfiles ,  roles ,  demographics | - | 
 | D社 | OneRoster1.2 CSV入力 | Java | なし | 記載なし | MIT | classes ,  courses ,  enrollments ,  orgs ,  users | - | 
 | F社 | OneRoster1.2 CSV入力 | Shell Script | なし | 記載なし | MIT | classes ,  enrollments ,  orgs ,  users | - | 
 | J社 | OneRoster1.2 CSV入力 | Ruby | Ruby on Rails | 記載なし | MIT | academicSessions ,  classes ,  courses ,  demographics ,  enrollements ,  orgs ,  roles ,  userProfiles ,  users | - | 
 | M社 | OneRoster1.2 CSV入力 | Java | Spring Framework | 記載なし | MIT | academicSessions ,  classes ,  corses ,  demographics ,  enrollments ,  orgs ,  roles ,  userProfiles ,  users | - | 
 | Q社 | OneRoster1.2 CSV入力 | JavaScript | Node.js ,  Express.js | 記載なし | MIT | orgs ,  roles ,  users | - | 
 | R社 | OneRoster1.2 CSV入力 | Dart | なし | 記載なし | MIT | academicSessions ,  classes ,  courses ,  enrollments ,  orgs ,  users | - | 
 | T社 | OneRoster1.2 CSV入力 | Java | Spring Framework | 記載なし | MIT | academicSessions ,  classes ,  courses ,  demographics ,  enrollments ,  manifest ,  orgs ,  roles ,  userProfiles ,  users | - | 
 | X社 | OneRoster1.2 CSV入力 | Ruby | なし | 記載なし | MIT | orgs , enrollments , classes , users | - | 
 | C社 | OneRoster1.2 CSV入力 | PHP | CakePHP | 記載なし | MIT | academicSessions ,  classes ,  courses ,  demographics ,  enrollments ,  orgs ,  roles ,  users | - | 
 | E社 | OneRoster1.2 CSV入力 | Ruby | Ruby on Rails | 記載なし | MIT | academicSessions ,  classes ,  courses ,  demographics ,  enrollements ,  orgs ,  roles ,  userProfiles ,  users | - | 
 | K社 | OneRoster1.2 CSV入力 | Python | なし | 記載なし | MIT | academicSessions ,  classes ,  courses ,  demographics ,  enrollments ,  manifest ,  orgs ,  roles ,  userProfiles ,  users | - | 
 | S社 | OneRoster1.2 CSV入力 | JavaScript | なし | 記載なし | MIT | users | - | 
 | X社 | OneRoster1.2 CSV入力 | JavaScript | Node.js ,  Express.js | 記載なし | MIT | manifest , academicSessions , classes , courses , enrollments , orgs , users , roles , demographics , userProfiles | - | 
 | Y社 | OneRoster1.2 CSV入力 | Python | なし | 記載なし | MIT | academicSessions ,  classes ,  demographics ,  enrollments ,  orgs ,  users ,  roles ,  manifest | - | 
 | AA社 | OneRoster1.2 CSV入力 | Ruby | なし | 記載なし | MIT | academicSessions ,  classes ,  courses ,  enrollments ,  manifest ,  orgs ,  roles ,  users | - | 
 | G社 | OneRoster1.2 REST出力 | C# | ASP.NET(.NET Framework 4.8) | 記載なし | MIT | - | getAcademicSession ,  getAllAcademicSessions ,  getAllClasses ,  getAllCourses ,  getAllDemographics ,  getAllEnrollments ,  getAllGradingPeriods ,  getAllOrgs ,  getAllSchools ,  getAllStudents ,  getAllTeachers ,  getAllTerms ,  getAllUsers ,  getClass ,  getClassesForCourse ,  getClassesForSchool ,  getClassesForStudent ,  getClassesForTeacher ,  getClassesForTerm ,  getClassesForUser ,  getCourse ,  getCoursesForSchool ,  getDemographics ,  getEnrollment ,  getEnrollmentsForClassInSchool ,  getEnrollmentsForSchool ,  getGradingPeriod ,  getGradingPeriodsForTerm ,  getOrg ,  getSchool ,  getStudent ,  getStudentsForClass ,  getStudentsForClassInSchool ,  getStudentsForSchool ,  getTeacher ,  getTeachersForClass ,  getTeachersForClassInSchool ,  getTeachersForSchool ,  getTerm ,  getTermsForSchool ,  getUser | 
 | X社 | OneRoster1.2 REST出力 | C# | ASP.NET(.NET Framework 4.8) | 記載なし | MIT | - | getAllAcademicSessions ,  getAcademicSession ,  getAllClasses ,  getClass ,  getAllCourses ,  getCourse ,  getAllEnrollments ,  getEnrollment ,  getAllGradingPeriods ,  getGradingPeriod ,  getAllOrgs ,  getOrg  , getAllSchools ,  getSchool ,  getAllStudents ,  getStudent ,  getAllTeachers ,  getTeacher ,  getAllTerms ,  getTerm ,  getAllUsers , getUser | 
 | B社 | OneRoster1.2 REST入力 | C++ | なし | 記載なし | MIT | - | getAllOrgs ,  getAllStudents ,  getAllTeachers ,  getStudentsForSchool ,  getTeacherForSchool | 
 | I社 | OneRoster1.2 REST入力 | Java | Spring Boot | 記載なし | MIT | - | getAllClasses ,  getAllOrgs ,  getAllUsers | 
 | U社 | OneRoster1.2 REST入力 | Java | Spring Boot | 記載なし | MIT | - | getAllClasses ,  getAllOrgs ,  getAllUsers | 
 | Y社 | OneRoster1.2 REST入力 | Python | なし | 記載なし | MIT | - | getAllAcademicSessions ,  getAllClasses ,  getAllDemographics ,  getAllEnrollments ,  getAllOrgs ,  getAllUsers | 

### xAPI

 | 事業者名 | 規格 | ソースコード言語 | フレームワーク | 基にしたxAPIプロファイル | ライセンス | 
 | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
 | A社 | xAPI出力 | JavaScript | Node.js | ADL Vocabulary/Audio Profile | MIT | 
 | B社 | xAPI出力 | PHP | Laravel | atrcallbrix/multilangsupport-ja/jpedudataspec | MIT | 
 | D社 | xAPI出力 | Java | なし | ADL Vocabulary | MIT | 
 | F社 | xAPI出力 | PHP | Laravel | ADL Vocabulary/TinCan Vocabulary | MIT | 
 | H社 | xAPI出力 | Python | なし | ADL Vocabulary/TinCan Vocabulary | MIT | 
 | I社 | xAPI出力 | Java | Spring Boot | ADL Vocabulary | MIT | 
 | O社 | xAPI出力 | PHP | なし | ADL Vocabulary / TinCan Vocabulary | MIT | 
 | U社 | xAPI出力 | Java | Spring Boot | ADL Vocaburary | MIT | 
 | Z社 | xAPI出力 | Java | なし | ADL Vocaburary | MIT | 

## ライセンスについて
ライセンスはそれぞれの事業者のフォルダ内にあるLICENSEもしくはLICENE.txtに準拠してください。

## 謝辞
本成果物はデジタル庁実証調査研究支援プロジェクトの成果物になります。
