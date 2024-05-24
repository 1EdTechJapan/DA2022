<?php
namespace App\Controller;

use App\Controller\AppController;

use Cake\Cache\Cache;
use Cake\Core\Configure;
use Cake\Http\Response;
use Cake\ORM\TableRegistry;

use App\Common\LtiUser;

class LtiToolsController extends AppController
{
    /**
     * LTI接続に必要なテストのIDなどの受け取りやユーザー情報などの作成
     */
    public function deeplinkwindow()
    {
        $session=$this->getRequest()->getSession();
        $author_id = $this->login_user->id;
        if (empty($author_id)){
            return self::showError("access denied.");
        } else {
            $status=intval($this->request->getQuery('status'),10);
            $review_role=intval($this->request->getQuery('review_role'),10);
            $review_id=intval($this->request->getQuery('review_id'),10);
            $content_id=intval($this->request->getQuery('id'),10);
            $group_id=intval($this->request->getQuery('tg'),10);
            $testcode=$this->request->getQuery('testcode');
            if ($status==0){
                if ($group_id===0){
                    return self::showError("invalid access.");
                }
                $status=3;//lti_message_hintが0だと空になることがあるのでDeeplinkのときはlti_message_hintは3にする
            } else if ($status==1){
                if ($content_id===0||$group_id===0){
                    return self::showError("invalid access.");
                }
            } else if ($status==2){
                if ($content_id===0||$group_id===0){
                    return self::showError("invalid access.");
                }
                if ($this->request->getQuery('review_id') != "" && $this->request->getQuery('review_role') !=""){
                    if ($review_role===0||$review_id===0){
                        return self::showError("invalid access.");
                    }
                }
            } else {
                return self::showError("invalid access.");
            }

            //OpenID,Deeplinkで使うユーザー情報をここで登録
            if (isset($this->login_user->user->uuid)){
                $uuid = $this->login_user->user->uuid;
            } else {
                $uuid=$this->login_user->uuid;
            }
            //団体情報
            $org_name=$this->login_school->name;
            $org_type="S";
            $org_id=$this->login_school->school_code;
            $org_link_id="S_".$this->login_school->id;
            LtiUser::setOrganizationInfo($uuid,$org_name,$org_type,$org_id,$org_link_id);
            //ユーザー情報
            $user_role=LtiUser::getUserRole($this->login_user->id,$uuid);
            if ($testcode=="1"){
                $user_role=0;
            }
            $user_name=$this->login_user->name;
            $user_id=$this->login_user->id;
            LtiUser::setUserInfo($uuid,$user_name,$user_id,$user_role);

            $status="lti_message_hint_test";
                        
            $this->set('status', $status);
            
            $this->set('id', $content_id);
            $this->set('review_id', $review_id);
            $this->set('callsubmit', true);
        }
    }
    
    /**
     * deeplinkwindow関数の処理によって得られた情報からToolに送るOIDCのパラメータを設定
     */
    public function jump()
    {
        $conf = Configure::read('Config.Lti');
        if ($conf === null) {
            Configure::load('config', 'default', true);
            $conf = Configure::read('Config.Lti');
        }
        $TOOL_ENDPOINT= $conf['tool_endpoint'];
        $PLATFORM_CLIENT_ID= $conf['platform_client_id'];
        $DEEPLINK_ENDPOINT= $conf['deeplink_endpoint'];
        $APP_URL= $conf['app_url'];

        if ($this->request->is('post')) {
            if (isset($this->login_user->user->uuid)){
                $uuid = $this->login_user->user->uuid;
            } else {
                $uuid = $this->login_user->uuid;
            }
            $user=LtiUser::getUserInfo($uuid);
            $iss = $APP_URL;
            $lti_message_hint=$this->request->getData('lti_message_hint');
            $content_item_id=intval($this->request->getData('content_item_id'),10);
            
            $select_request=intval($lti_message_hint,10);
            
            if ($lti_message_hint=="lti_message_hint_test"){
                $select_request=1;
            }

            $content_id=0;
            
            $target_link_uri = $DEEPLINK_ENDPOINT;
            
            $ContentItems = TableRegistry::getTableLocator()->get($CONTENT_ITEMS);
            $content_item = $ContentItems->find()->where(['id' => $content_item_id])->first();
            $content_id= $content_item->content_id;
            
            //OpenID,Deeplinkで使うコース情報をここで登録
            $group_id="".$content_item_id;
            LtiUser::setCourseInfo($uuid,$group_id);
            
            $ContentItems = TableRegistry::getTableLocator()->get($CONTENTS);

            $item = $ContentItems->find()->where(['id' => $content_id])->first();
            $content_id=$item->id;
            $target_link_uri = $item->url;
            $this->set('callsubmit', true);
            
            $client_id =  $PLATFORM_CLIENT_ID;
            $org=LtiUser::getOrganizationInfo($user->uuid);
            $lti_deployment_id = $org->deployment_id;
            $login_hint=$user->uuid;
            if (empty($iss)||empty($target_link_uri)||empty($login_hint)||empty($lti_message_hint)||empty($client_id)||empty($lti_deployment_id)||empty($content_id)||empty($TOOL_ENDPOINT)){
                return self::showError("invalid access.");
            }
            
            $this->set('iss', $iss);
            $this->set('target_link_uri', $target_link_uri);
            $this->set('login_hint', $login_hint);
            $this->set('lti_message_hint', $lti_message_hint);
            $this->set('client_id', $client_id);
            $this->set('lti_deployment_id', $lti_deployment_id);
            $this->set('TOOL_ENDPOINT', $TOOL_ENDPOINT);
        }
    }

    public function deleteContentItem(){
        $this->autoRender = false;
        $response = new Response();

        $response = $response->withType('application/json')->withStringBody('{"status": "done"}');
        return $response;
    }
    
}