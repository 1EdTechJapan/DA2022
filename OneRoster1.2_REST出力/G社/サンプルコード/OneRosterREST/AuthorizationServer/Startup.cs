using System;
using System.Linq;
using System.Security.Claims;
using System.Security.Principal;
using System.Threading.Tasks;
using Microsoft.Owin;
using Microsoft.Owin.Security.OAuth;
using Owin;

[assembly: OwinStartup(typeof(AuthorizationServer.Startup))]

namespace AuthorizationServer
{
    public class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            // ここで初期設定
            ConfigureAuth(app);
        }

        public void ConfigureAuth(IAppBuilder app)
        {
            // Setup Authorization Server
            var option = new OAuthAuthorizationServerOptions
            {
                // アクセストークンエンドポイントの設定
                TokenEndpointPath = new PathString("/OAuth/Token"),

                // HTTPを許可する（リリース時はHTTPSにしないといけないですが、デバックのときはこうしておきましょう）
                AllowInsecureHttp = true,

                // イベントコールバックメソッドの設定
                Provider = new OAuthAuthorizationServerProvider
                {
                    // ClientIdとClientSecretの検証
                    OnValidateClientAuthentication = ValidateClientAuthentication,
                    // ClientCredetailsのときの処理
                    OnGrantClientCredentials = GrantClientCredetails
                },
                // AccessTokenExpireTimeSpanはデフォルトで20:00
            };
            app.UseOAuthAuthorizationServer(option);
        }

        private Task ValidateClientAuthentication(OAuthValidateClientAuthenticationContext context)
        {
            string clientId;
            string clientSecret;

            context.TryGetBasicCredentials(out clientId, out clientSecret);

            // ClientIDとClientSecretをヘッダまたはフォームからGetする
            if (context.TryGetBasicCredentials(out clientId, out clientSecret) ||
                context.TryGetFormCredentials(out clientId, out clientSecret))
            {
                if (clientId == "123456" && clientSecret == "abcdef")
                {
                    // Client1のとき->OK
                    context.Validated();
                }
                /*
                else if (clientId == Clients.Client2.Id && clientSecret == Clients.Client2.Secret)
                {
                    // Client2のとき->OK
                    context.Validated();
                }
                */
                context.Validated();
            }
            return Task.FromResult(0);
        }

        private Task GrantClientCredetails(OAuthGrantClientCredentialsContext context)
        {
            // identityを生成
            var identity = new ClaimsIdentity(new GenericIdentity(context.ClientId, OAuthDefaults.AuthenticationType), context.Scope.Select(x => new Claim("urn:oauth:scope", x)));
            context.Validated(identity);

            return Task.FromResult(0);
        }
    }
}
