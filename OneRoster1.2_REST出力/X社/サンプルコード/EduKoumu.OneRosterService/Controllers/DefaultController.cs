using System.Configuration;
using System.Data.Entity;
using System.Data.SqlClient;
using System.Web;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    public class DefaultController : ApiController
    {
        [HttpGet]
        [Route("")]
        public IHttpActionResult GetSettings()
        {
            var settings = new
            {
                Name = "OneRoster Service 1.2 Provider",
                Version = "1.0",
                OneRosterDbStatus = CheckDbConnection(ConfigurationManager.ConnectionStrings["OneRosterDbContext"].ConnectionString),
            };

            return Ok(settings);
        }

        [HttpGet]
        // https://social.msdn.microsoft.com/Forums/en-US/27f1a1e3-19a4-4aa8-b9b9-efa8ae5266d1/webapi-2-route-attribute-with-string-parameter-containing-a-period-doesnt-bind?forum=aspwebapi
        [Route(Consts.WEBAPI_ROUTE_PREFIX + "/discovery/onerosterv1p2rostersservice_openapi3_v1p0.json")]
        public IHttpActionResult GetServiceDiscoveryFile()
        {
            // https://www.sensibledev.com/how-to-get-the-base-url-in-asp-net/
            var request = HttpContext.Current.Request;
            var appRootFolder = request.ApplicationPath;

            if (!appRootFolder.EndsWith("/"))
            {
                appRootFolder += "/";
            }

            var baseUrl =  string.Format(
                "{0}://{1}{2}",
                request.Url.Scheme,
                request.Url.Authority,
                appRootFolder
            );

            var swaggerDocUrl = baseUrl + "/swagger/docs/v1";

            return Redirect(swaggerDocUrl);
        }

        private dynamic CheckDbConnection(string connStr)
        {
            using (var db = new DbContext(connStr))
            {
                var dbConnected = false;
                try
                {
                    db.Database.Connection.Open();
                    db.Database.Connection.Close();
                    dbConnected = true;
                }
                catch (SqlException)
                {
                }
                return new
                {
                    DataSource = db.Database.Connection.DataSource,
                    DbName = db.Database.Connection.Database,
                    DbConnected = dbConnected,
                };
            }
        }        
    }
}
