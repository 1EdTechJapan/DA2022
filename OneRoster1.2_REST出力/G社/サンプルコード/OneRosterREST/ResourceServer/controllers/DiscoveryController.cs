using System.IO;
using System.Net.Http.Headers;
using System.Net.Http;
using System.Web.Http;
using System.Web;

namespace ResourceServer.controllers
{
    /// <summary>
    /// OpenAPIのJSONを返す
    /// </summary>
    [RoutePrefix("ims/oneroster/rostering/v1p2")]
    public class DiscoveryController : ApiController
    {
        //[Authorize]
        [Route("discovery/onerosterv1p2rostersservice_openapi3_v1p0.json")]
        public HttpResponseMessage getDiscovery()
        {
            // OpenAPI ファイルには、「onerosterv1p2rostersservice_openapi3_v1p0.json」という名前が必要です
            string path = HttpContext.Current.Server.MapPath("/assets/onerosterv1p2rostersservice_openapi3_v1p0.json");

            var response = this.Request.CreateResponse();
            response.Content = new StreamContent(new FileStream(path, FileMode.Open, FileAccess.Read));
            response.Content.Headers.ContentType = new MediaTypeHeaderValue("application/json");
            return response;
        }
    }
}
