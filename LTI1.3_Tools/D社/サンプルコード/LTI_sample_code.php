    public function ltiLoginAction()
    {
        // Set the default view variables
        $this->view->redirectUrl = $this->_config->lti->authRequestUrl;
        $launchUri = $this->_config->currentDomain . "/login/lti-launch";


        // Check if required parameters are present
        // if parameters are incomplete, do not continue with page
        if (empty($this->_request->getParam("iss"))
            || empty($this->_request->getParam("login_hint"))
            || empty($this->_request->getParam("target_link_uri"))) {
            return;
        }

        // Create the state based on request parameters
        $clientId = $this->_request->getParam("client_id") ?? $this->_config->lti->clientId;
        $loginHint = $this->_request->getParam("login_hint");
        $ltiMessageHint = $this->_request->getParam("lti_message_hint");

        $stateParams = Zend_Json::encode([
            "client_id" => $clientId,
            "login_hint" => $loginHint,
            "lti_mesage_hint" => $ltiMessageHint
        ]);

        // Retrieve a nonce and a valid state from backend via RESTful API
        $serviceNonce = (new REST_Api_Model())->getLoginNonce(["state" => $stateParams]);
        $nonce = $serviceNonce["nonce"];
        $state = !empty($serviceNonce["state"]) ? $serviceNonce["state"] : $serviceNonce["nonce"];

        // Requirements are successful
        // Setup view
        $authRequestParams = [
            "response_type" => "id_token",
            "prompt" => "none",
            "scope" => "openid",
            "response_mode" => "form_post",
            "redirect_uri" => $launchUri,
            "client_id" => $clientId,
            "login_hint" => $loginHint,
            "lti_message_hint" => $ltiMessageHint,
            "state" => $state,
            "nonce" => $nonce
        ];

        $this->view->redirectParams = $authRequestParams;
    }




    public function ltiLaunchAction()
    {
        // Set the default view variables
        $this->view->isLoginSuccessful = false;

        // Check if required parameters are present
        $token = $this->_request->getParam("id_token");
        $state = $this->_request->getParam("state");

        if (empty($token) || empty($state)) {
            $this->view->isLoginSuccessful = false;
            $this->view->errorMessage = "No token or state.";
            return;
        }

        // Authenticate the user
        try {
            $connection = (new EnglishCentral_Connection())->createConnectionFromLtiToken($token, $state);            
            $connection->save();

            // On successful login, redirect to the target resource
            $this->view->isLoginSuccessful = true;
            $this->_redirect("/target/resource/uri");

        } catch (Exception $e) {
            // On unsuccessful login, show an error message
            $this->view->isLoginSuccessful = false;
            $this->view->errorMessage = $e->getMessage();
        }
    }




