const express = require('express')
const router = express.Router()
const usersController = require('../../controllers/UsersController')
const logController = require('../../controllers/LogController')

// 接続確認用
router.get('/', (req, res) => {
    res.send('success')
    // usersController.get_accounts(req, res)
    // .then(result => {
    //     if (result.status === undefined)
    //         result.status = "200";
    //     res.status(result.status).json({body: result.body});
    // })
    // .catch(result => {
    //     res.send('error')
    // })
});

// ログ保存
router.post('/put_oneroster_log', (req, res) => {
    logController.put_oneroster_log(req.body)
	.then(result => {
		res.status(result.status).json(result.body);
	})
	.catch(result => {
		res.status(result.status).json(result.body);
	});
});

// POSTされてきたデータを受け取って、controllerに渡す
// 結果をviewに返す
router.post('/import_accounts', (req, res) => {
    let req_data, jp_error, count;
    usersController.import_one_roster(req, res) // ファイルをアップロードして、DB登録用のデータを作る
    .then(result => {
        // Japan Profileの仕様上のエラーがある場合、レスポンスにcountとjpErrorが含まれる
        if(result.count){
            count = result.count
            jp_error = result.jpError
        }

        if(!result.body.importData){
            //取り込み対象データなし
            res.status(result.status).json({"body": result.body, "jp_error": jp_error, "count": result.count});
            return
        }

        // 以下取り込み対象データがある場合の処理
        req_data = result.body.importData

        // 取り込み対象データの中で、DBのユーザデータを保存するテーブル内で重複しないものを取り出して配列に入れる、DB既存データとの差分をとるために使う（例：login_id）
        let arr_new_accounts = [];
        for(let i = 0; i < req_data.length; i++){
            let obj = req_data[i];
            arr_new_accounts.push(obj.login_id);
        }       

        usersController.get_account_list_all(req, res) // DBに登録済みのデータを取得する
        .then(async (result) => {
            // DB登録済みデータとの差分を見て、新規、更新、削除のためのデータを作る
            let req_data_insert, req_data_update, req_data_delete;
            if(result.body.length === 0){ // DBにまだデータが１件もない場合、差分見るまでもなく新規作成のみ
                req_data_insert = req_data;
                req_data_update = [];
                req_data_delete = [];  
            }
            else{
                let account_list = result.body;        
                // DB登録済みデータとの差分をとる 
                req_data_insert = makeDiffData(arr_new_accounts, req_data, account_list, "insert");
                req_data_update = makeDiffData(arr_new_accounts, req_data, account_list, "update");
                req_data_delete = makeDiffData(arr_new_accounts, req_data, account_list, "delete");      
            }            

            usersController.delete_account(req_data_delete) // 削除
            .then(result => {
                return usersController.update_account(req_data_update) // 更新
            })
            .then(result => {
                return usersController.bulk_insert_account(req_data_insert) // 新規作成
            })
            .then(result => {
                if (result.status === undefined)
                    result.status = 201;
                // 正常終了
                res.status(result.status).json({"body": result.body, "jp_error": jp_error, "count": count});
            })
            .catch(result => {
                console.log('fail:', result)
                let resBody = {filename: "db", line: "", message: result.body, error_type: "my app"}
                if (result.status === undefined)
                    result.status = 400;
                res.status(result.status).json({body: [resBody], count: 1});              
            })
        })
        .catch(result => {
            console.log('get_account_list_all fail:', result)
            let resBody = {filename: "db", line: "", message: result, error_type: "my app"}
            if (result.status === undefined)
			    result.status = 400;
            res.status(result.status).json({body: [resBody], count: 1});          
        })
    })
    .catch(result => {
		console.log("import accounts fail", result);
		if (result.status === undefined)
			result.status = 400;
		res.status(result.status).json({body: result.body, count: result.count});
    })
})

/**
 * 
 * @param {Array} arr_new 取り込み対象データのlogin_idの配列
 * @param {Array} req_data 取り込み対象データ
 * @param {Array} ac_list DB登録済みデータ 
 * @param {string} method insert or update or delete 
 * @returns 
 */
const makeDiffData = (arr_new, req_data, ac_list, method) => {
    let arr_new_login_id = [...arr_new]; //csvから取り込んだデータ
    let accounts_list = [...ac_list]; //DBに登録済みのデータ
    let data = [...req_data];

    let diffData = [];

    let arr_db_login_id = []
    for(let i = 0; i < accounts_list.length; i++){
        arr_db_login_id.push(accounts_list[i].login_id)
    }

    if(method === "insert"){
        // csvから取り込んだデータにあってDBにない
        const insertAccounts = arr_new_login_id.filter(x => !arr_db_login_id.includes(x));
        diffData = data.filter(d => insertAccounts.includes(d.login_id));
    }
    else if(method === "update"){
        // どちらにもある
        const updateAccunts = arr_new_login_id.filter(x => arr_db_login_id.includes(x));
        const updateData = data.filter(d => updateAccunts.includes(d.login_id));
        
        for(let i = 0; i < updateData.length; i++){
            let req_obj = Object.assign({}, updateData[i]);
            const db_update = accounts_list.find(a => a.login_id === req_obj.login_id);
            // （MongoDB利用想定、_idをキーにデータを更新するので、その情報が欲しい）
            let  shapeData = {
                "_id": db_update._id
            }

            let new_data = Object.assign(shapeData, req_obj)
            diffData.push(new_data);
        }
    }
    else if(method === "delete"){
        // DBにあってcsvから取り込んだデータにない
        const deleteAccounts = arr_db_login_id.filter(x => !arr_new_login_id.includes(x));

        for(let i = 0; i < deleteAccounts.length; i++){
            const db_delete = accounts_list.find(a => a.login_id === deleteAccounts[i]);
            // （MongoDB利用想定、_idとlogin_idをキーにデータを削除するので、その情報が欲しい）
            let new_data = {
                "_id": db_delete._id,
                "login_id": db_delete.login_id
            }
            diffData.push(new_data);
        }
    }

    return diffData;  
}

module.exports = router;