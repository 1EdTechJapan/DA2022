
using Newtonsoft.Json;

namespace ResourceServer.models.GUIDRef
{
    public class GUIDRefDType
    {
        public string href { get; set; }
        public string sourcedId { get; set; }
        public string type { get; set; }
    }

    public class RefClass
    {
        [JsonProperty("class")]
        public GUIDRefDType _class { get; set; }
    }

    public class RefChildren
    {
        public GUIDRefDType children { get; set; }
    }

    public class RefUser
    {
        public GUIDRefDType user { get; set; }
    }
}
