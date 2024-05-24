'use strict';

// 
// 
// LRS配信用スタディログの作成(json形式) ※問題回答(応答データから作成)
exports.getStudyLogForAnswered = (_resData, _correctData, _lrpData) => {
  // 
  // 基本データの設定
  let result = {
    "id": _resData.lrs_statement_id,
    "actor": {
      "objectType": "Agent",
      "account": {
        "homePage": _lrpData.account_homepage,
        "name": _resData.user_uuid
      }
    },
    "verb": {
      "id": "http://adlnet.gov/expapi/verbs/answered",
      "display": {
        "en": "answered"
      }
    },
    "object": {
      "objectType": "Activity",
      "id": _resData.activity_id
    },
    "result": {
      "success": _resData.result.success,
      "response": _resData.result.response
    },
    "context": {
      "platform": "publuslite",
      "language": "en",
      "contextActivities": {
        "category": [
          {
            "id": "http://id.tincanapi.com/activity/lrp/access_publuslite/0.9",
            "definition": {
              "type": "http://id.tincanapi.com/activitytype/source"
            }
          }
        ]
      }
    }
  }
  // 正解データから必要なデータを取得(正解データが存在する場合のみ処理) ※複数ある場合は先頭のデータを使用
  if (_correctData.length > 0) {
    // データ成型 (指定の型('true-false') の場合のみ処理)
    const data = _correctData[0];
    if (data.interactionType === 'true-false') {
      const value = data.correctResponsesPattern.join('');
      const pattern = (value === 'T') ? ['true'] : (value === 'F') ? ['false'] : data.correctResponsesPattern;
      data.correctResponsesPattern = pattern;
    }
    // データ追加 (correct_responses_gql_XXX { interactionType, correctResponsesPattern })
    result.object.definition = {
      "type": "http://adlnet.gov/expapi/activities/cmi.interaction",
      "interactionType": data.interactionType,
      "correctResponsesPattern": data.correctResponsesPattern
    }
    // データ追加 (correct_responses_gql_XXX { content_activity_id })
    result.context.contextActivities.parent = [
      {
        "id": data.content_activity_id
      }
    ]
  }
  // 作成データの返却
  return result;
}

// LRS配信用スタディログの作成(json形式) ※音声 --- 視聴完了(行動履歴データから作成)
exports.getStudyLogForAudioCompleted = (_histData, _lrpData, _threshold) => {
  // 
  // 視聴時間の変換 (秒 → PTnMnS or PTnYnMnS)
  const value = _histData.current % 3600;
  const second = value % 60;
  const minute = Math.floor(value / 60);

  const hour = Math.floor(_histData.current / 3600);
  const duration = (hour > 0) ? `PT${hour}H${minute}M${second}S` : `PT${minute}M${second}S`;

  // 基本データの設定
  let result = {
    "id": _histData.lrs_statement_id,
    "actor": {
      "objectType": "Agent",
      "account": {
        "homePage": _lrpData.account_homepage,
        "name": _histData.user_uuid
      }
    },
    "verb": {
      "id": "http://adlnet.gov/expapi/verbs/completed",
    },
    "object": {
      "objectType": "Activity",
      "id": _histData.activity_id,
      "definition": {
        "type": "https://w3id.org/xapi/audio/activity-type/audio"
      }
    },
    "result": {
      "extensions": {
        "https://w3id.org/xapi/video/extensions/time": _histData.current,
        "https://w3id.org/xapi/video/extensions/progress": _histData.progress_percent
      },
      "duration": duration
    },
    "context": {
      "platform": "publuslite",
      "language": "en",
      "contextActivities": {
        "parent": [
          {
            "id": _histData.content_activity_id
          }
        ],
        "category": [
          {
            "id": "http://id.tincanapi.com/activity/lrp/access_publuslite/0.9",
            "definition": {
              "type": "http://id.tincanapi.com/activitytype/source"
            }
          }
        ]
      },
      "extensions": {
        "https://w3id.org/xapi/video/extensions/length": _histData.total,
        "https://w3id.org/xapi/video/extensions/completion-threshold": _threshold
      }
    }
  }
  // 作成データの返却
  return result;
}

// 
// LRS配信用スタディログのPOST送信
async function postStudyLog(_lrsData, _studyLogs) {
  // 
  // データ送信に必要なデータの設定
  const postURL = _lrsData.url + "/statements";
  const headers = {
    Authorization: "Basic " + Buffer.from(_lrsData.user + ":" + _lrsData.password).toString('base64'),
    "X-Experience-API-Version": "1.0.3",
    "Content-type": "application/json",
  };

  try {
    // データ送信(まとめて送信)
    const response = await fetch(postURL, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(_studyLogs)
    });
    // 
    if (response.ok) {
      const body = await response.text();
      console.log(`request post success ${_studyLogs.length} / ${_studyLogs.length}`);
    }
    else {
      // データ送信(個別に送信)
      let successCount = 0;
      for (const studyLog of _studyLogs) {
        const response2 = await fetch(postURL, {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(studyLog)
        });
        const body = await response2.text();
        if (response2.ok) {
          successCount += 1;
        } else {
          console.error(body);
          console.error(JSON.stringify(studyLog));
        }
      }
      console.log(`request post success ${successCount} / ${_studyLogs.length}`);
    }
  }
  catch (error) {
    console.error(error.stack);
    console.error(`request post error. send url --- ${postURL}`);
  }
}
exports.postStudyLog = postStudyLog;
