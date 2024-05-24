<?php

error_reporting(0);

use \Firebase\JWT\JWT;
use \Firebase\JWT\JWK;
use \Firebase\JWT\Key;
use \IMSGlobal\LTI;

require_once dirname(__DIR__, 2).'/vendors/autoload.php';
require_once(dirname(__DIR__, 2).'/vendors/imsglobal/lti-1p3-tool/src/lti/lti.php');

App::uses('AppController', 'Controller');
App::import('Vendor', 'util/api');

/**
 * ApiController
 */
class ApiController extends AppController
{
    /**
     * 学習eポータルから学習ツールの起動を開始する
     *
     * params リクエストパラメータから以下のパラメーターを受け取る
     * client_kind      : 学習ツール識別子(mexcbtなど)
     * login_id         : 利用者ログインID
     * link_kind        : リンク種別 1:ディープリンク 2:リソースリンク
     * target_link_url  : リダイレクト先
     * lti_message_hint : 連携付帯情報（独自）
     *
     * return target_link_urlへのリダイレクト
     */
    public function launch()
    {
        $api = new Util\Api();
        //受け取ったパラメーターをログに出力
        $api->showDebugLog('launchにアクセス');
        
        //launchの入力チェックを行いリダイレクト先のURLを生成する
        $base_url = $this->checkLaunch();
        $base_url = $api->urlEncoding($base_url);
        
        //送信するパラメータをログに出力
        $api->showDebugLog('launchから送信_URL', (['URL'=>$base_url]));
        $api->showDebugLog('launchから送信_パラメータ', $api->getUrlParam($base_url));
        return $this->redirect($base_url);
    }

    /**
     * launchの入力チェックを行いリダイレクト先のURLを生成する
     *
     * return 遷移先のURL
     */
    public function checkLaunch()
    {
        #使用するモデルの読み込み
        $this->loadModel('LearningToolSetting');
        $this->loadModel('User');
        
        $error = "";
        $result = [];
        $lts = [];
        $api = new Util\Api();
    
        if (!empty($_GET)) {
            $param = $_GET;
        } elseif (!empty($_POST)) {
            $param = $_POST;
        }

        #必須パラメータの入力チェック
        $error = $api->checkLaunchParams($param);
        if (isset($error) && $error !== "") {
            $result = array('code'=>400, 'message'=> $error);
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        #ユーザー情報を取得する。UUIDが未設定であれば発行する
        $user = $this->User->searchByComnUserCd($param['login_id']);
        if (empty($user)) {
            $result = array('code'=>401, 'message'=> 'ユーザーを取得できませんでした。');
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        $user_xtype = $this->User->getXtype($user);
        #学習ツール識別子から学習ツールの設定情報を取得
        $lts = $this->LearningToolSetting->searchByClientKind($param['client_kind']);
        if (empty($lts)) {
            $result = array('code'=>400, 'message'=> '識別子から情報を取得できませんでした。');
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        } else {
            #操作権限チェック
            $error = $api->operationAuthorityCheck($lts[0]['LearningToolSetting'], $param['link_kind'], $user_xtype);
        }

        #エラーが存在するか
        if (isset($error) && $error !== "") {
            $result = array('code'=>403, 'message'=> $error);
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        #
        #以下、遷移先のURLを生成
        #
        $base_url = '';
        $base_url = $base_url . $lts[0]["LearningToolSetting"]['init_url'] . '?iss=';
        $base_url = $base_url . BASE_URL_RESOURCE;
        

        $base_url = $base_url . '&target_link_uri=';
        if ((empty($param['target_link_url']))) {
            if (strval($param['link_kind']) == DEEP_LINKING_REQUEST) {
                $base_url = $base_url . $lts[0]["LearningToolSetting"]['deeplink_url'];
            }

            if (strval($param['link_kind']) == RESOURCE_LINK_REQUEST) {
                $base_url = $base_url . $lts[0]["LearningToolSetting"]['launch_url'];
            }
        } else {
            $base_url = $base_url . $param['target_link_url'];
        }
        $uuid = $this->User->checkUuid($user);
        $base_url = $base_url . '&login_hint=' . $uuid ;

        $development_id = $lts[0]["LearningToolSetting"]['development_id'];
        if ($development_id != 'mexcbt') {
            $base_url = $base_url . '&lti_deployment_id=' . $development_id ;
        } else {
            $municipality_id = $api->getMunicipalityId($param['lti_message_hint']);
            $user_name = $user[0]['User']['comn_user_cd'];
            #ユーザ情報および学校情報を取得（詳細略）
            $base_url = $base_url . '&lti_deployment_id=' . $school_cd ;
        }

        if ((isset($param['lti_message_hint']))) {
            $base_url = $base_url . '&lti_message_hint=' . $param['lti_message_hint'];
        }
        return $base_url;
    }

    /**
     * AGS用アクセストークンを発行して返却する
     *
     * params 以下のリクエストパラメータ
     * grant_type : client_credentials(固定値)
     * client_assertion_type : urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer(固定値)
     * client_assertion : 以下をBodyに含むJWT
     *   iss   : 学習ツールのクライアントID
     *   sub   : 学習ツールのクライアントID
     *   aud   : 学習eポータルのTokenエンドポイントURL
     *   jti   : JWTの生成日時(UNIX時間)
     *   nbf   : JWTの有効期限(UNIX時間)
     *   scope : https://purl.imsglobal.org/spec/lti-ags/scope/score
     *
     * return 以下をJSON形式で返す
     * access_token : アクセストークン
     * token_type   : Bearer(固定値)
     * expires_in   : 3600(秒)
     * 
     */
    public function token()
    {
        # レンダーを行わないようにする
        $this->autoRender = false;
        #レスポンスタイプの指定
        $this->response->type('application/json');
        #使用するモデルの読み込み
        $this->loadModel('User');
        $this->loadModel('LearningToolSetting');
        $this->loadModel('AccessTokenHistory');

        $api = new Util\Api();
        $api->showDebugLog('tokenにアクセス');

        #必須パラメータの入力チェック
        if ($_SERVER["REQUEST_METHOD"] != "POST") {
            $param = $_GET ;
        } else {
            $param = $_POST ;
        }

        $uuid = $this->User->generateUuid4();

        $jwt = [];
        $jwts = explode('.', $param['client_assertion']);
        foreach (['header'=>0, 'payload' => 1] as $k => $v) {
            $signature = rtrim(strtr(($jwts[$v]), '+/', '-_'), '=');
            $jwt[$k] = json_decode(base64_decode($signature), true);
        }

        $client_id = $jwt['payload']['iss'];

        #学習ツール識別子から学習ツールの設定情報を取得
        $lts = $this->LearningToolSetting->searchByClientId($client_id);
        $jwks_url = $lts[0]["LearningToolSetting"]['jwks_url'];

        //入力パラメータのチェック
        $errors = $api->checkTokenParams($param);
        #$client_id = $lts[0]["LearningToolSetting"]['client_id'];
        if ($jwt['payload']['iss'] != $client_id) {
            array_push($errors, "issの値が不正。");
        }
        if ($jwt['payload']['sub'] != $client_id) {
            array_push($errors, "subの値が不正。");
        }
        if (!(in_array($jwt['payload']['aud'], ACCESS_TOKEN_ACQUISITION_API))) {
            array_push($errors, "audの値が不正。");
        }

        //公開キーを取得
        $key = $api->getPublicKey($jwks_url, $jwt);
        $publickey = openssl_pkey_get_details(JWK::parseKey($key));
        $publickey = $publickey["key"];
        
        //署名検証
        $_jwt = JWT::decode($param['client_assertion'], new Key($publickey, 'RS256'));

        //有効期限のチェック
        if (intval(time()) > intval($jwt['payload']['exp'])) {
            array_push($errors, "JWTの有効期限切れ");
        }
        $scopes = explode(' ', $param['scope']);
        if (!(in_array('https://purl.imsglobal.org/spec/lti-ags/scope/score', $scopes))) {
            array_push($errors, "scopeの値が不正");
        }
        
        if (is_array($errors) && !empty($errors)) {
            $result = array('code'=>400, 'message'=> implode(',', $errors));
            $api->showDebugLog('tokenにerror', $result);
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        $response_param = ['access_token' => $uuid,'token_type'=>'Bearer', 'expires_in' => 3600];

        $this->AccessTokenHistory->accessTokenRegistration($response_param, $lts);

        $api->showDebugLog('tokenのレスポンス', $response_param);
        echo json_encode($response_param);
    }

    /**
     * jwks 公開鍵を返却する
     *
     * param:なし
     *
     * return 公開鍵のリストをJSON形式で返却する
     */
    public function certs()
    {
        header("HTTP/1.1 200 OK");
        header('Cache-Control:no-store');
        header('Pragma:no-cache');
        $this->autoRender = false;
        $this->response->type('application/json;charset=UTF-8');

        $api = new Util\Api();
        $api->showDebugLog('jwksにアクセス');
        
        $json_certs = LTI\JWKS_Endpoint::new([RS_LEARNING_EPORTAL_KID => file_get_contents(PUBLIC_KEY_PATH)])->output_jwks();

        echo($json_certs);
    }

    /**
     * auth 認証リクエストを受けJWTを返す
     *
     * params 以下のリクエストパラメータを受け取る
     * scope            : スコープ openid(固定値)
     * response_type    : レスポンスタイプ id_token(固定値)
     * client_id        : 学習eポータルが学習ツールに発行したclient id
     * redirect_uri     : 応答が送信される先のリダイレクト URI
     * login_hint       : 利用者のUUID
     * state            : 学習ツール側で設定するランダム文字列。CSRF対策
     * response_mode    : form_post(固定値)
     * nonce            : 学習ツール側で設定するランダム文字列。リプレイアタック対策
     * prompt           : none(固定値)
     * lti_message_hint : OpenID Connect サードパーティーログインイニシエーションリクエストで指定した値がセットされる
     *
     * return 指定されたリダイレクトURLにリダイレクトする。 
     */
    public function authLoginUrl()
    {
        $this->layout = "";
        $this->loadModel('User');
        $this->loadModel('LearningToolSetting');
        $api = new Util\Api();
        //受け取ったパラメーターをログに出力
        $api->showDebugLog('authにアクセス');

        #必須パラメータの入力チェック
        if ($_SERVER["REQUEST_METHOD"] != "POST") {
            $param = $_GET ;
            $error = $api->checkAuthParams($_GET);
            $lts = $this->LearningToolSetting->searchByClientId($_GET['client_id']);
        } else {
            $param = $_POST ;
            $error = $api->checkAuthParams($_POST);
            $lts = $this->LearningToolSetting->searchByClientId($_POST['client_id']);
        }
        $municipality_id = $api->getMunicipalityId($param['lti_message_hint']);

        #エラーが存在するか
        if (isset($error) && $error !== "") {
            $result = array('code'=>400, 'message'=> $error);
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        if (empty($param['nonce'])) {
            $result = array('code'=>400, 'message'=> 'nonceが設定されていません');
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        if (empty($param['state'])) {
            $result = array('code'=>400, 'message'=> 'stateが設定されていません');
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }


        #client_idからLearningToolSettingが取得できているか
        if (is_array($lts) && empty($lts)) {
            $result = array('code'=>400, 'message'=> 'client_id 未登録');
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        } else {
            //リダイレクトを許可するURLを取得
            $redirect_urls = $this->LearningToolSetting->getRedirectUrls($lts[0]['LearningToolSetting']['redirect_urls']);

            #リダイレクト先が登録されているか
            $check_redirect_uri = $api->removeParam($param['redirect_uri']);
            if (!(in_array($check_redirect_uri, $redirect_urls))) {
                var_dump($check_redirect_uri);
                if (strpos($check_redirect_uri, '/lineitems/') !== false) {
                    // pass
                } else {                    
                    $result = array('code'=>400, 'message'=> 'リダイレクト先が正しくありません。');
                    echo json_encode($result, JSON_UNESCAPED_UNICODE);
                    exit;
                }
            }
        }

        #ユーザーが取得可能か
        $user = $this->User->searchByUuid($param['login_hint']);
        if (empty($user)) {
            $result = array('code'=>401, 'message'=> 'ユーザーを取得できませんでした。');
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        $coordination_type = $api->getCoordinationType($param['lti_message_hint']);

        $development_id = $lts[0]["LearningToolSetting"]['development_id'];
        if ($development_id != 'mexcbt') {
            //pass
        } else {
            $municipality_id = $api->getMunicipalityId($param['lti_message_hint']);
            $user_name = $user['comn_user_cd'];
            
            #ユーザ情報および学校情報を取得（省略）
            
            $development_id = $school_cd ;
        }
       
        #
        #以下、JWTを作成
        #
        $message_jwt = $api->messageJwtCreation();
        $message_jwt['aud'] = [$lts[0]['LearningToolSetting']['client_id']];
        $message_jwt['sub'] = $user['uuid'];
        $message_jwt['nonce'] = $param['nonce'];
        //$message_jwt['name'] = $user['comn_user_cd'];
        $message_jwt['iss'] = BASE_URL_RESOURCE;
        $message_jwt["https://purl.imsglobal.org/spec/lti/claim/deployment_id"] = $development_id;
        
        #lti_message_hintからコンテンツのuuidを取得（省略）

        if ($coordination_type == COORDINATION_TYPE_PROBLEM_SEARCH) {
            //問題検索DEEPLINK
            $deep_linking_settings_data = $this->User->generateUuid4();
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/message_type"] = "LtiDeepLinkingRequest" ;

            #$message_jwt["https://purl.imsglobal.org/spec/lti-ags/claim/endpoint"] = "";
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/target_link_uri"] = "";
            $message_jwt["https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"]["deep_link_return_url"] = DEEP_LINK_RETURN_URL;
            $message_jwt["https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"]["accept_types"] = ["ltiResourceLink"] ;
            $message_jwt["https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"]["accept_presentation_document_targets"] = ["window"] ;
            $message_jwt["https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"]["data"] = $deep_linking_settings_data;
            $message_jwt["https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings"]["accept_multiple"] = false;
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/roles"] = ['http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty', 'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor'];

        } else {
            $message_jwt["https://purl.imsglobal.org/spec/lti-ags/claim/endpoint"] = [
                "scope" => [
                    #"https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                    #"https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                    "https://purl.imsglobal.org/spec/lti-ags/scope/score"
                ]
            ];
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/message_type"] = "LtiResourceLinkRequest" ;
            $message_jwt['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']['lineitem'] =  BASE_URL_RESOURCE . '/rsapi/v1/ags/' . $municipality_id . $content_uuid .'/lineitems/0'; #. '?resource_link_id='.urlencode($param['lti_message_hint']) ;
        }

        $message_jwt["https://purl.imsglobal.org/spec/lti/claim/context"] = #タイトルを設定
 

        if ($coordination_type == COORDINATION_TYPE_ANSWER_RESULT) {
            # 下記フラグを適切に設定（詳細略）
            $flag_custom_show_score = true;
            $flag_custom_show_correct = true;

            $message_jwt['https://purl.imsglobal.org/spec/lti/claim/custom'] = [
                'for_user_id' => $api->getentranceExamPersonUuid($param['lti_message_hint']), 
                'for_roles' => [
                    'http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student',
                    'http://purl.imsglobal.org/vocab/lis/v2/membership#Learner'
                ],

                "custom_show_score" => $flag_custom_show_score,
                "custom_show_correct" => $flag_custom_show_correct
            ];
        } 
        
        if (#教員かどうかチェック)) {
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/roles"] = ['http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty', 'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor'];
        } else {
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/roles"] = ["http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student", "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"];
        }
        if ($coordination_type == COORDINATION_TYPE_PROBLEM_SEARCH) {
        } else {
            $count = $api->entranceExamTimes($param['lti_message_hint']);
            $student_uuid = $api->getentranceExamPersonUuid($param['lti_message_hint']);
            if (empty($student_uuid)) {
                $student_uuid = $user['uuid'];
            }
            $resource_link_id = $content_uuid . '_' . $student_uuid . '_' . sprintf('%03d', $count);
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/resource_link"] = ["id" => $resource_link_id, 'title' => $tool_title];
        }
        if ($coordination_type == COORDINATION_TYPE_EXAM) {
          $message_jwt["https://purl.imsglobal.org/spec/lti/claim/target_link_uri"] = #事前に取得したリソースＵＲＬを設定 
        }
        if ($coordination_type == COORDINATION_TYPE_ANSWER_RESULT) {
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/target_link_uri"] = #事前に取得したレビューＵＲＬを設定 
        }
        if ($coordination_type == COORDINATION_TYPE_OTHER) {
            $message_jwt["https://purl.imsglobal.org/spec/lti/claim/target_link_uri"] = $lts[0]["LearningToolSetting"]['launch_url'];
            $message_jwt["tool_consumer_instance_guid"] = $this->User->generateUuid4();
        }
        // @codingStandardsIgnoreEnd
        $jwt = JWT::encode(
            $message_jwt,
            file_get_contents(PRIVATE_KEY_PATH),
            'RS256',
            RS_LEARNING_EPORTAL_KID
        );
        if (!(isset($_REQUEST['redirect_uri']))) {
            $_REQUEST['redirect_uri'] = $add_param["https://purl.imsglobal.org/spec/lti-dl/claim/content_items"][0]["url"];
        }

        //リダイレクト時のJWTをログに出力
        $api->showDebugLog('authからリダイレクト', $message_jwt);

        $this->set(compact('jwt', 'deep_linking_settings_data', 'content_uuid'));
        $this->render('authLoginUrl');
    }

    /**
     * deepLinkingResponse
     *
     * param 下記の一覧のクレームが含まれるJSON Webトークン
     * iss   : 学習eポータルが学習ツールに発行したclient id
     * aud   : 学習eポータルのベースURLの配列
     * exp   : JWTの有効期限(UNIX時間)
     * iat   : JWTの生成日時(UNIX時間)
     * nonce : ノンス値
     * sage_type : LtiDeepLinkingResponse(固定値)
     * version : 1.3.0(固定値)
     * deployment_id : 学習ツール識別子
     * content_items : ユーザが選択したコンテンツの配列。
     * data          : 先行のDeepLinkingRequestのdeep_linking_settingsクレームのdataプロパティの値を返送する。
     * errormsg      : リクエストの検証でエラーになった場合に利用する
     * errorlog      : リクエストの検証でエラーになった場合に利用する
     *
     * render JWTのペイロード部分をJSON形式でビューに渡す
     */
    public function deepLinkingResponse()
    {
        $this->autoRender = false;
        $this->loadModel('LearningToolSetting');
        $api = new Util\Api();
        $api->showDebugLog('DeepLinkingResponse');
        $pay = explode('.', $_POST['JWT']);
        
        $signature = rtrim(strtr(($pay[1]), '-_', '+/'), '=');
        $data = (base64_decode($signature));

        $check_data = json_decode($data, true);

        $errors = $api->checkDeepLinkingResponse($check_data);
        if (!(empty($check_data['iss']))) {
            $lts = $this->LearningToolSetting->searchByClientId($check_data['iss']);
            if ((empty($lts))) {
                array_push($errors, "設定情報が見つかりません");
            } 
        }

        if (is_array($errors) && !empty($errors)) {
            $result = array('code'=>400, 'message'=> implode(',', $errors));
            $api->showDebugLog('deepLinkingResponseにerror', $result);
            echo json_encode($result, JSON_UNESCAPED_UNICODE);
            exit;
        }

        $this->set(compact('data'));
        $this->render('deep');
    }

    /**
     * ltiAgs
     *
     * param 以下のリクエストパラメータを受け取る
     * timestamp        : scoreが変更された時間
     * scoreGiven       : score（0を含む正の数字）
     * scoreMaximum     : max score（ScoreGivenを含む場合は必須）
     * comment          : 任意の文字列。
     * activityProgress : Initialized（開始前）/Started（開始）/InProgress（受験中）/Submitted（送信済み）/Completed（完了）
     * gradingProgress  : FullyGraded（採点済み）/Pending（最終成績保留中、人間の介入不要）/PendingManual（最終成績保留中、人間の介入必要）/Failed（採点失敗）/NotReady（未採点）
     * userId           : ResourceLinkRequestで受け取ったユーザID(sub)
     * 
     * return 
     */
    public function ltiAgs()
    {
        $this->loadModel('User');
        $this->autoRender = false;
        $this->response->type('application/json');

        $api = new Util\Api();
        $api->showDebugLog('AGSにアクセス');

        $uri = rtrim($_SERVER["REQUEST_URI"], '/');
        $uris = explode('/', $uri);
        $uri = substr($uri, strrpos($uri, '/') + 1);
        $uri = explode('?', $uri);
        $uri = $uri[0];

        if (empty($_POST)) {
            $param = $_GET ;
        } else {
            $param = $_POST ;
        }
        $contents_uuid = $uris[4];
        
        $contents_uuid = substr_replace($contents_uuid, "", 0, 3);
        $data = file_get_contents('php://input');
        $score = json_decode($data, true);
                
        $api->showDebugLog('params', $score);

        $user_id = $score['userId'];
        $value = $score['scoreGiven'];
        $user_uuid = $score['userId'];
       

        //スコアの記録（省略）

        header("HTTP/1.1 200 OK");
        header("Status: 200");
        header("Content-Type: text/plain");
        echo "OK";
    }
}
