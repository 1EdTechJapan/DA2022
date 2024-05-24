using EduKoumu.OneRosterService.Auth;
using Microsoft.Owin;
using Microsoft.Owin.Security.OAuth;
using Owin;
using System;

[assembly: OwinStartupAttribute(typeof(EduKoumu.OneRosterService.Startup))]
namespace EduKoumu.OneRosterService
{ 
    public class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            app.UseCors(Microsoft.Owin.Cors.CorsOptions.AllowAll);

            var options = new OAuthAuthorizationServerOptions
            {
                AllowInsecureHttp = false,
                TokenEndpointPath = new PathString("/token"),
                AccessTokenExpireTimeSpan = TimeSpan.FromSeconds(Consts.DEFAULT_TOKEN_EXPIRED_TIME),
                Provider = new OAuthProvider(),                
            };
            app.UseOAuthAuthorizationServer(options);
            app.UseOAuthBearerAuthentication(new OAuthBearerAuthenticationOptions());
        }
    }
}