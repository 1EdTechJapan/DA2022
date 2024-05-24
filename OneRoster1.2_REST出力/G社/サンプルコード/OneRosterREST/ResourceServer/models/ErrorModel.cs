
namespace ResourceServer.models.Error
{
    public class Rootobject
    {
        public string imsx_codeMajor { get; set; }
        public string imsx_severity { get; set; }
        public string imsx_description { get; set; }
        public Imsx_Codeminor imsx_CodeMinor { get; set; }
    }

    public class Imsx_Codeminor
    {
        public Imsx_Codeminorfield[] imsx_codeMinorField { get; set; }
    }

    public class Imsx_Codeminorfield
    {
        public string imsx_codeMinorFieldName { get; set; }
        public string imsx_codeMinorFieldValue { get; set; }
    }
}
