
namespace OneRosterCSV.Models.Course
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：courses
    // id指定エンドポイント：course

    public class Rootobject
    {
        public Cours[] courses { get; set; }
    }

    public class Cours
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public string title { get; set; }
        public Schoolyear schoolYear { get; set; }
        public string courseCode { get; set; }
        public string[] grades { get; set; }
        public string[] subjects { get; set; }
        public Org org { get; set; }
        public string[] subjectCodes { get; set; }
        public Resource[] resources { get; set; }
    }

    public class Metadata
    {
        public string permittedextensionpoint { get; set; }
    }

    public class Schoolyear
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class Org
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
