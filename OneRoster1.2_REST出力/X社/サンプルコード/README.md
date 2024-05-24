# デジタル校務 OneRoster Rostering Service v1.2 Providers

## 1. 概要

校務-学習系の連携のため、IMS OneRosterJapanProfileV1.2が定める規格に合わせたRESTAPIを行います。

Rostering Service v1.2 Providersのサンプルコード主に以下内容を示しています。

* 認証：1EdTech セキュリティ フレームワークのOAuth 2.0 Client-Credentials Grantの仕様をサポートしています。
* データモデル： 1EdTechのOneRosterv1p2RosteringServiceInfoModelの仕様をサポートしています。
* エンドポイント： サービスプロバイダのRosteringコンフォーマンスの必須である22本のエンドポイントをサポートしています。

このサンプルコード（Rostering Service v1.2）は ASP.NET 4.8 Web プロジェットとなり、1EdTechのOneRoster標準準拠認定されています。

## 2. プロジェクト構成

```bash
EduKoumu.OneRosterService
├── App_Start                                              //アプリケーションの設定
│   ├── WebApiConfig.cs
│   ├── SwaggerConfig.cs
├── Auth                                                   //認証機能
│   ├── WebApiAuthorizeAttribute.cs
│   ├── OAuthContextExtension.cs
│   ├── OAuthProvider.cs
├── Configurations                                         //認証クライアント情報の設定
│   ├── ClientSettings.cs
│   ├── ClientsConfigSection.cs
│   ├── ClientSetting.cs
├── Controllers                                            //Rostering エンドポイント（※データの出力）
│   ├── UsersController.cs
│   ├── AcademicSessionsController.cs
│   ├── ClassesController.cs
│   ├── CoursesController.cs
│   ├── DefaultController.cs
│   ├── EnrollmentsController.cs
│   ├── GradingPeriodsController.cs
│   ├── OrgsController.cs
│   ├── SchoolsController.cs
│   ├── StudentsController.cs
│   ├── TeachersController.cs
│   ├── TermsController.cs
├── Functions                                              //REST APIの実装（データの取得）
│   ├── UserFunction.cs
│   ├── AcademicSessionFunction.cs
│   ├── ClassFunction.cs
│   ├── CourseFunction.cs
│   ├── EnrollmentFunction.cs
│   ├── OrgFunction.cs
│   ├── IAcademicSessionFunction.cs
│   ├── IClassFunction.cs
│   ├── ICourseFunction.cs
│   ├── IEnrollmentFunction.cs
│   ├── IOrgFunction.cs
│   ├── IUserFunction.cs
├── DataModels                                             //データモデル及びDbContext
│   ├── OneRosterDbContext.cs
│   ├── OR_UserProfile.cs
│   ├── OR_AcademicSession.cs
│   ├── OR_Class.cs
│   ├── OR_Client.cs
│   ├── OR_Course.cs
│   ├── OR_Demographics.cs
│   ├── OR_Enrollment.cs
│   ├── OR_Org.cs
│   ├── OR_Role.cs
│   ├── OR_User.cs
├── Mappers                                                //データモデルの間のデータ変換処理
│   ├── UserProfileMapper.cs
│   ├── AcademicSessionMapper.cs
│   ├── ClassMapper.cs
│   ├── CourseMapper.cs
│   ├── EnrollmentMapper.cs
│   ├── OrgMapper.cs
│   ├── RoleMapper.cs
│   ├── UserMapper.cs
├── DataTypes                                              //OneRosterV1.2の標準データモデル
│   ├── AcademicSession
│   │   ├── SingleAcademicSessionDType.cs
│   │   ├── AcademicSessionDType.cs
│   │   ├── AcademicSessionSetDType.cs
│   │   └── SessionTypeEnum.cs
│   ├── Class
│   │   ├── SingleClassDType.cs
│   │   ├── ClassDType.cs
│   │   ├── ClassSetDType.cs
│   │   └── ClassTypeEnum.cs
│   ├── Course
│   │   ├── SingleCourseDType.cs
│   │   ├── CourseDType.cs
│   │   └── CourseSetDType.cs
│   ├── Enrollment
│   │   ├── SingleEnrollmentDType.cs
│   │   ├── EnrollmentDType.cs
│   │   ├── EnrollmentSetDType.cs
│   │   └── EnrolRoleEnum.cs
│   ├── Org
│   │   ├── SingleOrgDType.cs
│   │   ├── OrgDType.cs
│   │   ├── OrgSetDType.cs
│   │   └── OrgTypeEnum.cs
│   ├── User
│   │   ├── UserSetDType.cs
│   │   ├── CredentialDType.cs
│   │   ├── RoleDType.cs
│   │   ├── RoleEnum.cs
│   │   ├── RoleTypeEnum.cs
│   │   ├── SingleUserDType.cs
│   │   ├── UserDType.cs
│   │   ├── UserIdDType.cs
│   │   └── UserProfileDType.cs
│   ├── Imsx
│   │   ├── StatusInfoDTypeImsx_severity.cs
│   │   ├── CodeMinorDType.cs
│   │   ├── CodeMinorFieldDType.cs
│   │   ├── CodeMinorFieldDTypeImsx_codeMinorFieldValue.cs
│   │   ├── StatusInfoDType.cs
│   │   └── StatusInfoDTypeImsx_codeMajor.cs
│   ├── BaseStatusEnum.cs
│   ├── GUIDRefDType.cs
│   ├── GUIDRefTypeEnum.cs
│   ├── OrderByEnum.cs
│   ├── TrueFalseEnum.cs
├── Exceptions                                             //例外処理
│   ├── UnprocessableEntityException.cs
│   ├── ForbiddenException.cs
│   ├── GlobalExceptionHandler.cs
│   ├── InvalidFilterFieldException.cs
│   ├── InvalidSelectionFieldException.cs
│   ├── TooManyRequestException.cs
│   ├── UnauthorisedException.cs
│   ├── UnknownObjectException.cs
├── Properties                                             //アセンブリに関する一般的情報
│   ├── AssemblyInfo.cs
├── Utils                                                  //ユーティリティクラスとユーティリティ関数
│   ├── SelectionFieldsHelper.cs
│   ├── DateConverter.cs
│   ├── DateTimeISO8601Converter.cs
│   ├── GUIDRefDTypeHelper.cs
│   ├── QueryHelper.cs
├── Consts.cs                                              //定数
├── EduKoumu.OneRosterService.csproj                       
├── Global.asax        
├── Global.asax.cs     
├── packages.config    
├── Startup.cs         
├── Web.config         
├── Web.Debug.config   
└── Web.Release.config 
```

## 3. 認証

OAuth 2.0 Client-Credentials Grantを利用しています。
`Web.config` にクライアントIDとクライアントシークレットを定義します。
OAuth2リクエストを行うには、トークンエンドポイントにアクセスし、アクセストークン取得を行い得られた結果を返却します。

## 4. データモデル

OneRoster モデルとのマッピングは以下のとおりです。

| OneRoster Model        | Data Model           |
|------------------------|----------------------|
| Academic Session       | OR_AcademicSession   |
| Class                  | OR_Class             |
| Course                 | OR_Course            |
| Enrollment             | OR_Enrollment        |
| Org                    | OR_Org               |
| User, Student, Teacher | OR_User              |
| Demographic            | OR_Demographics      |
| Role                   | OR_Role              |
| UserProfile            | OR_UserProfile       |

### バリデーション

バリデーション要件は、 [OneRoster model specification]と[IMS OneRosterJapanProfileV1.2]の定義に従います。

### ページネーション, フィルタリング, ソーティングなど

ページネーションメカニズム、フィルタリングメカニズム、ソーティングメカニズム[paging, filtering, and sorting](https://www.imsglobal.org/oneroster-v11-final-specification#_Toc480451994)をサポートしています。

#### ページネーション
* limit：返される結果の数。デフォルト値は100です。
* offset：返される最初のレコードのインデックス（0から始まる）。デフォルト値は0です。

#### フィルタリング
* sort=[data_field]
* orderBy=[asc|desc]

#### フィルタリング
* filter=[data_field][predicate][value] or [data_field][predicate][value][logical][data_field][predicate][value]
* フィルタークエリはURLエンコードする必要があります。

## 5. Rostering エンドポイント

### 以下のRosteringエンドポイント(読み取り)をサポートしています。

| サービス                        | エンドポイント                  | HTTPメソッド   |
|--------------------------------|--------------------------------|---------------|
| getAllAcademicSessions         | /academicSessions              | GET           |
| getAcademicSession             | /academicSessions/{sourcedId}  | GET           |
| getAllClasses                  | /classes                       | GET           |
| getClass                       | /classes/{sourcedId}           | GET           |
| getAllCourses                  | /courses                       | GET           |
| getCourse                      | /courses/{sourcedId}           | GET           |
| getAllEnrollments              | /enrollments                   | GET           |
| getEnrollment                  | /enrollments/{sourcedId}       | GET           |
| getAllGradingPeriods           | /gradingPeriods                | GET           |
| getGradingPeriod               | /gradingPeriods/{sourcedId}    | GET           |
| getAllOrgs                     | /orgs                          | GET           |
| getOrg                         | /orgs/{sourcedId}              | GET           |
| getAllSchools                  | /schools                       | GET           |
| getSchool                      | /schools/{sourcedId}           | GET           |
| getAllStudents                 | /students                      | GET           |
| getStudent                     | /students/{sourcedId}          | GET           |
| getAllTeachers                 | /teachers                      | GET           |
| getTeacher                     | /teachers/{sourcedId}          | GET           |
| getAllTerms                    | /terms                         | GET           |
| getTerm                        | /terms/{sourcedId}             | GET           |
| getAllUsers                    | /users                         | GET           |
| getUser                        | /users/{sourcedId}             | GET           |

## 6. 参考資料

### 詳細は以下のOneRoster 1.2 Rostering Serviceの標準仕様に参照。

* [OneRoster 1.2 Rostering Service Information Model](https://www.imsglobal.org/sites/default/files/spec/oneroster/v1p2/rostering-informationmodel/OneRosterv1p2RosteringService_InfoModelv1p0.html)
* [OneRoster 1.2 Rostering Service REST Binding](https://www.imsglobal.org/sites/default/files/spec/oneroster/v1p2/rostering-restbinding/OneRosterv1p2RosteringService_RESTBindv1p0.html)
* [IMS OneRoster: Conformance and Certification](https://www.imsglobal.org/spec/oneroster/v1p2/cert/)
