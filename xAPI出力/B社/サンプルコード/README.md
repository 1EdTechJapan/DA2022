# xAPI　実証用サンプルコード
xApiステートメントを生成し、任意のLRSへ送信するサンプルコード
</br>
</br>
## **開発環境**
#### 開発言語
php8.0-8.2
#### フレームワーク
 Laravel9
</br>
</br>

## **xAPIステートメントの生成**
アプリケーションのスタディログを受け取り、xApiステートメントとして返します。
```
class xApiController 
{
    public function makeProgressedCourseStatement( $study_log ){
        ...
    }
    ...
}
```

## **xAPIステートメントの送信**
アプリケーションのスタディログを、xApiステートメントとして設定したLRSへ送信します。サンプルでは、スタディログは仮のもので固定になっています。
```
class xApiController 
{
    public function sendStatement( ){
        $stuty_logs = {仮のスタディログ}
        ...
        foreach($study_logs as $log){
            $array_statement[] = $this->makeProgressedCourseStatement($log);
        }
        ...
    }
    ...
}
```