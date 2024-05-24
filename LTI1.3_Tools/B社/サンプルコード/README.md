# LTI1.3Advantage　実証用サンプルコード
LTI1.3Advantageを実装したサンプルコード

## OIDC login
プラットフォームからのリクエストを処理して、プラットフォームにopenIDリクエストを行う。

リクエストにtarget_linkの指定がない場合は、トップページへのリダイレクトをデフォルトとする。
```
class LtiLoginController
{
    public function __invoke(Request $request)
    {
        ...
            if( $request->input("target_link_uri") == null ){
                 // Resourcelink を想定。
                return LTI\LTI_OIDC_Login::new( $db )
                    ->do_oidc_login_redirect( url("/redirect_atrcall") )
                    ->do_redirect();
            }else{
                // Deeplink またはDeeplinkから登録されたResourcelinkを想定
                return LTI\LTI_OIDC_Login::new( $db )
                    ->do_oidc_login_redirect($request->input("target_link_uri"))
                    ->do_redirect();
            }
        ...
    }
}

```

## DeepLinking
学習単位であるコースを指定したリソースリンクを作成する。

エンドポイントでコース指定画面を表示する。
```
class LtiDeepLinkController
{
    public function deepLinkLaunch(Request $request){
        ...

        return view('atrcall.select_atrcall_courses', ['launch'=>$launch_id, 'courses'=>$array_course]);
    }
    ...
}
```

コース選択画面
LTI/View/select_courses.php

```
...
<form action='deeplink_response' method="POST" >
    ...
    <?php 
        foreach( $courses as $key => $course ){ ?>
            <div class="mb-4">;                        
            <input type='radio' name='course' id="course_<?php echo $key ?>" value="<?php $course['id'] ?>" class='hidden peer'>
                <label for="course_<?php $key ?>" ...>
                <span ...><?php $course['name'] ?></span>
                </label>
            </div>
    <?php  } ?>
    ...
</form>
...
                             
```
受け取ったコース情報を用いてリソースリンクの設定を行い、プラットフォームへDeepLinkResponseする。
```
class LtiDeepLinkController
{
    public function deepLinkResponse(Request $request){
        ...
        $course = $request->input("course");
        $launch_id = $request->input("launch");
        $resource = LTI\LTI_Deep_Link_Resource::new()
            ->set_url( url("{サービスのURL}/$course") )
            ->set_custom_params(['course_id' => $course])
            ->set_title("ATRCALL BRIX course $course");
        ...
        $launch->get_deep_link()
            ->output_response_form([$resource]);
    }
}

```


## Names and Roles Service
メンバー情報を表示する画面　
LTI/View/list_user_by_lti_nrps.php

javascriptで非同期通信し、メンバー情報を取得する
```
$( function()
{ 
    ...
    $('#user_show_btn').on('click', function() {
        let launch_id = '';
        launch_id = $('#user_show_btn').data('launch');
        get_members( launch_id );
    });
    ...
})
...
function get_members( launch_id ){
    let xhr = new XMLHttpRequest();
    let url = '/{nrps_sample_url}/get_member?launch=' + launch_id;
    xhr.responseType = 'json';
    xhr.open("GET", url, true);
    xhr.send();
    xhr.onload = function() {
        ...
            // 用意が出来たらテーブルを作成
            show_member_table( xhr.response )
        ...
    };
    ....
}
```
非同期通信先で、NPRS機能でプラットフォームからメンバー情報を取得している
```
class LtiNamesAndRoleController 
{
    public function getMemberInfo(Request $request){
        $db = new Issue;
        $launch_id = $request->input("launch");
        // キャッシュからLTI Messageを獲得
        $launch = LTI\LTI_Message_Launch::from_cache($launch_id, $db);
        // LTI MessageからNRPSのエンドポイントを取得し、platformからユーザー情報を取得する。
        $members = $launch->get_nrps()->get_members();
        return response()->json($members);
    }
}
```

## Assignments and Grades Service

SCOREの送信とRESULTの表示を行う画面　LTI/View/show_result_by_lti_ags.php
```
    <p class="font-bold">成績を送る</p>
    <form name="myscore" ...>
        <input type="hidden" name="launch_id" value="{{$launch}}">
        <div >
            <label for="score" class="block font-bold">score: </label>
            <input type="number" min="0" max="100" name="score" id="score" ...>
        </div>
        <div>
            <label for="course" class="block font-bold">course: </label>
            <input type="text" name="course" id="course" ...>
        </div>
        <div>
            <label for="time" class="block font-bold">time: </label>
            <input type="number" min="0" name="time" id="time" ...>
        </div>
        <div>
            <label for="progress" class="block font-bold">progress: </label>
            <input type="number" step="0.01" min="0" max="100" name="progress" id="progress" ...>
        </div>
        <div class="mt-2 flex justify-center ">
            <button type="button" id="score_btn" ....>SCORE</button>
        </div>
    </form>

    <p class="font-bold">成績を確認する</p>
    <form name="results" ...>
        <input type="hidden" name="launch_id" value="{{$launch}}">
        ...
        <div class="mt-2 flex justify-center ">
            <button type="button" id="result_btn" ...>RESULT</button>
        </div>
    </form>

```

フォームに入力した成績情報を、Javascriptで非同期で送信。
```
$( function()
{
    ...
    $('#score_btn').on('click', function() {
        let xhr = new XMLHttpRequest();
        let url = '/ags_sample_url/score';
        let formData = new FormData(document.forms.myscore);
        xhr.responseType = 'json';
        xhr.open("POST", url, true);
        xhr.send( formData );
        xhr.onload = function() {
            if (xhr.status != 200) {
                console.log( `Error ${xhr.status}: ${xhr.statusText}` );
            } else { 
                // 結果を表示
                console.log( xhr.response );
            }
        };
        ...
    });
})
```
送信先で、AGS機能でプラットフォームに成績情報を送る（SCORE）
```
class LtiAssignmentAndGradeController
{
    public function postScore(Request $request){
        $course = $request->input('course');
        $db = new Issue;
        $launch = LTI\LTI_Message_Launch::from_cache($request->input('launch_id'), $db);
        ...
        // LTIメッセージから、AGSクレームを取得し、LTIライブラリのAGSクラスのインスタンスを作成。
        $grades = $launch->get_ags();
        $cb = New Carbon();
        // 得点
        $score = LTI\LTI_Grade::new()
            ->set_score_given($request->input('score'))
            ->set_score_maximum(100)
            ->set_timestamp($cb->format('Y-m-d\TH:i:s.vP')) // ISO8601+ミリ秒
            ->set_activity_progress('Completed')
            ->set_grading_progress('FullyGraded')
            ->set_user_id($launch->get_launch_data()['sub']);
        $score_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('score')
            ->set_score_maximum(100)
            ->set_label('Score')
            ->set_resource_id('ATRCALL_course_'. $course);
        // scoreエンドポイント(lineItemのリソースエンドポイント/scores)に、SCOREを送信する。
        $grades->put_grade($score, $score_lineitem);
        
        // 学習時間
        ...
        $grades->put_grade($time, $time_lineitem);

        // 進捗率
        ...
        $grades->put_grade($progress, $progress_lineitem);
    }
}
```

javascriptでRESULTを非同期で取得し、表示する。
```
$( function()
{
    ...
    // 非同期でlti1.3NRPSから得たメンバー情報をテーブルに追加する。
    $('#user_show_btn').on('click', function() {
        let launch_id = '';
        launch_id = $('#user_show_btn').data('launch');
        console.log( launch_id );
        get_members( launch_id );
    });
    ...
})
...
function get_members( launch_id ){
    let xhr = new XMLHttpRequest();
    let url = '/{ags_sample_url}/get_member?launch=' + launch_id;
    xhr.responseType = 'json';
    xhr.open("GET", url, true);
    xhr.send();
    xhr.onload = function() {
        ...
            // 用意が出来たらテーブルを作成
            show_member_table( xhr.response )
        ...
    };
    ...
}

function show_result_table( results ){
    $row = '';
    results.forEach(element => {
        $row += '<tr>';
        $row +=    '<td class="border">'+ element.userId +'</td>';
        $row +=    '<td class="border">'+ element.score +'</td>';
        $row +=    '<td class="border">'+ element.time +'</td>';
        $row +=    '<td class="border">'+ element.progress +'</td>';
        $row += '</tr>';
    });
    $('tbody').html($row);
    $('#result_list').removeClass('hidden');
}

```

通信先で、AGS機能でプラットフォームから成績情報を取得(RESULT)
```
class LtiAssignmentAndGradeController
{
    ...
    public function getResult(Request $request){
        $course = $request->input('course');
        $db = new Issue;
        $launch = LTI\LTI_Message_Launch::from_cache($request->input('launch'), $db);
        ...
        // LTIメッセージから、AGSクレームを取得し、LTIライブラリのAGSクラスのインスタンスを作成。
        $ags = $launch->get_ags();

        $score_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('score')
            ->set_score_maximum(100)
            ->set_label('Score')
            ->set_resource_id('ATRCALL_course_'. $course);
        // RESULTエンドポイント(lineItemのリソースエンドポイント/results)から、SCOREを取得する。
        $scores = $ags->get_grades($score_lineitem);

        ...
        $times = $ags->get_grades($time_lineitem);

        ...
        $progresses = $ags->get_grades($progress_lineitem);

        $result_array = [];
        foreach ($scores as $score) {
            $result = ['score' => $score['resultScore']];
            $result['userId'] = $score['userId'];
            foreach ($times as $time) {
                if ($time['userId'] === $score['userId']) {
                    $result['time'] = $time['resultScore'];
                    break;
                }
            }
            foreach ($progresses as $progress) {
                if ($progress['userId'] === $score['userId']) {
                    $result['progress'] = $progress['resultScore'];
                    break;
                }
            }
            $result_array[] = $result;
        }
        return response()->json($result_array);
    }
}
```