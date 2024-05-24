<?php

namespace App\Http\Controllers\Member;

use DB;
use Illuminate\Http\Request;
use Log;
use App;
use App\Http\Controllers\Controller;
// LTI連携時には以下は必須になります。
use \IMSGlobal\LTI;
use Src\Lti\LtiDatabase;
// ここまで

/**
 * LTIにて使用するログイン処理機能
 */
class LtiLoginController extends Controller
{
    /**
     * リダイレクト処理
     * @param $request リクエスト情報
     * @return テキストデータ （リダイレクト処理は、ライブラリにて実行される）
     */
    public function redirect(Request $request)
    {
        // check http or https
        if (isset($_SERVER['HTTP_X_CLIENT_SCHEME'])) {
            $scheme = $_SERVER['HTTP_X_CLIENT_SCHEME'] . '://';
        } elseif (isset($_SERVER['REQUEST_SCHEME'])) {
            $scheme = $_SERVER['REQUEST_SCHEME'] . '://';
        } else {
            $scheme = 'http://';
        }

        $url = $scheme . $_SERVER['HTTP_HOST'] . '/lti/login';

        // target_link_uriの存在チェック
        if(!isset($request->all()['target_link_uri']) || !$request->all()['target_link_uri']) {
            Log::debug('target_link_uriが存在しません。');
            return 'target_link_uriが存在しません。';
        }

        LTI\LTI_OIDC_Login::new(new LtiDatabase())->do_oidc_login_redirect($url)->do_redirect();

        return false;
    }

    /**
     * ログイン処理
     * @param $request リクエスト情報
     * @return テキストデータまたはTOPページへのリダイレクト
     */
    public function login(Request $request)
    {
        // LTIのlaunch処理を実行
        $launch = LTI\LTI_Message_Launch::new(new LtiDatabase())->validate();

        // 必要なパラメータを変数へ格納
        $uuid          = $launch->get_launch_data()['sub'];
        $first_name    = '';
        $last_name     = '';
        // $first_name    = $launch->get_launch_data()['family_name'];
        // $last_name     = $launch->get_launch_data()['given_name'];
        $deployment_id = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/deployment_id'];
        // lti_deployment_idをセッションから取得
        // $deployment_id = \SessionService::get('lti_deployment_id');

        // depramenbt_idが存在しない場合、ログイン不可のためテキストを返して返却
        if (!!!$deployment_id) {
            Log::debug('deployment_idが存在しません。');
            return 'deployment_idが存在しません。';
        }

        // deployment_idより学校コードを取得し、指定の学校用のコードを生成
        $school_code_temp = substr($deployment_id, strrpos($deployment_id, 'S_') + 2);
        if (stripos($school_code_temp, '_', 0) > 0) {
            $school_code      = substr($school_code_temp, 0, stripos($school_code_temp, '_', 0));
        } else {
            $school_code      = $school_code_temp;
        }
        $url_alias        = 'ltintt_S_' . $school_code;

        // 学校が登録されているか確認（事前登録が必要）
        // $m_corporation 学校が登録されている場合学校情報が格納される
        if ($m_corporation == null) {
            Log::debug('deployment_id[' . $url_alias . ']が存在しません。');
            return 'deployment_id[' . $url_alias . ']が存在しません。';
        }

        // すでに登録されているユーザがいる場合、DBから取得
        if ($entity == null) {
            DB::beginTransaction();
            try {

                // いない場合には自動登録処理

                DB::commit();
            } catch (\Exception $e){
                DB::rollBack();
                Log::error($e->getMessage());
                throw $e;
            }
        }

        // 特定のルールにてパスワードを生成
        $password = $uuid . '_' . $school_code;
        $request->merge(['identity' => $uuid, 'password' => $password]);

        // login
        Log::debug('login start:' . date('Y-m-d H:i:s'));

        // $result ログイン処理を実行し成功した場合には、ユーザ情報を再取得

        $session = \SessionService::get('member');
        if ($result) {
            // セッションにログイン情報を格納し、トップ画面へリダイレクト

        } else {

            // ログイン失敗画面へ遷移
        }
    }

}
