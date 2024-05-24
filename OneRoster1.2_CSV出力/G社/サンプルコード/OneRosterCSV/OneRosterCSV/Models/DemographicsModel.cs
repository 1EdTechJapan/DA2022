
namespace OneRosterCSV.Models.Demographic
{
    // RESTでのJSONのルートオブジェクト
    // 複数系エンドポイント：demographics
    // id指定エンドポイント：demographics (こちらも複数系表記)

    public class Rootobject
    {
        public Demographic[] demographics { get; set; }
    }

    public class Demographic
    {
        public string sourcedId { get; set; }
        public string status { get; set; }
        public string dateLastModified { get; set; }
        public Metadata metadata { get; set; }
        public string birthDate { get; set; }
        public string sex { get; set; }
        public string americanIndianOrAlaskaNative { get; set; }
        public string asian { get; set; }
        public string blackOrAfricanAmerican { get; set; }
        public string nativeHawaiianOrOtherPacificIslander { get; set; }
        public string white { get; set; }
        public string demographicRaceTwoOrMoreRaces { get; set; }
        public string hispanicOrLatinoEthnicity { get; set; }
        public string countryOfBirthCode { get; set; }
        public string stateOfBirthAbbreviation { get; set; }
        public string cityOfBirth { get; set; }
        public string publicSchoolResidenceStatus { get; set; }
    }

    public class Metadata
    {
        public string permittedextensionpoint { get; set; }
    }
}
