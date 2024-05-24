// 'use strict';
const statement_data = require("./statement-data");
const constant = require("./constant");

const uuids = require('uuid');
const dateFNS = require('date-fns');

// dynamoDB アクセス用オブジェクトの読み込み
const dynamoAccesser = require("./dynamodb-accesser");

// postgre sql アクセス用オブジェクトの読み込み
const pgAccesser = require("./postgre-accesser");

/// 
/// データ取得 (dynamo db、応答データ)
async function getResponsesData(_tableName, _dateStart, _dateEnd) {
  // 
  // 時刻変換(グリニッジ標準時間への変換) ※"yyyy-MM-ddTHH:mm:ss.SSSZ" のフォーマットで指定
  const startTime = _dateStart.toISOString();
  const endTime = _dateEnd.toISOString();

  // 検索パラメタの設定(ダミーPK, 時刻情報) ※GSIを使用して検索する
  const params = {
    TableName: _tableName,
    IndexName: 'xxxx-index',
    ExpressionAttributeNames: {'#key': 'xxxx', '#xxxx': 'xxxx'},
    ExpressionAttributeValues: {':xxxx': 'xxxx', ':sDate': startTime, ':eDate': endTime},
    KeyConditionExpression: '#key = :xxxxxxxxxxxxxxxxxxxxxx'
  };

  // 戻り値の返却(検索データ)
  const result = await dynamoAccesser.execQuery(params);
  return result;
}

// データ取得 (dynamo db、正解データ)
async function getCorrectResData(_tableName, _activity_id) {
  // 
  // 検索パラメタの設定(アクティビティID) ※GSIで取得
  const params = {
    TableName: _tableName,
    IndexName: 'xxxx-index',
    ExpressionAttributeNames: {'#key': 'xxxx'},
    ExpressionAttributeValues: {':xxxx': _activity_id},
    KeyConditionExpression: '#key = :xxxxxxxxxxxxxxxxxxxxxx'
  };

  // 戻り値の返却(検索データ)
  const result = await dynamoAccesser.execQuery(params);
  return result;
}

// データ更新 (dynamo db、応答データ)
async function updateResponsesData(_tableName, _userID, _datetime, _lrs_uuid) {
  // 
  // クエリパラメタ作成(新規カラム追加)
  const params = {
    TableName: _tableName,
    Key: {
      'xxxx': _userID,
      'xxxx': _datetime
    },
    ExpressionAttributeNames: {'#key': 'xxxx'},
    ExpressionAttributeValues: {':xxxx': _lrs_uuid},
    UpdateExpression: "set #key = :xxxxxxxxxxxxxxxxxxxxxx",
  };

  // 戻り値の返却(レスポンス結果)
  const result = dynamoAccesser.updateQuery(params);
  return result;
}

// 
// 処理開始・終了時刻の設定(東京標準時で 00:00:00.000 ～ 23:59:59.999 に設定) ※今日からN日前 ～ 昨日までの期間
const backDays = (process.argv.length > 2) ? parseInt(process.argv[2]) : 1;
const nowDate = dateFNS.format(new Date(), 'yyyy-MM-dd');

const startDateTime = new Date(`${nowDate}T00:00:00+09:00`);
startDateTime.setDate(startDateTime.getDate() - backDays);

const endDateTime = new Date(`${nowDate}T00:00:00+09:00`);
endDateTime.setMilliseconds(endDateTime.getMilliseconds() - 1);

console.log(`exec target datetime --- ${startDateTime.toLocaleString()} ~ ${endDateTime.toLocaleString()}`);

/// 
(async () => {
  // 
  try {
    // 登録済みのサービス名一覧の取得と一覧数文のループ
    const listServices = await pgAccesser.execQuery(constant.QUERY_SELECT_SERVICE_NAME);
    for (const services of listServices) {

      // サービス名に対応する各種データの取得
      const serviceName = services.name;
      const tableName = `xxxx_${serviceName}`;
      console.log(`exec start ${tableName} ...`);

      let responsesDataList = {}, lrpDataList = {};
      try {
        // サービス毎の応答データの取得 (例外発生時は、エラーログ表示後に次の処理へ移行)
        responsesDataList = await getResponsesData(tableName, startDateTime, endDateTime);

        // 取得したデータの確認 (応答データが存在しない場合は以降の処理を行わない)
        if (responsesDataList.length <= 0) {
          console.error(`${tableName} table data is empty \n`);
          continue;
        }

        // サービス毎のLRS送信先情報の取得 (CUSTOMSデータが存在しない場合は以降の処理を行わない)
        const customsData = await pgAccesser.execQuery(constant.QUERY_SELECT_CUSTOMS_LRS_DELIVERY_LIST(serviceName));
        if (customsData.length <= 0) {
          continue;
        }
        lrpDataList = customsData[0].bare_data.LRP;
      }
      catch (error) {
        console.error(error.stack);
        console.error(`${tableName} table not exist \n`);
        continue;
      }

      // 送信済みデータ数と一度に送れるデータ数の宣言
      let sendCount = 0;
      const sendLimitSize = parseInt(process.env.LRS_SEND_LIMIT_SIZE);

      // ユーザーID毎の関連データの一時格納領域の作成
      const userIDsDataList = {};

      do {
        // LRS送信用学習データの一時格納領域の作成
        const statementDataList = {};

        // LRS送信用の学習データの取得(応答データの件数が多いため、一定量で区切って処理を実行する)
        const startIndex = sendCount;
        const endIndex = sendCount + sendLimitSize;

        const responsesData = responsesDataList.slice(startIndex, endIndex);
        for (const data of responsesData) {

          // 正解データの取得 (activity_id をキーとして実行)
          const correctData = await getCorrectResData(`xxxx_${serviceName}`, data.activity_id);

          // データ登録キー(userID)の確認(リストにuserIDが存在しない場合は新規にデータを保持する)
          const keyUserID = data.user_id.toString();
          if (!(keyUserID in userIDsDataList)) {
            const salers = await pgAccesser.execQuery(constant.QUERY_SELECT_LRS_DELIVERY_SALERS_NAME(serviceName, data.user_id));
            const users = await pgAccesser.execQuery(constant.QUERY_SELECT_USERS_FOREIGNID(serviceName, data.user_id));
            userIDsDataList[keyUserID] = {
              "salersName": (salers.length > 0) ? salers[0].name : "default",
              "userUUID": (users.length > 0) ? users[0].foreign_id ?? uuids.v4() : uuids.v4()
            }
          }
          const userIDsData = userIDsDataList[keyUserID];

          // 送信データ格納先の取得(リストに送信先名が存在しない場合は新規作成)
          const salersName = userIDsData.salersName;
          if (!(salersName in statementDataList)) {
            statementDataList[salersName] = { "data": [] }
          }
          const statementData = statementDataList[salersName];
          const lrpData = ((salersName in lrpDataList) ? lrpDataList[salersName] : lrpDataList.default);

          // 送信用学習データの作成と保持
          try {
            // スタディログ管理用uuidの存在確認(未存在時は対象のDBに管理用uuidを追加)
            if (!('lrs_statement_id' in data)) {
              data.lrs_statement_id = uuids.v4();
              await updateResponsesData(tableName, data.user_id, data.datetime, data.lrs_statement_id);
            }
            // スタディログの作成と保持
            if (!('user_uuid' in data)) {
              data.user_uuid = userIDsData.userUUID;
            }
            const value = statement_data.getStudyLogForAnswered(data, correctData, lrpData);
            statementData.data.push(value);
          } catch (error) {
            console.error(error.stack);
            console.error(JSON.stringify(data));
          }
        }

        // データ送信(送信先名ごとにまとめて送信)
        for (const name of Object.keys(statementDataList)) {
          const lrsData = (name in lrpDataList) ? lrpDataList[name].lrs : lrpDataList.default.lrs;
          const statementData = statementDataList[name].data;
          await statement_data.postStudyLog(lrsData, statementData);
        }
        // データ送信数の更新
        sendCount += sendLimitSize;

      } while (sendCount <= responsesDataList.length);
      // 
      console.log(`exec finish ${tableName} ...`);
    }

  } catch (error) {
    console.error(error);
  }

  // pg コネクションを閉じる
  pgAccesser.disconnected();

})();
