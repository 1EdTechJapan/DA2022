using System.Collections.Generic;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// This is the container for a collection of user instances for a message payload. This may be empty if no instances are found that sustain the applied query constraints. The order is not significant.
    /// <br/>
    /// </summary>
    public class UserSetDType
    {
        /// <summary>
        /// The collection of user instances. The order is not significant. The corresponding query constraints may result in no instances being returned.
        /// <br/>
        /// </summary>        
        public List<UserDType> Users { get; set; }
    }
}