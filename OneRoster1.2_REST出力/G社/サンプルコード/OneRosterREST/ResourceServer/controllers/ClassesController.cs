using MongoDB.Bson;
using MongoDB.Driver;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Web;
using System.Web.Http;

namespace ResourceServer.controllers
{
    [Authorize]
    [RoutePrefix("ims/oneroster/rostering/v1p2")]
    public class ClassesController : ApiController
    {
        [Route("classes")]
        public string getAllClasses()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");

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

            return "{ \"classes\" : " + json + " }";
        }

        [Route("classes/{sourcedId}")]
        public string getClass(string sourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");

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

            return "{ \"class\" : " + json + " }";
        }

        [Route("terms/{termSourcedId}/classes")]
        public string getClassesForTerm(string termSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");

            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("terms.sourcedId", termSourcedId), RestParser.ApiResultType.Many);
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

            return "{ \"classes\" : " + json + " }";
        }

        [Route("courses/{courseSourcedId}/classes")]
        public string getClassesForCourse(string courseSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");

            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("course.sourcedId", courseSourcedId), RestParser.ApiResultType.Many);
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

            return "{ \"classes\" : " + json + " }";
        }

        [Route("students/{studentSourcedId}/classes")]
        public string getClassesForStudent(string studentSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(new BsonDocument("user.sourcedId", studentSourcedId)).Project("{_id: 0, class: 1}").ToList();

            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefClass>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c._class.sourcedId));
            }


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$or", preParams), RestParser.ApiResultType.Many);
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

            return "{ \"classes\" : " + json + " }";
        }

        [Route("teachers/{teacherSourcedId}/classes")]
        public string getClassesForTeacher(string teacherSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(new BsonDocument("user.sourcedId", teacherSourcedId)).Project("{_id: 0, class: 1}").ToList();

            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefClass>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c._class.sourcedId));
            }


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$or", preParams), RestParser.ApiResultType.Many);
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

            return "{ \"classes\" : " + json + " }";
        }

        [Route("schools/{schoolSourcedId}/classes")]
        public string getClassesForSchool(string schoolSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");


            // sourcedIdを取得
            var pre1Collection = database.GetCollection<BsonDocument>("rest_orgs");
            var pre1Documents = pre1Collection.Find(new BsonDocument("sourcedId", schoolSourcedId)).Project("{_id: 0, children: 1}").ToList();

            BsonArray pre1Params = new BsonArray
            {
                new BsonDocument("user.sourcedId", "")
            };

            var pre1List = JsonConvert.DeserializeObject<List<models.GUIDRef.RefChildren>>(pre1Documents.ToJson());
            foreach (var c in pre1List)
            {
                BsonDocument param = new BsonDocument("user.sourcedId", c.children.sourcedId);
                pre1Params.Add(param);
            }


            // sourcedIdを取得
            var pre2Collection = database.GetCollection<BsonDocument>("rest_enrollments");
            var pre2Documents = pre2Collection.Find(new BsonDocument("$or", pre1Params)).Project("{_id: 0, class: 1}").ToList();

            BsonArray pre2Params = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var pre2List = JsonConvert.DeserializeObject<List<models.GUIDRef.RefClass>>(pre2Documents.ToJson());
            foreach (var c in pre2List)
            {
                BsonDocument param = new BsonDocument("sourcedId", c._class.sourcedId);
                pre2Params.Add(param);
            }


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$or", pre2Params), RestParser.ApiResultType.Many);
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

            return "{ \"classes\" : " + json + " }";
        }

        [Route("users/{userSourcedId}/classes")]
        public string getClassesForUser(string userSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_classes");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(new BsonDocument("user.sourcedId", userSourcedId)).Project("{_id: 0, class: 1}").ToList();

            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefClass>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c._class.sourcedId));
            }


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$or", preParams), RestParser.ApiResultType.Many);
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

            return "{ \"classes\" : " + json + " }";
        }
    }
}
