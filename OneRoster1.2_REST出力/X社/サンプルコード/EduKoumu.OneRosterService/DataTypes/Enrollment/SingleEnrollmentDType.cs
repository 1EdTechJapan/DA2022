using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Enrollment
{
    /// <summary>
    /// This is the container for a single enrollment instance for a message payload.
    /// <br/>
    /// </summary>    
    public class SingleEnrollmentDType
    {        
        [Required]
        public EnrollmentDType Enrollment { get; set; } = new EnrollmentDType();
    }
}