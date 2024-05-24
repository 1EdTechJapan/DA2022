$('#btn-import').on('click', async function(e){
    e.preventDefault()

    $('#result-area').empty()

    let errorModal = new bootstrap.Modal(document.getElementById('errorModal'))
    errorModal.hide()

    let files = $('#inputFile')[0].files
    console.log(files)

    if(files.length === 0){
        showErrorModal("ファイルを選択してください。");
        return false;
    }

    let fileName = files[0].name
    let pos = fileName.lastIndexOf('.')
    if(fileName.slice(pos + 1) !== 'zip'){
        showErrorModal("zipファイルを選択してください。");
        return false;			
    }

    const formData = new FormData();
    formData.append('upload_file', files[0]);

    let res = await fetch('/users/import_accounts', {
        method: 'POST',
        body: formData
    });   

    let res_json = await res.json()
    if (res.ok){
        showSuccessLog(res_json)

        let log_data = {
            "name": fileName,
            "size": files[0].size,
            "error": 0,
            "error_msg": "",
            "jp_error": res_json.jp_error
        }
        let resLog = await fetch("/users/put_oneroster_log", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(log_data)
                    });
        if(!resLog.ok){
            console.log(resLog)
        }
    }
    else{
        showErrorLog(res_json)

        let log_data = {
            "name": fileName,
            "size": files[0].size,
            "error": res_json.count,
            "error_msg": res_json.body,
             "jp_error": ""
        }
        let resLog = await fetch("/users/put_oneroster_log", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(log_data)
                    });
        if(!resLog.ok){
            console.log(resLog)
        }
    }
    
    $('#inputFile')[0].value = ''
})

const showErrorModal = (message) => {
    let errorModal = new bootstrap.Modal(document.getElementById('errorModal'))
    $('#errorModalMsg').text(message)

    errorModal.show()
}

// 成功時のログ出力
const showSuccessLog = (data) => {
    let div = $('<div></div>').addClass('import-success');
    // Japan Profileの仕様上のエラーがあった場合、正常終了したけど一部取り込めなかったデータがあったことを表示する
    if(data.count){
        if(data.jp_error && data.jp_error.length > 0){
            let p = $('<p></p>').addClass('alert alert-success').text('処理は正常に終了しましたが、以下のデータはJapan Profileでは許可されないため取り込めませんでした。');
            let table =$('<table></table>').addClass("table").css({"margin-top": "24px"});
            let thead = $('<thead></thead>');
            let trHead = $('<tr></tr>');
            let th1 = $('<th></th>').text('ファイル名');
            let th2 = $('<th></th>').text('line');
            let th3 = $('<th></th>').text('内容');
            trHead.append(th1).append(th2).append(th3);
            thead.append(trHead);
            table.append(thead);
            let tbody = $('<tbody></tbody>')
            if(data.jp_error){
                for(let i = 0; i < data.jp_error.length; i++){
                    let trBody = $('<tr></tr>');
                    let td1 = $('<td></td>').text(data.jp_error[i].filename);
                    let td2 = $('<td></td>').text(data.jp_error[i].line);
                    let td3 = $('<td></td>').text(data.jp_error[i].message);
                    trBody.append(td1).append(td2).append(td3);
                    tbody.append(trBody);
                }
            }
            table.append(tbody);	
            div.append(p).append(table);	
        }
        else if(data.jp_error && data.jp_error.length === 0){
            let p = $('<p></p>').addClass('alert alert-success').text('取り込み対象となるデータがありませんでした。');
            div.append(p);
        }
    }
    else{
        let p = $('<p></p>').addClass('alert alert-success').text('データを正常にインポートしました。');
		div.append(p);	
    }
    $('#result-area').append(div)
}

// エラー時のログ出力
const showErrorLog = (error) => {
    let pTitle = $('<p></p>').addClass("alert alert-danger").text("CSVファイルのインポートに失敗しました。")
    let spanCnt = $('<span></span>').css({"font-size": "16px"})
    if(error.count){
        spanCnt.text(`全${error.count}件のエラーがあります。`)
    }
    let table =$('<table></table>').addClass("table").css({"margin-top": "24px"})
    let thead = $('<thead></thead>')
    let trHead = $('<tr></tr>')
    let th1 = $('<th></th>').text('ファイル名')
    let th2 = $('<th></th>').text('line')
    let th3 = $('<th></th>').text('内容')
    trHead.append(th1).append(th2).append(th3)
    thead.append(trHead)
    table.append(thead)
    let tbody = $('<tbody></tbody>')
    if(error.body){
        for(let i = 0; i < error.body.length; i++){
            let trBody = $('<tr></tr>')
            if(error.body[i].filename === "db"){
                let td = $('<td></td>').attr('colspan', 3).text('DBとの接続に失敗しました。')
                trBody.append(td)
            }
            else{
                let td1 = $('<td></td>').text(error.body[i].filename)
                let td2 = $('<td></td>').text(error.body[i].line)
                let td3 = $('<td></td>').text(error.body[i].message)
                trBody.append(td1).append(td2).append(td3)
            }
            tbody.append(trBody)
        }
    }
    table.append(tbody)
    $('#result-area').append(pTitle).append(spanCnt).append(table)
}