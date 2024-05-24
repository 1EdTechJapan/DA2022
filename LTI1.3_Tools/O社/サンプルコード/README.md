# LTI1.3 sample source

## Introduction

LTI1.3に準拠したシングルサインオンのサンプルソースです。

## Documentation

  LTI連携のライブラリを利用しています。ライブラリは、以下のリンクから入手してください。

* [lti-1-3-php-library](https://github.com/1EdTech/lti-1-3-php-library)

　※PHPバージョンが合わない場合は、適宜変更が必要です。

　サンプルソースでは、OIDCログイン処理を行い、コールバック後にuuid(v4)のチェック後、roleを判断して、先生または生徒のログイン処理を行います。学習eポータル側から接続情報を受け取り、接続設定ファイルに設定します。

## Branches

### 1.0

* PHP5対応
* OIDCログイン処理（lti_core_sso_call.php）
* コールバック後のログイン判断処理（lti_core_sso.php）
* 接続設定ファイル（local.json）

## Support

サンプルソースに対するサポートは行っておりません。
