# ltijs 学習eポータル標準モデル用サンプルコード

## Introduction

[Cvmcosta/ltijs](https://github.com/Cvmcosta/ltijs)
を用いた、学習eポータル標準モデルversion3.00の学習アプリ用コードです。

## Documentation

  標準モデルで規定しているlti core, lti deeplinkの他に、dynamic registrationにも対応しています。
  本コードではdbとしてfirebaseを使用しています。

  本コードでは学習eポータル標準モデルversion3.00に追加された仕様についての検査を行っております。

  実際のご自身のアプリに適用する場合は以下のコードが必要になると思われます。

    OneRosterで登録された情報とのチェック
    アクセスした人の役割、所属学校、所属クラスを獲得
    firebaseを使用する場合は Firebase カスタムトークンを使用たアプリの起動
    deeplinkの内部コンテンツを選択するメニュー
    
    　

