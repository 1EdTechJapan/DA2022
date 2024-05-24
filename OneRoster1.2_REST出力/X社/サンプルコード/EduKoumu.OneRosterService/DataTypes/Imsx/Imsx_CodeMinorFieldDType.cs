using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Imsx
{
    /// <summary>
    /// This is the container for a single code minor status code.
    /// <br/>
    /// </summary>
    public class Imsx_CodeMinorFieldDType
    {
        /// <summary>
        /// This should contain the identity of the system that has produced the code minor status code report. In most cases this will be the target service provider denoted as 'TargetEndSystem'. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Imsx_codeMinorFieldName { get; set; } = "TargetEndSystem";

        /// <summary>
        /// The code minor status code (this is a value from the corresponding enumerated vocabulary).
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public Imsx_CodeMinorFieldDTypeImsx_codeMinorFieldValue Imsx_codeMinorFieldValue { get; set; }

    }
}