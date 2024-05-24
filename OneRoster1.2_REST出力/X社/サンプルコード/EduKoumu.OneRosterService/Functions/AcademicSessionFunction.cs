using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.AcademicSession;
using EduKoumu.OneRosterService.Mappers;
using EduKoumu.OneRosterService.Utils;
using System.Linq;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public class AcademicSessionFunction : IAcademicSessionFunction
    {
        private readonly OneRosterDbContext db;

        public AcademicSessionFunction()
        {
            this.db = new OneRosterDbContext();
        }

        public async Task<AcademicSessionSetDType> GetAllAcademicSessions(
            int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields, SessionTypeEnum? sessionType = null)
        {
            var query = this.db.OR_AcademicSession as IQueryable<OR_AcademicSession>;

            if (sessionType.HasValue)
            {
                query = query.Where(x => x.Type == sessionType.Value.ToString());
            }

            var entities = await QueryHelper.Query(query, limit,offset,sort,orderBy, filter);

            return new AcademicSessionSetDType
            {
                AcademicSessions = AcademicSessionMapper.Map(entities, fields)
            }; 
        }

        public async Task<SingleAcademicSessionDType> GetAcademicSession(string sourcedId, string fields, SessionTypeEnum? sessionType = null)
        {
            var query = this.db.OR_AcademicSession as IQueryable<OR_AcademicSession>;

            if (sessionType.HasValue)
            {
                query = query.Where(x => x.Type == sessionType.Value.ToString());
            }

            var entity = await QueryHelper.GetBySourcedId(query, sourcedId);

            return new SingleAcademicSessionDType
            {
                AcademicSession = AcademicSessionMapper.Map(entity, fields)
            };
        }
    }
}