// MongoDB利用想定
const MongoClient = require('mongodb').MongoClient
const dbCred = require('../config/dbCred')

const cred = dbCred.DB_URI

exports.putOneRosterLog = async function(d){
    const client = new MongoClient(cred)

    let data = JSON.parse(d)
    let date = (new Date()).toISOString()

    try{
        const oneRosterDb = client.db("oneroster")
        const log = oneRosterDb.collection("oneroster-log")

        // ログとして保存する内容
        const doc = {
            "filename": data.name,
			"filesize": data.size,
			"error": data.error, // エラー数
			"error_msg": data.error_msg, // OneRosterの仕様上のエラー、jsやmongodbから返却されたエラーなど
			"jp_error": data.jp_error, // OneRoster Japan Profile 特有のエラー
			"created": date 
        }

        const result = await log.insertOne(doc)
        
        return result
    }
    catch(error){
        console.error(error)
        throw new Error(error)           
    }
    finally{
        await client.close()
    } 
}