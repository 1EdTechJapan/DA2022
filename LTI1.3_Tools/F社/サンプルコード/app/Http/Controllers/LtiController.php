<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Auth;
use App\Models\User;
use Exception;
use App\Http\Shares\LtiDatabase;
use IMSGlobal\LTI;

class LtiController extends Controller
{
    /**
     * Open Id Connect Login Request
     *
     * @param
     *    Request request   リクエストパラーメタ
     *
     * @return なし（リダイレクト）
     */
    public function login(Request $request) {
        try {
            // ログイン初期化要求を受け取り、プラットフォームに戻る
            LTI\LTI_OIDC_Login::new(new LtiDatabase())
            ->do_oidc_login_redirect($request['target_link_uri'])
            ->do_redirect();
        // ログイン初期化要求でエラーが発生した場合は画面上にエラーメッセージを出力
        } catch(Exception $e) {
            echo $e->getMessage();
        }
    }

    /**
     * LTI Message Launches
     *
     * @param
     *    Request request   リクエストパラーメタ
     *
     * @return なし（リダイレクト）
     */
    public function resourceLink(Request $request) {
        try {
            // メッセージを起動し、各種バリデーションチェックを行う
            $launch = LTI\LTI_Message_Launch::new(new LtiDatabase())
            ->validate();
        // 各種バリデーションチェックでエラーが発生した場合は画面上にエラーメッセージを出力
        } catch(Exception $e) {
            echo $e->getMessage();
            return;
        }

        // subを取得
        $user_account_id = $launch->get_launch_data()['sub'] ?? null;
        Log::debug('###LtiController::resourceLink##id_token###', ['fields' => $request['id_token']]);
        Log::debug('###LtiController::resourceLink##state###', ['fields' => $request['state']]);
        Log::debug('###LtiController::resourceLink##sub###', ['fields' => $user_account_id]);

        // iatが空の場合はエラー
        if (empty($launch->get_launch_data()['iat'])) {
            echo 'iat is empty';
            return;
        }

        // expが空の場合はエラー
        if (empty($launch->get_launch_data()['exp'])) {
            echo 'exp is empty';
            return;
        }

        // rolesを取得
        $roles = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/roles'] ?? null;
        // rolesが空の場合はエラー
        if (empty($roles)) {
            echo 'roles is empty';
            return;
        }
        $role_array = [
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Alumni",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Guest",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Member",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Mentor",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#None",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Observer",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Other",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#ProspectiveStudent",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff",
            "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Manager",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Member",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor",
            "http://purl.imsglobal.org/vocab/lis/v2/membership#Officer",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#AccountAdmin",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#Creator",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#None",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysAdmin",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#SysSupport",
            "http://purl.imsglobal.org/vocab/lis/v2/system/person#User"
        ];
        foreach($roles as $role) {
            // roleが指定値以外の場合はエラー
            if (!in_array($role, $role_array)) {
                echo 'Invalid roles【' . $role . '】';
                return;
            }
        }

        // target_link_uriが空の場合はエラー
        if (empty($launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/target_link_uri'])) {
            echo 'target_link_uri is empty';
            return;
        }

        // contextを取得
        $context = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/context'] ?? null;
        // contextのidを取得
        $context_id = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/context']['id'] ?? null;
        // contextが存在し、contextのidが空の場合はエラー
        if (!empty($context) && empty($context_id)) {
            echo 'context_id is empty';
            return;
        }

        // gradeを取得
        $custom_grade = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/custom']['grade'] ?? null;
        $custom_grade_array = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'J1', 'J2', 'J3'];
        // customのgradeが存在し、指定値以外の場合はエラー
        if (!empty($custom_grade) && !in_array($custom_grade, $custom_grade_array)) {
            echo 'Invalid custom_grade【' . $custom_grade . '】';
            return;
        }

        $UUIDv4 = '/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i';

        // tool_platformを取得
        $tool_platform = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/tool_platform'] ?? null;
        // tool_platformのguidを取得
        $tool_platform_gu_id = $launch->get_launch_data()['https://purl.imsglobal.org/spec/lti/claim/tool_platform']['guid'] ?? null;
        // tool_platformが存在し、tool_platformのgu_idが空の場合はエラー
        if (!empty($tool_platform) && empty($tool_platform_gu_id)) {
            echo 'tool_platform_guid is empty';
            return;
        // tool_platformのgu_idが空以外でUUIDv4形式以外の場合はエラー
        } else if (!empty($tool_platform_gu_id) && !preg_match($UUIDv4, $tool_platform_gu_id)) {
            echo 'Invalid tool_platform_guid【' . $tool_platform_gu_id . '】';
            return;
        }

        // subが空以外でUUIDv4形式以外の場合はエラー
        if (!empty($user_account_id) && !preg_match($UUIDv4, $user_account_id)) {
            echo 'Invalid sub【' . $user_account_id . '】';
            return;
        // subが空、または、subがユーザー情報に存在しない場合はトップ画面を表示
        } else if (empty($user_account_id) || User::where('account_id', $user_account_id)->get()->isEmpty()) {
            Log::debug('###LtiController::resourceLink##not exist account_id###');
            return view('top');
        } else {
            // ユーザー情報を取得してログイン
            $user = User::where('account_id', $user_account_id)->first();    
            Auth::login($user);

            // roleが1（生徒）の場合は、生徒のページにリダイレクト
            if ($user->role == 1) {
                Log::debug('###LtiController::resourceLink##exist student account_id###');
                return redirect('/students/lessons');
            // roleが2（先生）の場合は、先生のページにリダイレクト
            } elseif ($user->role == 2) {
                Log::debug('###LtiController::resourceLink##exist teacher account_id###');
                return redirect('/teachers/lessons');
            }
        }
    }
}
