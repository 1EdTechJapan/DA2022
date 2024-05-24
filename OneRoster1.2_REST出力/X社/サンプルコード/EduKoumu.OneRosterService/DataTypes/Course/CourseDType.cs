using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Course
{
    /// <summary>
    /// The information about a course. A Course is a course of study that, typically, has a shared curriculum although it may be taught to different students by different teachers. It is likely that several classes of a single course may be taught in a term. For example, a school runs Grade 9 English in the spring term. There are four classes, each with a different 30 students, taught by 4 different teachers. However the curriculum for each of those four classes is the same i.e. the course curriculum.
    /// <br/>
    /// </summary>    
    public class CourseDType
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
        /// The title of the course. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Title { get; set; }
                
        public GUIDRefDType SchoolYear { get; set; } // GUIDRefDType of AcademicSession

        /// <summary>
        /// The assigned course code. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string CourseCode { get; set; }

        /// <summary>
        /// Grade(s) for which the class is attended. The permitted vocabulary should be defined as part of the adoption and deployment process. See the Implementation Guide [OR-IMPL-12] for more details on how to define/use such a vocabulary. Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> Grades { get; set; }

        /// <summary>
        /// The set of subjects addresse by this course. This is a set of human readable strings.   Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> Subjects { get; set; }
                
        public GUIDRefDType Org { get; set; } // GUIDRefDType of Org

        /// <summary>
        /// This is a machine readable set of codes and the number should match the associated 'subjects' attribute. The vocabulary for this characteristic should be defined as part of the local addition of this specification (see the Implementation Guide [OR-IMPL-12] for more details). Model Primitive Datatype = NormalizedString.
        /// </summary>        
        public List<string> SubjectCodes { get; set; }

        /// <summary>
        /// The links to the associated resources if applicable i.e. the resource 'sourcedIds'.
        /// <br/>
        /// </summary>        
        public List<GUIDRefDType> Resources { get; set; } // GUIDRefDType of Resource
    }
}