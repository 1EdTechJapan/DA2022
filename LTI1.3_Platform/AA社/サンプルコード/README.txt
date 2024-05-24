LTI連携 APIモジュール

・リリースバージョン 1.0
・実装言語：PHP

【概要】
・LTI連携を行うためのAPIモジュールです。
・機能は以下の通りです。
  launch    ：OpenID Connect 開始（学習eポータルから学習ツールの起動を開始する）
  auth      ：OpenID Connect 認証を行い、リダイレクトする
  token     ：AGS用のアクセストークンを返却する
  certs     ：学習eポータルの公開鍵を返却する
  deepLinkingResponse：ディープリンクのレスポンスを受ける
  ltiAgs    ：AGSでスコアを登録する
・学習eポータルの業務系データへのアクセスについては詳細を記載しておりません

