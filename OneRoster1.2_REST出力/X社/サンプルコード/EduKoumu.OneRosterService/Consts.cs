namespace EduKoumu.OneRosterService
{
    public class Consts
    {
        public const string WEBAPI_ROUTE_PREFIX = "ims/oneroster/rostering/v1p2";

        public const int DEFAULT_LIMIT = 100;

        public const int DEFAULT_TOKEN_EXPIRED_TIME = 3600;

        public const string SCOPE_ROSTER_CORE_READONLY = "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly";

        public const string SCOPE_ROSTER_DEMOGRAPHICS_READONLY = "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-demographics.readonly";

        public const string SCOPE_ROSTER_READONLY = "https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly";
    }
}