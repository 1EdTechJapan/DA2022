const MongoClient = require('mongodb').MongoClient;

// LTI連携用に必須のライブラリ
const lti = require('ltijs').Provider;
// ここまで必須

const dbCred = require('../config/dbCred');
const cred = dbCred.DB_URI;

const ltiKeys = require('../lti-keys.json');
const ltiEncKey = ltiKeys.ltiEncKey;

lti.setup(ltiEncKey,
    {
        url: cred
    },
    {
        appUrl: "/",
        loginUrl: "/login",
        cookies: {
            secure: false,
            sameSite: 'None'
        }
    })

//プラットフォーム登録
//パラメータ等については下記URL参照
//https://cvmcosta.me/ltijs/#/
exports.registerPlatform = async function(d){    
    try{
        await lti.deploy();
        
        const plat = await lti.registerPlatform(
            {
                url: d.platform_url,
                name: d.platform_name,
                clientId: d.client_id,
                authenticationEndpoint: d.auth_url,
                accesstokenEndpoint: d.token_url,
                authConfig: {method: d.method, key: d.key}
            }
        )

        const kid = await plat.platformKid();
        console.log('kid:', kid)

        return kid;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    }
    finally{
        await lti.close()
    }
}

//deployment_idの登録
exports.registerDeploymentId = async function(d, kid){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const platform = ltiDb.collection("platform-did");

        const doc = {
            platformUrl: d.platform_url,
            clientId: d.client_id,
            kid: kid,
            deploymentId: d.deployment_id,
        }

        const result = await platform.insertOne(doc);

        return result;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    } 
    finally{
        await client.close()
    }  
}

//プラットフォームURLとclient IDからプラットフォーム取得
//パラメータ等については下記URL参照
//https://cvmcosta.me/ltijs/#/
exports.getPlatform = async function(d){
    try{
        await lti.deploy();

        const plat = await lti.getPlatform(d.platform_url, d.client_id)

        return plat;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    }   
    finally{
        await lti.close()
    }
}

//プラットフォームURLからプラットフォーム情報を取得
exports.getPlatformByUrl = async function(url){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const platform = ltiDb.collection("platforms");

        let platformInfo = [];

        if((await platform.estimatedDocumentCount()) === 0){
            return platformInfo;
        }

        const query = { platformUrl: { $eq: url } };
        const options = {
            projection: { _id: 1, platformUrl: 1, clientId: 1, kid: 1, authEndpoint:1 }
        }
        const docs = platform.find(query, options);
        await docs.forEach(doc => {
            platformInfo.push(doc);
        })

        return platformInfo;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    } 
    finally{
        await client.close()
    }  
}

//stateを保存
exports.saveState = async function(d){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const states = ltiDb.collection("states");

        const doc = {
            platformUrl: d.platform_url,
            clientId: d.client_id,
            kid: d.kid,
            state: d.state,
            created: (new Date()).toISOString()
        }

        const result = await states.insertOne(doc);

        return result;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    }
    finally{
        await client.close()
    }
}

//nonceを保存
exports.saveNonce = async function(d, str){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const nonces = ltiDb.collection("nonces");

        const doc = {
            platformUrl: d.platform_url,
            clientId: d.client_id,
            kid: d.kid,
            state: d.state,
            nonce: str,
            created: (new Date()).toISOString()
        }

        const result = await nonces.insertOne(doc);

        return result;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    }
    finally{
        await client.close()
    }
}

//stateを取得
exports.getState = async function(state){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const states = ltiDb.collection("states");

        let stateInfo = [];

        if((await states.estimatedDocumentCount()) === 0){
            return stateInfo;
        }

        const query = { state: { $eq: state } };
        const options = {
            projection: { _id: 1, state: 1, platformUrl:1, clientId: 1, kid: 1, created: 1 }
        }
        const doc = await states.findOne(query, options);
        stateInfo.push(doc);

        return stateInfo;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    }
    finally{
        await client.close()
    }
}

//nonceを取得
exports.getNonceByState = async function(state){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const nonces = ltiDb.collection("nonces");

        let nonceInfo = [];

        if((await nonces.estimatedDocumentCount()) === 0){
            return nonceInfo;
        }

        const query = { state: { $eq: state } };
        const options = {
            projection: { _id: 1, nonce: 1, platformUrl:1, clientId: 1, kid: 1, state: 1, created: 1 }
        }
        const doc = await nonces.findOne(query, options);
        nonceInfo.push(doc);

        return nonceInfo;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    }
    finally{
        await client.close()
    }
}

//プラットフォームの公開鍵情報と、deployment idを取得
exports.getPlatformJWKAndDid = async function(platform_url, client_id, kid){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const platform = ltiDb.collection("platforms");
        const platformDid = ltiDb.collection("platform-did");

        let newDoc;
        let platformInfo = [];

        if((await platform.estimatedDocumentCount()) === 0){
            return platformInfo;
        }

        if((await platformDid.estimatedDocumentCount()) === 0){
            return platformInfo;
        }

        const query = { platformUrl: { $eq: platform_url }, clientId: { $eq: client_id }, kid: { $eq: kid} };
        const options = {
            projection: { _id: 1,  authConfig: 1 }
        }      
        const doc = await platform.findOne(query, options);
        newDoc = doc;

        const options2 = {
            projection: { _id: 1,  deploymentId: 1 }
        }
        const doc2 = await platformDid.findOne(query, options2);
        newDoc.deploymentId = doc2.deploymentId;

        platformInfo.push(doc);

        return platformInfo;
    }
    catch(error){
        console.error(error);
        throw new Error(error);
    } 
    finally{
        await client.close()
    }  
}