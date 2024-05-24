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
/// データ取得 (dynamo db、行動履歴データ)
async function getActionHistoriesData(_tableName, _dateStart, _dateEnd) {
  // 
  // 時刻変換(1970/01/01 からの経過時間に変換) ※"yyyy-MM-dd 00:00:00.000" で設定されているのでミリ秒を除く
  const startTime = Math.floor(_dateStart.getTime() * 0.001);
  const endTime = Math.floor(_dateEnd.getTime() * 0.001);

  // 検索パラメタの設定(ダミーPK, 時刻情報) ※GSIを使用して検索する
  const params = {
    TableName: _tableName,
    IndexName: 'xxxx-index',
    ExpressionAttributeNames: {'#key': 'xxxx', '#xxxx': 'xxxx'},
    ExpressionAttributeValues: {':xxxx': 'xxxx', ':sTime': startTime, ':eTime': endTime},
    KeyConditionExpression: '#key = :xxxxxxxxxxxxxxxxxxxxxx'
  };

  // 戻り値の返却(検索データ)
  const result = await dynamoAccesser.execQuery(params);
  return result;
}

// データ更新 (dynamo db、行動履歴データ)
async function updateActionHistoriesData(_tableName, _userID, _timestamp, _lrs_uuid) {
  // 
  // クエリパラメタ作成(新規カラム追加)
  const params = {
    TableName: _tableName,
    Key: {
      'xxxx': _userID,
      'xxxx': _timestamp
    },
    ExpressionAttributeNames: {'#key': 'xxxx'},
    ExpressionAttributeValues: {':xxxx': _lrs_uuid},
    UpdateExpression: "set #key = :xxxxxxxxxxxxxxxxxxxxxx",
  };

  // 戻り値の返却(レスポンス結果)
  const result = await dynamoAccesser.updateQuery(params);
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

// 音再生完了の閾値の設定
const audioCompThreshold = parseInt(process.env.AUDIO_LISTENING_COMPLETION_THRESHOLD);

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

      let historiesDataList = {}, lrpDataList = {};
      try {
        // サービス毎の行動履歴データの取得(例外発生時は、エラーログ表示後に次の処理へ移行)
        historiesDataList = await getActionHistoriesData(tableName, startDateTime, endDateTime);

        // 取得したデータの確認(履歴データが存在しない場合は以降の処理を行わない)
        if (historiesDataList.length <= 0) {
          console.error(`${tableName} table data is empty \n`);
          continue;
        }

        // サービス毎のLRS送信先情報の取得(CUSTOMSデータが存在しない場合は以降の処理を行わない)
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

        // LRS送信用の学習データの取得(データ件数が多いため、一定量で区切って処理を実行する)
        const startIndex = sendCount;
        const endIndex = sendCount + sendLimitSize;

        const historiesData = historiesDataList.slice(startIndex, endIndex);
        for (const data of historiesData) {

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
              await updateActionHistoriesData(tableName, data.user_id, data.timestamp, data.lrs_statement_id);
            }
            // スタディログの作成と保持(視聴した割合が閾値以上の場合のみ処理)
            if (data.progress_percent >= audioCompThreshold) {
              if (!('user_uuid' in data)) {
                data.user_uuid = userIDsData.userUUID;
              }
              const value = statement_data.getStudyLogForAudioCompleted(data, lrpData, audioCompThreshold);
              statementData.data.push(value);
            }
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

      } while (sendCount <= historiesDataList.length);
      // 
      console.log(`exec finish ${tableName} ...`);
    }

  } catch (error) {
    console.error(error);
  }

  // pg コネクションを閉じる
  pgAccesser.disconnected();

})();
