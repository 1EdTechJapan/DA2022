using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.User;
using EduKoumu.OneRosterService.Mappers;
using EduKoumu.OneRosterService.Utils;
using System.Data.Entity;
using System.Linq;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public class UserFunction : IUserFunction
    {
        private readonly OneRosterDbContext db;

        public UserFunction()
        {
            this.db = new OneRosterDbContext();
        }

        public async Task<UserSetDType> GetAllUsers(
            int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields, RoleEnum? role = null)
        {
            var query = this.db.OR_User as IQueryable<OR_User>;

            // OR_User.OR_Enrollment.OR_Class must be included to get home class for user
            query = query.Include(x => x.OR_Enrollment.Select(y => y.OR_Class));                

            if (role.HasValue)
            {
                query = query.Where(x => x.Role == role.Value.ToString());
            }

            var entities = await QueryHelper
                .Query(query, limit, offset, sort, orderBy, filter);

            var tenantIds = entities.Select(x => x.TenantId).ToList();
            
            var tenantRoles = await this.db.OR_Role
                .Where(x => tenantIds.Contains(x.TenantId) &&
                  x.Status == BaseStatusEnum.active.ToString())
                .ToListAsync();

            var tenantUserProfiles = await this.db.OR_UserProfile
                .Where(x => tenantIds.Contains(x.TenantId) &&
                    x.Status == BaseStatusEnum.active.ToString())
                .ToListAsync();

            return new UserSetDType
            {
                Users = UserMapper.Map(entities, fields, tenantRoles, tenantUserProfiles)
            }; 
        }

        public async Task<SingleUserDType> GetUser(string sourcedId, string fields, RoleEnum? role = null)
        {
            var query = this.db.OR_User as IQueryable<OR_User>;

            // OR_User.OR_Enrollment.OR_Class must be included to get home class for user
            query = query.Include(x => x.OR_Enrollment.Select(y => y.OR_Class));

            if (role.HasValue)
            {
                query = query.Where(x => x.Role == role.Value.ToString());
            }

            var entity = await QueryHelper.GetBySourcedId(query, sourcedId);

            var tenantRoles = await this.db.OR_Role
                .Where(x => x.TenantId == entity.TenantId &&
                    x.Status == BaseStatusEnum.active.ToString())
                .ToListAsync();

            var tenantUserProfiles = await this.db.OR_UserProfile
                .Where(x => x.TenantId == entity.TenantId &&
                    x.Status == BaseStatusEnum.active.ToString())
                .ToListAsync();

            return new SingleUserDType
            {
                User = UserMapper.Map(entity, fields, tenantRoles, tenantUserProfiles)
            };
        }
    }
}