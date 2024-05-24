// MongoDB利用想定
const MongoClient = require('mongodb').MongoClient
const dbCred = require('../config/dbCred')

const cred = dbCred.DB_URI

exports.getAccountsListAll = async function(){
    const client = new MongoClient(cred)
    console.log('get accounts')

    try{
        const oneRosterDb = client.db("oneroster")
        const account = oneRosterDb.collection("account")
       
        if((await account.estimatedDocumentCount()) === 0){
            console.log("No documents found!");
            return;
        }

        let accoutList = [];

        const docs = account.find()
        await docs.forEach(doc => {
            // console.log(doc);
            accoutList.push(doc);
        })
        
        return accoutList
    }
    catch(error){
        console.error(error)
        throw new Error(error)           
    }
    finally{
        await client.close()
    } 
}

exports.getAccountsListForOneRoster = async function(){
    const client = new MongoClient(cred)
    console.log('get accounts one roster')

    
    try{
        const oneRosterDb = client.db("oneroster")
        const account = oneRosterDb.collection("account")

        let accoutList = []

        if((await account.estimatedDocumentCount()) === 0){
            console.log("No documents found!");
            return accoutList;
        }

        const query = { register_type: { $eq: "one-roster" } }
        const options = {
            sort: { login_id: 1 },
            projection: { _id: 1, login_id: 1, register_type: 1 }
        }
        const docs = account.find(query, options)
        await docs.forEach(doc => {
            accoutList.push(doc);
        })
        
        return accoutList
    }
    catch(error){
        console.error(error)
        throw new Error(error)           
    }
    finally{
        await client.close()
    } 
}

exports.bulkInsertAccounts = async function(d){
    const client = new MongoClient(cred)
    console.log('bulk insert account')

    try{
        const oneRosterDb = client.db("oneroster")
        const account = oneRosterDb.collection("account")

        const docs = d
        const options = { ordered: true }

        const result = await account.insertMany(docs, options)
        
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

exports.deleteAccount = async function(d){
    const client = new MongoClient(cred)
    console.log('delete account')

    try{
        const oneRosterDb = client.db("oneroster")
        const account = oneRosterDb.collection("account")

        const query = { _id: d._id, login_id: d.login_id }
        const result = await account.deleteOne(query)

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

exports.updateAccout = async function(d){
    const client = new MongoClient(cred)
    console.log('update account')

    try{
        const oneRosterDb = client.db("oneroster")
        const account = oneRosterDb.collection("account")
    
        const filter  = { _id: d._id }    
    
        const options = { upsert: true }
    
        const updateDoc = {
            $set: {
              login_id: d.login_id,
              display_name: d.display_name,
              password: d.password,
              fullname: d.fullname,
              organization: d.organization,
              phone: d.phone,
              register_type: "one-roster",
              modified: (new Date()).toISOString()
            },
        }
    
        const result = await account.updateOne(filter, updateDoc, options)

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