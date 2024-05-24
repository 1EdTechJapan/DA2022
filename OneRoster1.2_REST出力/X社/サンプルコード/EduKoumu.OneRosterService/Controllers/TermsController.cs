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
    public class TermsController : ApiController
    {
        private readonly IAcademicSessionFunction academicSessionFunction;

        public TermsController()
        {
            this.academicSessionFunction = new AcademicSessionFunction();
        }

        /// <summary>
        /// getAllTerms() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 学期のコレクション、すなわちすべての学期を取得するための読み取りリクエストです
        /// </remarks>
        /// <param name="limit">レスポンスに含まれる最大レコード数を定義する、ダウンロード分割値です。</param>
        /// <param name="offset">分割されたレスポンスメッセージで供給される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対するレスポンスの並べ替えの形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを特定するときに適用されるフィルタリングルールです。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するためのものです。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、これには 'codeMajor/severity' 値が 'success/status' が付随し、RESTバインディングのHTTPコードが '200' があります。</returns>
        [Route("terms")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllTerms(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var terms = await this.academicSessionFunction.GetAllAcademicSessions(limit, offset, sort, orderBy, filter, fields, SessionTypeEnum.term);
            return Ok(terms);
        }

        /// <summary>
        /// getTerm() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学期を読み取るために使用されます。指定された用語がサービスプロバイダー内で特定できない場合は、 'unknownobject'のステータスコードが報告される必要があります。
        /// </remarks>
        /// <param name="sourcedId">この用語の一意の識別子、GUID。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストが正常に完了し、レコードが返されました。これには、 'codeMajor / severity'値が'success / status'となり、RESTバインディングの場合はHTTPコードが '200'になります。</returns>
        [Route("terms/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetTerm(string sourcedId, string fields = null)
        {
            var term = await this.academicSessionFunction.GetAcademicSession(sourcedId, fields, SessionTypeEnum.term);
            return Ok(term);
        }

        /// <summary>
        /// getClassesForTerm() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の期間に関連するクラスのセットを取得するためのものです。指定された期間がサービスプロバイダ内で特定できない場合は、 'unknownobject' のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="termSourcedId">特定の期間の一意の識別子、GUID。</param>
        /// <param name="limit">応答メッセージに含まれるレコードの最大数を定義するダウンロードセグメンテーション値。</param>
        /// <param name="offset">セグメンテーションされた応答メッセージで最初に供給されるレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。orderByパラメータと共に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求に対するレスポンスの並べ替え形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供するレコードを識別するときに適用するフィルタリングルール。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用します。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合、これには 'codeMajor / severity' 値が 'success / status' と、RESTバインディングのHTTPコードが '200' が付属します。</returns>
        [Route("terms/{termSourcedId}/classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetClassesForTerm(string termSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getGradingPeriodsForTerm() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学期に関連する成績評価期間を取得するために使用します。サービスプロバイダ内で指定された学期を特定できない場合、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="termSourcedId">特定の学期の一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれる最大レコード数、ダウンロードセグメンテーション値を定義します。</param>
        /// <param name="offset">セグメント化されたレスポンスメッセージで最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。orderByパラメータと併用して使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対するレスポンスの並べ替え形式、昇順（asc）または降順（desc）です。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用するフィルタリングルールです。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するべきフィールドの範囲を識別します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、'success/status'の 'codeMajor / severity' 値が付属し、RESTバインディングの場合はHTTPコードが'200'です。</returns>
        [Route("terms/{termSourcedId}/gradingPeriods")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetGradingPeriodsForTerm(string termSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

    }
}
