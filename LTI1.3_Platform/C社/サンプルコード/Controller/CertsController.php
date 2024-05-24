<?php
namespace App\Controller\Lti;

use App\Controller\AppController;
use Cake\Http\Response;
use Cake\Event\Event;
use App\Common\JwksHelper;

class CertsController extends AppController
{
    public function beforeFilter(Event $event)
    {
        parent::beforeFilter($event);
    }

    /**
     * 学習eポータルの公開鍵を公開
     */
    public function index()
    {
        $this->autoRender = false;
        $jwks = JwksHelper::get_jwks();
        $response = new Response();
        $response = $response->withType('application/json')
        ->withStringBody(json_encode($jwks));
        return $response;
    }
}
