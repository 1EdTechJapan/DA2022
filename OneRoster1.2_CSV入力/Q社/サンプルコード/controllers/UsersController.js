// OneRoster連携用に必須のライブラリ
const Promise = require('promise')
const formidable = require('formidable')
const path = require("path")
const admZip = require("adm-zip")
const Readable = require('stream').Readable
const CsvReadableStream = require('csv-reader')
const AutoDetectDecoderStream = require('autodetect-decoder-stream')
const iconv = require('iconv-lite')
const jschardet = require('jschardet')
// ここまで必須

const UsersLib = require('../lib/UsersLib')

const crypto = require('crypto')
const pwdPolicy = new RegExp("^[a-zA-Z0-9_\\-\\$\\+\\?\\|@]{8,}$")
const pwdsecret = process.env.PWD_SECRET ?? 123456 //パスワードハッシュ化するときのシークレット、あくまでサンプルほんとはもっとちゃんとしたもの書いてね

// DBとの接続確認用
exports.get_accounts = function(req, res) {
    return new Promise((resolve, reject) => {
        UsersLib.getAccountsListAll()
        .then(result => {
            console.log('success:', result)
            resolve({"status": 200, "body": result})
        })
        .catch(result => {
            console.log('error:', result)
            reject({"status": 500, "body": result})
        })        
	})
}

/**
 * OneRoster連携メイン処理、各ファイルのチェックと、取り込み対象データの抽出を行う
 * @param {*} req POSTリクエスト
 * @param {*} res レスポンス
 * @returns
 * 
 * 返す内容
 * {
 *   status: number,                     ステータスコード
 *   body: Array<Object>,                取り込み対象データ、または、エラーの内容
 *   count: number | undefined,          エラー数
 *   jpError: Array<Object> | undefined  Japan Profileの仕様のエラーがある場合のみレスポンスに含む
 * }
 * エラーの内容は下記の形式で書く
 * {
 *  filename: string    エラーがあったファイル名
 *  line: string        エラーがあった行数 
 *  message: string     エラー内容
 *  error_type: string  エラーの原因（one roster:エラーがOneRosterの仕様によるもの、my app: エラーがシステム独自の仕様によるもの、one roster jp: エラーがJapan Profileの仕様によるもの）
 * }
 */
exports.import_one_roster = function(req, res){
    return new Promise((resolve, reject) => {
        const form = new formidable.IncomingForm() // POSTで送られてくるform-data解釈用
		let fields = [], files = []
		let errorCnt = 0
		form.maxFileSize = 50 * 1024 * 1024
        
		form.on('error', err => {
			errorCnt++
			reject({"status": 400, "body": [{"filename": "", "line": "", "message": err, error_type: ""}], "count": errorCnt})
			return false
		})        

        form.on('field', (field, val) => {
			var fv = {}
			fv[field] = val
			fields.push(fv)
		})

		form.on('file', (name, file) => {
			files.push({name: name, file: file})
		})

        form.on('end', async () => {
            // ファイルが選択されていない
			if(files.length !== 1){
				errorCnt++
				reject({"status": 400, "body": [{"filename": "", "line": "", "message": "ファイルを選択してください。", error_type: ""}], "count": errorCnt})
				return false
			}

			const item = files[0]
            let fileName = item.file.originalFilename
			let filePath = item.file.filepath
            // ファイルがzip形式でない
			if(path.extname(fileName) !== ".zip"){
				errorCnt++
				reject({"status": 400, "body": [{"filename": "", "line": "", "message": "zipファイルを選択してください。", error_type: ""}], "count": errorCnt})
				return false
			}

            // ここからファイル読み込みと内容チェック
			try{
				let entries = unZip(filePath)
				let manifest = checkManifest(entries)

                // manifest.csvがない
				if(!manifest){
					errorCnt++
					reject({"status": 400, "body": [{"filename": "", "line": "", "message": "manifest.csvファイルが存在しません。", error_type: "one roster"}], "count": errorCnt})
					return false
				}

                // manifest.csvの内容チェック
                const checkResult = await checkFiles(manifest, entries)
                // manifest.csvでbulkになっていたファイルの内容チェック
                await checkBulkFiles(entries, checkResult.body)

                // DBに保存するためデータを整形する
                // システムで使用するファイルのみを対象としてデータを読み込む（例：このシステムでは users.csv orgs.csv roles.csv を読み込み対象とする）
                const UsersCsv = entries.find(zipEntry => zipEntry.entryName.split('/').pop() === 'users.csv')
                const OrgsCsv = entries.find(zipEntry => zipEntry.entryName.split('/').pop() === 'orgs.csv')
                const RolesCsv = entries.find(zipEntry => zipEntry.entryName.split('/').pop() === 'roles.csv')

                // 念のため必要なファイルがあるときだけ読み込みするように
                if(UsersCsv !== undefined && OrgsCsv !== undefined && RolesCsv !== undefined ){
                    let users = await readCsvFile(UsersCsv.getData())
                    let orgs = await readCsvFile(OrgsCsv.getData())
                    let roles = await readCsvFile(RolesCsv.getData())

                    let dataErr = [], dataErrCnt = 0

                    // 各読み込み対象ファイルの内容チェック（各ファイルに共通の項目のチェック）
                    let resCheckUsers = checkData(users.message, 'users')
                    let resCheckUsersForMyApp = checkDataForMyApp(users.message, 'users') //システム独自仕様で必須な項目がある場合それのチェックをする
                    if(resCheckUsers.result === "error"){
                        dataErr = dataErr.concat(resCheckUsers.resBody)
                        dataErrCnt = dataErrCnt + resCheckUsers.count
                    }
                    if(resCheckUsersForMyApp.result === "error"){
                        dataErr = dataErr.concat(resCheckUsersForMyApp.resBody)
                        dataErrCnt = dataErrCnt + resCheckUsersForMyApp.count                 
                    }

                    let resCheckOrgs = checkData(orgs.message, 'orgs')                    
                    if(resCheckOrgs.result === "error"){
                        dataErr = dataErr.concat(resCheckOrgs.resBody)
                        dataErrCnt = dataErrCnt + resCheckOrgs.count
                    }
        
                    let resCheckRoles = checkData(roles.message, 'roles')
                    if(resCheckRoles.result === "error"){
                        dataErr = dataErr.concat(resCheckRoles.resBody)
                        dataErrCnt = dataErrCnt + resCheckRoles.count
                    }
        
                    if(dataErr.length !== 0){
                        reject({"status": 400, "body": dataErr, "count": dataErrCnt})
                        return false                                
                    }

                    // users.csvファイルの内容をチェック
                    let chkUsers = checkUsersFile(users.message)
                    if(chkUsers.result === "error"){
                        reject({"status": 400, "body": chkUsers.resBody, "count": chkUsers.count})
                        return false                                
                    }
        
                    // roles.csvファイルの内容をチェック
                    let chkRoles = checkRolesFile(roles.message, users.message, orgs.message)
                    if(chkRoles.result === "error"){
                        reject({"status": 400, "body": chkRoles.resBody, "count": chkRoles.count})
                        return false                             
                    }  						

                    // DB登録用にデータを整形
                    let req_data = makeRequestData(users.message, orgs.message, roles.message)
                    if(req_data.importData.length === 0){ 
                        // 取り込み対象データなし
                        resolve({"status": 200, "body": [{filename: "", line: "", message: "取り込み対象のデータがありません。", error_type: "my app"}], "count": 1, "jpError": req_data.jpError})
                        return false                          
                    }

                    // DB登録用のデータを返す
                    resolve({"status": 200, "body": req_data})
                }
                else{
                    let errorMsgs = []
                    if(UsersCsv === undefined){
                        errorCnt++
                        let m = {filename: "users.csv", line: "", message: "users.csvファイルが存在しません。", error_type: "one roster"}
                        errorMsgs.push(m)
                    }
                    if(OrgsCsv === undefined){
                        errorCnt++
                        let m = {filename: "orgs.csv", line: "", message: "orgs.csvファイルが存在しません。", error_type: "one roster"}
                        errorMsgs.push(m)
                    }
                    if(RolesCsv === undefined){
                        errorCnt++
                        let m = {filename: "roles.csv", line: "", message: "roles.csvファイルが存在しません。", error_type: "one roster"}
                        errorMsgs.push(m)
                    }       
                    reject({"status": 400, "body": errorMsgs, "count": errorCnt})
                }
			}
			catch(err){
                console.log(err)
                let status = err.status ?? 400
				if(err.body){
					let errBody = ""
					if(err.body.msg){
						errBody = err.body.msg
					}
					else{
						errBody = {filename: "", line: "", message: err.toString(), error_type: "my app"}
					}
			
					if(err.body.count){
						errorCnt = err.body.count
					}
					else{
						errorCnt++
					}

					reject({"status": status, "body": errBody, "count": errorCnt})
					return false
				}
				else{
					errorCnt++
					reject({"status": 400, "body": [{"filename": "", "line": "", "message": err.toString(), error_type: "my app"}], "count": errorCnt})
					return false
				}
			}
		})        

        form.encoding = 'utf-8'
		form.keepExtensions = true
		form.parse(req)   
    })
}

/**
 * zipを解凍して、ファイル群を返す
 * @param {string} filePath アップロードされたファイルのパス
 * @returns 
 */
const unZip = (filePath) => {
    const zip = new admZip(filePath)
    const zipEntries = zip.getEntries()

    return zipEntries
}

/**
 * 解凍されたファイル群の中に、manifest.csvが存在するかをチェック、存在する場合はそのデータを返す
 * @param {Array} entries zip解凍後のファイル群
 * @returns 
 */
const checkManifest = (entries) => {
    if(entries.length === 0){
        return false
    }

    const manifestCsv = entries.find(zipEntry => (zipEntry.entryName.split('/').pop()).toLowerCase() === "manifest.csv")

    if(manifestCsv !== undefined){
        return manifestCsv
    }

    return false
}

// manifest.csvの必須項目、これらが存在しない場合はエラー
const requiredItem = ["manifest.version", "oneroster.version", "file.academicSessions", "file.categories", "file.classes",
                        "file.classResources", "file.courses", "file.courseResources", "file.demographics", "file.enrollments", 
                        "file.lineItemLearningObjectiveIds","file.lineItems", "file.lineItemScoreScales", "file.orgs", 
                        "file.resources", "file.resultLearningObjectiveIds", "file.results", "file.resultScoreScales", "file.roles",
                        "file.scoreScales", "file.userProfiles", "file.userResources", "file.users"]

/**
 * manifest.csvのヘッダーの存在チェック
 * @param {Array} d 読み込んだデータの１行目（csvファイルのヘッダーにあたる行）
 * @param {Array} cols ヘッダー名の配列
 * @returns 
 */                        
const checkManifestHeader = (d, cols) => {
    const isHeader = d.every((elem, idx, arr) => {
        return elem === cols[idx]
    })

    return isHeader
}

/**
 * manifest.csvの必須項目の存在チェック
 * @param {Array} propArr チェックする項目(csvファイルの１列目)
 * @returns 
 */
const checkRequiredFile = (propArr) => {
    const isExist = requiredItem.every((elem) => {
        return propArr.includes(elem)
    })                   

    return isExist
}

/**
 * manifest.csv以外のファイルの存在チェック
 * @param {string} name 存在チェックするファイル名 
 * @param {Array} entries zip解凍後のファイル群
 * @returns 
 */
const checkExist = (name, entries) => {
    let fileName = name.split('.')[1] + ".csv"
    const isExist = entries.some((elem, idx, arr) => elem === fileName)

    return isExist
}

/**
 * manifest.csvの内容をチェック
 * @param {Object} manifest manifest.csv
 * @param {Array} entries zip解凍後のファイル群
 * @returns 
 */
const checkFiles = (manifest, entries) => {
    const mapEntries = entries.map(zipEntry => (zipEntry.entryName.split('/').pop()))
    return new Promise((resolve, reject) => {
        // 文字コード判別
        let det = jschardet.detect(manifest.getData())

        // UTF-8でない場合はエラー
        if(det.encoding === null){
            reject({status: 415, body: {msg: [{filename: "manifest.csv", line: "0", message: "Unsupported Media Type", error_type: "one roster"}], count: 1}})
        }

        if(det.encoding !== 'ascii' && det.encoding !== "UTF-8"){
            reject({status: 415, body: {msg: [{filename: "manifest.csv", line: "0", message: "Unsupported Media Type", error_type: "one roster"}], count: 1}})
        }
    
        // csvファイルを読み込む
        let str = iconv.decode(manifest.getData(), 'utf8')
        let strBuf = Buffer.from(str)
    
        let readable = new Readable()
        readable.push(strBuf)
        readable.push(null)
    
        const COLS = ["propertyName", "value"]
        let mfData = []
    
        let csvData = readable.pipe(new AutoDetectDecoderStream())
        csvData.pipe(CsvReadableStream({trim: true}))
        // csvとして読み込めなかった、csv形式になってない
        .on('data', row => {
            if(!Array.isArray(row) || !Array.isArray(row)){
                reject({status: 400, body: {msg: [{filename: "manifest.csv", line: "0", message: "データの形式が正しくありません。", error_type: "one roster"}], count: 1}})
            }
            mfData.push(row)
        })
        .on('end', () => {
            // データなし
            if(mfData.length === 0){
                reject({status: 400, body: {msg: [{filename: "manifest.csv", line: "0", message: "manifest.csvにデータが1行もありません。", error_type: "one roster"}], count: 1}})
            }

            // ヘッダー名重複チェック
            const s = new Set(mfData[0])
            if(s.size !== mfData[0].length){
                reject({status: 400, body: {msg: [{filename: "manifest.csv", line: "1", message: "ヘッダーのフィールド名が重複しています。", error_type: "one roster"}], count: 1}})
            }

            // 必要なヘッダーが存在するかチェック
            if(!checkManifestHeader(mfData[0], COLS)){
                reject({status: 400, body: {msg: [{filename: "manifest.csv", line: "1", message: "ヘッダーが不足しています。", error_type: "one roster"}], count: 1}})
            }

            // 各行のデータ存在チェック
            const mapPropName = mfData.map(elem => elem[0])
            if(!checkRequiredFile(mapPropName)){
                let lackItem = requiredItem.filter(x => !mapPropName.includes(x)) //不足している項目が何かエラーメッセージとして出力

                reject({status: 400, body: {msg: [{filename: "manifest.csv", line: "0", message: `manifest.csvの必須項目が不足しています。「${lackItem.join(',')}」に関するデータ行がありません。`, error_type: "one roster"}], count: 1}})
            }

            // manifest.csvの内容がOneRosterの仕様に沿っているかチェック
            let errMsg = [], errCnt = 0
            let bulkFiles = [] //bulk対象ファイルのデータ入れる配列
            for(let i = 1; i < mfData.length; i++){
                let propName = mfData[i][0]
                let val = mfData[i][1]

                let m
                if(propName === "manifest.version" && val !== "1.0"){
                    errCnt++      
                    m = {filename: "manifest.csv", line: (i+1).toString(), message: "manifest.csvのmanifest.versionは「1.0」のみ許可されます。", error_type: "one roster"}
                    errMsg.push(m)
                }

                if(propName === "oneroster.version" && val !== "1.2"){
                    errCnt++      
                    m = {filename: "manifest.csv", line: (i+1).toString(), message: "manifest.csvのoneroster.versionは「1.2」のみ許可されます。", error_type: "one roster"}
                    errMsg.push(m)
                }

                if(val === 'bulk'){
                    if(!checkExist(propName, mapEntries)){
                        errCnt++      
                        m = {filename: "manifest.csv", line: (i+1).toString(), message: `manifest.csvのvalueが「bulk」ですが、「${propName}」ファイルが存在しません。`, error_type: "one roster"}
                        errMsg.push(m)
                    }

                    // demographicsとuserProfiles以外のファイルは利用するしないにかかわらず読み込む（内容チェックにかける）ので、配列に入れておく
                    if(propName !== "file.demographics" && propName !== "file.userProfiles"){
                        bulkFiles.push(propName)
                    }
                }
                else if(val === 'absent'){
                    if(checkExist(propName, mapEntries)){
                        errCnt++      
                        m = {filename: "manifest.csv", line: (i+1).toString(), message: `manifest.csvのvalueが「absent」ですが、「${propName}」ファイルが存在します。`, error_type: "one roster"}
                        errMsg.push(m) 
                    }
                }
                else if(val === 'delta'){
                    errCnt++      
                    m = {filename: "manifest.csv", line: (i+1).toString(), message: `manifest.csvのvalueとして「delta」は許可されません。`, error_type: "one roster"}
                    errMsg.push(m) 
                }
            }

            if(errMsg.length !== 0){
                reject({status: 400, body: {msg: errMsg, count: errCnt}})
            }
    
            // エラーなしならbulk対象ファイルを返す
            resolve({status: 200, body: bulkFiles})
        })
    })
}

// ヘッダーの情報を別ファイルから取得
let headerInfo = require("./OneRosterHeader")

/**
 * bulk対象ファイルの読み込み、内容チェック
 * @param {Array} entries zip解凍後のファイル群 
 * @param {Array} check_files bulk対象ファイル 
 * @returns 
 */
const checkBulkFiles = (entries, check_files) => {
	return new Promise(async (resolve, reject) => {
		let errorMsg = [], errorCnt = 0
		for(let i = 0; i < check_files.length; i++){
            // ファイル名からデータ特定して取得
			const name = check_files[i].split('.')[1]
			const filename = name + '.csv'
			const csv = entries.find(zipEntry => (zipEntry.entryName.split('/').pop()).toLowerCase() === filename.toLowerCase())

            // 文字コード判別
			let det = jschardet.detect(csv.getData())

            // UTF-8でない場合はエラー
			if(det.encoding === null){
				errorCnt++
                m = {filename: filename, line: 0, message: "Unsupported Media Type", error_type: "one roster"}
                errorMsg.push(m)
				continue
			}

			if(det.encoding !== 'ascii' && det.encoding !== "UTF-8"){
				errorCnt++
                m = {filename: filename, line: 0, message: "Unsupported Media Type", error_type: "one roster"}
                errorMsg.push(m)
				continue			
			}

            // csvファイル読み込み
			const data = await readCsvFile(csv.getData())
            // データが正常に読み込めなかった場合は、status:error が帰ってくる
			if(data.status === "error"){
				errorCnt++
                m = {filename: filename, line: 0, message: data.message}
                errorMsg.push(m)
				continue		
			}

            // データが１行もない
			if(data.message.length === 0){
				errorCnt++
				m = {filename: filename, line: 0, message: `${filename}にデータが1行もありません。`, error_type: "one roster"}
				errorMsg.push(m)
				continue
			}

            // ヘッダー行しかない
			if(data.message.length < 2){ 
				errorCnt++
				m = {filename: filename, line: 0, message: `${filename}にヘッダー以外のデータがありません。`, error_type: "one roster"}
				errorMsg.push(m)
				continue			
			}

            // ヘッダーの重複チェック
			const headerRow = data.message[0]
			const s = new Set(headerRow)
			if(s.size !== headerRow.length){
				errorCnt++
				m = {filename: filename, line: 1, message: `${filename}のヘッダーのフィールド名が重複しています。`, error_type: "one roster"}
				errorMsg.push(m)
				continue	
			}

            // ヘッダーの並び順チェック
			const checkHeader = headerInfo.headers[name]
			const checkRes = checkHeader.every((elem, idx) => elem === headerRow[idx])
			if(!checkRes){
				errorCnt++
				m = {filename: filename, line: 1, message: "ヘッダーの並び順が正しくありません。", error_type: "one roster"}
				errorMsg.push(m)
				continue
			}

			const cols = headerInfo.requiredHeader[name]
			let cp = [...data.message] // csvファイルの内容を別配列にコピー
			cp.shift() // ヘッダー行削除

            // 必須項目が存在するか、値が空ではないかチェック
			cols.forEach(elem => {
				const idx = checkHeader.findIndex(x => x === elem)
				const arr = cp.map(y => y[idx])

				let m
				arr.forEach((z, index) => {
					if(z === "" || z === undefined || z === null){
						errorCnt++
						m = {filename: filename, line: (index+1).toString(), message: `${elem}は必須です。`, error_type: "one roster"}
						errorMsg.push(m)
					}				
				})
			})
		}

		if(errorCnt > 0){
			reject({status: 400, body: {msg: errorMsg, count: errorCnt}})
			return false
		}

		resolve({status: 200, body: "no error"})
	})
}

/**
 * csvファイルの内容を取得
 * @param {Buffer} bufData 
 * @returns 
 */
const readCsvFile = (bufData) => {
	return new Promise((resolve, reject) => {
		let str = iconv.decode(bufData, "utf8")
		let strBuf = Buffer.from(str)
	
		let readable = new Readable()
		readable.push(strBuf)
		readable.push(null)

		let csvData = readable.pipe(new AutoDetectDecoderStream())
		let data = []

		csvData.pipe(CsvReadableStream({trim: true}))
		.on('data', row => {
            // csvとして読み込めなかった、csv形式になってない
			if(!Array.isArray(row) || !Array.isArray(row)){
				resolve({"status": "error", "message": "データの形式が正しくありません。", error_type: "one roster"})
			}
			data.push(row)
		})
		.on('end', () => {
            // 読み込めたら結果（配列）を返す
			resolve({"status": "success", "message": data})
		})
	})
}

/**
 * DB登録対象ファイルの内容チェック（各ファイル共通の項目をチェック）
 * @param {Array} d 読み込み対象ファイルのデータ
 * @param {string} filename 読み込み対象ファイル名
 * @returns 
 */
const checkData = (d, filename) => {
	let cols = headerInfo.requiredHeader[filename]
    // 必須ヘッダーの存在チェック
    const isHeader = cols.every((elem) => {
        return d[0].includes(elem)
    })

    if(!isHeader){
        return {"result": "error", "resBody":  {filename: filename, line: "1", message: `${filename}.csvのヘッダーが不足しています。`, error_type: "one roster"}, "count": 1}
    }
	
	let cp = [...d]
    cp.shift() //ヘッダー行削除

    // sourcedIdの重複チェック
	const sidIdx = d[0].findIndex(elem => elem === "sourcedId")
    let arrSourceId = cp.map(elem => elem[sidIdx])
    const ssid = new Set(arrSourceId)
    if(ssid.size !== arrSourceId.length){
        let arrSourceId2 = [...arrSourceId]
        let dupMsg = []
        let dupCnt = 0
        for(let i = 0; i < arrSourceId.length; i++){
            let chk = arrSourceId2.filter(x => x === arrSourceId[i])
            let m
            if(chk.length > 1){
                dupCnt++
                m = {filename: filename, line: (i+1).toString(), message: `${filename}.csvファイル内で sourcedId「${arrSourceId[i]}」が重複しています。`, error_type: "one roster"}
                dupMsg.push(m)
            }
        }

        return {"result": "error", "resBody": dupMsg, "count": dupCnt}
    }

    let errMsg = [], errCnt = 0
    // sourcedIdがUUID形式かチェック
	const idx_sid = d[0].findIndex(x => x === "sourcedId")
	const arr_sourceId = cp.map(y => y[idx_sid])
	const regex = /^([A-Za-z0-9]{8})-([A-Za-z0-9]{4})-([A-Za-z0-9]{4})-([A-Za-z0-9]{4})-([A-Za-z0-9]{12})$/
	const check_sourceId = arr_sourceId.every(elem => {
		let id = elem.replace(/^\"/, '').replace(/\"$/, '')

		return regex.test(id)
	})

	if(!check_sourceId){
		let cs_msg
		arr_sourceId.forEach((x, i) => {
			if(!regex.test(x)){
				errCnt++
				cs_msg = {filename: filename, line: (i+1).toString(), message: "「sourcedId」の値がUUIDではありません。", error_type: "one roster"}
				errMsg.push(cs_msg)
			}
		})
	}

    if(errMsg.length !== 0){
        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    return {"result": "success", "resBody": "no error"} 
}

/**
 * システムに登録するうえで必須項目に空の値がないことをチェック（例：このシステムはパスワードの登録が必須である）
 * @param {Array} d 読み込み対象ファイルのデータ
 * @param {string} filename 読み込み対象ファイル名
 */
const checkDataForMyApp = (d, filename) => {
	const colForMyApp = headerInfo.requiredForMyApp[filename]
	let errMsg = [], errCnt = 0

    let cp = [...d]
    cp.shift() //ヘッダー行削除

    colForMyApp.forEach(elem => {
        const idx = d[0].findIndex(x => x === elem)
        const arr = cp.map(y => y[idx])

        let m
        arr.forEach((z, i) => {
            if(z === "" || z === undefined || z === null){
                errCnt++
                m = {filename: filename, line: (i+1).toString(), message: `${elem}は必須です。`, error_type: "my app"}
                errMsg.push(m)
            }
        })
    })

    if(errMsg.length !== 0){
        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    return {"result": "success", "resBody": "no error"} 
}

/**
 * users.csvファイルの内容をチェック
 * @param {*} users 
 * @returns 
 */
const checkUsersFile = (users) => {
    const header = users[0]
    let cp = [...users]
    cp.shift() //ヘッダー行削除

    let errMsg = [], errCnt = 0

    // enabledUserが「true」「false」かチェック
    const idx_enabled = header.findIndex(x => x === "enabledUser")
    const arr_enabled = cp.map(y => y[idx_enabled])
    const check_enabled = arr_enabled.every(elem => {
        elem = elem.replace(/^\"/, '').replace(/\"$/, '')
		if(elem === "true" || elem === "false"){
			return true
		}
		return false
    })

    // 「true」「false」以外の値が存在する場合
    if(!check_enabled){
        let ce_msg
        arr_enabled.forEach((x, i) => {
            x = x.replace(/^\"/, '').replace(/\"$/, '')
            if(x !== "true" && x !== "false"){
                errCnt++
                ce_msg = {filename: "users.csv", line: (i+1).toString(), message: "「enabledUser」の値が「true/false」ではありません。", error_type: "one roster"}
                errMsg.push(ce_msg)
            }
        })
    }

    // usernameの重複チェック
    const idx_name = header.findIndex(x => x === "username")
    const arr_name = cp.map(y => y[idx_name])
    const s_name = new Set(arr_name)
    if(s_name.size !== arr_name){
        let arr_name2 = [...arr_name]
        for(let i = 0; i < arr_name.length; i++){
            let chk = arr_name2.filter(x => x === arr_name[i])
            let cn_msg
            if(chk.length > 1){
                errCnt++
                cn_msg = {filename: "users.csv", line: (i+1).toString(), message: `username「${arr_name[i]}」が重複しています。`, error_type: "one roster"}
                errMsg.push(cn_msg)
            }
        }
    }

    // userMasterIdentifierの重複チェック
	const idx_masterId = header.findIndex(x => x === "userMasterIdentifier")
	const arr_masterId = cp.map(y => y[idx_masterId])
	const s_masterId = new Set(arr_masterId)
    if(s_masterId.size !== arr_masterId){
        let arr_masterId2 = [...arr_masterId]
        for(let i = 0; i < arr_masterId.length; i++){
            let chk = arr_masterId2.filter(x => x === arr_masterId[i])
            let cn_msg
            if(chk.length > 1){
                errCnt++
                cn_msg = {filename: "users.csv", line: (i+1).toString(), message: `userMasterIdentifier「${arr_masterId[i]}」が重複しています。`, error_type: "one roster"}
                errMsg.push(cn_msg)
            }
        }
    }

    //システムの仕様としてチェック必須なものの確認
    let response = checkUsersForMyApp(header, cp)
    if(response.arrMsg.length > 0){
        errMsg = errMsg.concat(response.arrMsg)
        errCnt = errCnt + response.count
    }

    if(errMsg.length !== 0){
        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    return {"result": "success", "resBody": "no error"}
}

/**
 * システムの仕様として確認したい項目のチェック（例：パスワードを使用する場合のバリデーション）
 * @param {Array} header users.csvのヘッダー
 * @param {Array} cp users.csvから読み込んだデータ（ヘッダー部分削除済みのもの）
 * @returns 
 */
const checkUsersForMyApp = (header, cp) => {
    let count = 0, msg, arrMsg = [];

	const idx_password = header.findIndex(x => x === "password")
	const arr_password = cp.map(y => y[idx_password])
	const check_pwdPolicy = arr_password.every(elem => {
        elem = elem.replace(/^\"/, '').replace(/\"$/, '')
		return pwdPolicy.test(elem)
	})

	if(!check_pwdPolicy){
        let cp_msg
        arr_password.forEach((x, i) => {
            x = x.replace(/^\"/, '').replace(/\"$/, '')
            if(!pwdPolicy.test(x)){
                count++
                msg = {filename: "users.csv", line: (i+1).toString(), message: "パスワードは 8 文字以上の英数字である必要があります。", error_type: "my app"}
                arrMsg.push(cp_msg)
            }
        })
	}

    return {arrMsg, count}
}

/**
 * role.csvファイルの内容をチェック
 * @param {Array} roles 
 * @param {Array} users 
 * @param {Array} orgs 
 * @returns 
 */
const checkRolesFile = (roles, users, orgs) => {
    const roleHeaders = roles[0]
    const userHeaders = users[0]
    const orgHeaders = orgs[0]

    let cpRoles = [...roles]
    cpRoles.shift()
    let cpUsers = [...users]
    cpUsers.shift()
    let cpOrgs = [...orgs]
    cpOrgs.shift()

    let errMsg = [], errCnt = 0

    // ロールの種類のチェック
    let roleItem = ["aide", "counselor", "districtAdministrator", "parent", "principal", "proctor", "relative", "siteAdministrator", "systemAdministrator", "student", "teacher", "guardian"]
    const idx_role = roleHeaders.findIndex(x => x === "role")
    const arr_role = cpRoles.map(y => y[idx_role])
    const check_role = arr_role.every(elem => {
        return roleItem.includes(elem)
    })

    if(!check_role){
        let cr_msg
        arr_role.forEach((x, i) => {
            if(!roleItem.includes(x)){
                errCnt++
                cr_msg = {filename: "roles.csv", line: (i+1).toString(), message: `roleには「${roleItem.join(',')}」のいずれかを指定しください。`, error_type: "one roster"}
                errMsg.push(cr_msg)
            }
        })        
        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    // userSourcedIdのチェック Roles.csv userSourcedId = Users.csv sourcedId
    const idx_uid = roleHeaders.findIndex(x => x === "userSourcedId")
    const idx_userId = userHeaders.findIndex(x => x === "sourcedId")
    const arr_role_uid = cpRoles.map(y => y[idx_uid])
    const arr_userId = cpUsers.map(y => y[idx_userId])

    const check_uid = arr_role_uid.every(elem => {
        return arr_userId.includes(elem)
    })

    if(!check_uid){
        let cu_msg
        arr_role_uid.forEach((x, i) => {
            if(!arr_userId.includes(x)){
                errCnt++
                cu_msg = {filename: "roles.csv", line: (i+1).toString(), message: `userSourcedId「${x}」がusers.csvに存在しません。`, error_type: "one roster"}
                errMsg.push(cu_msg)                
            }
        })
        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    // orgSourcedIdのチェック Roles.csv orgSourcedId = Orgs.csv sourcedId
    const idx_oid = roleHeaders.findIndex(x => x === "orgSourcedId")
    const idx_orgId = orgHeaders.findIndex(x => x === "sourcedId")
    const arr_role_oid = cpRoles.map(y => y[idx_oid])
    const arr_orgId = cpOrgs.map(y => y[idx_orgId])

    const check_oid = arr_role_oid.every(elem => {
        return arr_orgId.includes(elem)
    })

    if(!check_oid){
        let co_msg 
        arr_role_oid.forEach((x, i) => {
            if(!arr_orgId.includes(x)){
                errCnt++
                co_msg = {filename: "roles.csv", line: (i+1).toString(), message: `orgSourcedId「${x}」がorgs.csvに存在しません。`, error_type: "one roster"}
                errMsg.push(co_msg)                
            }
        })
        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    //roleTypeのチェック
    const dupUserId = arr_role_uid.filter((elem, idx, arr) => arr.lastIndexOf(elem) !== idx && arr.indexOf(elem) === idx)
    const uniUserId = arr_role_uid.filter((elem, idx, arr) => arr.lastIndexOf(elem) === idx && arr.indexOf(elem) === idx)

    const idx_roleType = roleHeaders.findIndex(x => x === "roleType")

    // 持っているroleがひとつの場合は、roleTypeはprimaryとなる
    let errUserIdUni = []
    let checkUni = uniUserId.every((elem) => {
        let userRole = cpRoles.find(item => item.includes(elem))
        if(userRole[idx_roleType] !== "primary"){
            errUserIdUni.push(elem)
        }

        return userRole[idx_roleType] === "primary"
    })

    if(!checkUni){
        let cuni_msg
        uniUserId.forEach((x, i) => {
            let userRole = cpRoles.find(item => item.includes(x))
            const idx = arr_role_uid.findIndex(r => r === x)

            if(userRole[idx_roleType] !== "primary"){
                errCnt++
                cuni_msg = {filename: "roles.csv", line: (idx + 1).toString(), message: "ユーザのroleが1種類の場合、roleTypeには「primary」を指定してください。", error_type: "one roster"}
                errMsg.push(cuni_msg)                
            }   
        })

        return {"result": "error", "resBody": errMsg, "count": errCnt}
    }

    // roleを2つ以上持つユーザは、うちひとつがprimaryで他はsecondaryとなる、primary2つ以上ある場合はエラー
    let errUserIdDup = []
    let roleTypeItem = ["primary", "secondary"]
    let checkDup = dupUserId.every((elem) => {
        let userRoles = cpRoles.filter(item => item.includes(elem))
        let user_roleTypes = userRoles.map(item => item[idx_roleType])

        let cntPrimary = user_roleTypes.reduce((prev, curr) => {
            return curr === "primary" ? prev + 1 : prev
        }, 0)

        if(cntPrimary === 0 || cntPrimary > 1){
            errUserIdDup.push(elem)
            return false
        }

        if(!user_roleTypes.includes("secondary")){
            errUserIdDup.push(elem)
            return false
        }

        let typeCheck = user_roleTypes.every(item => {
            return roleTypeItem.includes(item)
        })

        if(!typeCheck){
            errUserIdDup.push(elem)
            return false
        }

        return true
    })

    if(!checkDup){
        let cdup_msg
        dupUserId.forEach((x, i) => {
            let userRoles = cpRoles.filter(item => item.includes(x))
            let user_roleTypes = userRoles.map(item => item[idx_roleType])
            const idx = arr_role_uid.findIndex(r => r === x)

            let cntPrimary = user_roleTypes.reduce((prev, curr) => {
                return curr === "primary" ? prev + 1 : prev
            }, 0)

            if(cntPrimary === 0 || cntPrimary > 1){
                errCnt++
                cdup_msg = {filename: "roles.csv", line: (idx + 1).toString(), message: "ユーザのroleが2種類以上の場合、roleのうちひとつはroleType「primary」、その他にはroleType「secondary」を指定してください。", error_type: "one roster"}
                errMsg.push(cdup_msg)                
            } 

            if(!user_roleTypes.includes("secondary")){
                errCnt++
                cdup_msg = {filename: "roles.csv", line: (idx + 1).toString(), message: "ユーザのroleが2種類以上の場合、roleのうちひとつはroleType「primary」、その他にはroleType「secondary」を指定してください。", error_type: "one roster"}
                errMsg.push(cdup_msg)               
            }

            let typeCheck = user_roleTypes.every(item => {
                return roleTypeItem.includes(item)
            })

            if(!typeCheck){
                errCnt++
                cdup_msg = {filename: "roles.csv", line: (idx + 1).toString(), message: "ユーザのroleが2種類以上の場合、roleのうちひとつはroleType「primary」、その他にはroleType「secondary」を指定してください。", error_type: "one roster"}
                errMsg.push(cdup_msg)
            }
        })

        return {"result": "error", "resBody": errMsg,"count": errCnt}       
    }

    return {"result": "success", "resBody": "no error"}
}

/**
 * 取り込み用にデータを整形する
 * @param {Array} users 
 * @param {Array} orgs 
 * @param {Array} roles 
 * @returns 
 */
const makeRequestData = (users, orgs, roles) => {
    const roleHeaders = roles[0]
    const userHeaders = users[0]
    const orgHeaders = orgs[0]

    let cpRoles = [...roles]
    cpRoles.shift() // ヘッダー行削除
    let cpUsers = [...users]
    cpUsers.shift() // ヘッダー行削除
    let cpOrgs = [...orgs]
    cpOrgs.shift() // ヘッダー行削除

    let data = []

    // DBに登録するデータたち
    const idx_role = roleHeaders.findIndex(x => x === "role")
    const idx_oid = roleHeaders.findIndex(x => x === "orgSourcedId")
    const idx_uid = roleHeaders.findIndex(x => x === "userSourcedId")

    const idx_userId = userHeaders.findIndex(x => x === "sourcedId")
	const idx_masterId = userHeaders.findIndex(x => x === "userMasterIdentifier")
    const idx_prefFamilyName = userHeaders.findIndex(x => x === "preferredFamilyName")
    const idx_prefMiddleName = userHeaders.findIndex(x => x === "preferredMiddleName")
    const idx_prefGivenName = userHeaders.findIndex(x => x === "preferredGivenName")
    const idx_familyName = userHeaders.findIndex(x => x === "familyName")
    const idx_middleName = userHeaders.findIndex(x => x === "middleName")
    const idx_givenName = userHeaders.findIndex(x => x === "givenName")
    const idx_userName = userHeaders.findIndex(x => x === "username")
    const idx_password = userHeaders.findIndex(x => x === "password")
    const idx_phone = userHeaders.findIndex(x => x === "phone")

    const idx_orgId = orgHeaders.findIndex(x => x === "sourcedId")
    const idx_orgName = orgHeaders.findIndex(x => x === "name")

    // 取り込み対象のロールを絞り込む場合（例：roleがstudentのユーザーのみ取り込みたい）    
    const filRoles = cpRoles.filter(elem => elem[idx_role] === "student")

	let jp_error = []
	const regexKana = /^[ｦ-ﾟ]*$/
	const regexId = /^([A-Za-z0-9]{8})-([A-Za-z0-9]{4})-([A-Za-z0-9]{4})-([A-Za-z0-9]{4})-([A-Za-z0-9]{12})$/

    // roles.csvファイルにあるuserSourcedIdやorgSourcedIdから取り込み対象のユーザの名前や組織名を特定してデータを作る
    filRoles.forEach((elem, i) => {
		let jp_error_msg = ""
        const userId = elem[idx_uid]
        const orgId = elem[idx_oid]

        const userData = cpUsers.find(item => item[idx_userId] === userId)
        const orgData = cpOrgs.find(item => item[idx_orgId] === orgId)

        let userName = userData[idx_userName].substring(0, 255) // 255文字超えるものは切り捨てる
		userName = userName.replace(/^\"/, '').replace(/\"$/, '')
        // 重複登録しないように同じusernameの人がすでにいたらスキップする（ログインIDとして使用するなど、重複すると困る場合。重複していいならこの処理はコメントアウト）
        if(data.length > 0){
            let alreadyExist = data.some(d => d.login_id === userName)
            if(alreadyExist){
                return
            }
        }

        // userMasterIdentifierがGUID形式かチェック（Japan Profileの仕様）
		const userMasterId = userData[idx_masterId]
		if(!regexId.test(userMasterId)){
			jp_error_msg = jp_error_msg + `ユーザー「${userName}」のuserMasterIdentifierがGUID形式ではありません。`
		}

        let prefFamilyName = userData[idx_prefFamilyName]
        if(prefFamilyName !== "" && prefFamilyName !== undefined && prefFamilyName !== null){
            // preferredFamilyNameに半角カナが含まれているかチェック（Japan Profileの仕様）
			if(regexKana.test(prefFamilyName)){
				jp_error_msg = jp_error_msg + `ユーザー「${userName}」のpreferredFamilyNameに半角カナが含まれています。`	
			}

            prefFamilyName = prefFamilyName.substring(0, 255) // 255文字超えるものは切り捨てる
			prefFamilyName = prefFamilyName.replace(/^\"/, '').replace(/\"$/, '')
        }

        let prefMiddleName = userData[idx_prefMiddleName]
        if(prefMiddleName !== "" && prefMiddleName !== undefined && prefMiddleName !== null){
            // preferredMiddleNameに半角カナが含まれているかチェック（Japan Profileの仕様）
			if(regexKana.test(prefMiddleName)){
				jp_error_msg = jp_error_msg + `ユーザー「${userName}」のpreferredMiddleNameに半角カナが含まれています。`		
			}

            prefMiddleName = prefMiddleName.substring(0, 255) // 255文字超えるものは切り捨てる
			prefMiddleName = prefMiddleName.replace(/^\"/, '').replace(/\"$/, '')
        }

        let prefGivenName = userData[idx_prefGivenName]
        if(prefGivenName !== "" && prefGivenName !== undefined && prefGivenName !== null){
            // preferredGivenNameに半角カナが含まれているかチェック（Japan Profileの仕様）
			if(regexKana.test(prefGivenName)){
				jp_error_msg = jp_error_msg + `ユーザー「${userName}」のpreferredGivenNameに半角カナが含まれています。`
			}

            prefGivenName = prefGivenName.substring(0, 255) // 255文字超えるものは切り捨てる
			prefGivenName = prefGivenName.replace(/^\"/, '').replace(/\"$/, '')
        }

        let displayName = `${prefFamilyName} ${prefMiddleName} ${prefGivenName}`
        if(prefFamilyName === "" && prefMiddleName === "" && prefGivenName === ""){
            displayName = userData[idx_familyName].substring(0, 255) // 255文字超えるものは切り捨てる
        }

        let familyName = userData[idx_familyName]
        // familyNameに半角カナが含まれているかチェック（Japan Profileの仕様）
		if(regexKana.test(familyName)){
			jp_error_msg = jp_error_msg + `ユーザー「${userName}」のfamilyNameに半角カナが含まれています。`			
		}
		familyName = familyName.substring(0, 255) // 255文字超えるものは切り捨てる
		familyName = familyName.replace(/^\"/, '').replace(/\"$/, '')

        let middleName = userData[idx_middleName]
		if(middleName !== "" && middleName !== undefined && middleName !== null){
            // middleNameに半角カナが含まれているかチェック（Japan Profileの仕様）
			if(regexKana.test(middleName)){
				jp_error_msg = jp_error_msg + `ユーザー「${userName}」のmiddleNameに半角カナが含まれています。`
			}

            middleName = middleName.substring(0, 255) // 255文字超えるものは切り捨てる
			middleName = middleName.replace(/^\"/, '').replace(/\"$/, '')
        }

        let givenName = userData[idx_givenName]
		if(givenName !== "" && givenName !== undefined && givenName !== null){
            // givenNameに半角カナが含まれているかチェック（Japan Profileの仕様）
			if(regexKana.test(givenName)){
				jp_error_msg = jp_error_msg + `ユーザー「${userName}」のgivenNameに半角カナが含まれています。`
			}

            givenName = givenName.substring(0, 255) // 255文字超えるものは切り捨てる
			givenName = givenName.replace(/^\"/, '').replace(/\"$/, '')
        }

        let fullName = `${familyName} ${middleName} ${givenName}`

        let phoneNumber = userData[idx_phone].substring(0, 255) // 255文字超えるものは切り捨てる
		phoneNumber = phoneNumber.replace(/^\"/, '').replace(/\"$/, '')
        if(phoneNumber === "" || phoneNumber === undefined || phoneNumber === null){
            phoneNumber = "0"
        }

        let password = userData[idx_password].substring(0, 255) // 255文字超えるものは切り捨てる
		password = password.replace(/^\"/, '').replace(/\"$/, '')

        let orgName = orgData[idx_orgName]
        // organizationのnameに半角カナが含まれているかチェック（Japan Profileの仕様）
		if(regexKana.test(orgName)){
			jp_error_msg = jp_error_msg + `ユーザー「${userName}」のorganizationのnameに半角カナが含まれています。`
		}
		orgName = orgName.substring(0, 255) // 255文字超えるものは切り捨てる
		orgName = orgName.replace(/^\"/, '').replace(/\"$/, '')
		
        // DB登録用にデータ整形
        let dataItem = {
            "display_name": displayName,
            "login_id": userName,
            "fullname": fullName,
            "organization": orgName,
            "phone": phoneNumber,
            "password": password     
        }

		if(jp_error_msg !== ""){
			jp_error.push({filename: "users", line: (i+1).toString(), message: jp_error_msg, error_type: "one roster jp"})
			return
		}

        data.push(dataItem) // データを配列に入れる
    })

    return {importData: data, jpError: jp_error} // 登録用データ配列とエラーを返す 
}

/**
 * DBに登録済みのユーザ一覧を取得
 * @param {*} req 
 * @param {*} res 
 * @returns 
 */
exports.get_account_list_all = function(req, res){
    return new Promise((resolve, reject) => {
        UsersLib.getAccountsListForOneRoster()
        .then(result => {
            resolve({"status": 200, "body": result})
        })
        .catch(result => {
            console.log('error:', result)
            reject({"status": 400, "body": result})
        })        
	}) 
}

/**
 * DBにユーザを新規登録
 * @param {Array} d 新規登録対象ユーザデータ 
 * @returns 
 */
exports.bulk_insert_account = function(d){
    return new Promise((resolve, reject) => {
        if(d.length === 0){
			resolve({"status": 200, "body": "No insert target"})
			return true;
        }

        // 以下サンプル動かす用のデータ例
        let bulkData = []

        for(let i = 0; i < d.length; i++){
            const pwdhash = crypto.createHash('sha256')
			pwdhash.update(d[i].password + pwdsecret)     
            let reqData = {
				"subscription_type": "monthly",
				"login_id": d[i].login_id,
				"display_name": d[i].display_name,
				"password": pwdhash.digest('base64'),
				"fullname": d[i].fullname,
				"organization": d[i].organization,
				"phone": d[i].phone,
				"created": (new Date()).toISOString(),
				"plan": "paid",
				"plan_changed": (new Date()).toISOString(),
				"register_type": "one-roster",
				"modified": (new Date()).toISOString(),
			};
			bulkData.push(reqData)
        }

        UsersLib.bulkInsertAccounts(bulkData)
        .then(result => {
            resolve({"status": 201, "body": result})
        })
        .catch(result => {
            reject({"status": 400, "body": result})
        })
    })
}

/**
 * ユーザを削除
 * @param {Array} d 削除対象ユーザデータ 
 * @returns 
 */
exports.delete_account = function(d){
    return new Promise((resolve, reject) => {
        if(d.length === 0){
			resolve({"status": 200, "body": "No delete target"})
			return true;
		}
        
        // 以下サンプル動かす用のデータ例
        let error_res;
		let error = false;

        for(let i = 0; i < d.length; i++){
            UsersLib.deleteAccount(d[i])
            .then(result => {
                // continue
            })
            .catch((result => {
                error = true
				error_res = result          
            }))

            if(error){
				break
			}
        }

        if(error){
			reject({"status": 400, "body": error_res})
		}
		else{
			resolve({"status": 200, "body": d})
		}     
    })
}

/**
 * ユーザの更新
 * @param {Array} d 更新対象ユーザデータ
 * @returns 
 */
exports.update_account = function(d){
    return new Promise((resolve, reject) => {
        if(d.length === 0){
			resolve({"status": 200, "body": "No update target"})
			return true;
        }

        // 以下サンプル動かす用のデータ例
        let error_res;
		let error = false;

        for(let i = 0; i < d.length; i++){
            const pwdhash = crypto.createHash('sha256');
			pwdhash.update(d[i].password + pwdsecret);
            let reqData = {
                "_id": d[i]._id,
                "login_id": d[i].login_id,
				"display_name": d[i].display_name,
				"password": pwdhash.digest('base64'),
				"fullname": d[i].fullname,
				"organization": d[i].organization,
				"phone": d[i].phone
            }

            UsersLib.updateAccout(reqData)
            .then(result => {
                // continue
            })
            .catch((result => {
                error = true
				error_res = result          
            }))

            if(error){
				break
			}
        }

        if(error){
			reject({"status": 400, "body": error_res})
		}
		else{
			resolve({"status": 200, "body": d})
		}    
    })
}