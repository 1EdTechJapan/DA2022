using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Functions;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class UsersController : ApiController
    {
        private readonly IUserFunction userFunction;

        public UsersController()
        {
            this.userFunction = new UserFunction();
        }

        /// <summary>
        /// getAllUsers() API呼び出しのためのRESTリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// ユーザーのコレクション、すなわちすべてのユーザー（児童生徒や教職員などを含む）を取得するための読み取りリクエストです。
        /// </remarks>
        /// <param name="limit">レスポンスに含まれる最大レコード数、ダウンロードのセグメンテーション値を定義します。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで提供される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。orderByパラメーターと一緒に使用します。ソート順序は、[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストへの応答の並べ替え形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は、[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="filter">応答メッセージで提供されるレコードを識別する際に適用されるフィルタリングルールです。ソート順序は、[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供されるフィールド範囲を識別するためのパラメーターです。</param>
        /// <returns>リクエストは正常に完了し、コレクションが返されました。これには、 'codeMajor / severity'値が 'success / status'であり、RESTバインディングの場合はHTTPコードが '200'が伴います。</returns>
        [Route("users")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllUsers(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var users = await this.userFunction.GetAllUsers(limit, offset, sort, orderBy, filter, fields);
            return Ok(users);
        }

        /// <summary>
        /// getUser() API呼び出しのためのREST読み取り要求メッセージです。
        /// </summary>
        /// <remarks>
        /// 特定のユーザーを読み取るためのものです。指定されたユーザーがサービスプロバイダー内で特定できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">このユーザーの一意の識別子、GUID。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するためのものです。</param>
        /// <returns>リクエストが正常に完了し、レコードが返された場合、これは 'codeMajor/severity' 値 'success/status' に伴い、RESTバインディングの場合はHTTPコード '200' が返されます。</returns>
        [Route("users/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetUser(string sourcedId, string fields = null)
        {
            var user = await this.userFunction.GetUser(sourcedId, fields);
            return Ok(user);
        }

        /// <summary>
        /// getClassesForUser() API呼び出しのREST読み取り要求メッセージです。
        /// </summary>
        /// <remarks>
        /// 特定のユーザーに関連するクラスのセットを取得するために使用します。指定されたユーザーがサービスプロバイダー内で特定できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="userSourcedId">特定のユーザーのユニークな識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数であるダウンロードセグメンテーション値を定義します。</param>
        /// <param name="offset">セグメンテーションされた応答メッセージで提供される最初のレコードの番号。</param>
        /// <param name="sort">応答メッセージのレコードに使用するソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストへの応答の並べ替え形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">応答メッセージで提供されるレコードを識別する際に適用するフィルタリングルールです。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">応答メッセージで提供するフィールドの範囲を識別するために使用します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、'codeMajor / severity'値が'success / status'とともに、RESTバインディングのHTTPコードが '200'となります。</returns>
        [Route("users/{userSourcedId}/classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetClassesForUser(string userSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }
    }
}

