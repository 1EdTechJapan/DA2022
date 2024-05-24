<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use IMSGlobal\LTI;
use App\Models\Issue;
use Exception;

/**
 * platformからのtool起動時のログイン処理。
 *
 */
class LtiLoginController
{
    /**
     * platformからのtool起動時のログイン処理
     *
     * @param \Illuminate\Http\Request  $request
     */
    public function __invoke(Request $request)
    {
        // platformにidトークンの要求とリダイレクト先の指定
        $db=  new Issue;
        try{
            // platformにOIDCリクエストオブジェクトを渡す
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
        }catch(Exception $e){
            // エラー画面を表示
        }
        
    }
}
