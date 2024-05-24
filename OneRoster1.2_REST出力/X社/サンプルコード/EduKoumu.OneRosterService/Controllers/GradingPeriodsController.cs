using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.AcademicSession;
using EduKoumu.OneRosterService.Functions;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class GradingPeriodsController : ApiController
    {
        private readonly IAcademicSessionFunction academicSessionFunction;

        public GradingPeriodsController()
        {
            this.academicSessionFunction = new AcademicSessionFunction();
        }

        /// <summary>
        /// getAllGradingPeriods() API呼び出しのREST読み取り要求メッセージ。
        /// </summary>
        /// <remarks>
        /// コレクションの成績期間、例えばすべての成績期間(学期)を取得するために使用します。
        /// </remarks>
        /// <param name="limit">レスポンスに含める最大レコード数を定義するダウンロード分割値です。</param>
        /// <param name="offset">分割されたレスポンスメッセージに含まれる最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求への応答の順序形式、つまり昇順（asc）または降順（desc）を示します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージに含めるレコードを特定するときに適用するフィルタールールです。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージに含めるフィールドの範囲を識別します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返されました。これには、「success/status」の 'codeMajor/severity' 値が付属し、RESTバインディングの場合はHTTPコード「200」が伴います。</returns>
        [Route("gradingPeriods")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllGradingPeriods(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var gradingPeriods = await this.academicSessionFunction.GetAllAcademicSessions(limit, offset, sort, orderBy, filter, fields, SessionTypeEnum.gradingPeriod);
            return Ok(gradingPeriods);
        }

        /// <summary>
        /// getGradingPeriod() API呼び出しのREST読み取り要求メッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の成績期間を読み取るためのものです。指定された成績期間がサービスプロバイダ内で識別できない場合、"unknownobject"というステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">この成績期間のユニーク識別子、GUID。</param>
        /// <param name="fields">応答メッセージに含めるべきフィールド範囲を識別します。</param>
        /// <returns>要求が正常に完了し、レコードが返された場合、これには"success/status"の 'codeMajor/severity' 値が伴い、RESTバインディングにはHTTPコード'200'が伴います。</returns>
        [Route("gradingPeriods/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetGradingPeriod(string sourcedId, string fields = null)
        {
            var gradingPeriod = await this.academicSessionFunction.GetAcademicSession(sourcedId, fields, SessionTypeEnum.gradingPeriod);
            return Ok(gradingPeriod);
        }
    }
}
