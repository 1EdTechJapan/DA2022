$( function()
{

    $('input[type="radio"]').on('change', function() {
        $('button').removeAttr('disabled');
    });
    
    // 非同期でlti1.3NRPSから得たメンバー情報をテーブルに追加する。
    $('#user_show_btn').on('click', function() {
        let launch_id = '';
        launch_id = $('#user_show_btn').data('launch');
        console.log( launch_id );
        get_members( launch_id );
    });

    // 非同期通信。LTI1.3 AGS SCOREの送信。
    $('#score_btn').on('click', function() {
        let xhr = new XMLHttpRequest();
        let url = '/ags_sample_url/score';
        let formData = new FormData(document.forms.myscore);
        xhr.responseType = 'json';
        xhr.open("POST", url, true);
        xhr.send( formData );
        xhr.onload = function() {
            if (xhr.status != 200) {
                console.log( `Error ${xhr.status}: ${xhr.statusText}` );
            } else { 
                // 結果を表示
                console.log( xhr.response );
            }
        };
        xhr.onerror = function() {
            console.log("Request failed");
        };
        
    });

    // 非同期通信。LTI1.3 AGS RESULTの取得。
    $('#result_btn').on('click', function() {
        let formData = new FormData(document.forms.results);
        let launch_id = '';
        let course = '';
        
        launch_id = formData.get('launch_id');
        course = formData.get('course');
        console.log('launch:' + launch_id);
        console.log('course:' + course);
        
        get_results( launch_id, course );
    });
})

/**
 * メンバー情報をテーブルに追加する
 * 
 * @param {object} members
 */
function show_member_table( members ){
    console.log( members );
    $row = '';
    members.forEach(element => {
        $row += '<tr>';
        $row +=    '<td class="border">'+ element.user_id +'</td>';
        $row +=    '<td class="border">'+ element.name +'</td>';
        $row += '</tr>';
    });
    $('tbody').html($row);
}

/**
 * メンバー情報を非同期で取得する
 * 
 * @param {string} launch_id
 * 
 */
function get_members( launch_id ){
    let xhr = new XMLHttpRequest();
    let url = '/{nrps_sample_url}/get_member?launch=' + launch_id;
    xhr.responseType = 'json';
    xhr.open("GET", url, true);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status != 200) {
            console.log( `Error ${xhr.status}: ${xhr.statusText}` );
        } else { 
            // 用意が出来たらテーブルを作成
            show_member_table( xhr.response )
        }
    };
    xhr.onerror = function() {
        console.log("Request failed");
    };
}

/**
 * 成績情報をテーブルに追加する
 * 
 * @param {object} results
 */
function show_result_table( results ){
    $row = '';
    results.forEach(element => {
        $row += '<tr>';
        $row +=    '<td class="border">'+ element.userId +'</td>';
        $row +=    '<td class="border">'+ element.score +'</td>';
        $row +=    '<td class="border">'+ element.time +'</td>';
        $row +=    '<td class="border">'+ element.progress +'</td>';
        $row += '</tr>';
    });
    $('tbody').html($row);
    $('#result_list').removeClass('hidden');
}

/**
 * 成績情報を非同期で取得する
 * 
 * @param {string} launch_id
 * @param {string} course  
 */
function get_results( launch_id, course ){
    let xhr = new XMLHttpRequest();
    let url = '/{ags_sample_url}/result?launch=' + launch_id + '&course=' + course;
    xhr.responseType = 'json';
    xhr.open("GET", url, true);
    xhr.send();
    xhr.onload = function() {
        if (xhr.status != 200) {
            console.log( `Error ${xhr.status}: ${xhr.statusText}` );
        } else { 
            // 用意が出来たらテーブルを作成
            show_result_table( xhr.response )
        }
    };
    xhr.onerror = function() {
        console.log("Request failed");
    };
}

