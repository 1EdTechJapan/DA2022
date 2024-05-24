using EduKoumu.OneRosterService.Auth;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Org;
using EduKoumu.OneRosterService.Functions;
using System;
using System.Threading.Tasks;
using System.Web.Http;

namespace EduKoumu.OneRosterService.Controllers
{
    [RoutePrefix(Consts.WEBAPI_ROUTE_PREFIX)]
    public class SchoolsController : ApiController
    {
        private readonly IOrgFunction orgFunction;

        public SchoolsController()
        {
            this.orgFunction = new OrgFunction();
        }

        /// <summary>
        /// getAllSchools() API呼び出しのためのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 全ての学校のコレクションを取得するための読み取りリクエストです。
        /// </remarks>
        /// <param name="limit">レスポンスに含まれる最大レコード数であるダウンロードの分割値を定義するために使用します。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで供給される最初のレコード番号です。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用するソート基準を識別します。orderByパラメーターと一緒に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストへのレスポンスの並べ替え形式を識別します。昇順（asc）または降順（desc）のいずれかを使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用するフィルタリングルールです。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールド範囲を識別するために使用します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、それには'success / status'の'codeMajor / severity'値が付随し、RESTバインディングのHTTPコードが'200'になります。</returns>
        [Route("schools")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetAllSchools(int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            var orgs = await this.orgFunction.GetAllOrgs(limit, offset, sort, orderBy, filter, fields, OrgTypeEnum.school);
            return Ok(orgs);
        }

        /// <summary>
        /// getSchool() API呼び出しのためのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校を取得するための読み取りリクエストです。指定された学校がサービスプロバイダー内で特定できない場合、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="sourcedId">この学校の一意の識別子であるGUID。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールド範囲を識別するために使用します。</param>
        /// <returns>The request was successfully completed and a record has been returned. This would be accompanied by the 'codeMajor/severity' values of 'success/status' and for a REST binding a HTTP code of '200'.</returns>
        [Route("schools/{sourcedId}")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_CORE_READONLY + " " + Consts.SCOPE_ROSTER_READONLY)]
        public async Task<IHttpActionResult> GetSchool(string sourcedId, string fields = null)
        {
            var org = await this.orgFunction.GetOrg(sourcedId, fields, OrgTypeEnum.school);
            return Ok(org);
        }

        /// <summary>
        /// getClassesForSchool() API呼び出しのためのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校に関連するクラスのコレクションを取得するための読み取りリクエストです。指定された学校がサービスプロバイダー内で特定できない場合、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子であるGUID。</param>
        /// <param name="limit">ダウンロード分割値、つまり、応答に含まれるレコードの最大数を定義するために使用します。</param>
        /// <param name="offset">分割された応答メッセージで提供される最初のレコードの番号。</param>
        /// <param name="sort">応答メッセージのレコードに使用するソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求への応答の並べ替えの形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供するレコードを識別する際に適用するフィルタリングルールです。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールド範囲を識別するために使用します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、これには 'success/status'の 'codeMajor/severity' 値が伴い、RESTバインディングのHTTPコードは '200'になります。</returns>
        [Route("schools/{schoolSourcedId}/classes")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetClassesForSchool(string schoolSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getEnrollmentsForClassInSchool() API呼び出しのREST読み取り要求メッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校の特定のクラスに関連付けられた受講者のコレクションを読み取ります。サービスプロバイダー内で指定された学校と/またはクラスが特定できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">学校の一意の識別子（GUID）。</param>
        /// <param name="classSourcedId">クラスの一意の識別子（GUID）。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数であるダウンロード分割値を定義します。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで供給される最初のレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用するソート基準を識別します。orderByパラメーターと共に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストのレスポンスの順序を示すフォーム、すなわち昇順（asc）または降順（desc）。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用されるフィルタリングルール。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別します。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合、'codeMajor / severity'値が'success / status'となり、RESTバインディングのHTTPコードが'200'となります。</returns>
        [Route("schools/{schoolSourcedId}/classes/{classSourcedId}/enrollments")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetEnrollmentsForClassInSchool(string schoolSourcedId, string classSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getStudentsForClassInSchool() API呼び出しのためのREST読み取りリクエストメッセージ。
        /// </summary>
        /// <remarks>
        /// 特定の学校の特定のクラスに関連する生徒のコレクションを取得するための読み取りリクエストメッセージです。指定された学校と/またはクラスがサービスプロバイダ内で特定できない場合は、 'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子、GUID。</param>
        /// <param name="classSourcedId">クラスの一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数、ダウンロードセグメンテーション値を定義するためのパラメータです。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで提供される最初のレコード番号です。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用されるソート基準を識別します。orderByパラメータとともに使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストのレスポンスの並べ替え形式、つまり昇順（asc）または降順（desc）です。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを識別する際に適用されるフィルタリングルールです。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別するためのパラメータです。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合。これは 'codeMajor/severity'値が'success/status'となり、RESTバインディングのHTTPコードが '200'となります。</returns>
        [Route("schools/{schoolSourcedId}/classes/{classSourcedId}/students")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetStudentsForClassInSchool(string schoolSourcedId, string classSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// 「getTeachersForClassInSchool()」API呼び出しのRESTリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校で特定のクラスに関連する教師のコレクションを取得します。指定された学校と/またはクラスがサービスプロバイダー内で特定できない場合、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子、GUID。</param>
        /// <param name="classSourcedId">クラスの一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数であるダウンロードセグメンテーション値を定義します。</param>
        /// <param name="offset">セグメント化されたレスポンスメッセージで提供される最初のレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。orderByパラメータと併用します。ソート順序は、[UNICODE, 16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求に対するレスポンスの順序形式、つまり昇順（asc）または降順（desc）。ソート順序は、[UNICODE, 16]規格に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供されるレコードを特定するときに適用するフィルタリングルール。ソート順序は、[UNICODE, 16]規格に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するべきフィールドの範囲を識別します。</param>
        /// <returns>要求が正常に完了し、コレクションが返されました。これには、'success/status'の 'codeMajor / severity'値が伴い、RESTバインディングの場合はHTTPコード'200'が付属します。</returns>
        [Route("schools/{schoolSourcedId}/classes/{classSourcedId}/teachers")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetTeachersForClassInSchool(string schoolSourcedId, string classSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getCoursesForSchool() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校に関連するコースのコレクションを読み取るためのものです。サービスプロバイダー内で指定された学校が特定できない場合は、'unknownobject'のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">学校のユニーク識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数を定義する、ダウンロード分割値を指定します。</param>
        /// <param name="offset">セグメンテーションされた応答メッセージで提供される最初のレコードの番号。</param>
        /// <param name="sort">応答メッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータとともに使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされた要求に対する応答の並べ替え形式、すなわち昇順（asc）または降順（desc）を指定します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">応答メッセージで提供するレコードを識別する際に適用するフィルタリング規則。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">応答メッセージで提供する範囲を識別するために使用します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返されました。これには、'success/status'の'codeMajor/severity'値と、RESTバインディングの場合はHTTPコード '200'が伴います。</returns>
        [Route("schools/{schoolSourcedId}/courses")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetCoursesForSchool(string schoolSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getEnrollmentsForSchool() API呼び出しのREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校に関連する所属情報のコレクションを取得します。指定された学校がサービスプロバイダ内で特定できない場合、'unknownobject'ステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数である、ダウンロードのセグメンテーション値を定義するために使用されます。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで供給される最初のレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用されるソート基準を識別します。orderByパラメータと一緒に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対するレスポンスの並べ替えの形式、すなわち昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで供給するレコードを識別するときに適用するフィルタリングルール。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで供給するフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストは正常に完了し、コレクションが返されました。これには、 'codeMajor / severity'の値が'success / status'となり、RESTバインディングに対してHTTPコード'200'が伴います。</returns>
        [Route("schools/{schoolSourcedId}/enrollments")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetEnrollmentsForSchool(string schoolSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getStudentsForSchool() APIコール用のREST読み取りリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校に関連付けられた児童生徒のコレクションを読み取るために使用します。サービスプロバイダ内で指定された学校を特定できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子、GUIDです。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数を定義するダウンロードセグメンテーション値です。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージに含まれる最初のレコードの番号です。</param>
        /// <param name="sort">レスポンスメッセージ内のレコードに使用するソート基準を識別します。orderByパラメータと共に使用します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストへの応答の順序形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">応答メッセージに提供するレコードを識別するときに適用するフィルタリングルールです。ソート順序は[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">応答メッセージに含めるべきフィールドの範囲を識別するために使用されます。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合、これには「success/status」の「codeMajor/severity」値が伴い、RESTバインディングのHTTPコードは「200」となります。</returns>
        [Route("schools/{schoolSourcedId}/students")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetStudentsForSchool(string schoolSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// getTeachersForSchool() API呼び出しのREST読み取り要求メッセージ。
        /// </summary>
        /// <remarks>
        /// 特定の学校に関連付けられた教職員のコレクションを取得します。指定された学校がサービスプロバイダー内で特定できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子、GUID。</param>
        /// <param name="limit">レスポンスに含まれる最大レコード数を定義するダウンロードセグメンテーション値。</param>
        /// <param name="offset">セグメンテーションされた応答メッセージに供給される最初のレコードの番号。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用するソート基準を識別します。orderByパラメーターと一緒に使用します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対する応答の並べ替え形式、つまり昇順（asc）または降順（desc）を識別します。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージに提供するレコードを識別するときに適用するフィルタールール。ソート順序は[UNICODE、16]規格に従う必要があります。</param>
        /// <param name="fields">応答メッセージに提供するフィールドの範囲を識別します。</param>
        /// <returns>要求が正常に完了し、コレクションが返された場合、これには「codeMajor/severity」値が「success/status」およびRESTバインディングのHTTPコードが「200」が伴います。</returns>
        [Route("schools/{schoolSourcedId}/teachers")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetTeachersForSchool(string schoolSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }

        /// <summary>
        /// 「getTermsForSchool()」API呼び出しのRESTリクエストメッセージです。
        /// </summary>
        /// <remarks>
        /// 特定の学校に関連付けられた学期のコレクションを読み取り、取得するためのものです。サービスプロバイダー内で指定された学校を特定できない場合は、「unknownobject」のステータスコードを報告する必要があります。
        /// </remarks>
        /// <param name="schoolSourcedId">特定の学校の一意の識別子、GUIDです。</param>
        /// <param name="limit">レスポンスに含まれるレコードの最大数、ダウンロード分割値を定義します。</param>
        /// <param name="offset">セグメンテーションされたレスポンスメッセージで提供する最初のレコードの数です。</param>
        /// <param name="sort">レスポンスメッセージのレコードに使用するソート基準を識別します。orderByパラメーターと共に使用します。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="orderBy">ソートされたリクエストに対する応答の並べ替え形式、すなわち昇順（asc）または降順（desc）です。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="filter">レスポンスメッセージで提供するレコードを識別する際に適用するフィルター規則です。ソート順序は、[UNICODE、16]標準に従う必要があります。</param>
        /// <param name="fields">レスポンスメッセージで提供するフィールドの範囲を識別します。</param>
        /// <returns>リクエストが正常に完了し、コレクションが返された場合。これには、 'codeMajor / severity'値が 'success / status' となり、RESTバインディングではHTTPコードが '200' となります。</returns>
        [Route("schools/{schoolSourcedId}/terms")]
        [WebApiAuthorize(Scope = Consts.SCOPE_ROSTER_READONLY)]
        public IHttpActionResult GetTermsForSchool(string schoolSourcedId, int? limit = Consts.DEFAULT_LIMIT, int? offset = 0, string sort = null, OrderByEnum? orderBy = null, string filter = null, string fields = null)
        {
            throw (new NotImplementedException());
        }
    }
}
