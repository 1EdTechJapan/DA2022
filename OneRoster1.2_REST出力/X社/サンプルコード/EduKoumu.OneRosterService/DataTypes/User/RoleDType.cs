using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// The container for one mapping between a role and an org for the user.
    /// <br/>
    /// </summary>
    public partial class RoleDType
    {
        /// <summary>
        /// Indicates if this role is the primary or secondary role for that org. There MUST be one, and only one, primary role for each org.
        /// <br/>
        /// </summary>
        [Required]        
        [JsonConverter(typeof(StringEnumConverter))]
        public RoleTypeEnum RoleType { get; set; }

        /// <summary>
        /// The role of the user in the org. The permitted values are from an enumerated list. 
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public RoleEnum Role { get; set; }

        [Required]
        public GUIDRefDType Org { get; set; } // GUIDRefDType of Org

        /// <summary>
        /// The identifier for the system/tool/app access account that is relevant to this role in the org. The equivalent UserProfile should exist with a 'profileId' equal to this identifier value. Model Primitive Datatype = AnyURI.
        /// </summary>
        public Uri UserProfile { get; set; }

        /// <summary>
        /// The start date on which the role becomes active (inclusive).  Model Primitive Datatype = Date.
        /// </summary>
        [JsonConverter(typeof(DateConverter))]
        public DateTime? BeginDate { get; set; }

        /// <summary>
        /// The end date on which the role becomes inactive (exclusive).  Model Primitive Datatype = Date.
        /// </summary>
        [JsonConverter(typeof(DateConverter))]
        public DateTime? EndDate { get; set; }
    }
}