
namespace OneRosterCSV.Models.Teacher
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：users
    // id指定エンドポイント：user

    public class Rootobject
    {
        public User[] users { get; set; }
    }

    public class User
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public string userMasterIdentifier { get; set; }
        public string username { get; set; }
        public Userid[] userIds { get; set; }
        public string enabledUser { get; set; }
        public string givenName { get; set; }
        public string familyName { get; set; }
        public string middleName { get; set; }
        public string preferredFirstName { get; set; }
        public string preferredMiddleName { get; set; }
        public string preferredLastName { get; set; }
        public string pronouns { get; set; }
        public Role[] roles { get; set; }
        public Userprofile[] userProfiles { get; set; }
        public Primaryorg primaryOrg { get; set; }
        public string identifier { get; set; }
        public string email { get; set; }
        public string sms { get; set; }
        public string phone { get; set; }
        public Agent[] agents { get; set; }
        public string[] grades { get; set; }
        public string password { get; set; }
        public Resource[] resources { get; set; }
    }

    public class Metadata
    {
        public JapanProfile jp { get; set; }
    }

    public class JapanProfile
    {
        public string homeClass { get; set; }
    }

    public class Primaryorg
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class Userid
    {
        public string type { get; set; }
        public string identifier { get; set; }
    }

    public class Role
    {
        public string roleType { get; set; }
        public string role { get; set; }
        public Org org { get; set; }
        public string userProfile { get; set; }
        public string beginDate { get; set; }
        public string endDate { get; set; }
    }

    public class Org
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class Userprofile
    {
        public string profileId { get; set; }
        public string profileType { get; set; }
        public string vendorId { get; set; }
        public string applicationId { get; set; }
        public string description { get; set; }
        public Credential[] credentials { get; set; }
    }

    public class Credential
    {
        public string type { get; set; }
        public string username { get; set; }
        public string password { get; set; }
        public string permittedextensionpoint { get; set; }
    }

    public class Agent
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class Resource
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }
}
