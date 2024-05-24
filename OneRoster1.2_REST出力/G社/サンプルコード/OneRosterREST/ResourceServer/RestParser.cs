using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Web;
using System.Linq;

using TSQL;
using TSQL.Statements;
using TSQL.Tokens;
using System.Net;
using MongoDB.Driver;
using MongoDB.Bson;

namespace ResourceServer
{
    /// <summary>
    /// クエリパラメータのFilter解析結果
    /// </summary>
    public class FilterToken
    {
        public string Field { get; set; }
        public string Operator { get; set; }
        public string FieldValue { get; set; }
        public string SearchOperator { get; set; }
    }

    /// <summary>
    /// クエリパラメーター解析
    /// </summary>
    public class RestParser
    {
        public enum ApiResultType 
        {
            One,
            Many
        }

        /// <summary>
        /// コンストラクタ
        /// </summary>
        public RestParser()
        {
        }

        /// <summary>
        /// クエリパラメータを自動処理しJSONを構築して返す
        /// </summary>
        /// <param name="collection">対象のコレクション</param>
        /// <param name="findParam">URIパラメータがあれば条件を指定</param>
        /// <param name="apiResultType">API取得タイプの指定</param>
        /// <returns></returns>
        /// <exception cref="RestException"></exception>
        public string BuildJSON(IMongoCollection<BsonDocument> collection, BsonDocument findParam, ApiResultType apiResultType)
        {
            // クエリパラメータをパース
            NameValueCollection queryParam = HttpUtility.ParseQueryString(HttpContext.Current.Request.Url.Query);

            // filter
            string[] filter = queryParam.GetValues("filter");
            if (filter != null)
            {
                List<FilterToken> parsedFilter = FilterParse(filter[0]);

                // 演算子置き換え
                for (var i = 0; i < parsedFilter.Count; i++)
                {
                    var p = parsedFilter[i];

                    bool operatorOK = false;
                    if (string.Compare("=", p.Operator, true) == 0)
                    {
                        p.Operator = "$eq";
                        operatorOK = true;
                    }
                    if (string.Compare("!=", p.Operator, true) == 0)
                    {
                        p.Operator = "$ne";
                        operatorOK = true;
                    }
                    if (string.Compare(">", p.Operator, true) == 0)
                    {
                        p.Operator = "$gt";
                        operatorOK = true;
                    }
                    if (string.Compare(">=", p.Operator, true) == 0)
                    {
                        p.Operator = "$gte";
                        operatorOK = true;
                    }
                    if (string.Compare("<", p.Operator, true) == 0)
                    {
                        p.Operator = "$lt";
                        operatorOK = true;
                    }
                    if (string.Compare("<=", p.Operator, true) == 0)
                    {
                        p.Operator = "$lte";
                        operatorOK = true;
                    }
                    if (string.Compare("~", p.Operator, true) == 0)
                    {
                        p.Operator = "$in";
                        operatorOK = true;
                    }
                    if (operatorOK == false)
                    {
                        // 例外生成
                        throw new RestException(HttpStatusCode.BadRequest, p.Operator, "invalid_filter_field");
                    }

                    bool searchOperatorOK = false;
                    if (string.Compare("and", p.SearchOperator, true) == 0)
                    {
                        p.SearchOperator = "$and";
                        searchOperatorOK = true;
                    }
                    if (string.Compare("or", p.SearchOperator, true) == 0)
                    {
                        p.SearchOperator = "$or";
                        searchOperatorOK = true;
                    }
                    if (searchOperatorOK == false)
                    {
                        // 例外生成
                        throw new RestException(HttpStatusCode.BadRequest, p.SearchOperator, "invalid_filter_field");
                    }
                }

                // MongoDB.Find用のパラメータ作成
                for (var i = 0; i < parsedFilter.Count; i++)
                {
                    var p = parsedFilter[i];

                    BsonDocument currentParam = new BsonDocument(p.Field, new BsonDocument(p.Operator, p.FieldValue));
                    findParam = new BsonDocument(p.SearchOperator, new BsonArray { findParam, currentParam });
                }
            }


            // sort
            BsonDocument sortParam = new BsonDocument("sourcedId", 1);

            string[] sort = queryParam.GetValues("sort");
            if (sort != null)
            {
                sortParam = new BsonDocument(sort[0], 1);

                // orderBy
                string[] orderBy = queryParam.GetValues("orderBy");
                if (orderBy != null)
                {
                    if (string.Compare(orderBy[0], "desc", true) == 0)
                    {
                        sortParam = new BsonDocument(sort[0], -1);
                    }
                }
            }


            // offset (既定:0)
            int skipValue = 0;
            string[] offset = queryParam.GetValues("offset");
            if (offset != null)
            {
                skipValue = Int32.Parse(offset[0]);
            }

            // limit (既定:100)
            int limitValue = 100;
            string[] limit = queryParam.GetValues("limit");
            if (limit != null)
            {
                limitValue = Int32.Parse(limit[0]);
            }


            // fields
            string projectionValue = "{_id: 0}";

            string[] fields = queryParam.GetValues("fields");
            if (fields != null)
            {
                string[] selectedFields = fields[0].Split(',');
                foreach (var field in selectedFields)
                {
                    projectionValue += " " + field + ": 1,";
                }
                if (selectedFields.Length > 0)
                {
                    // 末尾のカンマを削除してカッコで囲む
                    projectionValue = projectionValue.Substring(0, projectionValue.Length - 1);
                    projectionValue = "{" + projectionValue + "}";
                }
            }


            // データを取得
            var documents = collection.Find(findParam).Sort(sortParam).Project(projectionValue).Skip(skipValue).Limit(limitValue).ToList();

            // 合計数をヘッダ(X-Total-Count)にセットする
            var allDocuments = collection.Find(findParam).ToList();
            HttpContext.Current.Response.AppendHeader("X-Total-Count", allDocuments.Count.ToString());

            // 1件のみ取得するAPIのとき
            if (apiResultType == ApiResultType.One && documents.Count > 0)
            {
                return documents[0].ToJson();
            }

            // 複数件取得するAPIのとき
            if (documents.Count > 0)
            {
                return documents.ToJson();
            }

            // 取得されなかったとき
            return "null";
        }

        /// <summary>
        /// クエリパラメータのFilterを構文解析
        /// </summary>
        private List<FilterToken> FilterParse(string filter)
        {
            TSQLSelectStatement select = TSQLStatementReader.ParseStatements(@"SELECT * FROM dummy WHERE " + filter)[0] as TSQLSelectStatement;

            // パース結果
            List<FilterToken> result = new List<FilterToken>();

            if (select.Where != null)
            {
                FilterToken ruleValue = new FilterToken();
                foreach (TSQLToken token in select.Where.Tokens)
                {
                    string tokenType = token.Type.ToString();
                    string tokenText = token.Text;

                    switch (tokenType)
                    {
                        case "Character":
                            ruleValue.Field += tokenText;
                            break;
                        case "Keyword":
                            if (string.IsNullOrEmpty(ruleValue.SearchOperator))
                            {
                                ruleValue.SearchOperator = tokenText;
                            }
                            else
                            {
                                ruleValue.SearchOperator += " " + tokenText;
                            }

                            break;
                        case "Operator":
                            ruleValue.Operator = tokenText;
                            break;
                        case "Identifier":
                            ruleValue.Field += tokenText;
                            break;
                        case "Variable":
                        case "StringLiteral":
                        case "NumericLiteral":
                            ruleValue.FieldValue = tokenText;
                            if (!string.IsNullOrEmpty(ruleValue.SearchOperator) && ruleValue.SearchOperator.Equals("WHERE"))
                            {
                                ruleValue.SearchOperator = "AND";
                            }
                            result.Add(ruleValue);
                            ruleValue = new FilterToken();
                            break;
                        default:
                            break;
                    }
                }
            }

            return result;
        }
    }
}