# 学習eポータル標準モデル用OneRoster CSV取り込み　dartサンプルコード

## Introduction

dartで書かれた学習eポータル標準モデルOneRoster CSV取り込み用サンプルコードです。
外部ライブラリ　dart:convert  package:archive package:csv を使用しています。
オプションで学習eポータル標準モデルには準拠していないファイルも取り込めるようにしています。

## Documentation

...
　OneRoster.checkZIP(Iterable<dynamic> zipFile, Function ok, Function ng);
...
`zipFile`でファイル本体を渡すことで、OneRoster japan Profile　の形式に準拠しているかをチェックし、`ok`, `ng`のいずれかの関数が呼び出されます。dartのライブラリ`package:csv`では改行コードの自動判定はしないため、まず改行コードのチェックをしてからその結果で呼び出しています。ファイルの中身はutf8でエンコードされていることとして処理されており、違うコード系を渡されても文字化けをして処理されます。

実際に使う場合は、結果の名簿を表示して目視で文字化けしていないことを確認してのち、DBに登録する必要があります。

...
  OneRoster or = OneRoseter(map);
  or.check();
...
一つのcsvファイルをデコードすると`List<List<dynamic>>>`になります。これを各ファイルごとの辞書にしたものを`map`として渡すと実行できます。`check()`はOneRoster japan profileとしてチェックし、検査に失敗すると例外を発生させます。成功すると次の行に進むので、ここにDBへの登録のコードを書きます。

...
  OneRoster or = OneRoseter(map);
  or.japanProfile = false;
  or.check();
...
により、japan profileのチェックをさせないこともできます。
    　
より詳細な動きはコード内のコメントをご覧ください。

デジタル庁教育関連データの実証検証で使用した、テストデータでの検証は行なっていますが、検証から漏れている部分には検査が不十分の可能性があります。実際のアプリケーションからの使用の場合は、運用で正当性チェック（たとえば全校の人数、各クラスの人数など）を行なってからDBへの登録をする必要があります。