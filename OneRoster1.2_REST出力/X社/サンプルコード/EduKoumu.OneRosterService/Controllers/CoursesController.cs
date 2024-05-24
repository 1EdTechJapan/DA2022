using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Functions;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class CoursesController : ApiController
    {
        private readonly ICourseFunction courseFunction;

        public CoursesController()
        {
            this.courseFunction = new CourseFunction();
        }

        /// <summary>
        /// getAllCourses() API呼び出しのためのREST読み取り要求メッセージ。
        /// </summary>
        /// <remarks>
        /// 全てのコースのコレクションを取得します。
        /// </remarks>
        /// <param name="limit">レスポンスに含まれる最大レコード数であるダウンロードセグメンテーション値を定義します。</param>
        /// <param name="offset">セグメンテーションされた応答メッセージで提供される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメーターと一緒に使用してください。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求へのレスポンスの順序形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">応答メッセージで提供されるレコードを識別する際に適用されるフィルター規則です。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">応答メッセージに含まれるフィールドの範囲を識別するために使用されます。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合、これには「codeMajor/severity」値が付随し、「success/status」のRESTバインディングの場合、HTTPコードは「200」になります。</returns>
        [Route("courses")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllCourses(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var courses = await this.courseFunction.GetAllCourses(limit, offset, sort, orderBy, filter, fields);
            return Ok(courses);
        }        

        /// <summary>
        /// getCourse() API呼び出しのためのREST読み取り要求メッセージ。
        /// </summary>
        /// <remarks>
        /// 特定のコースを取得します。指定したコースがサービスプロバイダー内で特定できない場合、 'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">このコースの一意の識別子、GUIDです。</param>
        /// <param name="fields">応答メッセージに含まれるフィールドの範囲を識別するために使用されます。</param>
        /// <returns>要求が正常に完了し、レコードが返された場合、これには「codeMajor/severity」値が付随し、「success/status」のRESTバインディングの場合、HTTPコードは「200」になります。</returns>
        [Route("courses/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetCourse(string sourcedId, string fields = null)
        {
            var course = await this.courseFunction.GetCourse(sourcedId, fields);
            return Ok(course);
        }

        /// <summary>
        /// getClassesForCourse() API呼び出しのREST読み取りリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 特定のコースに関連するクラスセットを取得するために使用されます。指定されたコースがサービスプロバイダ内で特定できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="courseSourcedId">特定のコースの一意の識別子であるGUID。</param>
        /// <param name="limit">ダウンロード分割値を定義するために使用され、応答に含まれる最大レコード数を示します。</param>
        /// <param name="offset">セグメント化された応答メッセージで最初に提供されるレコード番号。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用されるソート基準を識別します。orderByパラメータと共に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストへの応答の順序を識別します。つまり、昇順（asc）または降順（desc）です。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用されるフィルタリングルールです。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">応答メッセージで提供するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、これには 'codeMajor / severity' 値が 'success / status' が付属し、RESTバインディングの場合はHTTPコードが '200' が返されます。</returns>
        [Route("courses/{courseSourcedId}/classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetClassesForCourse(string courseSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }
    }
}
