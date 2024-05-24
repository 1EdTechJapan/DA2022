// 'use strict';

// aws dynamoDB アクセス用オブジェクトの作成
const AWS = require("aws-sdk");
AWS.config.update({ region: "ap-northeast-1", });

const docClient = new AWS.DynamoDB.DocumentClient();


// 
// クエリ実行 (dynamodb) ※主にデータ検索に使用
async function execQueryToDynamoDB(_params) {
  // 
  let list = [];
  try {
    // クエリ実行(一度ですべて取得できなかった場合は繰り返し取得する)
    while (true) {
      const result = await docClient.query(_params).promise();
      if (result.Items) {
        list.push(...result.Items);
      }
      if (result.LastEvaluatedKey) {
        _params.ExclusiveStartKey = result.LastEvaluatedKey;
      } else {
        break;
      }
    }
  } catch (error) {
    console.error(error.stack);
    list = [];
  }
  // 戻り値の返却(検索データ)
  return list;
}

// クエリ実行 (dynamodb) ※データ更新
async function updateQueryToDynamoDB(_params) {
  // 
  let result = null;
  try {
    // クエリ実行(update)
    result = await docClient.update(_params).promise();
  } catch (error) {
    console.error(error.stack);
  }
  // 戻り値の返却(レスポンス結果)
  return result;
}

// 接続を閉じる
async function disconnected() {
}


// 
// 対象オブジェクトをエクスポート
exports.execQuery = execQueryToDynamoDB;
exports.updateQuery = updateQueryToDynamoDB;
exports.disconnected = disconnected;
