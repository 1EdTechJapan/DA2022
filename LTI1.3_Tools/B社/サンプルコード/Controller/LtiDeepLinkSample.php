<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use IMSGlobal\LTI;
use App\Models\Issue;
use App\Models\Course;
use Exception;

/**
 *  LTI1.3 Advantage DeepLinkingに関する処理をするクラス
 *
 */
class LtiDeepLinkController
{
    /**
     * Deeplinkエンドポイント
     *
     * @param \Illuminate\Http\Request $request
     * @return \Illuminate\Contracts\View\View|\Illuminate\Contracts\View\Factory
     */
    public function deepLinkLaunch(Request $request){
        // 弊社システムの学習単位であるコースを指定する画面を表示

        // IssueクラスでPlatformに関する情報を管理している。
        $db = new Issue;
        try{       
            // LTI Messsageを管理するクラスのインスタンスを作成。受信したLTI Messageをバリデーションする。
            $launch = LTI\LTI_Message_Launch::new($db)
                ->validate($request->all());
        }catch(Exception $e){
            // エラー画面を表示
        }
        $launch_id = $launch->get_launch_id(); // キャッシュしたデータを参照するために必要
        // コース情報を管理するCourseクラスから、コース情報を取得する。
        $courses = Course::select('course_id', 'name')
            ->orderBY('order')
            ->get();
        $array_course = [];
        foreach($courses as $course){
            $array_course[] = array('id'=>$course->course_id, 'name'=>$course->name);
        }
        // コースを選択する画面を表示
        return view('atrcall.select_atrcall_courses', ['launch'=>$launch_id, 'courses'=>$array_course]);
    }

    /**
     * DeeplinkResponseを返す
     *
     * @param Illuminate\Http\Request $request 
     * @return \Illuminate\Http\Response
     */
    public function deepLinkResponse(Request $request){
        $db = new Issue;
        $course = $request->input("course");
        $launch_id = $request->input("launch");

        $resource = LTI\LTI_Deep_Link_Resource::new()
            ->set_url( url("{サービスのURL}/$course") )
            ->set_custom_params(['course_id' => $course])
            ->set_title("ATRCALL BRIX course $course" );
        // キャッシュからLTI Messageを取得
        $launch = LTI\LTI_Message_Launch::from_cache($launch_id, $db);
        // 送信
        $launch->get_deep_link()
            ->output_response_form([$resource]);
    }

}
