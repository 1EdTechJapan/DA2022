
namespace OneRosterCSV.Models.Manifest
{

    public class Rootobject
    {
        public Manifest[] manifests { get; set; }
    }

    public class Manifest
    {
        public string propertyName { get; set; }
        public string value { get; set; }
    }
}
