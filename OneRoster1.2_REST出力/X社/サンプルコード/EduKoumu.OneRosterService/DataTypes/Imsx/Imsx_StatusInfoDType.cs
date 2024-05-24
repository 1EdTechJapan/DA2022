using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Imsx
{
    /// <summary>
    /// This is the container for the status code and associated information returned within the HTTP messages received from the Service Provider. For the OneRoster Rostering service this object will only be returned to provide information about a failed request i.e. it will NOT be in the payload for a successful request. See Appendix B for further information on the interpretation of the information contained within this class.
    /// <br/>
    /// </summary>
    public class Imsx_StatusInfoDType
    {
        /// <summary>
        /// The code major value (from the corresponding enumerated vocabulary). See Appendix B for further information on the interpretation of this set of codes. The permitted vocabulary for the values for the CodeMajor field.
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public Imsx_StatusInfoDTypeImsx_codeMajor Imsx_codeMajor { get; set; }

        /// <summary>
        /// The severity value (from the corresponding enumerated vocabulary). See Appendix B for further information on the interpretation of this set of codes.
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public Imsx_StatusInfoDTypeImsx_severity Imsx_severity { get; set; }

        /// <summary>
        /// A human readable description supplied by the entity creating the status code information. Model Primitive Datatype = String.
        /// </summary>        
        public string Imsx_description { get; set; }
                
        public Imsx_CodeMinorDType Imsx_CodeMinor { get; set; }
    }
}