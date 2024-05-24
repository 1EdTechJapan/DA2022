namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Org
    {
        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2214:DoNotCallOverridableMethodsInConstructors")]
        public OR_Org()
        {
            OR_Class = new HashSet<OR_Class>();
            OR_Course = new HashSet<OR_Course>();
            OR_Enrollment = new HashSet<OR_Enrollment>();
            OR_Children = new HashSet<OR_Org>();
            OR_User = new HashSet<OR_User>();
        }

        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        public int DantaiId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        [Required]
        [StringLength(255)]
        public string Name { get; set; }

        [Required]
        [StringLength(15)]
        public string Type { get; set; }

        [StringLength(255)]
        public string Identifier { get; set; }

        public Guid? Parent { get; set; }

        public int? CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserId { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public bool? DeleteFlg { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Class> OR_Class { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Course> OR_Course { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Enrollment> OR_Enrollment { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Org> OR_Children { get; set; }

        public virtual OR_Org OR_Parent { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_User> OR_User { get; set; }
    }
}
