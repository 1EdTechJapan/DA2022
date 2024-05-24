using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Org
{
    /// <summary>
    /// This is the container for a single org instance for a message payload.
    /// <br/>
    /// </summary>
    public class SingleOrgDType
    {
        [Required]
        public OrgDType Org { get; set; } = new OrgDType();
    }
}