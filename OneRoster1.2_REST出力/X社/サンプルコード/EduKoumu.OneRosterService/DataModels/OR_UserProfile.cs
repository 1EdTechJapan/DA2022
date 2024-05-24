namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_UserProfile
    {
        [Key]
        public Guid SourcedId { get; set; }

        public int TenantId { get; set; }

        [Required]
        [StringLength(15)]
        public string Status { get; set; }

        public DateTime DateLastModified { get; set; }

        public Guid User { get; set; }

        [Required]
        [StringLength(15)]
        public string ProfileType { get; set; }

        [Required]
        [StringLength(15)]
        public string VenderId { get; set; }

        [StringLength(15)]
        public string ApplicationId { get; set; }

        [StringLength(255)]
        public string Description { get; set; }

        [Required]
        [StringLength(15)]
        public string CredentialType { get; set; }

        [Required]
        [StringLength(255)]
        public string Username { get; set; }

        [StringLength(255)]
        public string Password { get; set; }

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
