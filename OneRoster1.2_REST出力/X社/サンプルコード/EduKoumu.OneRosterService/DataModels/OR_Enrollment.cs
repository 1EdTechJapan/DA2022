namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Enrollment
    {
        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        public int StudentTeacherShozokuId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        public Guid Class { get; set; }

        public Guid School { get; set; }

        public Guid User { get; set; }

        [Required]
        [StringLength(15)]
        public string Role { get; set; }

        public bool? Primary { get; set; }

        [Column(TypeName = "date")]
        public DateTime? BeginDate { get; set; }

        [Column(TypeName = "date")]
        public DateTime? EndDate { get; set; }

        [StringLength(3)]
        public string StudentCode { get; set; }

        public int? CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserId { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public bool? DeleteFlg { get; set; }

        public virtual OR_Class OR_Class { get; set; }

        public virtual OR_Org OR_Org { get; set; }

        public virtual OR_User OR_User { get; set; }
    }
}
