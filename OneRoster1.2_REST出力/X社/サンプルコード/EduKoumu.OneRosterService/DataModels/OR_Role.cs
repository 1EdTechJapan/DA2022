namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Role
    {
        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        public Guid Org { get; set; }

        [Required]
        [StringLength(15)]
        public string RoleType { get; set; }

        [Required]
        [StringLength(15)]
        public string Role { get; set; }

        [Column(TypeName = "date")]
        public DateTime? BeginDate { get; set; }

        [Column(TypeName = "date")]
        public DateTime? EndDate { get; set; }

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
    }
}
