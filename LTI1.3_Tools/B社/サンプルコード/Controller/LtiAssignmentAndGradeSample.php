<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use IMSGlobal\LTI;
use App\Models\Issue;
use Exception;
use Carbon\Carbon;

class LtiAssignmentAndGradeController
{
    /**
     * AGS SCORE機能を利用し、成績情報を送信
     *
     * @param $request Illuminate\Http\Request
     * 
     */
    public function postScore(Request $request){
        $course = $request->input('course');
        $db = new Issue;
        $launch = LTI\LTI_Message_Launch::from_cache($request->input('launch_id'), $db);
        if (!$launch->has_ags()) {
            throw new Exception("Don't have grades!");
        }
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
        $time = LTI\LTI_Grade::new()
            ->set_score_given($request->input('time'))
            ->set_score_maximum(999)
            ->set_timestamp($cb->format('Y-m-d\TH:i:s.vP'))
            ->set_activity_progress('Completed')
            ->set_grading_progress('FullyGraded')
            ->set_user_id($launch->get_launch_data()['sub']);
        $time_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('time')
            ->set_score_maximum(999)
            ->set_label('Time Taken')
            ->set_resource_id('ATRCALL_course_'. $course);
        $grades->put_grade($time, $time_lineitem);

        // 進捗率
        $progress = LTI\LTI_Grade::new()
            ->set_score_given($_REQUEST['progress'])
            ->set_score_maximum(100)
            ->set_timestamp($cb->format('Y-m-d\TH:i:s.vP')) 
            ->set_activity_progress('Completed')
            ->set_grading_progress('FullyGraded')
            ->set_user_id($launch->get_launch_data()['sub']);
        $progress_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('progress')
            ->set_score_maximum(100)
            ->set_label('Progress')
            ->set_resource_id('ATRCALL_course_'. $course);
        $grades->put_grade($progress, $progress_lineitem);
    }

    /**
     * AGS RESULT機能を利用し、成績情報を取得。取得した成績情報をjson形式で返す
     *
     * @param Illuminate\Http\Request $request 
     * @return \Illuminate\Http\JsonResponse
     */
    public function getResult(Request $request){
        $course = $request->input('course');
        $db = new Issue;
        $launch = LTI\LTI_Message_Launch::from_cache($request->input('launch'), $db);
        if (!$launch->has_ags()) {
            throw new Exception("Don't have grades!");
        }
        // LTIメッセージから、AGSクレームを取得し、LTIライブラリのAGSクラスのインスタンスを作成。
        $ags = $launch->get_ags();

        $score_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('score')
            ->set_score_maximum(100)
            ->set_label('Score')
            ->set_resource_id('ATRCALL_course_'. $course);
        // RESULTエンドポイント(lineItemのリソースエンドポイント/results)から、SCOREを取得する。
        $scores = $ags->get_grades($score_lineitem);

        $time_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('time')
            ->set_score_maximum(999)
            ->set_label('Time Taken')
            ->set_resource_id('ATRCALL_course_'. $course);
        $times = $ags->get_grades($time_lineitem);

        $progress_lineitem = LTI\LTI_Lineitem::new()
            ->set_tag('progress')
            ->set_score_maximum(100)
            ->set_label('Progress')
            ->set_resource_id('ATRCALL_course_'. $course);
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

    /**
     * LTI1.3 AGS　SCOREとRESULTを実行する画面を返す
     *
     * @param \Illuminate\Http\Request $request
     * @return \Illuminate\Http\Response
     */
    public function showResult(Request $request){
        $db = new Issue;
        // バリデーション
        try{       
            $launch = LTI\LTI_Message_Launch::new($db)
                ->validate($request->all());
        }catch(Exception $e){
            // エラー画面を表示
        }
        $launch_id = $launch->get_launch_id(); // キャッシュしたデータを参照するために必要     
        return view('atrcall.show_result_by_lti_ags', ['launch'=>$launch_id]);
    }
}
