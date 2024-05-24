using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.AcademicSession;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public interface IAcademicSessionFunction
    {
        Task<AcademicSessionSetDType> GetAllAcademicSessions(int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields, SessionTypeEnum? sessionType = null);

        Task<SingleAcademicSessionDType> GetAcademicSession(string sourcedId, string fields, SessionTypeEnum? sessionType = null);
    }
}
