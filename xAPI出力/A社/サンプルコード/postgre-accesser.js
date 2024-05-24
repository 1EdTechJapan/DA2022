// 'use strict';

// postgre sql アクセス用オブジェクトの作成と接続
const { Client } = require('pg');

const pgClient = new Client({
  user: process.env.POSTGRE_SQL_USER_NAME,
  host: process.env.POSTGRE_SQL_HOST_NAME,
  database: process.env.POSTGRE_SQL_AM_DATABASE,
  password: process.env.POSTGRE_SQL_PASSWORD,
  port: 5432
});
pgClient.connect()
  .then(() => console.log('postgre sql connection success'))
  .catch((error) => console.error('postgre sql connection error', error.stack));


// 
// クエリ実行 (postgre sql)
async function execQueryToPostgre(_params) {
  // 
  let list = [];
  try {
    // クエリ実行
    const result = await pgClient.query(_params);
    if (result.rows) {
      list.push(...result.rows);
    }
  }
  catch (error) {
    console.error(error.stack);
    list = [];
  }
  // 戻り値の返却(検索データ)
  return list;
}

// 接続を閉じる
async function disconnected() {
  pgClient.end()
  .then(() => console.log('postgre sql has disconnected'))
  .catch((error) => console.error('error during disconnection', error.stack));
}


// 
// 対象オブジェクトをエクスポート
exports.execQuery = execQueryToPostgre;
exports.disconnected = disconnected;
