using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.User;
using EduKoumu.OneRosterService.Utils;
using System;

namespace EduKoumu.OneRosterService.Mappers
{
    public class RoleMapper
    {
        public static RoleDType Map(OR_Role entity) =>
            new RoleDType
            {
                RoleType = (RoleTypeEnum)Enum.Parse(typeof(RoleTypeEnum), entity.RoleType),
                Role = (RoleEnum)Enum.Parse(typeof(RoleEnum), entity.Role),
                Org = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.org, entity.Org),
                UserProfile = string.IsNullOrWhiteSpace(entity.UserProfiles) ? null :
                    new Uri(GUIDRefDTypeHelper.GetBaseUrl() + "userProfiles/" + entity.UserProfiles),
                BeginDate = entity.BeginDate,
                EndDate = entity.EndDate
            };
    }
}