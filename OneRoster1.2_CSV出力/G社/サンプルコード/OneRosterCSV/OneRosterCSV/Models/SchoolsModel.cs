
namespace OneRosterCSV.Models.School
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：orgs
    // id指定エンドポイント：org

    public class Rootobject
    {
        public Org[] orgs { get; set; }
    }

    public class Org
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public string name { get; set; }
        public string type { get; set; }
        public string identifier { get; set; }
        public Parent parent { get; set; }
        public Child[] children { get; set; }
    }

    public class Metadata
    {
        public string permittedextensionpoint { get; set; }
    }

    public class Parent
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class Child
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }
}
