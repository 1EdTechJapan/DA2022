// LTI連携用に必須のライブラリ
const jwt = require('jsonwebtoken');
const jwksClient = require('jwks-rsa');
const crypto = require('crypto');
// ここまで必須

const ltiKeys = require('../lti-keys.json');
const tidSecret = ltiKeys.tidSecret; //データエンコードに使う

const LtiLib = require('../lib/LtiLib');
const LogLib = require('../lib/LogLib');

//プラットフォーム情報の登録
exports.register_platform = (req, res) => {
    let d = req.body;
    return new Promise((resolve, reject) => {
        if(!d){
            return reject({status: 400, body: "登録するデータがありません"})
        }

        LtiLib.getPlatform(d)
        .then(result => {
            if(!result){
                LtiLib.registerPlatform(d)
                .then(result => {
                    return LtiLib.registerDeploymentId(d, result); //deployment_idも登録する
                })
                .then(result => {
                    resolve({status:201, body: "登録成功"});
                })
                .catch(err => {
                    console.log("register platform error:", err);
                    reject(err);
                })
            }
            else{
                resolve({status: 200, body: "すでに登録済みです"})
            }
        })
        .catch(err => {
            console.log("get platform error:", err);
            reject(err);
        })
    })
}

//リクエストデータ検証、OIDC認証用データ作成のためDBから必要項目を取得
/**
 * 
 * @param {*} d プラットフォームから送られてきたリクエストデータ
 * @returns 
 * 
 * 返す内容
 * {
 *  status: number  ステータスコード
 *  body: Object    OIDC認証用データ
 * }
 * 
 * bodyの内容
 * {
 *  id,                DBにプラットフォーム登録時自動採番されるID
 *  kid,
 *  client_id,
 *  platform_url,
 *  auth_request_url,  プラットフォームOIDC認証エンドポイント
 *  state,
 *  nonce
 * }
 */
exports.reqLtiAuth = (d) => {
    return new Promise((resolve, reject) => {
        let platformInfo;
        //登録済みのプラットフォーム情報を取得する
        LtiLib.getPlatformByUrl(d.iss)
        .then(result => {
            if(result.length === 0){
                return reject({status: 400, body: "プラットフォームが登録されていません"});
            }
            else{
                platformInfo = {
                    id:  result[0]._id,
                    kid: result[0].kid,
                    client_id: result[0].clientId,
                    platform_url: result[0].platformUrl,  
                    auth_request_url: result[0].authEndpoint
                }

                //リクエストデータにclient_idが含まれている場合、DB登録済みのものと一致するかチェック
                if(d.client_id && result[0].clientId != d.client_id){
                    return reject({status: 400, body: "client idが登録されているものと一致しません"});
                }

                //stateとnonceを作成
                const state = "state-" + crypto.randomUUID();
                let nonceStr = crypto.randomBytes(16).toString('base64');
                const nonce = crypto.createHash('sha256').update(nonceStr + tidSecret).digest('hex');

                platformInfo.state = state;
                platformInfo.nonce = nonce;

                //stateとnonceをDBに保存しておく
                LtiLib.saveState(platformInfo)
                .then(result => {
                    LtiLib.saveNonce(platformInfo, nonceStr)
                    .then(result => {
                        //リクエスト内容を保存する
                        LogLib.saveLtiRequestLog(d, 'login-request')
                        .then(result => {
                            resolve({status: 200, body: platformInfo}) //OIDC認証用データ作成の情報を返す
                        })
                        .catch(err => {
                            console.log("save login request log error:", err);
                            reject(err); 
                        })
                    })
                    .catch(err => {
                        console.log("save nonce error:", err);
                        reject(err); 
                    })
                })
                .catch(err => {
                    console.log("save state error:", err);
                    reject(err); 
                })
            }
        })
        .catch(err => {
            console.log("get platform by URL error:", err);
            reject(err);
        })
    })
}

//認証レスポンス（id_token）検証
/**
 * 
 * @param {*} d プラットフォームから送られてきたデータ
 * @returns 
 * 
 * 返す内容
 * {
 *  status: number  ステータスコード
 *  body: Any       認証成功ならコンテンツ表示に必要な情報を返すなど、システムの仕様に合わせる
 * }
 */
exports.authLaunch = function(d) {
    return new Promise((resolve, reject) => {
        const state = d.state;

        let doc;
        let idToken, header, payload;
        let platform_url, client_id, kid, deployment_id;
        let sign_err, decoded_data;

        //stateを取得
        LtiLib.getState(state)
        .then(result => {
            if(result.length === 0){
                return reject({status: 400, body: "無効なstateです"});
            }

            //stateが作成されてから時間が経ちすぎている場合、セッションタイムアウト
            let created = new Date(result[0].created);
            let nowDate = new Date();
            const limit = 24*3600*1000; //リミットはシステムの仕様による

            if(nowDate.getTime() - created.getTime() > limit){
                return reject({status: 400, body: 'Session Timeout'});
            }

            //nonceを取得
            LtiLib.getNonceByState(state)
            .then(result => {
                if(result.length === 0){
                    return reject({status: 400, body: "無効なnonceです"});
                }
                doc = result[0];

                idToken = d.id_token;
                let spToken = idToken.split('.');
    
                //id_tokenがヘッダー、ペイロード、サインの３つになっていない
                if(spToken.length !== 3){             
                    return reject({status: 400, body: "無効なid_tokenです"});
                }

                let bufHeader = spToken[0];
                bufHeader = bufHeader.replace(/ /g, '+');
                header = Buffer.from(bufHeader, 'base64').toString();
                header = JSON.parse(header);
    
                let bufPayload = spToken[1];
                bufPayload = bufPayload.replace(/ /g, '+');
                payload = Buffer.from(bufPayload, 'base64').toString();
                payload = JSON.parse(payload);

                //ヘッダーとペイロードの確認
                const checks = checkAuthReq(header, payload, doc);
                if(checks.status !== 200){       
                    return reject(checks);
                }

                platform_url = doc.platformUrl;
                client_id = doc.clientId;
                kid = doc.kid;

                let req_data = {
                    header: bufHeader,
                    payload: bufPayload,
                    token: idToken,
                    decHeader: header,
                    decPayload: payload
                }

                //ログを保存しておく
                LogLib.saveLtiRequestLog(req_data, 'launch-request')
                .then(result => {
                    //サイン検証のための公開鍵をDBから取得
                    return LtiLib.getPlatformJWKAndDid(platform_url, client_id, kid);
                })
                .then(async result => {
                    if(result.length !== 1){
                        return reject({status: 400, body: "Bad request"})
                    }

                    deployment_id = result[0].deploymentId;

                    //keyset url か rsa かで処理がちょっと変わる
                    if(result[0].authConfig.method === "JWK_SET"){
                        // keyset url の場合、ライブラリを使って鍵情報を取得する
                        const client = jwksClient({
                            jwksUri: result[0].authConfig.key,
                            timeout: 30000
                        });

                        try{
                            let signKey;
                            if(header.kid){
                                const key = await client.getSigningKey(header.kid);
                                signKey = key.getPublicKey();
                            }
                            else{
                                const key = await client.getSigningKey();
                                signKey = key.getPublicKey();   
                            }     

                            //検証
                            jwt.verify(idToken, signKey, { nonce: payload.nonce }, function(err, decode){
                                let verify_result;
                                let log_data = {                   
                                    "kid": kid,
                                    "client_id": client_id,
                                };
                                if(err){
                                    console.log('err:', err)
                                    verify_result = "fail";
                                    sign_err = err;
                                    log_data.sign_err = sign_err;
                                }
                                else{
                                    verify_result = "success";
                                    decoded_data = decode;
                                    log_data.iss = decode.iss;
                                    log_data.aud = decode.aud;
                                    log_data.nonce = decode.nonce;
                                }
    
                                log_data.verify_result = verify_result;
                                
                                //検証結果を保存する
                                return LogLib.saveTokenLog(idToken, log_data)
                            })
                        }
                        catch(err){
                            console.log('jwk catch error:', err)
                            sign_err = err
                            return reject({status: 401, body: err});
                        }
                    }
                    else if(result[0].authConfig.method === "RSA_KEY"){
                        try{
                            // rsa の場合
                            let signKey = result[0].authConfig.key;

                            //改行がないと検証に失敗するので、改行を入れる
                            let keyStr = signKey.replace('-----BEGIN PUBLIC KEY-----', "").replace('-----END PUBLIC KEY-----', "");
                            keyStr = keyStr.trim().replace(/ /g, '\n');
                            let pem = "-----BEGIN PUBLIC KEY-----\n";
                            pem += keyStr + "\n";
                            pem += "-----END PUBLIC KEY-----\n";

                            //検証
                            jwt.verify(idToken, pem, { nonce: payload.nonce }, function(err, decode){
                                let verify_result;
                                let log_data = {                   
                                    "kid": kid,
                                    "client_id": client_id,
                                };
                                if(err){
                                    console.log('err2:', err)
                                    verify_result = "fail";
                                    sign_err = err;
                                    log_data.sign_err = sign_err;
                                }
                                else{
                                    verify_result = "success";
                                    decoded_data = decode;
                                    log_data.iss = decode.iss;
                                    log_data.aud = decode.aud;
                                    log_data.nonce = decode.nonce;
                                }
    
                                log_data.verify_result = verify_result;
    
                                //検証結果を保存する
                                return LtiLib.saveTokenLog(idToken, log_data)
                            })
                        }
                        catch(err){
                            console.log('rsa catch error:', err)
                            sign_err = err
                            return reject({status: 401, body: err});
                        }
                    }
                })
                .then(result => {
                    if(sign_err){ //検証結果がエラーだった場合
                        return reject({status: 401, body: sign_err})
                    }

                    //必須のclaimを確認する
                    const checkClaims = checkRequiredClaims(decoded_data, deployment_id);
                    if(checkClaims.status !== 200){
                        return reject(checkClaims);
                    }

                    //custom claim等から表示するコンテンツの情報を取得するなど、システム独自に必須項目がある場合ここでチェック
                    //ex 1. sub を login_id の一部として使用する場合
                    let sub = "";
                    if(!decoded_data.sub){
                        return reject({status: 400, body: "sub がありません"})  
                    }
                    else{
                        sub = decoded_data.sub;
                    }
                    //ex 2. custom claim に content_id を指定して表示コンテンツを特定する場合
                    const customClaim = "https://purl.imsglobal.org/spec/lti/claim/custom";
                    if(!decoded_data[customClaim]){
                        return reject({status: 400, body: "custom claim がありません"})  
                    }
                    if(!decoded_data[customClaim].content_id){
                        return reject({status: 400, body: "content_id がありません"})         
                    }                    
                    //システムの仕様に合わせてコンテンツ表示等に必要なユーザー情報を作っておく（例：login_id, content_idでコンテンツ表示の処理をする）
                    let userData = {
                        "login_id": `user_${sub}`,
                        "content_id": decoded_data[customClaim].content_id
                    }

                    //学習eポータル独自、subはuuid v4である必要がある
                    //チェックしてエラーログを残す
                    const sub_regex_uuid = /^([a-f0-9]{8})-([a-f0-9]{4})-([a-f0-9]{4})-([a-f0-9]{4})-([a-f0-9]{12})$/;
                    const sub_regex_v4 = /^([a-f0-9]{8})-([a-f0-9]{4})-(4[a-f0-9]{3})-([a-f0-9]{4})-([a-f0-9]{12})$/;
                    if(!sub_regex_uuid.test(sub)){
                        let sub_error = {body: `sub(${sub})はuuidではありません。`};
    
                        LogLib.saveErrorLog(JSON.stringify(sub_error), "sub check")
                        .then(result => {
                            resolve({status: 200, body: userData})   
                        })
                        .catch(err => {
                            console.log("auth for launch err sub uuid check:", err);
                            reject(err);            
                        })
                    }
                    else if(!sub_regex_v4.test(sub)){      
                        let sub_error = {body: `sub(${sub})はuuid v4ではありません。`}; 

                        LogLib.saveErrorLog(JSON.stringify(sub_error), "sub check")
                        .then(result => {
                            resolve({status: 200, body: userData})   
                        })
                        .catch(err => {
                            console.log("auth for launch err sub uuid v4 check:", err);
                            reject(err);            
                        })                           
                    }  
                    else{
                        resolve({status: 200, body: userData}); //認証レスポンス検証完了、コンテンツ表示に必要な情報等を返す
                    }     
                })
                .catch(err => {
                    console.log("save launch request log error:", err);
                    reject(err); 
                })
            })
            .catch(err => {
                console.log("get nonce error:", err);
                reject(err);    
            })
        })
        .catch(err => {
            console.log("get state error:", err);
            reject(err);
        })
    })
}

//ヘッダーとペイロードの確認
const checkAuthReq = (header, payload, doc) => {
    let errorRes;

    let aud = payload.aud;
    const iss = payload.iss;
    const nonce = payload.nonce.replace(/ /g, '+');

    //issがDBに登録されているプラットフォーム情報と一致するか確認
    if(iss !== undefined && iss !== doc.platformUrl){
        errorRes = {status: 400, body: "不正なissです"};
        return errorRes;
    }

    //aud存在チェック
    if(!aud){
        errorRes = {status: 400, body: "不正なaudです"};
        return errorRes;
    }

    //audがある場合、DBに登録済みのclient_idと一致するか確認
    if(Array.isArray(aud)){
        if(aud.length > 1){
            let filAud = aud.filter(d => d === doc.clientId);
            if(filAud.length === 0){
                errorRes = {status: 400, body: "不正なaudです"};
                return errorRes;
            }
            else{
                aud = filAud[0];
            }
        }
        else if(aud.length === 1){
            aud = aud[0];
        }
        else{
            errorRes = {status: 400, body: "不正なaudです"};
            return errorRes;  
        }
    }

    if(aud !== doc.clientId){
        errorRes = {status: 400, body: "不正なaudです"};
        return errorRes;  
    }

    let nowDate = new Date();

    //expがある場合、期限が切れていないか確認
    if(payload.exp !== undefined){
        let date;
        try{
            date = new Date(payload.exp * 1000)
        }
        catch(err){
            errorRes = {status: 400, body: err}
            return errorRes;         
        }
    
        try{
            date = new Date(payload.iat * 1000)
        }
        catch(err){
            errorRes = {status: 400, body: err}
            return errorRes;         
        }

        if((nowDate.getTime() / 1000) > payload.exp){
            errorRes = {status: 400, body: "Tokenの期限が切れています"};
            return errorRes;
        }
    }

    //nonceがDBに保存されているものと一致するか確認
    let checkNonce = crypto.createHash('sha256').update(doc.nonce + tidSecret).digest('hex');
    if(nonce !== checkNonce){
        errorRes = {status: 400, body: "不正なnonceです"};
        return errorRes;
    }

    //iatがある場合、tokenが古すぎないか確認
    if(payload.iat !== undefined){
        const limit2 = 10 * 60; //リミットはシステムの仕様による
         if((nowDate.getTime() / 1000) - payload.iat > limit2){
            errorRes = {status: 400, body: 'TOkenが古すぎます'};
            return errorRes;
        }
    }

    //アルゴリズムを確認
    if(header.alg !== "RS256"){
        errorRes = {status: 400, body: "アルゴリズムがRS256ではありません"};
        return errorRes;
    }

    return {status: 200, body: "no error"}
}

//必須のclaimを確認
const checkRequiredClaims  = (data, deployment_id) => {
    let errorRes;

    const msgTypeClaim = "https://purl.imsglobal.org/spec/lti/claim/message_type";
    const versionClaim = "https://purl.imsglobal.org/spec/lti/claim/version";
    const deployIdClaim = "https://purl.imsglobal.org/spec/lti/claim/deployment_id";
    const targetLinkClaim = "https://purl.imsglobal.org/spec/lti/claim/target_link_uri"
    const resourceLinkClaim = "https://purl.imsglobal.org/spec/lti/claim/resource_link";
    const roleClaim = "https://purl.imsglobal.org/spec/lti/claim/roles";
    const contextClaim = "https://purl.imsglobal.org/spec/lti/claim/context"

    if(!data[versionClaim]){
        errorRes = {status: 400, body: "version claim がありません"}
        return errorRes;
    }
    if(data[versionClaim] !== "1.3.0"){
        errorRes = {status: 400, body: "LTI version が 1.3.0 ではありません"}
        return errorRes;
    }
    if(!data[msgTypeClaim]){
        errorRes = {status: 400, body: "message_type claim がありません"}
        return errorRes;    
    }
    if(data[msgTypeClaim] !== "LtiResourceLinkRequest"){
        errorRes = {status: 400, body: "message_type が LtiResourceLinkRequest ではありません"}
        return errorRes;  
    }
    if(!data[deployIdClaim]){
        errorRes = {status: 400, body: "deployment_id claim がありません"}
        return errorRes;    
    }
    if(data[deployIdClaim] !== deployment_id){
        errorRes = {status: 400, body: "deployment_id が登録されている値と一致しません"}
        return errorRes;  
    }
    if(!data[targetLinkClaim]){
        errorRes = {status: 400, body: "target link uri claim がありません"}
        return errorRes;  
    }
    if(!!data[resourceLinkClaim]){
        errorRes = {status: 400, body: "resource_link claim がありません"}
        return errorRes;  
    }
    if(!data[resourceLinkClaim].id){
        errorRes = {status: 400, body: "無効な resource link id です"}
        return errorRes;
    }
    if(!data[roleClaim]){
        errorRes = {status: 400, body: "roles claim がありません"}
        return errorRes;  
    }
    if(data[roleClaim].length === 0){
        errorRes = {status: 400, body: "roles claim が空です"}
        return errorRes;
    }
    if(data[contextClaim] && !data[contextClaim].id){
        errorRes = {status: 400, body: "context claim に id がありません"}
        return errorRes;
    }
    if(data[platformClaim] && !data[platformClaim].guid){
        errorRes = {status: 400, body: "tool platform claim に guid がありません"}
        return errorRes;
    }

    return {status: 200, body: "No error"}
}