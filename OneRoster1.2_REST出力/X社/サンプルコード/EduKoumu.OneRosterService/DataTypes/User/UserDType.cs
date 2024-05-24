using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.User
{
    /// <summary>
    /// Users, Teachers and Students are human beings that are teaching or studying in a class respectively. A single User class is used to represent both teachers and students and a role property is used to distinguish a user's natural role.Humans may have relationships with other humans. For example, a student may have parents. The 'agents' attribute allows for relationships between humans to be expressed. Note that these are typically from the point of view of the student - so a student will link to its parents (via the agent attribute). The reverse view MUST also be modeled, so for example, a user of role 'parent' MUST have agents that are of type 'student'. Note: Teachers MUST NOT be set as agents of students i.e. the teaching relationship is covered via enrollments. 
    /// <br/>
    /// </summary>
    public class UserDType
    {
        /// <summary>
        /// The sourcedId of the object. All objects MUST be identified by a Source Identifier. This is a GUID  System ID for an object. This is the GUID that SYSTEMS will refer to when making API calls, or when needing to identify an object. It is RECOMMENDED that systems are able to map whichever local ids (e.g. database key fields) they use to SourcedId.  The sourcedId of an object is considered an addressable property of an entity and as such will not be treated as Personally Identifiable Information (PII) by certified products.  Therefore, as a part of certification, vendors will be required to declare that they will notify customers via documentation or other formal and documented agreement that sourcedIds should never contain PII in general, but particularly users. This means that if a customer includes a student name in an enrollment.sourcedId, it will not fall to any certified product to protect the enrollment.sourcedId as PII, or even the userSourcedId field in the enrollment record. Model Primitive Datatype = String.
        /// </summary>        
        [Required]
        public string SourcedId { get; set; }

        /// <summary>
        /// All objects MUST BE either 'active' or 'tobedeleted'.  Something which is flagged 'tobedeleted' is to be considered safe to delete. Systems can delete records that are flagged as such if they wish, but they are not under any compulsion to do so. In v1.1 the enumeration value of 'inactive' was removed and so for backwards compatibility all such marked objects should be interpreted as 'tobedeleted'.
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public BaseStatusEnum Status { get; set; }

        /// <summary>
        /// All objects MUST be annotated with the dateTime upon which they were last modified. This enables requesters to query for just the latest objects. DateTimes MUST be expressed in W3C profile of [ISO 8601] and MUST contain the UTC timezone. Model Primitive Datatype = DateTime.
        /// </summary>        
        [Required]
        [JsonConverter(typeof(DateTimeISO8601Converter))]
        public DateTime DateLastModified { get; set; }
                
        public Dictionary<string, Object> Metadata { get; set; }

        /// <summary>
        /// The master unique identifier for this user. This is NOT the same as the user's interoperability 'sourcedId'. This should be used to ensure that all of the system identifiers/accounts etc. can be reconciled to the same user. How this identifier is assigned and its format is beyond the scope of this specification. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string UserMasterIdentifier { get; set; }

        /// <summary>
        /// The user name assigned to the user. NOTE - This has been kept for backwards compatibility with OneRoster 1.1 and the new 'userProfiles' characteristic SHOULD be used instead. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string Username { get; set; }

        /// <summary>
        /// The set of external user identifiers that should be used for this user, if for some reason the sourcedId cannot be used. This might be an active directory id, an LTI id, or some other machine-readable identifier that is used for this person.
        /// <br/>
        /// </summary>        
        public List<UserIdDType> UserIds { get; set; }

        /// <summary>
        /// This is used to determine whether or not the record is active in the local system. 'false' denotes that the record is active but system access is curtailed according to the local administration rules.
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public TrueFalseEnum EnabledUser { get; set; }

        /// <summary>
        /// The given name. Also, known as the first name. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string GivenName { get; set; }

        /// <summary>
        /// The family name. Also, known as the last name. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string FamilyName { get; set; }

        /// <summary>
        /// The set of middle names. If more than one middle name is needed separate using a space e.g. 'Wingarde Granville'. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public string MiddleName { get; set; }

        /// <summary>
        /// The user's preferred first name. This attribute was added in version 1.2. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public string PreferredFirstName { get; set; }

        /// <summary>
        /// The user's preferred middle name(s). This attribute was added in version 1.2. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public string PreferredMiddleName { get; set; }

        /// <summary>
        /// The user's preferred last name. This attribute was added in version 1.2. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public string PreferredLastName { get; set; }

        /// <summary>
        /// The pronoun(s) by which this person is referenced. Examples (in the case of English) include 'she/her/hers', 'he/him/his', 'they/them/theirs', 'ze/hir/hir', 'xe/xir', or a statement that the person's name should be used instead of any pronoun. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public string Pronouns { get; set; }

        /// <summary>
        /// The set of roles for each of the orgs to which the user is affilliated. This is expressed as a set of role/org tuples.
        /// <br/>
        /// </summary>
        [Required]
        [MinLength(1)]
        public List<RoleDType> Roles { get; set; } = new List<RoleDType>();

        /// <summary>
        /// The set of system/app/tool profiles for the user.
        /// <br/>
        /// </summary>        
        public List<UserProfileDType> UserProfiles { get; set; }
                
        public GUIDRefDType PrimaryOrg { get; set; } // GUIDRefDType of Org

        /// <summary>
        /// An identifier for the user. NOTE - This characteristic is kept for backwards compatibility with OneRoster 1.1/1.0. The 'userIds' characteristic SHOULD be used instead. Model Primitive Datatype = String.
        /// </summary>        
        public string Identifier { get; set; }

        /// <summary>
        /// The email address for the user. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string Email { get; set; }

        /// <summary>
        /// The SMS number for the user. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string Sms { get; set; }

        /// <summary>
        /// The phone number for the user. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string Phone { get; set; }

        /// <summary>
        /// The links to other people i.e. User 'sourcedIds'.
        /// <br/>
        /// </summary>        
        public List<GUIDRefDType> Agents { get; set; } // GUIDRefDType of User

        /// <summary>
        /// Grade(s) for which a user with role 'student' is enrolled. The permitted vocabulary should be defined as part of the adoption and deployment process. See the Implementation Guide [OR-IMPL-12] for more details on how to define/use such a vocabulary. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> Grades { get; set; }

        /// <summary>
        /// A top-level password for the user. Care should be taken when using this field and the password SHOULD be encrypted. Model Primitive Datatype = String.
        /// </summary>        
        public string Password { get; set; }

        /// <summary>
        /// The identifiers (GUIDs) for the set of resources that are to be made available to the user. These are the sourcedIds that should be used for obtaining the metadata about the resources using the OR 1.2 Resources Service [OR-RES-SM-12].
        /// <br/>
        /// </summary>        
        public System.Collections.Generic.List<GUIDRefDType> Resources { get; set; } // GUIDRefDType of Resource

    }
}