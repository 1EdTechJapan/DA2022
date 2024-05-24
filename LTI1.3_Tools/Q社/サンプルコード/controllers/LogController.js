const LogLib = require('../lib/LogLib');

//エラーログ保存処理
exports.put_lti_error_log = function(d, type){
	return new Promise((resolve, reject) => {
		LogLib.saveErrorLog(JSON.stringify(d), type)
		.then(result => {
			resolve(result)
		})
		.then(result => {
			reject(result);
		})
	})
}