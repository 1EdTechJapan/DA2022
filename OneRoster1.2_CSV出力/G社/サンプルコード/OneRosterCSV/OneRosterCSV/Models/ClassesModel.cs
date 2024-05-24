
namespace OneRosterCSV.Models.Class
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：classes
    // id指定エンドポイント：class

    public class Rootobject
    {
        public Class1[] classes { get; set; }
    }

    public class Class1
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public string title { get; set; }
        public string classCode { get; set; }
        public string classType { get; set; }
        public string location { get; set; }
        public string[] grades { get; set; }
        public string[] subjects { get; set; }
        public Course course { get; set; }
        public School school { get; set; }
        public Term[] terms { get; set; }
        public string[] subjectCodes { get; set; }
        public string[] periods { get; set; }
        public Resource[] resources { get; set; }
    }

    public class Metadata
    {
        public JapanProfile jp { get; set; }
    }

    public class JapanProfile
    {
        public string specialNeeds { get; set; }
    }

    public class Course
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

    public class Term
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
