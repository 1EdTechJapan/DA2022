namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Course
    {
        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2214:DoNotCallOverridableMethodsInConstructors")]
        public OR_Course()
        {
            OR_Class = new HashSet<OR_Class>();
        }

        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        public Guid SchoolYear { get; set; }

        [Required]
        [StringLength(255)]
        public string Title { get; set; }

        [StringLength(255)]
        public string CourseCode { get; set; }

        public bool Taisho1Flg { get; set; }

        public bool Taisho2Flg { get; set; }

        public bool Taisho3Flg { get; set; }

        public bool Taisho4Flg { get; set; }

        public bool Taisho5Flg { get; set; }

        public bool Taisho6Flg { get; set; }

        public bool Taisho7Flg { get; set; }

        public bool Taisho8Flg { get; set; }

        public bool Taisho9Flg { get; set; }

        public Guid Org { get; set; }

        [StringLength(255)]
        public string Subjects { get; set; }

        [StringLength(255)]
        public string SubjectCodes { get; set; }

        public int CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserID { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public bool? DeleteFlg { get; set; }

        public virtual OR_AcademicSession OR_AcademicSession { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Class> OR_Class { get; set; }

        public virtual OR_Org OR_Org { get; set; }
    }
}
