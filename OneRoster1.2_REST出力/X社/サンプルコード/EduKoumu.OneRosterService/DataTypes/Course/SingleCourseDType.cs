using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Course
{
    /// <summary>
    /// This is the container for a single course instance for a message payload.
    /// <br/>
    /// </summary>    
    public class SingleCourseDType
    {        
        [Required]
        public CourseDType Course { get; set; } = new CourseDType();
    }
}