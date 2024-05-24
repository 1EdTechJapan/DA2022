using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Class
{
    /// <summary>
    /// A class is an instance of a course, onto which students and teachers are enrolled. A class is typically held within a term.
    /// <br/>
    /// </summary>
    public partial class ClassDType
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
        /// The tile/label for the class. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Title { get; set; }

        /// <summary>
        /// The class code. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public string ClassCode { get; set; }

        /// <summary>
        /// The type of class. This is based upon an enumerated vocabulary.
        /// <br/>
        /// </summary>
        [JsonConverter(typeof(StringEnumConverter))]
        public ClassTypeEnum ClassType { get; set; }

        /// <summary>
        /// The location for the class e.g. 'Room 19'. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public string Location { get; set; }

        /// <summary>
        /// The grade(s) who attend the class. The permitted vocabulary should be defined as part of the adoption and deployment process. See the Implementation Guide [OR-IMPL-12] for more details on how to define/use such a vocabulary. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> Grades { get; set; }

        /// <summary>
        /// The set of subjects addressed by this class e.g. 'chemistry'. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> Subjects { get; set; }

        [Required]
        public GUIDRefDType Course { get; set; } // GUIDRefDType of Course

        [Required]
        public GUIDRefDType School { get; set; } // GUIDRefDType of Org

        /// <summary>
        /// The links to the set of terms or semesters (academicSession) i.e. the set of 'sourcedIds' for the terms within the associated school year.
        /// <br/>
        /// </summary>
        [Required]
        [MinLength(1)]
        public List<GUIDRefDType> Terms { get; set; } = new List<GUIDRefDType>(); // GUIDRefDType of AcademicSession

        /// <summary>
        /// This is a machine readable set of codes and the number should match the associated 'subjects' attribute. The vocabulary for this characteristic should be defined as part of the local addition of this specification (see the Implementation Guide [OR-IMPL-12] for more details). Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> SubjectCodes { get; set; }

        /// <summary>
        /// The time slots in the day that the class will be given. Examples are 1 or a list of 1, 3, 5, etc. Model Primitive Datatype = NormalizedString.
        /// </summary>
        public List<string> Periods { get; set; }

        /// <summary>
        /// The links to the set of associated resources i.e. the Resource 'sourcedIds'.
        /// <br/>
        /// </summary>        
        public System.Collections.Generic.List<GUIDRefDType> Resources { get; set; } // GUIDRefDType of Resource
    }
}