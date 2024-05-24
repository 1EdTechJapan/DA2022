const Promise = require('promise')

const LogLib = require('../lib/LogLib')

/**
 * ログの保存
 * @param {*} d 保存するログデータ 
 * @returns 
 */
exports.put_oneroster_log = function(d){
    return new Promise((resolve, reject) => {
		LogLib.putOneRosterLog(JSON.stringify(d))
		.then(result => {
			resolve({"status": 201, "body": result})
		})
		.catch(result => {
			reject({"status": 400, "body": result})
		})		
	})
}