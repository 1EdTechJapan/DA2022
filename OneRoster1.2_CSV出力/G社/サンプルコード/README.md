# ASP.NET OneRosterCSV・REST サンプル

## ■ 概要

校務支援システムのデータを任意のデータベースから MongoDB に変換し OneRosterCSV 出力する OneRosterCSV プロジェクトと、
MongoDB から REST API で出力する OneRosterREST プロジェクトを含む。任意のデータベースから MongoDB に変換する箇所は
校務支援システムに合わせて追加で実装する必要がある。OneRosterREST プロジェクトには AuthorizationServer と ResourceServer が存在しており
AuthorizationServer は OAuth 2.0 Client Credentials を担当し、ResourceServer は REST API を担当する。

## ■ 環境

ASP.NET(.NET Framework 4.8)  
MongoDB 6.0.3 Community

## ■ 各ディレクトリとファイルについて

```
.
├── OneRosterCSV
│   ├── OneRosterCSV
│   │   ├── Global.asax
│   │   ├── Global.asax.cs: 設定および共通処理
│   │   ├── Models: 構造を表すファイル群
│   │   │   ├── AcademicSessionModel.cs
│   │   │   ├── ClassesModel.cs
│   │   │   ├── CoursesModel.cs
│   │   │   ├── DemographicsModel.cs
│   │   │   ├── EnrollmentsModel.cs
│   │   │   ├── GradingPeriodsModel.cs
│   │   │   ├── JapanSpecialModel.cs
│   │   │   ├── ManifestModel.cs
│   │   │   ├── OrgsModel.cs
│   │   │   ├── SchoolsModel.cs
│   │   │   ├── StudentsModel.cs
│   │   │   ├── TeachersModel.cs
│   │   │   ├── TermsModel.cs
│   │   │   └── UsersModel.cs
│   │   ├── OneRosterCSV.csproj
│   │   ├── Properties
│   │   │   └── AssemblyInfo.cs
│   │   ├── ProprietaryConverter.cs: 任意のデータベースから MongoDB に変換する処理
│   │   ├── Start.aspx: プロジェクト開始ページ
│   │   ├── Start.aspx.cs
│   │   ├── Start.aspx.designer.cs
│   │   ├── Web.Debug.config
│   │   ├── Web.Release.config
│   │   ├── Web.config
│   │   ├── libmongocrypt.dylib
│   │   ├── libmongocrypt.so
│   │   ├── mongocrypt.dll
│   │   └── packages.config
│   └── OneRosterCSV.sln: OneRosterCSV のソリューションファイル
├── OneRosterREST
│   ├── AuthorizationServer: 認証サーバー
│   │   ├── AuthorizationServer.csproj
│   │   ├── Properties
│   │   │   └── AssemblyInfo.cs
│   │   ├── Startup.cs: OAuth認証部
│   │   ├── Web.Debug.config
│   │   ├── Web.Release.config
│   │   ├── Web.config: OAuthアクセストークンの暗号化キー含む(ResourceServerと同値にしておくこと、セキュリティのために必ず再作成すること)
│   │   └── packages.config
│   ├── ClientCredentialGrant.sln: OneRosterREST のソリューションファイル
│   └── ResourceServer: REST APIサーバー
│       ├── Global.asax
│       ├── Global.asax.cs: 設定および共通処理
│       ├── Properties
│       │   └── AssemblyInfo.cs
│       ├── ResourceServer.csproj
│       ├── RestException.cs
│       ├── RestParser.cs: REST API リクエスト解析部
│       ├── Startup.cs
│       ├── Web.Debug.config
│       ├── Web.Release.config
│       ├── Web.config: OAuthアクセストークンの暗号化キー含む(AuthorizationServerと同値にしておくこと、セキュリティのために必ず再作成すること)
│       ├── assets
│       │   └── onerosterv1p2rostersservice_openapi3_v1p0.json
│       ├── controllers: REST API コントローラー群
│       │   ├── AcademicSessionsController.cs
│       │   ├── ClassesController.cs
│       │   ├── CoursesController.cs
│       │   ├── DemographicsController.cs
│       │   ├── DiscoveryController.cs
│       │   ├── EnrollmentsController.cs
│       │   ├── GradingPeriodsController.cs
│       │   ├── OrgsController.cs
│       │   ├── SchoolsController.cs
│       │   ├── StudentsController.cs
│       │   ├── TeachersController.cs
│       │   ├── TermsController.cs
│       │   └── UsersController.cs
│       ├── libmongocrypt.dylib
│       ├── libmongocrypt.so
│       ├── models: 構造を表すファイル群
│       │   ├── ErrorModel.cs
│       │   └── GUIDRefModel.cs
│       ├── mongocrypt.dll
│       └── packages.config
└── README.md
```

## ■ OneRosterCSV サンプル実行

MongoDB をあらかじめインストールする。  
サンプルでは「mongodb://localhost:27017」として接続する。

- Visual Studio 2022 で OneRosterCSV.sln を開く。
- プロジェクトをビルドする。
- Start.aspx を開始ページとして実行する。
- 画面上のボタンから校務支援システムのデータを MongoDB に変換、および OneRosterCSV 出力する。

## ■ OneRosterREST サンプル実行

MongoDB に校務支援システムのデータを変換しておく。  
サンプルでは「mongodb://localhost:27017」として接続する。

- Visual Studio 2022 で ClientCredentialGrant.sln を開く。
- プロジェクトをビルドする。
- AuthorizationServer を実行する。
- clientID 123456 clientSecret abcdef で認証しアクセストークンを得る。

Windows のコマンドプロンプトにて以下のコマンドでアクセストークンを取得。

```
curl -XPOST http://localhost:11625/OAuth/Token -H "Authorization:Basic MTIzNDU2OmFiY2RlZg==" -H "Content-Type: application/x-www-form-urlencoded" -d "grant_type=client_credentials"
```

アクセストークンが取得できる。

```
{"access_token":"hJUjiRKSKwj650WAHOcHkiGdDPXtHCG1I3DWf-HozL9F13suimR-3JW57P9qlpvt80XUfav0L0wfX5jWyx-T-HunOUicl_rPT6xos_v6qqi15WQCgXTWTFpXIqX49KfM4LpmEolT1yv3emGftGROzmEsLRuKc882zVBxbZCajcplO6wWLDSvRKxpPLiIqCmZMP-yqJY0dub87idiJ-VKXt3myG0","token_type":"bearer","expires_in":1199}
```

- ResourceServer を実行する。
- 先ほど取得した access_token で REST API にアクセスする。

```
curl http://localhost:38385/ims/oneroster/rostering/v1p2/academicSessions -H "Authorization:Bearer "hJUjiRKSKwj650WAHOcHkiGdDPXtHCG1I3DWf-HozL9F13suimR-3JW57P9qlpvt80XUfav0L0wfX5jWyx-T-HunOUicl_rPT6xos_v6qqi15WQCgXTWTFpXIqX49KfM4LpmEolT1yv3emGftGROzmEsLRuKc882zVBxbZCajcplO6wWLDSvRKxpPLiIqCmZMP-yqJY0dub87idiJ-VKXt3myG0"
```

- 例えば以下のようなデータが取得できる。

```
"{ \"academicSessions\" : [{ \"sourcedId\" : \"27047527-802f-453b-8fd9-f6bc20b32e73\", \"status\" : \"active\", \"dateLastModified\" : \"2023-02-10 05:05:21.299Z\", \"metadata\" : null, \"title\" : \"2022年度\", \"startDate\" : \"2022-04-01\", \"endDate\" : \"2023-03-31\", \"type\" : \"schoolYear\", \"parent\" : null, \"children\" : null, \"schoolYear\" : \"2022\" }, { \"sourcedId\" : \"5d3554b1-b0b6-4adf-a7cd-3bfadd72373e\", \"status\" : \"active\", \"dateLastModified\" : \"2023-02-10 05:05:21.299Z\", \"metadata\" : null, \"title\" : \"2021年度\", \"startDate\" : \"2021-04-01\", \"endDate\" : \"2022-03-31\", \"type\" : \"schoolYear\", \"parent\" : null, \"children\" : null, \"schoolYear\" : \"2021\" }] }"
```
