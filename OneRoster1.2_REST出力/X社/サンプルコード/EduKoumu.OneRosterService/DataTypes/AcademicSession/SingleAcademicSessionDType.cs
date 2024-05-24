using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.AcademicSession
{
    /// <summary>
    /// This is the container for a single academicSession instance for a message payload.
    /// <br/>
    /// </summary>    
    public partial class SingleAcademicSessionDType
    {        
        [Required]
        public AcademicSessionDType AcademicSession { get; set; } = new AcademicSessionDType();
    }
}