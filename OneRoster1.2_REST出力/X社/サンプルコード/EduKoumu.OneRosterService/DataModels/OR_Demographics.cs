namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Demographics
    {
        [Key]
        public Guid User { get; set; }

        public int TenantId { get; set; }

        public int MemberId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        [Column(TypeName = "date")]
        public DateTime? BirthDate { get; set; }

        [Required]
        [StringLength(15)]
        public string Sex { get; set; }

        public bool? AmericanIndianOrAlaskaNative { get; set; }

        public bool? Asian { get; set; }

        public bool? BlackOrAfricanAmerican { get; set; }

        public bool? NativeHawaiianOrOtherPacificIslander { get; set; }

        public bool? White { get; set; }

        public bool? DemographicRaceTwoOrMoreRaces { get; set; }

        public bool? HispanicOrLatinoEthnicity { get; set; }

        [Required]
        [StringLength(50)]
        public string CountryOfBirthCode { get; set; }

        [Required]
        [StringLength(50)]
        public string StateOfBirthAbbreviation { get; set; }

        [Required]
        [StringLength(50)]
        public string CityOfBirth { get; set; }

        [Required]
        [StringLength(50)]
        public string PublicSchoolResidenceStatus { get; set; }

        public int? CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserId { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public bool? DeleteFlg { get; set; }
    }
}
