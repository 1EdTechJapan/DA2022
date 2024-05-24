using System.Collections.Generic;

namespace EduKoumu.OneRosterService.DataTypes.AcademicSession
{
    /// <summary>
    /// This is the container for a collection of academicSessions instances for a message payload. This may be empty if no instances are found that sustain the applied query constraints. The order is not significant.
    /// <br/>
    /// </summary>    
    public partial class AcademicSessionSetDType
    {
        /// <summary>
        /// The collection of academicSession instances. The order is not significant. The corresponding query constraints may result in no instances being returned.
        /// <br/>
        /// </summary>        
        public List<AcademicSessionDType> AcademicSessions { get; set; }
    }
}