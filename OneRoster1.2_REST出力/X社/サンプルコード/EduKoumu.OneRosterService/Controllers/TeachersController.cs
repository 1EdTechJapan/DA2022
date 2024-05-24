using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.User;
using EduKoumu.OneRosterService.Functions;
using Newtonsoft.Json;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class TeachersController : ApiController
    {
        private readonly IUserFunction userFunction;

        public TeachersController()
        {
            this.userFunction = new UserFunction();
        }

        /// <summary>
        /// getAllTeachers() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 全ての教職員のコレクションを取得するための読み取りリクエストです
        /// </remarks>
        /// <param name="limit">レスポンスに含まれるレコードの最大数を定義するためのパラメータです。</param>
        /// <param name="offset">セグメント化されたレスポンスメッセージで供給される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。orderByパラメータと共に使用します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求に対するレスポンスの並べ替え形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用されるフィルタリングルールです。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するためのパラメータです。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合、これは 'success / status'の 'codeMajor / severity'値に伴い、RESTバインディングのHTTPコード'200'となります。</returns>
        [Route("teachers")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllTeachers(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var users = await this.userFunction.GetAllUsers(limit, offset, sort, orderBy, filter, fields, RoleEnum.teacher);
            return Ok(users);
        }

        /// <summary>
        /// getTeacher() API呼び出しののREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の教職員を取得するために使用します。サービスプロバイダー内で指定された教職員が特定できない場合、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">指定ユーザー(教職員)のユニークな識別子、GUID。</param>
        /// <param name="fields">レスポンスメッセージで供給するフィールドの範囲を識別するためのパラメーター。</param>
        /// <returns>リクエストは正常に完了し、レコードが返されました。これには、'success/status'の'codeMajor/severity'値が伴い、RESTバインディングではHTTPコード'200'が含まれます。</returns>
        [Route("teachers/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetTeacher(string sourcedId, string fields = null)
        {
            var user = await this.userFunction.GetUser(sourcedId, fields, RoleEnum.teacher);
            return Ok(user);
        }

        /// <summary>
        /// getClassesForTeacher() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の教職員に関連するクラスセットを取得するためです。指定された教職員がサービスプロバイダ内で特定できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="teacherSourcedId">特定のユーザー(教職員)のユニークな識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれる最大レコード数を定義するダウンロードセグメンテーション値です。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで供給される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用するソート基準を識別します。orderByパラメータと共に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対するレスポンスの順序形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別するときに適用するフィルタリングルールです。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返されました。これには、「success/status」の「codeMajor/severity」値が伴い、RESTバインディングの場合はHTTPコード「200」が伴います。</returns>
        [Route("teachers/{teacherSourcedId}/classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetClassesForTeacher(string teacherSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

    }
}
