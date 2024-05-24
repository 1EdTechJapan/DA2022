using MongoDB.Bson;
using MongoDB.Driver;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Web;
using System.Web.Http;

namespace ResourceServer.controllers
{
    // 5.4 Enumerated Class UML/JSON Mapping
    // EnrolRoleEnum { administrator | proctor | student | teacher }.

    // REPORT enrollments経由で取得する

    [Authorize]
    [RoutePrefix("ims/oneroster/rostering/v1p2")]
    public class StudentsController : ApiController
    {
        [Route("students")]
        public string getAllStudents()
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_users");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(new BsonDocument("role", "student")).Project("{_id: 0, user: 1}").ToList();


            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefUser>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c.user.sourcedId));
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

            return "{ \"users\" : " + json + " }";
        }

        [Route("students/{sourcedId}")]
        public string getStudent(string sourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_users");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(
                new BsonDocument("$and", new BsonArray
                {
                    new BsonDocument("role", "student"),
                    new BsonDocument("user.sourcedId", sourcedId)
                }
                )).Project("{_id: 0, user: 1}").ToList();


            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefUser>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c.user.sourcedId));
            }


            string json = "";
            try
            {
                RestParser p = new RestParser();
                json = p.BuildJSON(collection, new BsonDocument("$or", preParams), RestParser.ApiResultType.One);
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

            return "{ \"user\" : " + json + " }";
        }

        [Route("schools/{schoolSourcedId}/classes/{classSourcedId}/students")]
        public string getStudentsForClassInSchool(string schoolSourcedId, string classSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_users");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(
                new BsonDocument("$and", new BsonArray
                {
                    new BsonDocument("role", "student"),
                    new BsonDocument("school.sourcedId", schoolSourcedId),
                    new BsonDocument("class.sourcedId", classSourcedId)
                }
                )).Project("{_id: 0, user: 1}").ToList();


            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefUser>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c.user.sourcedId));
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

            return "{ \"users\" : " + json + " }";
        }

        [Route("schools/{schoolSourcedId}/students")]
        public string getStudentsForSchool(string schoolSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_users");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(
                new BsonDocument("$and", new BsonArray
                {
                    new BsonDocument("role", "student"),
                    new BsonDocument("school.sourcedId", schoolSourcedId)
                }
                )).Project("{_id: 0, user: 1}").ToList();


            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefUser>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c.user.sourcedId));
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

            return "{ \"users\" : " + json + " }";
        }

        [Route("classes/{classSourcedId}/students")]
        public string getStudentsForClass(string classSourcedId)
        {
            var client = new MongoClient(Global.mongodbConnection);
            var database = client.GetDatabase(Global.mongodbDatabase);
            var collection = database.GetCollection<BsonDocument>("rest_users");


            // sourcedIdを取得
            var preCollection = database.GetCollection<BsonDocument>("rest_enrollments");
            var preDocuments = preCollection.Find(
                new BsonDocument("$and", new BsonArray
                {
                    new BsonDocument("role", "student"),
                    new BsonDocument("class.sourcedId", classSourcedId)
                }
                )).Project("{_id: 0, user: 1}").ToList();


            BsonArray preParams = new BsonArray
            {
                new BsonDocument("sourcedId", "")
            };

            var preList = JsonConvert.DeserializeObject<List<models.GUIDRef.RefUser>>(preDocuments.ToJson());
            foreach (var c in preList)
            {
                preParams.Add(new BsonDocument("sourcedId", c.user.sourcedId));
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

            return "{ \"users\" : " + json + " }";
        }
    }
}
