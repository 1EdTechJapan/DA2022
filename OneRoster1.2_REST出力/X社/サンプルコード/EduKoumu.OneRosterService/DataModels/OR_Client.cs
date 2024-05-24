namespace EduKoumu.OneRosterService.DataModels
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel.DataAnnotations;
    using System.ComponentModel.DataAnnotations.Schema;
    using System.Data.Entity.Spatial;

    public partial class OR_Client
    {
        [DatabaseGenerated(DatabaseGeneratedOption.None)]
        public int Id { get; set; }

        public int TenantId { get; set; }

        [StringLength(50)]
        public string ClientName { get; set; }

        [StringLength(50)]
        public string ClientCode { get; set; }

        [Required]
        [StringLength(16)]
        public string ConsumerKey { get; set; }

        [Required]
        [StringLength(255)]
        public string ConsumerSecret { get; set; }

        public int? CrtUserId { get; set; }

        [StringLength(205)]
        public string CrtUserName { get; set; }

        public DateTime? CrtDateTime { get; set; }

        public int? UpdUserId { get; set; }

        [StringLength(205)]
        public string UpdUserName { get; set; }

        public DateTime? UpdDatetime { get; set; }

        public bool? DeleteFlg { get; set; }
    }
}
