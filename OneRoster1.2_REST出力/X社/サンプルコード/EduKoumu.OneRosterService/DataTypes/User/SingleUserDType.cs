using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// This is the container for a single user instance for a message payload.
    /// <br/>
    /// </summary>    
    public class SingleUserDType
    {        
        [Required]
        public UserDType User { get; set; } = new UserDType();
    }
}