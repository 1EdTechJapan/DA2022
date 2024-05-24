using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Class
{
    /// <summary>
    /// This is the container for a single class instance for a message payload.
    /// <br/>
    /// </summary>
    public class SingleClassDType
    {
        [Required]
        public ClassDType Class { get; set; } = new ClassDType();

    }
}