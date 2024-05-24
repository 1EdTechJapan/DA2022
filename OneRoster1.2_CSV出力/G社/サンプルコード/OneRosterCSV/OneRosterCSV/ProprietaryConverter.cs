using System;

using MongoDB.Bson;
using MongoDB.Bson.Serialization;
using MongoDB.Driver;

namespace OneRosterCSV
{
    /// <summary>
    /// 校務システムのデータをOneRoster用に変換する専用のコンバーター
    /// </summary>
    public class ProprietaryConverter
    {

        #region MongoDBデータ追加サンプル

        /// <summary>
        /// 校務システムデータ変換サンプルコード
        /// </summary>
        public void ToMongodbSample()
        {
            // 校務システムからデータを取得
            // 【本セクションで各校務システムに合わせてデータの取得、および加工処理を実施】


            // mongodb(class)のモデルを作成
            Models.Class.Class1 obj = new Models.Class.Class1
            {
                sourcedId = Guid.NewGuid().ToString(),
                status = "active",
                dateLastModified = Global.GetIso8601UTC(),
                title = "1年1組",
                grades = new string[3] { "P1", "P2", "P3" },
                course = new Models.Class.Course() { href = "href", sourcedId = "sourcedId", type = "type" },
                classCode = null,
                classType = "homeroom",
                location = null,
                school = new Models.Class.School() { href = "href", sourcedId = "sourcedId", type = "type" },
                terms = new Models.Class.Term[2] {
                    new Models.Class.Term() { href = "href", sourcedId = "sourcedId", type = "type" },
                    new Models.Class.Term() { href = "href", sourcedId = "sourcedId", type = "type" }
                },
                subjects = null,
                subjectCodes = null,
                periods = null,
                metadata = new Models.Class.Metadata()
                {
                    jp = new Models.Class.JapanProfile()
                    {
                        specialNeeds = "False"
                    }
                }
            };


            // mongodb(class)に格納
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);

            string text = obj.ToJson();

            var document = BsonSerializer.Deserialize<BsonDocument>(text);
            var collection = database.GetCollection<BsonDocument>("rest_classes");
            collection.InsertOne(document);
        }

        #endregion


        #region ProprietarySource

        /// <summary>
        /// 校務システムのデータをmongodbに変換
        /// </summary>
        public void ToMongodbProprietary()
        {
            // TODO 各校務システムに合わせてMongoDBへの変換処理を実装してください。
        }

        /// <summary>
        /// MongoDBにデータを変換した日を記録しておき日本仕様対応用のZIPファイル名のために取得
        /// </summary>
        public string GetJapanZipFilename()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("japanSpecials");

            var documents = collection.Find(new BsonDocument()).ToList();

            string dateOutput = documents[0].GetValue(documents[0].IndexOfName("dateOutput")).ToString();
            string identifier = documents[0].GetValue(documents[0].IndexOfName("identifier")).ToString();

            return "RO_" + dateOutput + "_" + identifier + ".zip";
        }

        #endregion
    }
}