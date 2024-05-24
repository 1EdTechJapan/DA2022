using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Enrollment;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public interface IEnrollmentFunction
    {
        Task<EnrollmentSetDType> GetAllEnrollments(int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields);

        Task<SingleEnrollmentDType> GetEnrollment(string sourcedId, string fields);
    }
}
