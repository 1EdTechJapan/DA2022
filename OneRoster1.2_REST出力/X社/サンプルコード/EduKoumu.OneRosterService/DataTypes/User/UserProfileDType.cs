using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// The container for the information about a User Profile that will provide the user with access to some system, application, tool, etc.
    /// <br/>
    /// </summary>
    public class UserProfileDType
    {
        /// <summary>
        /// The unique identifier for the profile. This does not need to be a globally unique identifier but it must be unique within the scope of the user. Model Primitive Datatype = AnyURI.
        /// </summary>
        [Required]        
        public Uri ProfileId { get; set; }

        /// <summary>
        /// The type of profile. This should be a human readable label that has some significance in the context of the related system, app, tool, etc. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string ProfileType { get; set; }

        /// <summary>
        /// The unique identifier for the vendor of the system, tool, app, etc. which requires the use of this profile. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string VendorId { get; set; }

        /// <summary>
        /// Identifier for the application associated with the account. The nature, and how this identifier is assigned is not defined by this specification. This may have a value of 'default' to denote this account should be used for default access to all applications related to this vendor. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string ApplicationId { get; set; }

        /// <summary>
        /// A human readable description of the use of the profile. This should not contain any security information for access to the account. Model Primitive Datatype = String.
        /// </summary>        
        public string Description { get; set; }

        /// <summary>
        /// The set of credentials that are available for access to this profile.
        /// <br/>
        /// </summary>        
        public List<CredentialDType> Credentials { get; set; }
    }
}