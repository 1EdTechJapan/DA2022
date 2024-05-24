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
    public class GradingPeriodsController : ApiController
    {
        [Route("gradingPeriods")]
        public string getAllGradingPeriods()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("type", "gradingPeriod"), RestParser.ApiResultType.Many);
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

        [Route("gradingPeriods/{sourcedId}")]
        public string getGradingPeriod(string sourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", sourcedId),
                new BsonDocument("type", "gradingPeriod")
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

        [Route("terms/{termSourcedId}/gradingPeriods")]
        public string getGradingPeriodsForTerm(string termSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            // REPORT parentのSourcedIdが一致するもののうちtermのものを出力            
            BsonArray preParams = new BsonArray
            {
                new BsonDocument("parent.sourcedId", termSourcedId),
                new BsonDocument("type", "gradingPeriod")
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
