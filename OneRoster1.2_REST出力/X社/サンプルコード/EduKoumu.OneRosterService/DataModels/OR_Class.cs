namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Class
    {
        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2214:DoNotCallOverridableMethodsInConstructors")]
        public OR_Class()
        {
            OR_Enrollment = new HashSet<OR_Enrollment>();
        }

        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        public int ShozokuId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        [Required]
        [StringLength(255)]
        public string Title { get; set; }

        public bool Taisho1Flg { get; set; }

        public bool Taisho2Flg { get; set; }

        public bool Taisho3Flg { get; set; }

        public bool Taisho4Flg { get; set; }

        public bool Taisho5Flg { get; set; }

        public bool Taisho6Flg { get; set; }

        public bool Taisho7Flg { get; set; }

        public bool Taisho8Flg { get; set; }

        public bool Taisho9Flg { get; set; }

        public Guid Course { get; set; }

        [StringLength(255)]
        public string ClassCode { get; set; }

        [Required]
        [StringLength(10)]
        public string ClassType { get; set; }

        [StringLength(255)]
        public string Location { get; set; }

        public Guid School { get; set; }

        public Guid SchoolYear { get; set; }

        [StringLength(255)]
        public string Subjects { get; set; }

        [StringLength(255)]
        public string SubjectCodes { get; set; }

        [StringLength(255)]
        public string Periods { get; set; }

        public bool SpecialNeedsFlg { get; set; }

        public int? CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserId { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public bool? DeleteFlg { get; set; }

        public virtual OR_AcademicSession OR_AcademicSession { get; set; }

        public virtual OR_Course OR_Course { get; set; }

        public virtual OR_Org OR_Org { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Enrollment> OR_Enrollment { get; set; }
    }
}
