using MongoDB.Bson;
using MongoDB.Driver;
using System.Web;
using System.Web.Http;

namespace ResourceServer.controllers
{
    // 5.4 Enumerated Class UML/JSON Mapping
    // SessionTypeEnum { gradingPeriod | semester | schoolYear | term }.

    [Authorize]
    [RoutePrefix("ims/oneroster/rostering/v1p2")]
    public class TermsController : ApiController
    {
        [Route("terms")]
        public string getAllTerms()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("type", "term"), RestParser.ApiResultType.Many);
            }
            catch (RestException ex)
            {
                HttpContext.Current.Response.StatusCode = (int)ex.statusCode;
                models.Error.Rootobject error = new models.Error.Rootobject
                {
                    imsx_codeMajor = "failure",
                    imsx_severity = "error",
                    imsx_description = ex.exceptionName + " " + ex.exceptionValue
                };
                return error.ToJson();
            }

            return "{ \"academicSessions\" : " + json + " }";
        }

        [Route("terms/{sourcedId}")]
        public string getTerm(string sourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", sourcedId),
                new BsonDocument("type", "term")
            };


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$and", preParams), RestParser.ApiResultType.One);
            }
            catch (RestException ex)
            {
                HttpContext.Current.Response.StatusCode = (int)ex.statusCode;
                models.Error.Rootobject error = new models.Error.Rootobject
                {
                    imsx_codeMajor = "failure",
                    imsx_severity = "error",
                    imsx_description = ex.exceptionName + " " + ex.exceptionValue
                };
                return error.ToJson();
            }

            return "{ \"academicSession\" : " + json + " }";
        }

        [Route("schools/{schoolSourcedId}/terms")]
        public string getTermsForSchool(string schoolSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            // REPORT parentのSourcedIdが一致するもののうちtermのものを出力            
            BsonArray preParams = new BsonArray
            {
                new BsonDocument("parent.sourcedId", schoolSourcedId),
                new BsonDocument("type", "term")
            };


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$and", preParams), RestParser.ApiResultType.Many);
            }
            catch (RestException ex)
            {
                HttpContext.Current.Response.StatusCode = (int)ex.statusCode;
                models.Error.Rootobject error = new models.Error.Rootobject
                {
                    imsx_codeMajor = "failure",
                    imsx_severity = "error",
                    imsx_description = ex.exceptionName + " " + ex.exceptionValue
                };
                return error.ToJson();
            }

            return "{ \"academicSessions\" : " + json + " }";
        }
    }
}
