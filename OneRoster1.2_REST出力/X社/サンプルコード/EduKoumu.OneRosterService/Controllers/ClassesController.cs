using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.Functions;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class ClassesController : ApiController
    {
        private readonly IClassFunction classFunction;

        public ClassesController()
        {
            this.classFunction = new ClassFunction();
        }

        /// <summary>
        /// getAllClasses() APIコールのREST読み取りリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 全てのクラスのコレクションを読み取るために使用します。
        /// </remarks>
        /// <param name="limit">レスポンスメッセージに含まれる最大レコード数を定義するために使用されます。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで提供される最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータとともに使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対する応答の順序を指定するために使用されます。昇順（asc）または降順（desc）を指定します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別するときに適用されるフィルタリングルールです。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストは正常に完了し、コレクションが返されました。これには、 'codeMajor/severity'値が 'success/status' となり、RESTバインディングのHTTPコードが '200' が伴います。</returns>
        [Route("classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllClasses(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var classes = await this.classFunction.GetAllClasses(limit, offset, sort, orderBy, filter, fields);
            return Ok(classes);
        }

        /// <summary>
        /// getClass() APIコールのREST読み取りリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 特定のクラスを読み取るために使用します。サービスプロバイダ内で指定されたクラスを識別できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">このクラスの一意の識別子、GUIDです。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストは正常に完了し、レコードが返されました。これには、 'codeMajor/severity'値が 'success/status' となり、RESTバインディングのHTTPコードが '200' が伴います。</returns>
        [Route("classes/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetClass(string sourcedId, string fields = null)
        {
            var @class = await this.classFunction.GetClass(sourcedId, fields);
            return Ok(@class);
        }

        /// <summary>
        /// getStudentsForClass() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定のクラスに関連付けられた児童生徒のコレクションを読み取るために使用します。指定されたクラスがサービスプロバイダー内で識別できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="classSourcedId">クラスの一意の識別子、GUID。</param>
        /// <param name="limit">応答に含まれるレコードの最大数を定義するダウンロードセグメンテーション値。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで提供される最初のレコードの番号。</param>
        /// <param name="sort">応答メッセージのレコードに使用されるソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対する応答の並べ替えの形式、すなわち昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別するときに適用するフィルタリングルールです。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供する必要があるフィールドの範囲を識別します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、これには'success/status'の 'codeMajor / severity'値が伴い、RESTバインディングの場合はHTTPコードが'200'になります。</returns>
        [Route("classes/{classSourcedId}/students")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetStudentsForClass(string classSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getTeachersForClass() API呼び出しのためのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定のクラスに関連付けられた教職員のコレクションを取得します。指定されたクラスがサービスプロバイダ内で特定できない場合は、「unknownobject」というステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="classSourcedId">クラスの一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数、すなわちダウンロードセグメンテーション値を定義するために使用します。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで供給される最初のレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用されるソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートリクエストに対する応答の並べ替え形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを特定するときに適用するフィルタリングルールです。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するために使用します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返されました。これには、「codeMajor/severity」値が「success/status」となり、RESTバインディングに対するHTTPコードが「200」となります。</returns>
        [Route("classes/{classSourcedId}/teachers")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetTeachersForClass(string classSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }
    }
}
