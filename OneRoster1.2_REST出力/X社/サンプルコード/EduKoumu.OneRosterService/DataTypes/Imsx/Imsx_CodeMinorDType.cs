using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Imsx
{
    /// <summary>
    /// This is the container for the set of code minor status codes reported in the responses from the Service Provider.
    /// <br/>
    /// </summary>
    public class Imsx_CodeMinorDType
    {
        /// <summary>
        /// Each reported code minor status code.
        /// <br/>
        /// </summary>
        [Required]
        [MinLength(1)]
        public List<Imsx_CodeMinorFieldDType> Imsx_codeMinorField { get; set; } = new List<Imsx_CodeMinorFieldDType>();
    }
}