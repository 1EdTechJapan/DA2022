#SQLに渡す引数とするps1の引数を取得
#$Deltaは[switch]によりDeltaパラメータが存在する場合True、パラメータがない場合Falseを返すよう設定している。
Param([parameter(mandatory = $true)][string]$TenantId, [Switch]$Delta, [string]$ReferenceDateTime)

#エラーが起こった際に操作を停止するPowerShellのユーザー設定変数
$ErrorActionPreference = "Stop"

#configファイル名
$config = "config.txt"

#configファイル必須要素確認用の配列
$configKeys = ("DB_INSTANCE", "DB_NAME", "TARGET_DIR", "LOG_DIR", "INTEGRATED_SECURITY", "DB_USER", "DB_PASSWORD")

#CSV出力に用いるSQLファイル名とCSVファイル名
$SQLTable = ("academicSessions", "classes", "courses", "enrollments", "orgs", "users", "demographics", "roles", "userProfiles")

#manifest.csvに格納する可変値をKeyValue形式で設定
$manifestHash = @{ }
$manifestHash["manifest.version"] = "1.0"
$manifestHash["oneroster.version"] = "1.2"
$manifestHash["source.systemName"] = "Digital Koumu Student Information System"
$manifestHash["source.systemCode"] = "v2.0.7.10"

#manifest.csvに出力するデータのKeyの配列、配列区切りの間にfile.〇〇を出力
$manifestData = (("manifest.version", "oneroster.version"), ("source.systemName", "source.systemCode"))

#manifest.csv作成時に確認するCSVファイル名（OneRosterデータモデルで定義される全てのCSVファイル名を確認）
#$manifestTable = ("academicSessions", "categories", "classes", "classResources", "courses", "courseResources", "demographics", "enrollments", "lineItems", "orgs", "resources", "results", "users", "roles", "userProfile")
$manifestTable = ("academicSessions", "categories", "classes", "classResources", "courses", "courseResources", "demographics", "enrollments", "lineItemLearningObjectiveIds", "lineItems", "lineItemScoreScales", "orgs", "resources", "resultLearningObjectiveIds", "results", "resultScoreScales", "roles", "scoreScales", "userProfiles", "userResources", "users")

#差分出力に用いる最終実行日時が格納されているファイル名
$diff = "diff.txt"

#UTF8BOMなしのエンコーディング形式の宣言
$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False

#ログファイル出力フォルダの既定値
#ログ出力フォルダ検出前にエラーが発生した場合に既定値に出力する
$defaultLogsDirectory = "$PSScriptRoot\logs"

#ログ出力用タイムスタンプ
function logTimeStamp { (Get-Date).ToString("yyyy/MM/dd HH:mm:ss") }
 
#ログファイル名出力用タイムスタンプ
function fileTimeStamp { (Get-Date).ToString("yyyyMMdd") }

#エラーがあった場合、その後の全処理をexitを用いて省略する

#エラーをキャッチする
try {
    #ファイル名の一部として用いるため、CSV出力方式を文字列として持つ。
    $CSVOutputMethod = "bulk"
    if ($Delta) { $CSVOutputMethod = "delta" }

    ###############################
    #設定ファイルの読み込み
    ###############################
    #設定ファイルからファイル出力フォルダとログ出力フォルダの絶対パス、データベースの情報、user.userIdsに設定するtypeの情報を取得する。
    #取得したパスを取得した変数に書き込む。
    #設定ファイルが存在しない、またはログ出力フォルダの設定に不備がある場合、その旨を原因としてコマンドライン上と既定のログ出力フォルダにログを出力し、バッチを終了する。
    #ログ出力フォルダ以外の設定に不備がある場合、その旨を原因としてコマンドライン上と指定されたログ出力フォルダにログを出力し、バッチを終了する。

    #設定ファイルの存在チェック
    if (!(Test-Path $PSScriptRoot\$config)) {
        (logTimeStamp) + " バッチの実行を開始しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $config が見つかりませんでした。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    #空文字のみの行をコメント文として認識する。
    #設定ファイルの"#"から始まる文字列をコメント文として認識する。
    $configData = Get-Content "$PSScriptRoot\$config" | Where-Object { $_.trim() -ne "" }
    $configData = $configData | Select-String -NotMatch -Pattern '^#.*'
    
    #変数名と値を設定ファイルから読み込む。
    foreach ($configRow in $configData) {
        #splitを用いるため型変換
        $configSplit = ([string]$configRow).split("=")
        Set-Variable -Name ($configSplit[0]) -Value ($configSplit[1])
    }

    #ログ出力フォルダの設定項目が存在しない場合
    if (!(Test-Path Variable:"LOG_DIR")) {
        (logTimeStamp) + " バッチの実行を開始しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " $config が見つかりました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $config 内の LOG_DIR の設定が存在しません。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }
    
    #ログ出力フォルダの設定項目に値が設定されていない場合
    if ([string]::IsNullOrEmpty((Get-Variable("LOG_DIR") -value))) {
        (logTimeStamp) + " バッチの実行を開始しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " $config が見つかりました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $config 内の LOG_DIR の値が設定されていません。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    #ログ出力フォルダの存在チェックを行い、ログを書き込む準備をする（ログフォルダ下にログファイルが存在した場合、追記、存在しなかった場合、作成）。
    #指定されたログ出力フォルダが存在しない場合、その旨を原因としてコマンドライン上と既定のログ出力フォルダにログを出力して、バッチを終了する。
    #既定のログ出力フォルダが存在しない場合、その旨を原因としてコマンドライン上にログを出力し、バッチを終了する。

    #ログ出力フォルダの検出
    if (!(split-path $LOG_DIR -IsAbsolute)) {
        $LOG_DIR = "$PSScriptRoot\$LOG_DIR"
    }

    if (Test-Path "$LOG_DIR") {
        (logTimeStamp) + " バッチの実行を開始しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " $config が見つかりました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " $LOG_DIR が見つかりました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    }
    #ログ出力フォルダが確認できない場合
    else {
        #指定されたログ出力フォルダが既定値だった場合、コマンドライン上にログを出力して終了。
        if ($LOG_DIR -eq $defaultLogsDirectory) {
            (logTimeStamp) + " バッチの実行を開始しました。"
            (logTimeStamp) + " $config が見つかりました。"
            (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $LOG_DIR が見つかりませんでした。"
            (logTimeStamp) + " バッチの実行を終了しました。"
            exit
        }
        
        #指定されたログ出力フォルダが既定値ではなく、既定のログ出力フォルダが存在した場合、コマンドライン上と既定のログ出力フォルダにログを出力して終了。
        if (Test-Path "$defaultLogsDirectory") {
            (logTimeStamp) + " バッチの実行を開始しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " $config が見つかりました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " $LOG_DIR が見つからなかったため、$defaultLogsDirectory にログを出力します。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $LOG_DIR が見つかりませんでした。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            exit
        }

        #指定されたログ出力フォルダが既定値ではなく、既定のログ出力フォルダが存在しない場合、コマンドライン上にログを出力して終了。
        (logTimeStamp) + " バッチの実行を開始しました。"
        (logTimeStamp) + " $config が見つかりました。"
        (logTimeStamp) + " $LOG_DIR が見つからなかったため、$defaultLogsDirectory にログを出力します。"
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $defaultLogsDirectory が見つかりませんでした。"
        (logTimeStamp) + " バッチの実行を終了しました。"
        exit
    }
}
#エラーが起きたときここでハンドリングし、エラー文をコマンドラインに出力する
catch [Exception] {
    (logTimeStamp) + " バッチの実行を開始しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    (logTimeStamp) + " $config が見つかりました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: エラー: $_ " | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$defaultLogsDirectory\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    exit
}

try {
    #認証別に設定ファイルの必須項目があるかどうか判断
    $keyNum = $configKeys.Length
    if ($INTEGRATED_SECURITY -eq "true") { $keyNum -= 2 }
    for ($i = 0; $i -lt $keyNum ; $i++) {
        $configKey = $configKeys[$i]

        #ログ出力フォルダの設定は確認しているため、スキップ
        if ($configKey -eq "LOG_DIR") { continue }

        #設定項目が存在しない場合
        if (!(Test-Path Variable:"$configKey")) {
            (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $config 内の $configKey の設定が存在しません。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            exit
        }

        #設定項目に値が設定されていない場合
        if ([string]::IsNullOrEmpty((Get-Variable($configKey) -value))) {
            (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $config 内の $configKey の値が設定されていません。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            exit
        }
    }

    #ファイル出力フォルダの存在チェックをし、ファイル出力フォルダが存在しない場合、その旨を原因としてコマンドライン上と指定されたログファイルに記述し、バッチを終了する。
    #ファイル出力フォルダの検出
    if (!(split-path $TARGET_DIR -IsAbsolute) -and !(([System.Uri]$TARGET_DIR).IsUnc)) {
        # PSファイルパスを補完
        $TARGET_DIR = "$PSScriptRoot\$TARGET_DIR"
    }

    if (Test-Path $TARGET_DIR) {
        (logTimeStamp) + " $TARGET_DIR が見つかりました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    }
    #ファイル出力フォルダが確認できない場合
    else {
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $TARGET_DIR が見つかりませんでした。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    ###############################
    #CSVファイルの出力
    ###############################
    #sqlcmdで用いるPowerShellの引数をBase64でデコードする
    #Base64形式かどうか確認
    if (!($TenantId -match "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$")) {
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: 引数TenantIdはBase64形式ではありません。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))    
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    #Base64でデコード
    [Byte[]]$TenantId = [System.Convert]::FromBase64String($TenantId)
    [string]$TenantId = [System.Text.Encoding]::Default.GetString($TenantId)

    #TryParseのため初期化
    $intTenantId = 0

    #Base64でデコードした値がINT型に変換できるか確認
    if (![int]::TryParse($TenantId, [ref]$intTenantId)) {
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: 引数TenantIdをBase64でデコードした値がINT型ではありません。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))    
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    #出力方式がDeltaであるか判断する。
    #出力方式がDeltaである場合、
    #変数ReferenceDateTimeが存在するか判断する。
    if ($delta) {
        #SQL Serverで扱えるDatetime型の最低値を格納
        $sqlReferenceDateTime = ([Datetime]"1753/01/01 00:00:00")

        #変数ReferenceDateTimeが存在しない場合、
        #diff.txtが存在するかどうか判断する。
        if ($ReferenceDateTime -eq "") {
            #diff.txtが存在した場合、
            #diff.txtの値をsqlcmdに渡す変数sqlReferenceDateTimeとして設定する。
            #diff.txtを読み込んだ旨と
            #sqlReferenceDateTime以降のデータを出力することをログ出力する。
            if (Test-Path $PSScriptRoot\$diff) {
                $diffDate = Get-Content "$PSScriptRoot\$diff"

                #parse可能でなかった場合、失敗した旨を原因とともにログ出力する、その後スクリプトを終了する。
                if (![Datetime]::TryParse($diffDate, [ref]$sqlReferenceDateTime)) {
                    (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $diff の値が不正な日時または形式です。yyyy/MM/dd HH:mm:ssの形式で指定ください。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                    (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                    exit
                }

                #SQL ServerのDatetime型の最低値を下回っていないかの確認と現在以降を指定していないかの確認
                if (!($sqlReferenceDateTime -ge ([Datetime]"1753/01/01 00:00:00") -and $sqlReferenceDateTime -le (Get-Date))) {
                    (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $diff に指定された日時の入力形式は正しいですが、日時が範囲外です。1753/01/01 00:00:00から" + "現在時刻の間で入力して下さい。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                    (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                    exit
                }

                (logTimeStamp) + " " + $sqlReferenceDateTime.ToString("yyyy/MM/dd HH:mm:ss") + " 以降のデータを出力いたします。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            }
            #diff.txtが存在しない場合、初期実行として認識され、
            #全データの出力を出力するためsqlReferenceDateTimeには初期値として設定しているDateTime型の最低値を与える。
            #diff.txtが存在しない旨と全データを出力する旨をログ出力する。
            else {
                (logTimeStamp) + " $diff が存在しないため、全ての期間のデータを出力いたします。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            }	
        }
        #変数ReferenceDateTimeが存在した場合、
        else {
            #変数ReferenceDateTimeの値が、DateTime型に変換可能かを判断し、
            #sqlcmdに渡す変数sqlReferenceDateTimeとして設定する。
            #sqlReferenceDateTime以降のデータを出力することをログ出力する。

            #parse可能でなかった場合、失敗した旨を原因とともにログ出力する、その後スクリプトを終了する。
            if (![Datetime]::TryParse($ReferenceDateTime, [ref]$sqlReferenceDateTime)) {
                (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: 引数 ReferenceDateTime の値が不正な日時または形式です。yyyy/MM/dd HH:mm:ssの形式で入力ください。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                exit
            }

            #SQL ServerのDatetime型の最低値を下回っていないかの確認と現在以降を指定していないかの確認
            if (!($sqlReferenceDateTime -ge ([Datetime]"1753/01/01") -and $sqlReferenceDateTime -le (Get-Date))) {
                (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: 引数ReferenceDateTimeに指定された日時の入力形式は正しいですが、日時が範囲外です。1753/01/01 00:00:00から" + "現在時刻の間で入力して下さい。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
                exit
            }

            (logTimeStamp) + " " + $sqlReferenceDateTime.ToString("yyyy/MM/dd HH:mm:ss") + " 以降のデータを出力いたします。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        }
    }
    #出力方式がDeltaでない場合、
    #空文字をsqlcmdに渡す変数sqlReferenceDateTimeとして設定する。
    else {
        $sqlReferenceDateTime = ""
    }

    #sqlcmdに設定ファイルから取り出したDB名等のパラメータを渡し、7種類のCSVファイルを出力する。
    #orgs,academicSessions,users,courses,classes,enrollments,manifest7種
    #各データの出力開始時に開始ログを、終了時に成否と出力件数、失敗原因を出力する。
    #CSVファイルの出力に失敗した場合は、出力対象のCSVファイルにSQL Serverエラーメッセージが出力されるため、それを読み込みログに出力する。
    #DOS ERRORLEVELを取得し、sqlcmdコマンドの成否チェックを行う。
    #処理が失敗していた場合、後続のsqlcmdコマンドは実行せず、バッチ処理自体を終了する。
    
    #CSV出力用一時フォルダの作成
    $CSVOutputFolder = $TARGET_DIR + "\" + (New-Guid).guid
    New-Item $CSVOutputFolder -ItemType Directory | Out-Null

    #データベース接続の際に認証方式別に接続するため、データベースの認証方式を確認する
    #SQLを用いてCSVを出力する
    for ($i = 0; $i -lt $SQLTable.Length; $i++) {
        #処理するTableを変更する。
        $localTable = $SQLTable[$i]
        (logTimeStamp) + " $localTable.csv の出力を開始しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        
        if (!(Test-Path $PSScriptRoot\sql\$localTable.sql)) {
            (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $PSScriptRoot\sql\$localTable.sql が見つかりませんでした。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            Remove-Item -Path $CSVOutputFolder -Recurse -Force
            (logTimeStamp) + " CSVファイルを削除しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            exit
        }

        if ($INTEGRATED_SECURITY -eq "true") {
            (logTimeStamp) + " Windows認証で接続します。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))

            #Windows認証でSQL Serverに接続し、各SQLファイルを実行する
            #USER_IDS_TYPE_LABELが存在する場合、user.userIds出力のためクエリにUSER_IDS_TYPE_LABELとして渡す。
            #users.csvの出力の際にはUSER_IDS_TYPE_LABELの引数を付与する処理を追記する。
            if ($localTable -eq "users") {
                #USER_IDS_TYPE_LABELの項目がないとき引数としてNULLを付与する。
                if (!(Test-Path Variable:"USER_IDS_TYPE_LABEL")) {
                    sqlcmd -S $DB_INSTANCE -E -d $DB_NAME -b -u -s"," -W -i $PSScriptRoot\sql\$localTable.sql -o $CSVOutputFolder\$localTable.csv -v TenantId = `'$intTenantId`' -v USER_IDS_TYPE_LABEL = NULL -v ReferenceDateTime = `'$SQLReferenceDateTime`'
                }
                #USER_IDS_TYPE_LABELの項目の値を引数に付与する。
                else {
                    sqlcmd -S $DB_INSTANCE -E -d $DB_NAME -b -u -s"," -W -i $PSScriptRoot\sql\$localTable.sql -o $CSVOutputFolder\$localTable.csv -v TenantId = `'$intTenantId`' -v USER_IDS_TYPE_LABEL = `'$USER_IDS_TYPE_LABEL`' -v ReferenceDateTime = `'$SQLReferenceDateTime`'
                }
            }
            else {
                sqlcmd -S $DB_INSTANCE -E -d $DB_NAME -b -u -s"," -W -i $PSScriptRoot\sql\$localTable.sql -o $CSVOutputFolder\$localTable.csv -v TenantId = `'$intTenantId`' -v ReferenceDateTime = `'$SQLReferenceDateTime`'
            }
        }
        else {
            (logTimeStamp) + " SQL Server認証で接続します。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))

            #非統合認証でSQL Severに接続し、各SQLファイルを実行する
            #USER_IDS_TYPE_LABELが存在する場合、user.userIds出力のためクエリにUSER_IDS_TYPE_LABELとして渡す。
            #users.csvの出力の際にはUSER_IDS_TYPE_LABELの引数を付与する処理を追記する。
            if ($localTable -eq "users") {
                #USER_IDS_TYPE_LABELの項目がないとき引数としてNULLを付与する。
                if (!(Test-Path Variable:"USER_IDS_TYPE_LABEL")) {
                    sqlcmd -S $DB_INSTANCE -U $DB_USER -P $DB_PASSWORD -d $DB_NAME -b -u -s"," -W -i $PSScriptRoot\sql\$localTable.sql -o $CSVOutputFolder\$localTable.csv -v  TenantId = `'$intTenantId`' -v USER_IDS_TYPE_LABEL = NULL -v ReferenceDateTime = `'$SQLReferenceDateTime`'
                }
                #USER_IDS_TYPE_LABELの項目の値を引数に付与する。
                else {
                    sqlcmd -S $DB_INSTANCE -U $DB_USER -P $DB_PASSWORD -d $DB_NAME -b -u -s"," -W -i $PSScriptRoot\sql\$localTable.sql -o $CSVOutputFolder\$localTable.csv -v  TenantId = `'$intTenantId`' -v USER_IDS_TYPE_LABEL = `'$USER_IDS_TYPE_LABEL`' -v ReferenceDateTime = `'$SQLReferenceDateTime`'
                }
            }
            else {
                sqlcmd -S $DB_INSTANCE -U $DB_USER -P $DB_PASSWORD -d $DB_NAME -b -u -s"," -W -i $PSScriptRoot\sql\$localTable.sql -o $CSVOutputFolder\$localTable.csv -v  TenantId = `'$intTenantId`' -v ReferenceDateTime = `'$SQLReferenceDateTime`'
            }
        }
        
        #DOS ERRORLEVELを取得し、sqlcmdコマンドの成否チェックを行う、非であったとき、スクリプトを停止する
        if ($LASTEXITCODE) {
            if (Test-Path $CSVOutputFolder/$localTable.csv) {
                (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: " + (Get-Content $CSVOutputFolder/$localTable.csv) | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            }
            Remove-Item -Path $CSVOutputFolder -Recurse -Force
            (logTimeStamp) + " CSVファイルを削除しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            exit
        }

        #改行コード維持のため、一度CSVに出力してから配列の境目に改行コードを用いて出力
        $CSVDataLine = (Get-Content $CSVOutputFolder/$localTable.csv -Raw)
        $CSVData = $CSVDataLine -Split "\r\n"
        
        #ヘッダファイルのみの時CSVファイルとして出力しないため、処理途中で出力するCSVファイルは削除する。
        Remove-Item $CSVOutputFolder\$localTable.csv
        
        #CSVファイルの出力件数を取得し、ログに書き込む
        #実行したクエリと、クエリに渡した変数をログに書き込む
        #CSVファイルの不要なハイフン、記述されている出力件数を削除
        
        #CSV出力後に件数を表示するために件数を退避する
        $outputNum = $CSVData[$CSVdata.Length - 2]

        #件数の表示文中から数字のみを抽出する
        $outputNum = $outputNum -replace "\D", ""
        
        #ヘッダ列に付随するハイフン文字列を削除する（要素を空にする）
        $CSVdata[2 - 1] = $null
        
        #末尾の出力件数を削除する（要素を空にする）
        $CSVdata[$CSVdata.Length - 1] = $null
        $CSVdata[$CSVdata.Length - 2] = $null
        
        #行削除を反映する（空白行を削除する）
        $CSVdata = $CSVdata -ne ""

        #ヘッダ列を無視するため分岐条件を$CSVdata.Length-1とし、データが出力されていないものを検出
        if ($CSVdata.Length - 1 -eq 0) {
            (logTimeStamp) + " 出力するデータ行が存在しないため、$localTable.csv の出力をスキップしました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))  
        }
        else {
            #SQLデータを変換したものをBomなしUtf-8としてCSVファイルで出力
            [System.IO.File]::WriteAllLines("$CSVOutputFolder\$localTable.csv", $CSVdata, $Utf8NoBomEncoding)
            #ログ出力
            (logTimeStamp) + " $localTable.csv の出力が終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            (logTimeStamp) + " 出力件数: $outputNum 件出力しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        }

        #SQLに渡した変数をログに出力
        if ($localTable -eq "users") {
            if (!(Test-Path Variable:"USER_IDS_TYPE_LABEL")) {
                (logTimeStamp) + " 変数: TenantId = `'$intTenantId`', ReferenceDateTime = `'$SQLReferenceDateTime`', USER_IDS_TYPE_LABEL = NULL" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            }
            else {
                (logTimeStamp) + " 変数: TenantId = `'$intTenantId`', ReferenceDateTime = `'$SQLReferenceDateTime`', USER_IDS_TYPE_LABEL = `'$USER_IDS_TYPE_LABEL`'" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
            }
        }
        else {
            (logTimeStamp) + " 変数: TenantId = `'$intTenantId`', ReferenceDateTime = `'$SQLReferenceDateTime`'" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        }

        (logTimeStamp) + " 実行したクエリ:" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        Get-Content $PSScriptRoot\sql\$localTable.sql | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    }

    #manifest.csvを作成する。
    (logTimeStamp) + " manifest.csv の出力を開始しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    $manifestOutData += "propertyName,value`r`n"

    #manifest.csvのうちmanifest.version、oneroster.versionのデータを作成した変数に格納する。
    for ($i = 0; $i -lt $manifestData[0].Length; $i++) {
        #Dataを入れ替え次の出力に移る
        $localData = $manifestData[0][$i]
        $manifestOutData += "`"" + $localData + "`",`"" + $manifestHash[$localData] + "`"`r`n"
    }
    
    #manifest.csvのうち file.〇〇のデータは各CSVが存在するか確認し、確認できた場合値に変数CSVOutputMethodの値を設定し、確認できない場合値を”absent”と設定する。
    for ($i = 0; $i -lt $manifestTable.Length; $i++) {
        $localTable = $manifestTable[$i]
        $manifestOutData += "`"file." + $localTable + "`","
        if (Test-Path $CSVOutputFolder\$localTable.csv) {
            $manifestOutData += "`"$CSVOutputMethod`"`r`n"
            (logTimeStamp) + " $localTable.csv が見つかりました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        }
        else {
            $manifestOutData += "`"absent`"`r`n"
        } 
    }

    #manifest.csvのうちsource.systemName、digitalkoumu.oneroster.versionのデータを作成した変数に格納する。
    for ($i = 0; $i -lt $manifestData[1].Length; $i++) {
        #Dataを入れ替え次の出力に移る
        $localData = $manifestData[1][$i]
        $manifestOutData += "`"" + $localData + "`",`"" + $manifestHash[$localData]
        if ($manifestData[1].Length -ne $i + 1) {
            $manifestOutData += "`"`r`n"
        }
    }
    $manifestOutData += "`"`r`n"
    #manifest.csv作成のためのデータを格納する変数からmanifest.csvを作成する。
    #SQLデータを変換したものをBomなしUtf-8としてCSVファイルで出力
    [System.IO.File]::WriteAllText("$CSVOutputFolder\manifest.csv", $manifestOutData, $Utf8NoBomEncoding)

    (logTimeStamp) + " manifest.csv の出力が終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))

    ###############################
    #CSVファイルのZIP化
    ###############################
    #ZIPファイルの名称はbulkとdeltaとで出力ファイル名を変更。
    $OutputZip = "oneroster_$CSVOutputMethod" + "_" + (Get-Date).ToString("yyyyMMddHHmmss") + ".zip"
    
    (logTimeStamp) + " $OutputZip の出力を開始しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))

    #CSVファイルをまとめてZIP化する。
    #CSVファイルをすべて削除する。
    Compress-Archive -Path $CSVOutputFolder\*.csv -DestinationPath $TARGET_DIR\$OutputZip -Force
    Remove-Item -Path $CSVOutputFolder -Recurse -Force
    (logTimeStamp) + " CSVファイルを削除しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    (logTimeStamp) + " $OutputZip の出力が終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    ##############################
}
#エラーが起きたときここでハンドリングし、エラー文をログファイルとコマンドラインに出力する
#ログファイルの存在が明らかなためログファイルおよびコマンドラインに出力
catch [Exception] {
    #diff.txtに読み込み権限がなかった場合のエラー処理
    if ($_.FullyQualifiedErrorId -eq "GetContentReaderUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetContentCommand") {
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $_ " | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    #ZIPファイル出力フォルダに書き込み権限がなかった場合のエラー処理
    if ($_.FullyQualifiedErrorId -eq "CreateDirectoryUnauthorizedAccessError,Microsoft.PowerShell.Commands.NewItemCommand") {
        (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $Target_DIR へのアクセスが拒否されました。 " | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
        exit
    }

    #diff.txt、ZIPファイル出力フォルダに権限がなかった場合以外のエラー処理
    (logTimeStamp) + " ZIPファイル の出力に失敗しました。原因: $_ " | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    Remove-Item -Path $CSVOutputFolder -Recurse -Force
    (logTimeStamp) + " CSVファイルを削除しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    exit
}

try {
    #CSVOutputMethodの値がdeltaであり、かつ引数ReferenceDateTimeが存在するか確認を行う
    #CSVOutputMethodの値がdeltaで、引数ReferenceDateTimeが指定されていない場合、現在の時刻を記述したdiff.txtをCSVフォルダ直下に上書き保存する。
    #diff.txtを作成した旨をログ出力する。
    if ($Delta -and $ReferenceDateTime -eq "") {
        [System.IO.File]::WriteAllText("$PSScriptRoot\$diff", (Get-Date -Format "yyyy/MM/dd HH:mm:ss"), $Utf8NoBomEncoding)
        (logTimeStamp) + " diff.txtの作成を行いました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    }

    #バッチの正常終了処理
    (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
}
#エラーが起きたときここでハンドリングし、エラー文をログファイルとコマンドラインに出力する
#ログファイルの存在が明らかなためログファイルおよびコマンドラインに出力
catch [Exception] {
    Remove-Item $TARGET_DIR\$OutputZip
    (logTimeStamp) + " diff.txtの作成に失敗しました。整合性保持のため作成したZIPファイルを削除しました。原因: $_ " | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    (logTimeStamp) + " バッチの実行を終了しました。" | Tee-Object -a ("$LOG_DIR\oneroster_$CSVOutputMethod.log." + (fileTimeStamp))
    exit
}