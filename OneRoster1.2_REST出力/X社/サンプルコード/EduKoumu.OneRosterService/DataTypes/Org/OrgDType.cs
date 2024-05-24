using EduKoumu.OneRosterService.Utils;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes.Org
{
    /// <summary>
    /// ORG is defined here as a structure for holding organizational information. An ORG might be a school, or it might be a local, statewide, or national entity. ORGs will typically have a parent ORG (up to the national level), and children, allowing a hierarchy to be established. School is defined here as the place where the learning happens. Most commonly this is the data that describes a bricks and mortar building, or, in the case of a virtual school, the virtual school organization. For enrollment and result reporting purposes, little information about this organization is required. A common example of a local organization is a school district.
    /// <br/>
    /// </summary>
    public class OrgDType
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
        /// The name of the organization. Model Primitive Datatype = NormalizedString.
        /// </summary>
        [Required]
        public string Name { get; set; }

        /// <summary>
        /// The type of organization. This uses a predefined vocabulary.
        /// <br/>
        /// </summary>        
        [JsonConverter(typeof(StringEnumConverter))]
        public OrgTypeEnum Type { get; set; }

        /// <summary>
        /// Human readable identifier for this org e.g. NCES ID. Model Primitive Datatype = String.
        /// </summary>
        [Required]
        public string Identifier { get; set; }
                
        public GUIDRefDType Parent { get; set; } // GUIDRefDType of Org

        /// <summary>
        /// The 'sourcedIds' for the set of child organizations.
        /// <br/>
        /// </summary>        
        public List<GUIDRefDType> Children { get; set; } // GUIDRefDType of Org
    }
}