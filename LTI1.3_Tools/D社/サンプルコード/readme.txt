内容物について
このサンプルコードはLTI 1.3の仕様に従って弊社のTOP画面の呼び出しとログインを行っています。

注意点
このサンプルコードは弊社の実装するLTI連携プログラムの一部であるため、サンプルコード単体で実行することは出来ません。

環境
Java 8
PHP 7.4.33,Angular 15

#PHP LTI Integration
## Steps
1. The platform sends an **initLogin** request
2. The tool responds with an **authentication** request
3. The platform responds with a **resourceLink** request

## Step 1 - initLogin
1. The tool checks that the required parameters are present
2. The tool generates a state and a nonce

## Step 2 - authentication request
1. The tool sends an **authentication** request to the pre-defined authentication URL of the platform with the required parameters via either POST or GET method.

## Step 3 - resource link request 
1. The tool receives the id_token from the platform
2. The tool verifies the state and id_token contents
3. On success, the tool authenticates the user and starts the authenticated session, then redirects the user to the resource.
