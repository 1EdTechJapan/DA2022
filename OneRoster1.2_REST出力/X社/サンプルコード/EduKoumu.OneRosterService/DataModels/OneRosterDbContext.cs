using System.Data.Entity;

namespace EduKoumu.OneRosterService.DataModels
{
    public partial class OneRosterDbContext : DbContext
    {
        public OneRosterDbContext()
            : base("name=OneRosterDbContext")
        {
        }

        public virtual DbSet<OR_AcademicSession> OR_AcademicSession { get; set; }
        public virtual DbSet<OR_Class> OR_Class { get; set; }
        public virtual DbSet<OR_Client> OR_Client { get; set; }
        public virtual DbSet<OR_Course> OR_Course { get; set; }
        public virtual DbSet<OR_Demographics> OR_Demographics { get; set; }
        public virtual DbSet<OR_Enrollment> OR_Enrollment { get; set; }
        public virtual DbSet<OR_Org> OR_Org { get; set; }
        public virtual DbSet<OR_Role> OR_Role { get; set; }
        public virtual DbSet<OR_User> OR_User { get; set; }
        public virtual DbSet<OR_UserProfile> OR_UserProfile { get; set; }

        protected override void OnModelCreating(DbModelBuilder modelBuilder)
        {
            modelBuilder.Entity<OR_AcademicSession>()
                .Property(e => e.SchoolYear)
                .IsFixedLength()
                .IsUnicode(false);

            modelBuilder.Entity<OR_AcademicSession>()
                .HasMany(e => e.OR_Children)
                .WithOptional(e => e.OR_Parent)
                .HasForeignKey(e => e.Parent);

            modelBuilder.Entity<OR_AcademicSession>()
                .HasMany(e => e.OR_Class)
                .WithRequired(e => e.OR_AcademicSession)
                .HasForeignKey(e => e.SchoolYear)
                .WillCascadeOnDelete(false);

            modelBuilder.Entity<OR_AcademicSession>()
                .HasMany(e => e.OR_Course)
                .WithRequired(e => e.OR_AcademicSession)
                .HasForeignKey(e => e.SchoolYear);

            modelBuilder.Entity<OR_Class>()
                .HasMany(e => e.OR_Enrollment)
                .WithRequired(e => e.OR_Class)
                .HasForeignKey(e => e.Class);

            modelBuilder.Entity<OR_Client>()
                .Property(e => e.ConsumerKey)
                .IsFixedLength()
                .IsUnicode(false);

            modelBuilder.Entity<OR_Client>()
                .Property(e => e.ConsumerSecret)
                .IsUnicode(false);

            modelBuilder.Entity<OR_Course>()
                .HasMany(e => e.OR_Class)
                .WithRequired(e => e.OR_Course)
                .HasForeignKey(e => e.Course);

            modelBuilder.Entity<OR_Enrollment>()
                .Property(e => e.StudentCode)
                .IsUnicode(false);

            modelBuilder.Entity<OR_Org>()
                .HasMany(e => e.OR_Class)
                .WithRequired(e => e.OR_Org)
                .HasForeignKey(e => e.School)
                .WillCascadeOnDelete(false);

            modelBuilder.Entity<OR_Org>()
                .HasMany(e => e.OR_Course)
                .WithRequired(e => e.OR_Org)
                .HasForeignKey(e => e.Org)
                .WillCascadeOnDelete(false);

            modelBuilder.Entity<OR_Org>()
                .HasMany(e => e.OR_Enrollment)
                .WithRequired(e => e.OR_Org)
                .HasForeignKey(e => e.School)
                .WillCascadeOnDelete(false);

            modelBuilder.Entity<OR_Org>()
                .HasMany(e => e.OR_Children)
                .WithOptional(e => e.OR_Parent)
                .HasForeignKey(e => e.Parent);

            modelBuilder.Entity<OR_Org>()
                .HasMany(e => e.OR_User)
                .WithMany(e => e.OR_Org)
                .Map(m => m.ToTable("OR_UserOrg").MapLeftKey("Org").MapRightKey("User"));

            modelBuilder.Entity<OR_User>()
                .Property(e => e.Grades)
                .IsFixedLength()
                .IsUnicode(false);

            modelBuilder.Entity<OR_User>()
                .HasMany(e => e.OR_Enrollment)
                .WithRequired(e => e.OR_User)
                .HasForeignKey(e => e.User);

            modelBuilder.Entity<OR_User>()
                .HasMany(e => e.OR_User1)
                .WithOptional(e => e.OR_User2)
                .HasForeignKey(e => e.Agents);
        }
    }
}
