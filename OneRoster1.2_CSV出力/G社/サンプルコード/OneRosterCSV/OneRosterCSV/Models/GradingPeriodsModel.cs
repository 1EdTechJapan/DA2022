
namespace OneRosterCSV.Models.GradingPeriod
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：academicSessions
    // id指定エンドポイント：academicSession

    public class Rootobject
    {
        public Academicsession[] academicSessions { get; set; }
    }

    public class Academicsession
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public string title { get; set; }
        public string startDate { get; set; }
        public string endDate { get; set; }
        public string type { get; set; }
        public Parent parent { get; set; }
        public Child[] children { get; set; }
        public string schoolYear { get; set; }
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
