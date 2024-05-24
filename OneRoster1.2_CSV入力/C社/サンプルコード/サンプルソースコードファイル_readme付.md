# OneRoster CSV サンプルコード

## 環境

* PHP

## サンプルコード

 * 画面上でZIPファイルを選択後、ボタン押下でイベントimport()を実行。
 * OneRoster仕様に関するチェックを行い、エラーがあれば同画面でエラー表示、<br>
   エラーがなければ次画面（確認画面）に遷移する。（本ファイルにおおむね記載）  
 * 次画面（確認画面）で再度ボタンを押下すると、自社システムに関するチェックを行う。（独自処理のため割愛）
 * 自社独自領域にかかわるパラメータは別文字に置き換えている。


```

use App\Form\ImportZipFileForm_admin;
use ZipArchive;

/**
 * 名簿取込み
 */
class TeachersController extends AppController
{
    private $validate_fileds = [
        //各CSVの項目名を変数化（詳細は割愛）
    ];

    /**
     * 読み込み
     */
    public function import()
    {
        //自社独自領域のため詳細は割愛（学校情報を取得）

            $success = true;

            // 名簿(OneRoster zip形式)
                $this->loadComponent('PageSession', [
                    'name'     => 'import',
                    'actions' => ['import', ●●],
                ]);

                $form = new ImportZipFileForm_admin();
                if (!$form->execute($data)) $success = false;
                if ($success) {

                    //自社独自領域を割愛（取込み画面、学校ごとの条件分岐）
                    //ZIP解凍
                    $zip_path = Upfile::generateTempPath('zip');
                    rename($data["file"]["tmp_name"], $zip_path);
                    $zip_name = explode('.', $data["file"]["name"])[0];

                    $zip_obj = new ZipArchive();
                    if ($zip_obj->open($zip_path)) {
                        $this->deleteDir('/tmp/' . $zip_name);
                        if (!$zip_obj->extractTo('/tmp/' . $zip_name)) {
                            $success = false;
                            $form->setErrors(['file' => ['_validationError' => 'zipファイルの解凍に失敗しました。データ出力からやり直してください。']]);
                        } else {
                            if ($handler = opendir('/tmp/' . $zip_name)) {
                                while ($filename = readdir($handler)) {
                                    if ($filename == '.' || $filename == '..') {
                                        continue;
                                    }
                                    if (is_dir('/tmp/' . $filename) && ($filename == $zip_name)) {
                                        continue;
                                    }

                                    $ext = explode('.', $filename);
                                    $ext = strtolower(end($ext));
                                    // ファイル形式チェック3(CSVファイルのみか)
                                    if ($ext != 'csv') {
                                        $success = false;
                                        $form->setErrors(['file' => ['_validationError' => 'データ形式に問題があるため読み込めません。データ出力からやり直してください。']]);
                                        break;
                                    }
                                }
                            }
                        }
                        $zip_obj->close();
                    } else {
                        $success = false;
                        $form->setErrors(['file' => ['_validationError' => 'zipファイルの解凍に失敗しました。データ出力からやり直してください。']]);
                    }

                    if ($success) {
                        // ファイル形式チェック4
                        if (!file_exists('/tmp/' . $zip_name . '/manifest.csv')) {
                            $success = false;
                            $form->setErrors(['file' => ['_validationError' => 'データが不足しているか、バージョンに誤りがあるため読み込めません。データ出力からやり直してください。']]);
                        }
                    }

                    if ($success) {
                        $manifest_obj = fopen('/tmp/' . $zip_name . DS . 'manifest.csv', 'r');
                        $manifest = [];
                        while (!feof($manifest_obj)) {
                            if ($row = fgetcsv($manifest_obj)) {
                                $manifest[] = $row;
                            }
                        }
                        //manifestファイルのヘッダーチェック
                        if ($manifest[0][0] != 'propertyName' || $manifest[0][1] != 'value') {
                            $success = false;
                            $form->setErrors(['file' => ['_validationError' => 'データが不足しているか、バージョンに誤りがあるため読み込めません。データ出力からやり直してください']]);
                        }
                        unset($manifest[0]);
                        // 4 manifest.csvが存在する、かつ、manifest.csvの「manifest.version」「oneroster.version」が正しいか
                        $manifest = array_combine(array_column($manifest, 0), array_column($manifest, 1));
                        fclose($manifest_obj);
                        if (@$manifest["manifest.version"] !== '1.0' || @$manifest["oneroster.version"] !== '1.2') {
                            $success = false;
                            $form->setErrors(['file' => ['_validationError' => 'データが不足しているか、バージョンに誤りがあるため読み込めません。データ出力からやり直してください。']]);
                        }
                    }

                    $file_count = 0;
                    $exisit_file = [];
                    $all_exist_file = [];
                    $no_exist_file = [];
                    if ($success) {
                        foreach ($manifest as $filename => $v) {
                            if ($v == 'bulk' || $v == 'delta') {
                                $file_count++;
                                $exisit_file[] = explode('.', $filename)[1];
                            }

                            if ($v == 'absent') {
                                $no_exist_file[] =  explode('.', $filename)[1];
                            }

                            $all_exist_file[] = explode('.', $filename)[1];
                        }
                        // 5 manifest.csvで、absent以外で定義されているファイル数分、csvファイルが存在するか
                        $scandir_dir = scandir('/tmp/' . $zip_name);
                        foreach ($scandir_dir as $file) {
                            if ($file == "." || $file == ".." || $file == 'manifest.csv') {
                                continue;
                            }

                            if (in_array(explode('.', $file)[0], $no_exist_file)) {
                                $success = false;
                                $form->setErrors(['file' => ['_validationError' => 'データが不足しているため読み込めません。データ出力からやり直してください。']]);
                                break;
                            }

                            if (!in_array(explode('.', $file)[0], $all_exist_file)) {
                                $success = false;
                                $form->setErrors(['file' => ['_validationError' => 'データが不足しているため読み込めません。データ出力からやり直してください。']]);
                                break;
                            }
                        }
                    }
                    if ($success) {
                        if (count($scandir_dir) - 3 < $file_count) {
                            $success = false;
                            Log::error('manifest.csvで、absent以外で定義されているファイル数分、csvファイルが存在しません');
                            $form->setErrors(['file' => ['_validationError' => 'データが不足しているため読み込めません。データ出力からやり直してください。']]);
                        }
                    }
                    if ($success) {
                        // 各csvファイル名チェック
                        foreach ($exisit_file as $filename) {
                            if (!isset($this->validate_fileds[$filename])) {
                                $success = false;
                                $form->setErrors(['file' => ['_validationError' => 'データ内容に誤りがあるため読み込めません。データ出力からやり直してください。']]);
                                break;
                            }
                            if (!is_file('/tmp/' . $zip_name . DS . $filename . '.csv')) {
                                $success = false;
                                Log::error($filename . '.csvファイルが存在しません');
                                $form->setErrors(['file' => ['_validationError' => 'データが不足しているため読み込めません。データ出力からやり直してください。']]);
                                break;
                            }
                            // 7  各csvファイル内のデータ形式チェック（文字コード、符号化形式）
                            if (count($this->validate_fileds[$filename])) {
                                $file_str = file_get_contents('/tmp/' . $zip_name . DS . $filename . '.csv', FALSE, NULL);
                                $charset[1] = substr($file_str, 0, 1);
                                $charset[2] = substr($file_str, 1, 1);
                                $charset[3] = substr($file_str, 2, 1);
                                $has_bom = ord($charset[1]) == 239 && ord($charset[2]) == 187 && ord($charset[3]) == 191;
                                if ($has_bom) {
                                    $success = false;
                                    Log::error($filename . '.csv ファイルがBOM存在する');
                                    $form->setErrors(['file' => ['_validationError' => 'データ形式に問題があるため読み込めません。データ出力からやり直してください。']]);
                                    break;
                                }

                                if (mb_detect_encoding($file_str, 'UTF-8', true) != 'UTF-8') {
                                    $success = false;
                                    Log::error($filename . '.csv ファイルが UTF-8ではありません');
                                    $form->setErrors(['file' => ['_validationError' => 'データ形式に問題があるため読み込めません。データ出力からやり直してください。']]);
                                    break;
                                }

                                // 8 各csvファイル内のヘッダー名が正しいか（大文字・小文字も区別する）
                                $file_obj = fopen('/tmp/' . $zip_name . DS . $filename . '.csv', 'r');
                                $row = fgetcsv($file_obj);
                                // 10 各csvファイル内の、2行目以降にフィールド数分値が存在するか
                                if ($file_obj) {
                                    while (($value_rows = fgetcsv($file_obj)) !== FALSE) {
                                        if (count($value_rows) != count($this->validate_fileds[$filename])) {
                                            $success = false;
                                            Log::error($filename . '.csvファイル内の、2行目以降にフィールド数分値がではありません');
                                            $form->setErrors(['file' => ['_validationError' => 'データ構成に問題があるため読み込めません。データ出力からやり直してください。']]);
                                            break;
                                        }
                                    }
                                }

                                foreach ($this->validate_fileds[$filename] as $i => $field) {
                                    // 9 各csvファイル内のヘッダー名が指定数存在し、指定順になっているか
                                    if (strcmp($row[$i], $field) != 0) {
                                        $success = false;
                                        Log::error($filename . ".csv ファイルのヘッダー名 {$row[$i]} が正しくありません");
                                        $form->setErrors(['file' => ['_validationError' => 'データ内容に誤りがあるため読み込めません。データ出力からやり直してください。']]);
                                        break;
                                    }
                                }
                                fclose($file_obj);
                            }
                        }
                    }

                    //データ取込用の一時テーブル作成（自社独自領域のため詳細は割愛）
                    //各CSVを取込み＋バリデーション実施
                    // ここから
                    if ($success) {
                        //一時テーブルの初期化
                        $this->drop_all_tables();
                        //1.
                        if (!$this->createTmpTable('テーブル名')) {
                            $success = false;
                            $form->setErrors(['file' => ['_validationError' => '']]);
                        }
                        $file_data = ['name' => 'orgs.csv', 'tmp_name' => '/tmp/' . $zip_name . DS . 'orgs.csv'];
                        $this->importテーブル名($file_data);
                        try {
                            $this->ImportCSV->validates();
                            $this->ImportCSV->execute();
                        } catch (\Exception $e) {
                            $this->drop_all_tables();
                            $success = false;
                            Log::error($e->getMessage());
                            $form->setErrors(['file' => ['_validationError' => '取り込むデータに不正な値があります。データ出力からやり直してください。']]);
                        }
                    }
                    // ここまでを繰り返して各CSVを取り込む（自社独自領域のため詳細は割愛）

                    if ($success) {
                        //自社独自領域のため詳細は割愛（取込画面によって条件分岐）
                        //学校コードで絞り込み（詳細割愛）
                        $this->loadModel('Orgs');
                        if (count($orgs_sourcedid = $this->Orgs->find()
                            ->select(['sourcedid'])
                            ->where(['identifier not in' => $学校コード])
                            ->extract('sourcedid')->toArray()) > 0) {
                            Log::error('学校不一致件数:' . count($orgs_sourcedid) . ' sourcedid:' . join(",", $orgs_sourcedid));
                            $this->Orgs->query()->delete()
                                ->where(['sourcedid in' => $orgs_sourcedid])
                                ->execute();
                        }

                        //年度で絞り込み（詳細割愛）
                        $this->loadModel('Academicsessions');
                        if (count($academicsessions_sourcedid = $this->Academicsessions->find()
                            ->select(['sourcedid'])
                            ->where(['schoolyear not in' => $年度])
                            ->extract('sourcedid')->toArray()) > 0) {
                            Log::error("年度不一致件数:" . count($academicsessions_sourcedid) . " sourcedid:" . join(',', $academicsessions_sourcedid));
                            $this->Academicsessions->query()->delete()
                                ->where(['sourcedid in' => $academicsessions_sourcedid])
                                ->execute();
                        }

                        //取込み対象データの存在チェック（なければ処理終了　詳細は割愛）

                        //CSVデータの紐づけ処理（詳細は割愛）に失敗したら処理終了
                        if (!$success) {
                            $this->drop_all_tables();
                            $form->setErrors(['file' => ['_validationError' => '取り込むデータに不備があります。データ出力からやり直してください。']]);
                        }
                    }
                    if ($success) {
                        //必須項目チェック
                        $academicsessions_num = count($this->Academicsessions->find()
                            ->where(['title' => ''])
                            ->all()
                            ->toArray());
                        $courses_num = count($this->Courses->find()
                            ->where(['title' => ''])
                            ->all()
                            ->toArray());
                        $roles_num = count($this->Roles->find()
                            ->where(['role' => ''])
                            ->all()
                            ->toArray());
                        $rusers_num = count($this->Rusers->find()
                            ->where(['or' => [
                                'enableduser' => '',
                                'username' => '',
                                'usermasteridentifier' => '',
                                'preferredgivenname' => '',
                                'preferredfamilyname' => '',
                                'metadata_jp_kanagivenname' => '',
                                'metadata_jp_kanafamilyname' => '',
                                'metadata_jp_homeclass' => NULL
                            ]])
                            ->all()
                            ->toArray());
                        if ($rusers_num || $roles_num || $courses_num || $academicsessions_num) {
                            $success = false;
                            $this->drop_all_tables();
                            Log::error('csvテーブル内の必須項目存在しません');
                            $form->setErrors(['file' => ['_validationError' => '取り込むデータに不備があります。データ出力からやり直してください。']]);
                        }
                    }
                    if ($success) {
                        //自社独自領域のため詳細は割愛（自社製品に取り込めないデータが含まれるかチェック）
                    }
                    if ($success) {
                        //更新・登録・削除を判断（自社独自領域のため詳細は割愛）
                        //処理件数の取得処理実行（自社独自領域のため詳細は割愛）
                    }

                    if (file_exists('/tmp/' . $zip_name)) {
                        @unlink('/tmp/' . $zip_name);
                    }
                }
                if ($success) {
                    //自社独自領域のため詳細は割愛（チェック処理終了後、問題なければ取り込み処理を実行）
                }
        
    }

    //取り込むための一時テーブルを作成（自社独自領域のため詳細は割愛）
    protected function createTmpTable($type)
    {
    }

    //一時テーブルの初期化処理（自社独自領域のため詳細は割愛）
    private function drop_all_tables()
    {
    }

    //
    //各csvの取込み＋バリデーション（詳細は自社独自領域のため割愛）
    //例としてorgsに関する処理のみ記載
    public function importテーブル名($file_data)
    {
        $this->loadModel('●●');
        $this->loadComponent('ImportCSV', [
            'debug'   => false,
            'file_data'  => $file_data,
            'model_name'  => '●●',
            'transaction_max' => 10000,
            'aliases' => [
                'sourcedId'  => 'sourcedid',
                'status'  => 'status',
                'dateLastModified'  => 'datelastmodified',
                'name'  => 'name',
                'type'  => 'type',
                'identifier'  => 'identifier',
                'parentSourcedId'  => 'parentsourcedid'
            ],

            'required_cols' => ['sourcedid'],

            'data_filter' => function ($row) {
                if ($row['status'] && !in_array($row['status'], ['active', 'tobedeleted'])) {
                    throw new \RuntimeException('orgs.csv ファイルの列 status の値が正しくありません');
                }
                if ($row['datelastmodified'] && !preg_match('/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}).(\d{3})Z$/', $row['datelastmodified'])) {
                    throw new \RuntimeException('orgs.csv ファイルの列 datelastmodified の値が正しくありません');
                }
                if ($row['name'] && (mb_convert_kana($row['name'], 'KV', 'utf-8') != $row['name'])) {
                    throw new \RuntimeException('orgs.csv ファイルの列 name の値が正しくありません');
                }
                if (!in_array($row['type'], ['school', 'district'])) {
                    throw new \RuntimeException("orgs.csv ファイルの列 type の値が正しくありません");
                }

                if ($row['type'] == 'district' && !($row['parentsourcedid'] == '' || $row['parentsourcedid'] == 'NULL')) {
                    throw new \RuntimeException("orgs.csv ファイルの列 parentsourcedid の値が正しくありません");
                }
                if ($row['parentsourcedid']  == 'NULL') $row['parentsourcedid'] = null;

                if ($row['name'] == '') {
                    throw new \RuntimeException("orgs.csv ファイルの列 name の値が正しくありません");
                }

                if ($row['type'] == '') {
                    throw new \RuntimeException("orgs.csv ファイルの列 type の値が正しくありません");
                }

                if ($row['identifier']) {
                    if (strlen($row['identifier']) > 20) {
                        throw new \RuntimeException("orgs.csv ファイルの列 identifier の値が正しくありません");
                    }

                    if (preg_match('/^[a-zA-Z]+$/', $row['identifier'])) {
                        throw new \RuntimeException("orgs.csv ファイルの列 identifier の値が正しくありません");
                    }

                    if (!preg_match('/\d+/', $row['identifier'])) {
                        throw new \RuntimeException("orgs.csv ファイルの列 identifier の値が正しくありません");
                    }
                }

                return $row;
            }

        ]);
    }

    private function deleteDir($dir)
    {
        if ($handle = @opendir($dir)) {
            while (($file = readdir($handle)) !== false) {
                if (($file == ".") || ($file == "..")) {
                    continue;
                }
                if (is_dir($dir . '/' . $file)) {
                    $this->deleteDir($dir . '/' . $file);
                } else {
                    unlink($dir . '/' . $file);
                }
            }
            @closedir($handle);
            @rmdir($dir);
        }
    }
}

```