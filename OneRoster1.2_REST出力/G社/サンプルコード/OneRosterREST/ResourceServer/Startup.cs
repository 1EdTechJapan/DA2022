using System;
using System.Threading.Tasks;
using System.Web.Http;
using Microsoft.Owin;
using Owin;

[assembly: OwinStartup(typeof(ResourceServer.Startup))]

namespace ResourceServer
{
    // クラスの追加→OWIN Startupクラス
    public class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            app.UseOAuthBearerAuthentication(new Microsoft.Owin.Security.OAuth.OAuthBearerAuthenticationOptions());
        }
    }
}
