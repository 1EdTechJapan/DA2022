using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System;
using System.ComponentModel.DataAnnotations;

namespace EduKoumu.OneRosterService.DataTypes
{
    /// <summary>
    /// This is the container for reference to a OneRoster 'Academic Session' object that has an allocated sourcedId (GUID).
    /// <br/>
    /// </summary>
    public class GUIDRefDType
    {
        /// <summary>
        /// The URI for the type of object being referenced. Model Primitive Datatype = AnyURI.
        /// </summary>
        [Required]
        public Uri Href { get; set; }

        /// <summary>
        /// The globally unique identifier of the object being referenced. Model Primitive Datatype = String.
        /// </summary>
        [Required]
        public string SourcedId { get; set; }

        /// <summary>
        /// The type of object being referenced i.e. an 'academicSession'.
        /// <br/>
        /// </summary>
        [Required]
        [JsonConverter(typeof(StringEnumConverter))]
        public GUIDRefTypeEnum Type { get; set; }
    }
}