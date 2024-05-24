using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Functions;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]    
    public class OrgsController : ApiController
    {
        private readonly IOrgFunction orgFunction;

        public OrgsController()
        {
            this.orgFunction = new OrgFunction();
        }

        /// getAllOrgs() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// コレクションの組織団体、つまりすべての組織団体を読み取り、取得します。
        /// </remarks>
        /// <param name="limit">レスポンスメッセージに含まれるレコードの最大数を示す、ダウンロードのセグメンテーション値を定義するためのパラメータです。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで提供される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は、[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートリクエストの応答の並べ替え形式、すなわち昇順（asc）または降順（desc）を識別します。ソート順序は、[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用するフィルタリングルールです。ソート順序は、[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するためのパラメータです。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、これには 'success / status'の 'codeMajor / severity'値が付随し、RESTバインディングではHTTPコード '200'が付与されます。</returns>
        [HttpGet]
        [Route("orgs")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllOrgs(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var orgs = await this.orgFunction.GetAllOrgs(limit, offset, sort, orderBy, filter, fields);
            return Ok(orgs);
        }

        /// <summary>
        /// getOrg() API呼び出しのREST読み取りリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 特定の組織団体を読み取るためのメッセージです。指定された組織団体がサービスプロバイダ内で特定できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">この組織団体のユニーク識別子、GUID。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別します。</param>
        /// <returns>リクエストは正常に完了し、レコードが返されました。これは、「success/status」の 'codeMajor/severity' 値と、RESTバインディングのHTTPコード '200' が伴います。</returns>
        [HttpGet]
        [Route("orgs/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetOrg(string sourcedId, string fields = null)
        {
            var org = await this.orgFunction.GetOrg(sourcedId, fields);
            return Ok(org);
        }

    }
}
