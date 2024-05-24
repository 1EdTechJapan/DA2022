using EduKoumu.OneRosterService.Exceptions;
using log4net;
using System;
using System.Linq;
using System.Reflection;
using System.Security.Claims;
using System.Web;
using System.Web.Http;
using System.Web.Http.Controllers;

namespace EduKoumu.OneRosterService.Auth
{
    /// <summary>
    /// WebAPI用独自認可属性
    /// </summary>
    [AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, Inherited = true, AllowMultiple = true)]
    public class WebApiAuthorizeAttribute : AuthorizeAttribute
    {
        public string Scope { get; set; }

        /// <summary>
        /// Logger
        /// </summary>
        private static readonly ILog logger = LogManager.GetLogger(MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// 認可チェック
        /// </summary>
        /// <param name="actionContext">コンテキスト</param>
        /// <returns>チェック結果</returns>
        protected override bool IsAuthorized(HttpActionContext actionContext)
        {
            if (actionContext == null)
            {
                logger.Error("Authorization fail: 入力パラメータの必須項目[コンテキスト]がNULL");                
                return false;
            }

            // 認証チェック
            if (!actionContext.RequestContext.Principal.Identity.IsAuthenticated)
            {
                // 認証されていない場合、認可エラー
                logger.Warn($"Authorization fail: 認証されていないユーザーから[{HttpContext.Current.Request.Path}]にアクセスがありました。");
                return false;
            }           

            var userIdentity = (ClaimsIdentity)actionContext.RequestContext.Principal.Identity;
            var claim = userIdentity.Claims
               .Where(c => c.Type == "scope")
               .SingleOrDefault();

            if (claim == null)
            {
                throw new ForbiddenException("Scope not found!");
            }

            var claimScopes = claim.Value.Split(' ');
            var allowedScopes = this.Scope.Split(' ');
            var notAllowedScopes = allowedScopes.Intersect(claimScopes);

            if (!allowedScopes.Intersect(claimScopes).Any())
            {
                throw new ForbiddenException($"Allowed scopes: '{string.Join(",", allowedScopes)}' not found!");
            }

            return true;
        }

        /// <summary>
        /// 認可失敗時のハンドリング
        /// </summary>
        /// <param name="actionContext">コンテキスト</param>
        protected override void HandleUnauthorizedRequest(HttpActionContext actionContext)
        {
            if (actionContext.RequestContext.Principal.Identity.IsAuthenticated)
            {
                // 認可エラー（レスポンスに、HTTPステータスコード：403を設定）
                throw new ForbiddenException("Access Forbidden");  
            }
            else
            {
                // 認証エラー
                // カスタマイズンなし（レスポンスに、HTTPステータスコード：401を設定）
                throw new UnauthorisedException("Unauthorized");
            }
        }
    }
}