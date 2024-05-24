const express = require('express');
const router = express.Router();

const logController = require('../../controllers/LogController');
const ltiController = require('../../controllers/LtiController');

// router.get('/', function(req, res) {
//     res.send('success');
// });

//プラットフォーム情報の登録
router.post('/register_platform', async (req, res) => {
	ltiController.register_platform(req, res)
	.then(result => {
		res.status(result.status).json(result);
	})
	.catch(result => {
		console.log("register fail:", result);
		res.status(result.status).json(result);	
	})
})

//Login initiation url サードパーティ開始ログイン用エンドポイント
router.post('/login', function(req, res) {
    let d = req.body;
    // 必須項目の存在チェック
    if(d.iss === undefined){
        let err_data = {body: "iss がありません"};
        //エラーログを残す
        logController.put_lti_error_log(err_data, "login")
        .then(result => {
            res.status(result.status).json(err_data);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 

        return;
    }
    //必須項目の存在チェック
    if(d.login_hint === undefined){
        let err_data = {body: "login_hint がありません"};
        //エラーログを残す
        logController.put_lti_error_log(err_data, "login")
        .then(result => {
            res.status(result.status).json(err_data);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 

        return;
    }

    //リクエストデータ検証、OIDC認証用データ作成及びRedirect
    ltiController.reqLtiAuth(d)
    .then(result => {
        let redirect_uri = "";
        let error = "";
        if(d.target_link_uri){
            try{
                let tlu =  new URL(d.target_link_uri);
                redirect_uri = tlu.protocol + '//' + tlu.host + '/lti/launches';
            }
            catch(err){
                error = err;
            }
        }
        else{
            error = "target link uri が空です";
        }

        if(redirect_uri !== ""){
            //OIDC認証用のクエリを作成
            let qs = "response_type=id_token"
                        + "&scope=openid"
                        + "&response_mode=form_post"
                        + "&prompt=none"
                        + "&login_hint=" + d.login_hint
                        + "&redirect_uri=" + encodeURIComponent(redirect_uri)
                        + "&client_id=" + result.body.client_id
                        + "&state=" + result.body.state
                        + "&nonce=" + result.body.nonce;

            if(d.lti_message_hint){
                qs += "&lti_message_hint=" + d.lti_message_hint
            }

            const url = result.body.auth_request_url + "?" + qs;

            //プラットフォームOIDC認証エンドポイントへリダイレクト
            res.redirect(url);
        }
        else{
            //エラーログを残す
            let res_result = {body: error};
            logController.put_lti_error_log(res_result, "login")
            .then(result => {
                res.status(result.status).json(res_result);
            })
            .catch(result => {
                res.status(result.status).json(result);
            })      
        }
    })
    .catch(result => {
        console.log("fail auth login:", result);
        //エラーログを残す
        let res_result = {body: result};
        logController.put_lti_error_log(res_result, "login")
        .then(result => {
            res.status(result.status).json(res_result);
        })
        .catch(result => {
            res.status(result.status).json(result);
        })          
    })

})

//Login initiation url サードパーティ開始ログイン用エンドポイント
router.get('/login', function(req, res) {
    let d = req.query;
    //必須項目の存在チェック
    if(d.iss === undefined){
        let err_data = {body: "iss がありません"};
        //エラーログを残す
        logController.put_lti_error_log(err_data, "login")
        .then(result => {
            res.status(result.status).json(err_data);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 

        return;
    }
    //必須項目の存在チェック
    if(d.login_hint === undefined){
        let err_data = {body: "login_hint がありません"};
        //エラーログを残す
        logController.put_lti_error_log(err_data, "login")
        .then(result => {
            res.status(result.status).json(err_data);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 

        return;
    }

    //リクエストデータ検証、OIDC認証用データ作成及びRedirect
    ltiController.reqLtiAuth(d)
    .then(result => {
        let redirect_uri = "";
        try{
            let tlu =  new URL(d.target_link_uri);
            redirect_uri = tlu.protocol + '//' + tlu.host + '/lti/launches';
        }
        catch(err){
            console.error(err);
            redirect_uri = req.protocol + '//' + req.get('host') + '/lti/launches';
        }

        //OIDC認証用のクエリを作成
        let qs = "response_type=id_token"
                    + "&scope=openid"
                    + "&response_mode=form_post"
                    + "&prompt=none"
                    + "&login_hint=" + d.login_hint
                    + "&redirect_uri=" + encodeURIComponent(redirect_uri)
                    + "&client_id=" + result.body.client_id
                    + "&state=" + result.body.state
                    + "&nonce=" + result.body.nonce;

        if(d.lti_message_hint){
            qs += "&lti_message_hint=" + d.lti_message_hint
        }

        const url = result.body.auth_request_url + "?" + qs;

        //プラットフォームOIDC認証エンドポイントへリダイレクト
        res.redirect(url);
    })
    .catch(result => {
        console.log("fail auth login:", result);
        //エラーログを残す
        let res_result = {body: result};
        logController.put_lti_error_log(res_result, "login")
        .then(result => {
            res.status(result.status).json(res_result);
        })
        .catch(result => {
            res.status(result.status).json(result);
        })  
    })
})

router.post('/launches', function(req, res){
    //必須項目の存在チェック
    if(!req.body.state){
        let d = {body: "state がありません"};
        //エラーログを残す
        logController.put_lti_error_log(d, "launch")
        .then(result => {
            res.status(result.status).json(d);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 

        return;
    }
    //必須項目の存在チェック
    if(!req.body.id_token){
        let d = {body: "id_token がありません"};
        //エラーログを残す
        logController.put_lti_error_log(d, "launch")
        .then(result => {
            res.status(result.status).json(d);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 

        return;
    }

    //認証レスポンス（id_token）検証
    ltiController.authLaunch(req.body)
    .then(result => {
        //認証処理成功
        //システムの仕様にしたがってコンテンツの表示処理を行う
    })
    .catch(result => {
        console.log("fail auth launch:", result);
        let status = result.status;
		if(!status){
			status = 500
		}

        //エラーログを残す
        let res_result = {body: result};
        logController.put_lti_error_log(res_result, "launch")
        .then(result => {
            res.status(status).json(res_result);
        })
        .catch(result => {
            res.status(result.status).json(result);
        }) 
    })
})

module.exports = router;