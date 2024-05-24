# デジタル校務 OneRoster CSV出力バッチプログラム

## 1. 概要
デジタル校務のOneRoster用データベースからOneRoster CSVファイル群を出力するバッチです。
このバッチの起動モードには、データベースに登録されているデータを全件出力するBulkモードと、指定日時以降に更新されたデータを差分出力するDeltaモードの2種類があります。差分出力に用いる日時を指定する方法には、定期実行を想定した前回の実行時刻を取得する方法と、手動実行を想定したバッチスクリプトのパラメータで基準となる日時を指定する方法の2種類があります。  
Windows PowerShellで ```oneroster_export.ps1``` を実行してください。起動時オプションは以下の通りです。

### Powershellの起動オプション 

``` -ExecutionPolicy RemoteSigned ```
署名の無いPowerShellスクリプトの実行を許可します（インターネットからダウンロードしたファイルは実行時に確認されます）。

``` -File "Filepath" "Args" ```
実行するスクリプトファイルへのパスとスクリプトファイルに渡す引数を指定します。

### バッチスクリプトの起動オプション

``` -TenantId "TenantId" ```
取得するテナントのお客様Id（TenantId）をBase64エンコードしたものを指定します。このオプションは必須です。

``` -Delta ```
Deltaモードで起動します。指定しない場合は、Bulkモードで起動します。このオプションは任意です。

``` -ReferenceDateTime "ReferenceDateTime" ```
Deltaモードで起動する場合、いつ以降に更新されたデータを差分出力するか指定できます。日付書式は「yyyy/MM/dd HH:mm:ss」、タイムゾーンはJSTです。「yyyy/MM/dd」のみ指定した場合は、「yyyy/MM/dd 00:00:00」として解釈されます。このオプションは任意です。Bulkモードでこのオプションを指定した場合は、無視されます。

### 起動モードごとの実行方法
#### Bulkモード
Bulkモードで起動する場合は、バッチスクリプトの起動オプションにTenantIdのみを指定してください。このモードで起動した場合は、指定したTenantIdのデータで、statusがactiveに設定されている全てのデータが出力されます。  
例``` Powershell -ExecutionPolicy RemoteSigned -File .\CSV\oneroster_export.ps1 -TenantId "TenantId"```

#### Deltaモード（前回実行日時以降の差分を出力）
Deltaモードで起動し、前回実行日時以降の差分を出力する場合は、バッチスクリプトの起動オプションにTenantIdと、Deltaを指定してください。このモードでの初回実行時は、指定したTenantIdの全てのデータが出力されます。スクリプトの実行に成功した場合は、最終実行日時を含んだdiff.txtが作成されます。二回目以降の実行時は、指定したTenantIdのデータで、diff.txtに保存された最終実行日時以降の差分が出力されます。このモードは、タスクスケジューラ等から定期実行することを想定しています。  
例``` Powershell -ExecutionPolicy RemoteSigned -File .\CSV\oneroster_export.ps1 -TenantId "TenantId" -Delta```

#### Deltaモード（指定日時以降の差分を出力）
Deltaモードで起動し、指定日時以降の差分を出力する場合は、バッチスクリプトの起動オプションにTenantId、Delta、ReferenceDateTimeを指定してください。 このモードで実行した場合は、指定したTenantIdのデータで、ReferenceDateTimeに指定した日時以降の差分が出力されます。このモードで実行しても、最終実行日時を保存しているdiff.txtは更新されません。このモードは、手動で実行することを想定しています。  
例``` Powershell -ExecutionPolicy RemoteSigned -File .\CSV\oneroster_export.ps1 -TenantId "TenantId" -Delta -ReferenceDateTime "yyyy/MM/dd HH:mm:ss"```

## 2. アプリケーション設定

設定ファイルは ```config.txt``` となっています。
バッチを起動する際はこちらの設定ファイルに値を設定します。
設定ファイルの説明を以下に示します。

1. 設定ファイルでは ```#``` から始まる文字列をコメント文とみなします。
2. Windows認証を用いる場合は、以下の5項目を記述してください。
    * DB_INSTANCE、DB_NAME、TARGET_DIR、LOG_DIR、INTEGRAETD_SECURITY
        - DB_USER、DB_PASSWORDの行頭に ```#``` を挿入してください。
3. SQL Server認証を用いる場合は、以下の7項目を記述してください。
    * DB_INSTANCE、DB_NAME、DB_USER、DB_PASSWORD、TARGET_DIR、LOG_DIR、INTEGRAETD_SECURITY
4. 加えて、User.UserIdsカラムの値を出力する場合は、以下の項目を記述してください。
    * USER_IDS_TYPE_LABEL

### config.txt設定項目

1. **DB_INSTANCE**：出力するデータが格納されているデータベースのSQL Serverのインスタンス名です。
2. **DB_NAME**：出力するデータが格納されているデータベース名です。
3. **DB_USER**：出力するデータが格納されているデータベースで、SQL Server認証に使用するユーザ名です。
4. **DB_PASSWORD**：出力するデータが格納されているデータベースで、SQL Server認証に使用するパスワードです。
5. **TARGET_DIR**：ルートディレクトリを ```CSV``` としたときの、出力ファイルの出力先ディレクトリ名です。（既定値： ```target```）
    * 例: ```C:\Users\Desktop\CSV\target``` の場合、```target```
    * または、出力ファイルの出力先ディレクトリの絶対パスです。
        - 例: ```C:\Users\Desktop\CSV\target``` の場合、 ```C:\Users\Desktop\CSV\target```
6. **LOG_DIR**：ルートディレクトリを ```CSV``` としたときの、ログファイルの出力先ディレクトリ名です。（既定値: ```logs```）
    * 例: ```C:\Users\Desktop\CSV\logs``` の場合、 ```logs```
    * または、ログファイルの出力先ディレクトリ名の絶対パスです。
        - 例: ```C:\Users\Desktop\CSV\logs``` の場合、 ```C:\Users\Desktop\CSV\logs```
7. **INTEGRATED_SECURITY**：データベース接続の際に使用する認証を決定する値です。（```true```/```false```）
    * Windows認証を用いる場合は ```true``` 、SQL Server認証を用いる場合は ```false``` です。
8. **USER_IDS_TYPE_LABEL** : IDの種別を示す文字列です。（既定値: ```LTI```）
	* User.UserIdsカラム（{type:identifier}）の"type"の値を決定します。
	* この項目が設定されていない場合、もしくはDBのUser.UserIdsカラムの値がNULLの場合は、User.UserIdsカラムの値は出力されません。

出力するOneRosterバージョンや、出力元システムのバージョン情報等は、manifest.csvに記載されます。manifest.csvに記載する内容を変更するには、```oneroster_export.ps1```内の```manifestHash```変数の値を編集します。設定項目の内容は以下の通りです。

### manifest.csv設定項目

1. **manifest.version**：manifest.csvのバージョンです。（既定値：1.0）
2. **oneroster.version**：OneRosterのバージョンです。（既定値：1.2）
3. **source.systemName**：出力元システムの名称です。（既定値：Digital Koumu Student Information System）
4. **source.systemCode**：このバッチを含む、デジタル校務 OneRosterオプションのバージョンです。（既定値：v2.0.7.10）

## 3.アプリケーションの動作
このバッチを実行すると、新デジタル校務のOneRoster用データベースに登録されているデータを、Bulkモードの場合は全て、Deltaモードの場合は指定した日時以降に更新されたデータのみをCSVとして出力し、圧縮したZIPファイルが作成されます。
作成されるファイルは以下の通りです。

### ZIPファイル

|  ファイル名  |  説明  |
| ---- | ---- |
|  RO_yyyyMMdd_団体コード.zip  |  yyyyMMddは実行終了日時が記載されます。団体コードに教育委員会または学校コードが記載されます。 |

### CSVファイル

|  ファイル名  |  説明  |
| ---- | ---- |
|  manifest.csv  |  提供されるCSVファイルの種類など  |
|  academicSessions.csv  |  年度、学期などの期間  |
|  classes.csv  |  コースの実体として、特定の時限に特定の教員により行われる授業  |
|  courses.csv  |  各年度・学期、学年ごとの課程、教科  |
|  enrollments.csv |  クラスに対するユーザの登録情報  |
|  orgs.csv  |  教育委員会、学校などの組織、団体  |
|  users.csv  |  児童生徒、教職員、保護者に共通の「人」のデータ  |
|  roles.csv  |  児童生徒、教職員、管理職、保護者などのロール情報  |
|  demographics.csv  |  児童生徒、教職員の統計情報  |
|  userProfiles.csv  |  児童生徒、教職員、保護者のユーザープロファイル情報  |

### 適用される処理
このバッチでは、CSVファイルを出力する際に以下の処理が適用されます。BulkモードとDeltaモードでは出力されるCSVファイルの形式が異なります。

#### 共通

* 指定したTenantIdのデータが出力されます。
* deleteFlgがtrue以外のデータが出力されます。

#### Bulkモード

* statusがactiveのデータが出力されます。
* statusとdatelastModifiedは空文字として出力されます。

#### Deltaモード
* dateLastModifiedが指定した日時以降のデータが出力されます。
* dateLastModifiedはタイムゾーンがJSTからUTCに変換されて出力されます。

## 4.注意事項
このバッチに関する注意事項を以下に記載します。

### データの一貫性について
OneRosterの仕様上は、Bulkモードで出力されたZIPファイルに含まれる各CSVファイルのデータは意味的に一貫している必要があります。しかし、このバッチでは、出力されたデータが意味的に一貫していることは確認していません。
例えば、Enrollmentに紐づくUserのレコードが論理削除された場合は、enrollments.csvには論理削除されたUserのSourcedIdが含まれますが、users.csvには論理削除されたUserのデータが含まれない状態になります。
これは、OneRoster用データベース内の意味的に一貫していないデータがある場合、それを除外せずそのまま出力することによって、意味的に一貫していないデータが含まれていることに気づきやすくするためです。そのため、取込み側のシステムではデータが意味的に一貫していることを確認して頂く必要があります。

### Orgに所属していないUserについて
OneRosterの仕様上は、Userは一つ以上のOrgに所属している必要があります。しかし、このバッチでは、「データの一貫性について」と同様の理由で、Userが一つ以上のOrgに所属していることは確認していません。OneRoster用のデータベースに、Orgに所属していないUserが登録されていた場合は、orgSourcedIdの値が空文字で出力されます。

### UserOrgテーブルについて
UserOrgテーブルには、dateLastModifiedカラムが存在しないため、UserOrgテーブルのみが更新された場合は、Deltaモードで実行時に、差分を判定できません。そのため、UserOrgテーブルを更新する場合は、該当するUserテーブルのレコードのdateLastModifiedを更新して頂き、それを以て差分を判定します。

### deleteFlgの扱いについて
各テーブルのdelteFlgカラムの値をtrueに設定すると、このバッチの出力からは除外されます。ただし、OneRosterの仕様上は、データを削除する場合にはstatusをtobedeletedとして取込み側のシステムにデータを削除することを伝える必要があります。
statusがtobedeletedとして取込まれたことがないデータのdeleteFlgをtrueに設定して出力から除外すると、取込み側のシステムにデータの削除を伝えることができません。そのため、deleteFlgをtrueに設定する前に、statusをtobedeletedとして出力し、取込み側のシステムにデータを取込む必要があります。

### diff.txtの値が不正だった場合
このバッチをDeltaモードで実行し前回実行日時以降の差分を出力する場合は、diff.txtに最終実行日時の情報が保存されます。正常のフローで発生することはありませんが、もしdiff.txtに不正な値が保存されていると、最終実行日時が取得できず処理を行うことができません。diff.txtの値が正常に取得できない旨のエラーが発生した場合は、diff.txtに最終実行日時を「yyyy/MM/dd HH:mm:ss」の形式で保存し直すか、一度diff.txtを削除してDeltaモードで前回実行日時以降の差分を出力すると、初回は全件が出力され、二回目以降は前回実行日時以降のデータが差分出力されるようになります。

### ログ出力に失敗した場合
設定ファイルの書式が誤っていたり、設定したログファイルの出力先ディレクトリが存在しなかったりした場合、このバッチは既定の出力先ディレクトリ ```logs``` にバッチの実行が失敗した原因をログ出力します。なお、 ```logs``` が存在しなかったり、アクセス権が無かったりした場合、コマンドラインのみにバッチの実行が失敗した原因をログ出力します。