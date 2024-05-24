
using MongoDB.Bson.Serialization.Attributes;

namespace OneRosterCSV.Models.Enrollment
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：enrollments
    // id指定エンドポイント：enrollment

    public class Rootobject
    {
        public Enrollment[] enrollments { get; set; }
    }

    public class Enrollment
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public User user { get; set; }

        [BsonElement("class")]
        public Class1 _class { get; set; }
        public School school { get; set; }
        public string role { get; set; }
        public string primary { get; set; }
        public string beginDate { get; set; }
        public string endDate { get; set; }
    }

    public class Metadata
    {
        public JapanProfile jp { get; set; }
    }

    public class JapanProfile
    {
        public string ShussekiNo { get; set; }
        public string PublicFlg { get; set; }
    }

    public class User
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class Class1
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class School
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }
}
