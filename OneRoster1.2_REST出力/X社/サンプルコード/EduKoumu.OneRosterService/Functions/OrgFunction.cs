using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Org;
using EduKoumu.OneRosterService.Mappers;
using EduKoumu.OneRosterService.Utils;
using System.Linq;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public class OrgFunction : IOrgFunction
    {
        private readonly OneRosterDbContext db;

        public OrgFunction()
        {
            this.db = new OneRosterDbContext();
        }

        public async Task<OrgSetDType> GetAllOrgs(
            int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields, OrgTypeEnum? orgType = null)
        {
            var query = this.db.OR_Org as IQueryable<OR_Org>;

            if (orgType.HasValue)
            {
                query = query.Where(x => x.Type == orgType.Value.ToString());
            }

            var entities = await QueryHelper.Query(query, limit, offset, sort, orderBy, filter);

            return new OrgSetDType
            {
                Orgs = OrgMapper.Map(entities, fields)
            }; 
        }

        public async Task<SingleOrgDType> GetOrg(string sourcedId, string fields, OrgTypeEnum? orgType = null)
        {
            var query = this.db.OR_Org as IQueryable<OR_Org>;

            if (orgType.HasValue)
            {
                query = query.Where(x => x.Type == orgType.Value.ToString());
            }

            var entity = await QueryHelper.GetBySourcedId(query, sourcedId);

            return new SingleOrgDType
            {
                Org = OrgMapper.Map(entity, fields)
            };
        }
    }
}