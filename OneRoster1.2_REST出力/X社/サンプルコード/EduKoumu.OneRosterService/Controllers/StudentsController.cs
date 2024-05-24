using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.User;
using EduKoumu.OneRosterService.Functions;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class StudentsController : ApiController
    {
        private readonly IUserFunction userFunction;

        public StudentsController()
        {
            this.userFunction = new UserFunction();
        }

        /// <summary>
        /// getAllStudents() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 全ての児童生徒のコレクションを取得するための読み取りリクエストです。
        /// </remarks>
        /// <param name="limit">応答メッセージに含まれるレコードの最大数、つまりダウンロードセグメンテーション値を定義するためのものです。</param>
        /// <param name="offset">セグメンテーションされた応答メッセージに供給される最初のレコードの番号です。</param>
        /// <param name="sort">応答メッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータと共に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求への応答の並べ替えの形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">応答メッセージで提供されるレコードを識別する際に適用されるフィルタリング規則です。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">応答メッセージに含まれるフィールドの範囲を識別するためのものです。</param>
        /// <returns>要求は正常に完了し、コレクションが返されました。これには、'codeMajor/severity'の値が'success/status'であり、RESTバインディングの場合はHTTPコードが'200'が伴います。</returns>
        [Route("students")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllStudents(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var users = await this.userFunction.GetAllUsers(limit, offset, sort, orderBy, filter, fields, RoleEnum.student);
            return Ok(users);
        }

        /// <summary>
        /// getStudent() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の教職員を取得するために使用します。サービスプロバイダ内で指定された生徒が特定できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">指定のユーザー(児童生徒)の一意の識別子、GUID。</param>
        /// <param name="fields">応答メッセージで提供するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>要求が正常に完了し、レコードが返された場合。これには、'codeMajor/severity'値が 'success/status'と、RESTバインディングの場合はHTTPコードが '200'が付随します。</returns>
        [Route("students/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetStudent(string sourcedId, string fields = null)
        {
            var user = await this.userFunction.GetUser(sourcedId, fields, RoleEnum.student);
            return Ok(user);
        }

        /// <summary>
        /// getClassesForStudent() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の児童生徒に関連するクラスセットを取得するためのものです。 サービスプロバイダー内で指定された児童生徒を特定できない場合、 'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="studentSourcedId">特定のユーザー(児童生徒)の一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数、つまりダウンロード分割値を定義します。</param>
        /// <param name="offset">セグメンテッドレスポンスメッセージで供給される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。 orderByパラメータと一緒に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対するレスポンスの順序形式、つまり昇順（asc）または降順（desc）を指定します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別するときに適用するフィルタリングルールです。 ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供されるフィールドの範囲を識別します。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合、 'codeMajor / severity'値が 'success / status'となり、RESTバインディングのHTTPコードが '200'となります。</returns>
        [Route("students/{studentSourcedId}/classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetClassesForStudent(string studentSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

    }
}
