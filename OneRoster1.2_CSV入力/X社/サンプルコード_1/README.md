OneRoster連携サンプル

■ 環境
Ruby: v3.2.1

■ 使用ライブラリ（OneRoster連携のために必須のもの）
・rubyzip 2.3.2
・csv 3.2.6

■ 各ディレクトリとファイルについて

|- modules
|  各サブルーチン
|  |- csv_handler.rb : CSVの処理
|  |- debugger.rb : ログユーティリティ
|  |- file_handler.rb : ファイル/ディレクトリ ユーティリティ
|  |- importable.rb : インポート処理
|  |- validatable.rb : バリデーションクラス  実装サブクラス毎で実装される
|
|- base.rb : 基底クラス
|
|- oneroaster_test.rb : テストに使用した実装クラス
|
| README : 本ファイル


