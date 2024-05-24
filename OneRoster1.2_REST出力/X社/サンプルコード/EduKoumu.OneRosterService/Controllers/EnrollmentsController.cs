using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Functions;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class EnrollmentsController : ApiController
    {
        private readonly IEnrollmentFunction enrollmentFunction;

        public EnrollmentsController()
        {
            this.enrollmentFunction = new EnrollmentFunction();
        }

        /// <summary>
        /// getAllEnrollments() API 呼び出し用の REST 読み取りリクエスト メッセージです。
        /// </summary>
        /// <remarks>
        /// すべての所属情報を含む、所属情報のコレクションを読み取るために使用します。
        /// </remarks>
        /// <param name="limit">レスポンスに含まれるレコードの最大数であるダウンロード分割値を定義します。</param>
        /// <param name="offset">セグメント化されたレスポンスメッセージで供給される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用する並べ替え基準を識別します。orderBy パラメーターと共に使用します。ソート順序は [UNICODE, 16] 標準に従う必要があります。</param>
        /// <param name="orderBy">ソートリクエストのレスポンスの並べ替えの形式、すなわち昇順 (asc) または降順 (desc) を指定します。ソート順序は [UNICODE, 16] 標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用されるフィルターのルールです。ソート順序は [UNICODE, 16] 標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストは正常に完了し、コレクションが返されました。これには、'codeMajor/severity' 値の 'success/status' と、REST バインディングに対する HTTP コードの '200' が伴います。</returns>
        [Route("enrollments")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllEnrollments(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var enrollments = await this.enrollmentFunction.GetAllEnrollments(limit, offset, sort, orderBy, filter, fields);
            return Ok(enrollments);
        }

        /// <summary>
        /// 「getEnrollment()」API呼び出しのREST読み取りリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 特定の所属情報を取得するための読み取り、取得リクエストです。サービスプロバイダー内で指定された所属情報を特定できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">この登録の一意の識別子、GUID。</param>
        /// <param name="fields">応答メッセージに含めるフィールドの範囲を識別するためのパラメーター。</param>
        /// <returns>リクエストが正常に完了し、レコードが返された場合、「success/status」の「codeMajor/severity」値が伴い、RESTバインディングのHTTPコード「200」となります。</returns>
        [Route("enrollments/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetEnrollment(string sourcedId, string fields = null)
        {
            var enrollment = await this.enrollmentFunction.GetEnrollment(sourcedId, fields);
            return Ok(enrollment);
        }
    }
}
