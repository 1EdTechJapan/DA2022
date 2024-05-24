using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// This is the set of external user identifiers that should be used for this user, if for some reason the sourcedId cannot be used. This might be an active directory id, an LTI id, or some other machine-readable identifier that is used for this person.
    /// <br/>
    /// </summary>
    public partial class UserIdDType
    {
        /// <summary>
        /// The type of identifier. This is no predefined vocabuary. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Type { get; set; }

        /// <summary>
        /// The user identifier. Model Primitive Datatype = String.
        /// </summary>
        [Required]
        public string Identifier { get; set; }

    }
}