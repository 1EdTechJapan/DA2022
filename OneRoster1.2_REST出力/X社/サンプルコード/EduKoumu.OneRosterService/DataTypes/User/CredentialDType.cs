using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// The container for a single set of credentials for an account.
    /// <br/>
    /// </summary>    
    public class CredentialDType
    {
        /// <summary>
        /// The type of credentials for the profile. This should be indicative of when this specific credential should be used. Model Primitive Datatype = String.
        /// </summary>
        [Required]
        public string Type { get; set; }

        /// <summary>
        /// The username. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Username { get; set; }

        /// <summary>
        /// The password in this set of credentials.  Care should be taken to ensure that no unencrypted value is revealed. Model Primitive Datatype = String.
        /// </summary>        
        public string Password { get; set; }
    }
}