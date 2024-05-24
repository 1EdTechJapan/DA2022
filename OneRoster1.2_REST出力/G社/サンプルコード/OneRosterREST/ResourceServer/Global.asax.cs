using System;
using System.Web.Http;

namespace ResourceServer
{
    // クラスの追加→グローバルアプリケーションクラス
    // 今回はApplication_Startだけあればいい
    public class Global : System.Web.HttpApplication
    {
        // データベース接続文字
        public static readonly string mongodbConnection = "mongodb://localhost:27017";
        public static readonly string mongodbDatabase = "oneroster";

        protected void Application_Start(object sender, EventArgs e)
        {
            // Microsoft.AspNet.WebApi.WebHostをnugetから追加すること
            GlobalConfiguration.Configure(WebApiConfig.Register);
        }
    }

    public static class WebApiConfig
    {
        public static void Register(HttpConfiguration config)
        {
            // Web API configuration and services
            config.Formatters.Remove(config.Formatters.XmlFormatter);
            config.Formatters.Add(config.Formatters.JsonFormatter);

            // Web API routes
            config.MapHttpAttributeRoutes();

            // The API Root URL MUST be /ims/oneroster.
            config.Routes.MapHttpRoute(
                name: "DefaultApi",
                routeTemplate: "ims/oneroster/rostering/v1p2/{controller}/{id}",
                defaults: new { id = RouteParameter.Optional }
            );
        }
    }
}