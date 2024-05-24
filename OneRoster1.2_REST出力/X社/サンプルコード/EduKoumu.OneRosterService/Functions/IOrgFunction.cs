using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Org;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public interface IOrgFunction
    {
        Task<OrgSetDType> GetAllOrgs(int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields, OrgTypeEnum? orgType = null);

        Task<SingleOrgDType> GetOrg(string sourcedId, string fields, OrgTypeEnum? orgType = null);
    }
}
