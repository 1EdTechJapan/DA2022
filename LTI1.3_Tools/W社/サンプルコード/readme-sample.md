# about
* SpringBootを用いてLTI v1.3 Coreを実装する

# Prerequisites

- java 8
- gradle
- CentOS7

# Usage

- 本機能は既存システムのマルチプロジェクトとして実装されているため、単体での動作を想定しない
- gradleに `compile project` として記載することで、マルチプロジェクトとして動作させることを想定する
- サンプルコード化しているため、一部ソースのみを抜粋している

## initLoginRequest
*  `OIDCController`
* initLoginリクエストはfillterでの処理は行わず、Controllerで処理を行う
* バリデーションチェックを実施後、事前に連携されているプラットフォームの情報と照合してリダイレクトURLを生成する

## ResourceLinkRequest
* PreAuthenticationとしてFilterで処理を実施する
* AbstractPreAuthenticatedProcessingFilter : `LtiPreAuthenticatedProcessingFilter`
* 1EdTech Security Framework、Learning Tools Interoperability Core Specification、LTI実証実験に基づいたid_tokenの検証を行ったのち、認証情報をprincipalとして格納する
* principalに格納された認証情報を元に、学習ツール内で管理しているユーザー情報とマッピングし、ログイン処理を行う(独自処理のため割愛)
