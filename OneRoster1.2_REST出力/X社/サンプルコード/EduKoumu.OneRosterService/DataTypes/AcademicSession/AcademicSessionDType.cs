using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.AcademicSession
{
    /// <summary>
    /// The container for an academicSession. An academicSession represents a duration of time. Typically they are used to describe terms, grading periods, and other durations e.g. school years. Term is used to describe a period of time during which learning will take place. Other words for term could be in common use around the world e.g. Semester. The important thing is that Term is a unit of time, often many weeks long, into which classes are scheduled. Grading Period is used to represent another unit of time, that within which line items are assessed. A term may have many grading periods, a grading period belongs to a single term. A class may be assessed over several grade periods (represented by a line item being connected to a grading period). The parent / child attributes of academic sessions allow terms to be connected to their grading periods and vice-versa. 
    /// <br/>
    /// </summary>
    public class AcademicSessionDType
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
        /// The title/label for the academic session. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Title { get; set; }

        /// <summary>
        /// The start date for the academic session. The start date is included in the academic session. This is in [ISO 8601] format of 'YYYY-MM-DD'. Model Primitive Datatype = Date.
        /// </summary>
        [Required]
        [JsonConverter(typeof(DateConverter))]
        public DateTime StartDate { get; set; }

        /// <summary>
        /// The end date for the academic session. The end date is excluded from the academic session. This is in [ISO 8601] format of 'YYYY-MM-DD'. Model Primitive Datatype = Date.
        /// </summary>
        [Required]
        [JsonConverter(typeof(DateConverter))]
        public DateTime EndDate { get; set; }

        /// <summary>
        /// The type of academic session. This is based upon an enumerated vocabulary.
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public SessionTypeEnum Type { get; set; }
                
        public GUIDRefDType Parent { get; set; } // GUIDRefDType of AcademicSession

        /// <summary>
        /// The set of links to the child AcademicSessions i.e. a set of AcademicSession 'sourcedIds'.
        /// <br/>
        /// </summary>        
        public List<GUIDRefDType> Children { get; set; } // GUIDRefDType of AcademicSession

        /// <summary>
        /// The school year for the academic session.  This year should include the school year end e.g. 2014. This is in the [ISO 8601] format of 'YYYY'. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string SchoolYear { get; set; }
    }
}