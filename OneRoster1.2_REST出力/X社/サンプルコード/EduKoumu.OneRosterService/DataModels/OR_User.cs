namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_User
    {
        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2214:DoNotCallOverridableMethodsInConstructors")]
        public OR_User()
        {
            OR_Enrollment = new HashSet<OR_Enrollment>();
            OR_User1 = new HashSet<OR_User>();
            OR_Org = new HashSet<OR_Org>();
        }

        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        public int MemberId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        public bool EnabledUser { get; set; }

        [Required]
        [StringLength(15)]
        public string Role { get; set; }

        [Required]
        [StringLength(255)]
        public string Username { get; set; }

        [StringLength(255)]
        public string UserIds { get; set; }

        [Required]
        [StringLength(50)]
        public string GivenName { get; set; }

        [Required]
        [StringLength(50)]
        public string FamilyName { get; set; }

        [StringLength(105)]
        public string MiddleName { get; set; }

        [StringLength(50)]
        public string KanaGivenName { get; set; }

        [StringLength(50)]
        public string KanaFamilyName { get; set; }

        [StringLength(105)]
        public string KanaMiddleName { get; set; }

        [StringLength(50)]
        public string PreferredFirstName { get; set; }

        [StringLength(50)]
        public string PreferredLastName { get; set; }

        [StringLength(105)]
        public string PreferredMiddleName { get; set; }

        [StringLength(50)]
        public string KanapreferredFirstName { get; set; }

        [StringLength(50)]
        public string KanapreferredLastName { get; set; }

        [StringLength(105)]
        public string KanapreferredMiddleName { get; set; }

        [StringLength(255)]
        public string Identifier { get; set; }

        [StringLength(255)]
        public string UserMasterIdentifier { get; set; }

        [StringLength(255)]
        public string Email { get; set; }

        [StringLength(255)]
        public string SMS { get; set; }

        [StringLength(255)]
        public string Phone { get; set; }

        public Guid? Agents { get; set; }

        [StringLength(2)]
        public string Grades { get; set; }

        [StringLength(255)]
        public string Password { get; set; }

        [StringLength(255)]
        public string UserProfiles { get; set; }

        public int? CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserId { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public bool? DeleteFlg { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Enrollment> OR_Enrollment { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_User> OR_User1 { get; set; }

        public virtual OR_User OR_User2 { get; set; }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Usage", "CA2227:CollectionPropertiesShouldBeReadOnly")]
        public virtual ICollection<OR_Org> OR_Org { get; set; }
    }
}
