using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Enrollment;
using EduKoumu.OneRosterService.Mappers;
using EduKoumu.OneRosterService.Utils;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public class EnrollmentFunction : IEnrollmentFunction
    {
        private readonly OneRosterDbContext db;

        public EnrollmentFunction()
        {
            this.db = new OneRosterDbContext();
        }

        public async Task<EnrollmentSetDType> GetAllEnrollments(
            int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields)
        {
            var entities = await QueryHelper
                .Query(this.db.OR_Enrollment, limit, offset, sort, orderBy, filter);

            return new EnrollmentSetDType
            {
                Enrollments = EnrollmentMapper.Map(entities, fields)
            };
        }

        public async Task<SingleEnrollmentDType> GetEnrollment(string sourcedId, string fields)
        {
            var entity = await QueryHelper.GetBySourcedId(this.db.OR_Enrollment, sourcedId);

            return new SingleEnrollmentDType
            {
                Enrollment = EnrollmentMapper.Map(entity, fields)
            };
        }
    }
}