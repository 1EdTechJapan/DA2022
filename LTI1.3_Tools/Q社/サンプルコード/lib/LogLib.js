const MongoClient = require('mongodb').MongoClient;

const dbCred = require('../config/dbCred');
const cred = dbCred.DB_URI;

//LTIのリクエストの内容を保存（サードパーティ開始ログイン用エンドポイントに送られてきたものとツール起動用(Launch)エンドポイントに送られてきたものをそれぞれ保存）
exports.saveLtiRequestLog = async function(d, type){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const logRequestLti = ltiDb.collection("request-logs");

        const doc = {
            type: type, //エンドポイントのタイプ　login or launch
            data: d, //リクエスト内容
            created: (new Date()).toISOString()
        }

        const result = await logRequestLti.insertOne(doc);

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

//id_tokenの認証結果を保存
exports.saveTokenLog = async function(idToken, data){
    const client = new MongoClient(cred);

    try{
        const ltiDb = client.db("lti");
        const tokenLog = ltiDb.collection("token-logs");

        const doc = {
            iss: data.iss,
            aud: data.aud,
            nonce: data.nonce,
            token: idToken,
            kid: data.kid,
            client_id:data.client_id,
            verify: data.verify_result,
            received: (new Date()).toISOString()
        }

        const result = await tokenLog.insertOne(doc);

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

//エラーログを保存
exports.saveErrorLog = async function(data, type){
    const client = new MongoClient(cred);
    let d = JSON.parse(data);

    try{
        const ltiDb = client.db("lti");
        const errorLog = ltiDb.collection("error-logs");

        const doc = {
            "type": type, //エラーが起きた場所 login or launch or sub check(学習eポータル独自のエラーなのでそうと分かるように保存)
			"data": d.body, //エラー内容
			"created": (new Date()).toISOString()
        }

        const result = await errorLog.insertOne(doc);

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