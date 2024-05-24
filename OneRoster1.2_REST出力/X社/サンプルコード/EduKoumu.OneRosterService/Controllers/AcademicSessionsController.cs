using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Functions;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class AcademicSessionsController : ApiController
    {
        private readonly IAcademicSessionFunction academicSessionFunction;

        public AcademicSessionsController()
        {
            this.academicSessionFunction = new AcademicSessionFunction();
        }

        /// <summary>
        /// getAllAcademicSessions() API呼び出しのためのRESTリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 全ての年度、学期のコレクションを読み取るためのものです。
        /// </remarks>
        /// <param name="limit">レスポンスに含める最大レコード数を定義するダウンロード分割値。</param>
        /// <param name="offset">セグメント化された応答メッセージで供給される最初のレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータと共に使用します。ソート順序は[UNICODE, 16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求への応答の順序形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE, 16]規格に従う必要があります。</param>
        /// <param name="filter">応答メッセージで提供されるレコードを識別するときに適用するフィルタリングルール。ソート順序は[UNICODE, 16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供すべきフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストは正常に完了し、コレクションが返されました。これには、コードメジャー/重大度の値が「success/status」、およびRESTバインディングのHTTPコード「200」が伴います。</returns>
        [Route("academicSessions")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllAcademicSessions(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var academicSessions = await this.academicSessionFunction.GetAllAcademicSessions(limit, offset, sort, orderBy, filter, fields);
            return Ok(academicSessions);
        }

        /// <summary>
        /// getAcademicSession() API呼び出し用のRESTリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 特定の年度、学期を読み取り、取得します。指定された年度、学期がサービスプロバイダ内で特定できない場合は、「unknownobject」のステータスコードが報告される必要があります。
        /// </remarks>
        /// <param name="sourcedId">この学期の一意の識別子、GUID。</param>
        /// <param name="fields">レスポンスメッセージに含める必要があるフィールドの範囲を識別します。</param>
        /// <returns>要求が正常に完了し、レコードが返された場合。これには、 'codeMajor / severity'値が'success / status'およびRESTバインディングのHTTPコードが '200'が伴います。</returns>
        [Route("academicSessions/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAcademicSession(string sourcedId, string fields = null)
        {
            var academicSession = await this.academicSessionFunction.GetAcademicSession(sourcedId, fields);
            return Ok(academicSession);
        }
    }
}
