<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use IMSGlobal\LTI;
use App\Models\Issue;
use Exception;

/**
 *  LTI1.3 Advantage NRPSに関する処理をするクラス
 *
 */
class LtiNamesAndRoleController 
{
    /**
     * LTI1.3 Advantage NRPS
     * プラットフォームからユーザー情報を取得し、json形式で返す
     *
     * @param $request Illuminate\Http\Request
     * @return \Illuminate\Http\JsonResponse
     */
    public function getMemberInfo(Request $request){

        $db = new Issue;
        $launch_id = $request->input("launch");
        // キャッシュからLTI Messageを獲得
        $launch = LTI\LTI_Message_Launch::from_cache($launch_id, $db);
        // LTI MessageからNRPSのエンドポイントを取得し、platformからユーザー情報を取得する。
        $members = $launch->get_nrps()->get_members();
        return response()->json($members);
    }

    /**
     * LTI1.3 NRPS機能で取得したユーザー情報を表示する。
     *
     * @param \Illuminate\Http\Request $request
     * @return \Illuminate\Http\Response
     */
    public function showMemberInfo(Request $request){
        $db = new Issue;
        // バリデーション
        try{       
            $launch = LTI\LTI_Message_Launch::new($db)
                ->validate($request->all());
        }catch(Exception $e){
            // エラー画面を表示
        }
        $launch_id = $launch->get_launch_id(); // キャッシュしたデータを参照するために必要
        return view('atrcall.list_user_by_lti_nrps', ['launch'=>$launch_id]);
    }

}
