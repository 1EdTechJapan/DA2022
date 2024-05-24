using System.Collections.Generic;

namespace EduKoumu.OneRosterService.DataTypes.Class
{

    /// <summary>
    /// This is the container for a collection of classes instances for a message payload. This may be empty if no instances are found that sustain the applied query constraints. The order is not significant.
    /// <br/>
    /// </summary>    
    public class ClassSetDType
    {
        /// <summary>
        /// The collection of class instances. The order is not significant. The corresponding query constraints may result in no instances being returned.
        /// <br/>
        /// </summary>        
        public List<ClassDType> Classes { get; set; }

    }
}