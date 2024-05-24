using EduKoumu.OneRosterService.Configurations;
using log4net;
using Microsoft.Owin.Security;
using Microsoft.Owin.Security.OAuth;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Reflection;
using System.Security.Claims;
using System.Threading.Tasks;
using System.Web;

namespace EduKoumu.OneRosterService.Auth
{
    public class OAuthProvider : OAuthAuthorizationServerProvider
    {
        /// <summary>
        /// Logger
        /// </summary>
        private static readonly ILog logger = LogManager.GetLogger(MethodBase.GetCurrentMethod().DeclaringType);

        public override Task ValidateClientAuthentication(OAuthValidateClientAuthenticationContext context)
        {
            string clientId;
            string clientSecret;

            if (!context.TryGetBasicCredentials(out clientId, out clientSecret) &&
                !context.TryGetFormCredentials(out clientId, out clientSecret))
            {
                // The client credentials could not be retrieved.

                var errorMessage = "Client credentials could not be retrieved. ";
                logger.Error(errorMessage + $"(from {context.Request.RemoteIpAddress})");

                context.SetCustomError("invalid_client", "Client credentials could not be retrieved.");
                context.Rejected();
                return Task.CompletedTask;
            }

            var clientsConfig = ConfigurationManager.GetSection("clientsConfig") as ClientsConfigSection;

            var clientSetting = clientsConfig.ClientSettings[clientId];
            if (clientSetting == null)
            {
                var errorMessage = "Client Id not found.";
                logger.Error(errorMessage + $"(from {context.Request.RemoteIpAddress})");

                context.SetCustomError("invalid_client", errorMessage);
                context.Rejected();
                return Task.CompletedTask;
            }
            if (clientSetting.Secret != clientSecret)
            {
                // Client could not be validated.
                var errorMessage = "Client credentials are invalid.";
                logger.Error(errorMessage + $"(from {context.Request.RemoteIpAddress})");

                context.SetCustomError("invalid_client", errorMessage);
                context.Rejected();
                return Task.CompletedTask;
            }

            var scope = context.Parameters["scope"]?.ToString();
            if(string.IsNullOrWhiteSpace(scope))
            {
                var errorMessage = "Scope required!";
                logger.Error(errorMessage + $"(from {context.Request.RemoteIpAddress})");

                context.SetCustomError("invalid_client", errorMessage);
                context.Rejected();
                return Task.CompletedTask;
            }

            scope = HttpUtility.UrlDecode(scope);

            var requestScopes = scope.Split(' ').ToList();
            var allowedScopes = clientSetting.Scope.Split(' ').ToList();
            var validScopes = requestScopes.Intersect(allowedScopes).ToList();
            if (!validScopes.Any())
            {
                var errorMessage = $"Scopes: no valid scopes found in request!";
                logger.Error(errorMessage + $"(from {context.Request.RemoteIpAddress})");

                context.SetCustomError("invalid_client", errorMessage);
                context.Rejected();
                return Task.CompletedTask;
            }

            // Client has been verified.
            context.OwinContext.Set("oauth:scope", string.Join(" ", validScopes));
            logger.Info($"client id '{clientId}' with scope '{string.Join(" ", validScopes)}' verified. (from {context.Request.RemoteIpAddress})");

            context.Validated(clientId);
            return Task.CompletedTask;
        }

        public override Task GrantClientCredentials(OAuthGrantClientCredentialsContext context)
        {            
            var scope = context.OwinContext.Get<string>("oauth:scope");

            var identity = new ClaimsIdentity(context.Options.AuthenticationType);
            identity.AddClaim(new Claim("scope", scope));

            var properties = new Dictionary<string, string>
            {
                {"scope", scope},
            };
            var ticket = new AuthenticationTicket(identity, new AuthenticationProperties(properties));
            context.Validated(ticket);
            return Task.CompletedTask;
        }

        public override Task TokenEndpoint(OAuthTokenEndpointContext context)
        {
            foreach (var property in context.Properties.Dictionary)
            {
                if (!property.Key.StartsWith(".")) // ".expires" ".issue" will not returned
                {
                    context.AdditionalResponseParameters.Add(property.Key, property.Value);
                }
            }

            return Task.CompletedTask;
        }
    }
}