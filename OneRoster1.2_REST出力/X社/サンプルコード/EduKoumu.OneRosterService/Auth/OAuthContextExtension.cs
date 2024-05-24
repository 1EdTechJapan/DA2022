using Microsoft.Owin.Security.OAuth;
using Newtonsoft.Json;
using System.IO;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Auth
{
    public static class OAuthContextExtension
    {
        public static void SetCustomError(this OAuthValidateClientAuthenticationContext context, string error, string errorMessage)
        {
            var json = new ResponseMessage
            { error = error, description = errorMessage }.ToJsonString();
            context.SetError(json);
            context.Response.Write(json);
            Invoke(context);
        }

        public static string ToJsonString(this object obj)
        {
            return JsonConvert.SerializeObject(obj);
        }

        static async Task Invoke(OAuthValidateClientAuthenticationContext context)
        {
            var owinResponseStream = new MemoryStream();
            var customResponseBody = new System.Net.Http.StringContent(JsonConvert.SerializeObject(new ResponseMessage()));
            var customResponseStream = await customResponseBody.ReadAsStreamAsync();
            await customResponseStream.CopyToAsync(owinResponseStream);
            context.Response.ContentType = "application/json";
            context.Response.ContentLength = customResponseStream.Length;
            context.Response.Body = owinResponseStream;
        }
    }

    public class ResponseMessage
    {
        public string error { get; set; }

        public string description { get; set; }
    }
}