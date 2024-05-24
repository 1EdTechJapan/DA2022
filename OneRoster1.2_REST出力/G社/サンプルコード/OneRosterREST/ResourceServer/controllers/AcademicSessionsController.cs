using MongoDB.Bson;
using MongoDB.Driver;
using System.Web;
using System.Web.Http;

namespace ResourceServer.controllers
{
    [Authorize]
    [RoutePrefix("ims/oneroster/rostering/v1p2")]
    public class AcademicSessionsController : ApiController
    {
        [Route("academicSessions")]
        public string getAllAcademicSessions()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument(), RestParser.ApiResultType.Many);
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
        
        [Route("academicSessions/{sourcedId}")]
        public string getAcademicSession(string sourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_academicSessions");

            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("sourcedId", sourcedId), RestParser.ApiResultType.One);
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
    }
}
