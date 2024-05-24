using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Class;
using EduKoumu.OneRosterService.DataTypes.User;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;
using System.Linq;

namespace EduKoumu.OneRosterService.Mappers
{
    public class UserMapper
    {
        private const string MetaData_JP_KanaGivenName = "jp.kanaGivenName";
        private const string MetaData_JP_KanaFamilyName = "jp.kanaFamilyName";
        private const string MetaData_JP_KanaMiddleName = "jp.kanaMiddleName";
        private const string MetaData_JP_HomeClass = "jp.homeClass";

        private const string UserIdDTypeType = "Koumu";

        public static UserDType Map(OR_User entity, string fields, List<OR_Role> tenantRoles, List<OR_UserProfile> tenantUserProfiles)
        {
            var homeClass = entity.OR_Enrollment
                .Where(x => x.Status == BaseStatusEnum.active.ToString())
                .Where(x => x.BeginDate.HasValue && x.BeginDate <= DateTime.Today)
                .Where(x => x.EndDate.HasValue && x.EndDate >= DateTime.Today)
                .Where(x => x.OR_Class.ClassType == ClassTypeEnum.homeroom.ToString())
                .FirstOrDefault()?
                .Class;

            var userProfiles = tenantUserProfiles
                .Where(x => x.Status == BaseStatusEnum.active.ToString())
                .Where(x => x.User == entity.SourcedId)
                .ToList();

            var primaryOrg = entity.OR_Org
                .Where(x => x.Status == BaseStatusEnum.active.ToString())
                .FirstOrDefault();

            var userRole = string.IsNullOrWhiteSpace(entity.Role) ? null :
                tenantRoles
                    .Where(x => x.Role == entity.Role)
                    .Where(x => x.TenantId == entity.TenantId)
                    .Where(x => primaryOrg != null && x.Org == primaryOrg.SourcedId)
                    .Where(x => x.BeginDate.HasValue && x.BeginDate <= DateTime.Today)
                    .Where(x => x.EndDate.HasValue && x.EndDate >= DateTime.Today)
                    .FirstOrDefault();

            var user = new UserDType
            {
                SourcedId = entity.SourcedId.ToString(),
                Status = (BaseStatusEnum)Enum.Parse(typeof(BaseStatusEnum), entity.Status),
                DateLastModified = entity.DateLastModified,
                Metadata = new Dictionary<string, object>
                {
                    { MetaData_JP_KanaGivenName, entity.KanapreferredFirstName },
                    { MetaData_JP_KanaFamilyName, entity.KanapreferredLastName },
                    { MetaData_JP_KanaMiddleName, entity.KanapreferredMiddleName },
                    { MetaData_JP_HomeClass, homeClass },
                },
                UserMasterIdentifier = entity.UserMasterIdentifier,
                Username = entity.Username,
                UserIds = string.IsNullOrWhiteSpace(entity.UserIds) ? null :
                    new List<UserIdDType>
                    {
                        new UserIdDType
                        {
                           Type = UserIdDTypeType,
                           Identifier = entity.UserIds,
                        }                    
                    },
                EnabledUser = entity.EnabledUser ? TrueFalseEnum.@true : TrueFalseEnum.@false,
                GivenName = entity.GivenName,
                FamilyName = entity.FamilyName,
                MiddleName = entity.MiddleName,
                PreferredFirstName = entity.PreferredFirstName,
                PreferredMiddleName = entity.PreferredMiddleName,
                PreferredLastName = entity.PreferredLastName,
                Pronouns = null, 
                Roles = userRole == null ? null : 
                    new List<RoleDType>
                    {
                        RoleMapper.Map(userRole),
                    },
                UserProfiles = userProfiles.Select(x => UserProfileMapper.Map(x)).ToList(),
                PrimaryOrg = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.org, primaryOrg?.SourcedId),
                Identifier = entity.Identifier,
                Email = entity.Email,
                Sms = entity.SMS,
                Phone = entity.Phone,
                Agents = entity.Agents.HasValue ? 
                    new List<GUIDRefDType>
                    {
                        GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.user, entity.Agents),                        
                    } : null,
                Grades = entity.Grades?.Split(',').ToList(),
                Password = entity.Password,
                Resources = null,
            };

            return SelectionFieldsHelper.SetNotSelectedFieldsToNull(user, fields);
        }

        public static List<UserDType> Map(List<OR_User> entities, string fields, List<OR_Role> tenantRoles, List<OR_UserProfile> tenantUserProfiles) =>
            entities.Select(x => Map(x, fields, tenantRoles, tenantUserProfiles)).ToList();
    }
}