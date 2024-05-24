using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Enrollment
{
    /// <summary>
    /// An enrollment is the name given to an individual taking part in a class. In the vast majority of cases, users will be students learning in a class, or teachers teaching the class. Other roles are also possible.
    /// <br/>
    /// </summary>    
    public class EnrollmentDType
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

        [Required]
        public GUIDRefDType User { get; set; } // GUIDRefDType of User;

        [Required]
        public GUIDRefDType Class { get; set; } // GUIDRefDType of Class;

        [Required]
        public GUIDRefDType School { get; set; } // GUIDRefDType of Org;

        /// <summary>
        /// The role of the user for this class in the school e.g teacher, student, etc. This is from an enumerated vocabulary.
        /// <br/>
        /// </summary>        
        [JsonConverter(typeof(StringEnumConverter))]
        public EnrolRoleEnum Role { get; set; }

        /// <summary>
        /// Applicable only to teachers. Only one teacher should be designated as the primary teacher for a class (this value set as 'true') in the period defined by the begin/end dates.
        /// <br/>
        /// </summary>        
        [JsonConverter(typeof(StringEnumConverter))]
        public TrueFalseEnum? Primary { get; set; }

        /// <summary>
        /// The start date for the enrollment (inclusive). This date must be within the period of the associated Academic Session for the class (Term/Semester/SchoolYear). Use the [ISO 8601] format of 'YYYY-MM-DD'. Model Primitive Datatype = Date.
        /// </summary>
        [JsonConverter(typeof(DateConverter))]
        public DateTime? BeginDate { get; set; }

        /// <summary>
        /// The end date for the enrollment (exclusive).  This date must be within the period of the associated Academic Session for the class (Term/Semester/SchoolYear). Use the [ISO 8601] format of 'YYYY-MM-DD'. Model Primitive Datatype = Date.
        /// </summary>
        [JsonConverter(typeof(DateConverter))]
        public DateTime? EndDate { get; set; }
    }
}