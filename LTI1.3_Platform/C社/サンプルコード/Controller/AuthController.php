<?php

use App\Controller\AppController;
use Cake\Http\Response;
use Cake\ORM\TableRegistry;
use Cake\Utility\Text;
use App\Common\LtiUser;
use App\Common\LtiLibrary;
use Cake\Core\Configure;

class AuthController extends AppController
{

    /**
     * OpenID Connect 認証リクエスト
     */
    public function index()
    {
        $scope = self::getQuery('scope');
        $responsetype = self::getQuery('response_type');
        $clientid = self::getQuery('client_id');
        $redirecturi = self::getQuery('redirect_uri');
        $loginhint = self::getQuery('login_hint');
        $ltimessagehint = self::getQuery('lti_message_hint');
        $state = self::getQuery('state');
        $responsemode = self::getQuery('response_mode');
        $nonce = self::getQuery('nonce');
        $prompt = self::getQuery('prompt');
        
        $session=$this->getRequest()->getSession();
        
        if ($session_lti_message_hint==""){
            $this->autoRender = false;
            $response = new Response();
            $response = $response->withType('application/json')->withStringBody("auth access denied.");
            return $response;
        }
        
        $org=LtiUser::getOrganizationInfo($loginhint);
        $deployment_id=$org->deployment_id;
        $user=LtiUser::getUserInfo($loginhint);
        $course=LtiUser::getCourseInfo($loginhint);
        $review_user=LtiUser::getReviewUserInfo($loginhint);
        LtiUser::delete($loginhint);
        list($log_hint, $dep_id, $msg_hint, $content_item_id, $content_id, $group_id) = explode(',', $session_lti_message_hint, 6);
        
        $msg_flag=($ltimessagehint!="" && $ltimessagehint===$msg_hint);
        $dep_flag=($deployment_id===$dep_id);

        list($ok,$error,$desc)=self::validate($user,$scope,$responsemode,$responsetype,$clientid,$redirecturi,$loginhint, $state,$nonce,$prompt,$dep_flag,$msg_flag);
        
        if ($ok) {
            if ($ltimessagehint=="lti_message_hint_test"){
                $msghint=1;
            } else {
                $msghint=intval($ltimessagehint,10);
            }
            $ContentItems = TableRegistry::getTableLocator()->get($CONTENTS);
            if ($msghint==3){
                //DeepLinkingRequest
                
                // id_token deep_linking_settings data (必須)　lti/content-returnへのデータ受け渡しや戻ってきたときのチェックに使う
                //$group_idはdataで受け渡す
                $csrf_token=Text::uuid();
                $csrf_token_id=time();
                //トークンの期限はキャッシュの期限（1day）
                Cache::write('lti_csrf_'.$csrf_token_id.$csrf_token , ($csrf_token_id) ,'lti');
                
                list($endpoint, $params) = LtiLibrary::lti_build_content_item_selection_request($deployment_id,$course,$user,$group_id, $nonce,$csrf_token,$csrf_token_id);
                
            } else if ($msghint==1){
                //ResourceLinkRequest
                $score_id=0;

                // 自社独自領域のため詳細は割愛

                list($endpoint, $params) = LtiLibrary::lti_build_resouce_link_request($org,$course,$user, $endpoint, $nonce,$score_id);
            } else if ($msghint==2){
                //ResourceLinkRequest
                $score_id=0;
                $review_user_uuid="";
                $review_user_role=0;

                // 自社独自領域のため詳細は割愛

                list($endpoint, $params) = LtiLibrary::lti_build_resouce_link_request($org,$course,$user, $endpoint, $nonce,$score_id,1,$review_user_uuid,$review_user_role);
            } else {
                $error = 'error_lti_message_hint';
                $desc = 'unknown_value';
                $ok=false;
            }
        }
        if (!$ok) {
            if (isset($state)) {
                $state="";
            }
            if (isset($nonce)) {
                $nonce="";
            }
            $params['error'] = $error;
            if (!empty($desc)) {
                $params['error_description'] = $desc;
            }
            
            $this->autoRender = false;
            $response = new Response();
            $response = $response->withType('application/json')->withStringBody(json_encode(['error'=>$params['error'],"error_description"=>$params['error_description'] ]));
            return $response;
        }
        if (isset($state)) {
            $params['state'] = $state;
        }
        
        $this->set('params', $params);
        $this->set('redirecturi', $redirecturi);
    }
    
    
    private function getQuery($key){
        $value= $this->request->query($key);
        if (empty($value)){
            $value = $this->request->data($key);
        }
        return $value;
    }
    
    private function validate($user,$scope,$responsemode,$responsetype,$clientid,$redirecturi,$loginhint,$state,$nonce,$prompt,$dep_flag,$msg_flag)
    {
        $error = '';
        $desc = '';
        $conf = Configure::read('Config');
        if ($conf === null) {
            Configure::load('config', 'default', true);
            $conf = Configure::read('Config');
        }
        $PLATFORM_CLIENT_ID= $conf['platform_client_id'];
        $TOOL_REDIRECT_URL= $conf['tool_redirect_url'];
        $ok = !empty($scope) && !empty($responsemode) && !empty($responsetype) && !empty($clientid) &&
              !empty($redirecturi) && !empty($loginhint) && !empty($nonce) && !empty($state) && !empty($prompt);
        
        if (!$ok) {
            $error = 'invalid_request';
        }
        if ($ok && ($scope !== 'openid')) {
            $ok = false;
            $error = 'invalid_scope';
        }
        if ($ok && ($responsetype !== 'id_token')) {
            $ok = false;
            $error = 'unsupported_response_type';
        }
        if ($ok) {
            $ok = ($clientid === $PLATFORM_CLIENT_ID);
            if (!$ok) {
                $error = 'unauthorized_client';
            }
        }
        if ($ok) {
            $ok =($redirecturi === htmlspecialchars($TOOL_REDIRECT_URL));
            if (!$ok) {
                $error = 'invalid_redirect_url';
                $desc = $redirecturi;
            }
        }
        if ($ok) {
            $ok = $dep_flag;
            if (!$ok) {
                $error = 'unauthorized_deployment_id';
            }
        }
        if ($ok) {
            $ok = $msg_flag;
            if (!$ok) {
                $error = 'unauthorized_lti_message_hint';
            }
        }
        if ($ok && is_null($user) && $user->uuid===$loginhint) {
            $ok = false;
            $error = 'access_denied';
        }
        if ($ok) {
            if (isset($responsemode)) {
                $ok = ($responsemode === 'form_post');
                if (!$ok) {
                    $error = 'invalid_request';
                    $desc = 'Invalid response_mode';
                }
            } else {
                $ok = false;
                $error = 'invalid_request';
                $desc = 'Missing response_mode';
            }
        }
        if ($ok && ($prompt !== 'none')) {
            $ok = false;
            $error = 'invalid_request';
            $desc = 'Invalid prompt';
        }
        return [$ok, $error, $desc];
    }
}
