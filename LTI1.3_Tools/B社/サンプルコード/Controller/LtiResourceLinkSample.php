<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use IMSGlobal\LTI;
use App\Models\Issue;
use App\Models\User;
use Exception;

/**
 *  LTI1.3 ResourceLinkに関連する処理をまとめたクラス
 */
class LtiResourceLinkController 
{
    /**
     * ResourceLinkにより、トップページへリダイレクト。
     *
     * リダイレクト先を指定されなかった場合は、トップページにリダイレクトする。
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function redirectAtrCall(Request $request ) {
        $lti_message = $request->all();
        $data = $this->getLtiMessageLauncheData($lti_message);
        //subクレームのuser_idが存在するか確認
        $user_id = $data['sub'];
        $users = new User;
        //有効なユーザーを返す（存在する、かつ有効期限内）
        $vaild_users = $users->exist_and_valid($user_id);
        //ユーザーがいなかった場合
        $user_num = $vaild_users->count();
        if( $user_num === 0 ){      
            // エラー画面を表示
        }
        // 自社独自領域のため、詳細は割愛。別サーバーにあるサービスのトップページにリダイレクトする。
        $redirect_url =  $redirect_url = $this->makeUrlAtrcallTop($user_id);
        return redirect()->away($redirect_url, 308);
    }

     /**
     * サービスの指定されたコースへのリダイレクト
     * 
     * DeepLinkingで作成されたResourceLinkを想定
     *
     * @param string $course
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\RedirectResponse
     */
    public function redirectCourceOfAtrCall($course, Request $request ) {
        $course_id = $course;
        $lti_messages = $request->all();
        $data = $this->getLtiMessageLauncheData( $lti_messages );
        // subクレームのuser_idが存在するか確認
        $user_id = $data['sub'];
        $users = new User;
        //有効なユーザーを返す（存在する、かつ有効期限内）
        $vaild_users = $users->exist_and_valid($user_id);
        //ユーザーがいなかった場合
        $user_num = $vaild_users->count();
        if( $user_num === 0 ){
            // エラー画面を表示
        }
        // 自社独自領域のため、詳細は割愛。別サーバーにあるサービスのトップページにリダイレクトする。
        $redirect_url =  $redirect_url = $this->makeUrlAtrcallCourse($user_id, $course_id);
        return redirect()->away($redirect_url, 308);
    }

    /**
     * リダイレクトするATRCALLのURLを作成(TOPページ)
     * 
     * @return string
     */
    private function makeUrlAtrcallTop($user_id){
        // 自社独自領域のため、詳細は割愛。
        return $redirect_url;
    }
    
     /**
     * リダイレクトするATRCALLのURLを作成(指定したコース)
     * 
     * @return string
     */
    private function makeUrlAtrcallCourse($user_id, $course_id){
        // 自社独自領域のため、詳細は割愛。
        return $redirect_url;
    }

    /**
     * LTI message launcheをバリデーションし,必要なデータを取得
     * 
     * @param  array $lti_message 
     * @return array|object
     */
    private function getLtiMessageLauncheData($lti_message){
        //ATRCALLへのリダイレクト先のURLを作成
        $db = new Issue;
        try{       
            $launch = LTI\LTI_Message_Launch::new($db)
                ->validate($lti_message);
        }catch(Exception $e){
            // エラー画面表示
        }
        
        $data = $launch->get_launch_data();
        return $data;
    }

}
