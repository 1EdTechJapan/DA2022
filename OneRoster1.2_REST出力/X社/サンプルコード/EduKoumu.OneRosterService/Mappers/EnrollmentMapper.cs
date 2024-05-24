using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Enrollment;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;
using System.Linq;

namespace EduKoumu.OneRosterService.Mappers
{
    public class EnrollmentMapper
    {
        private const string MetaData_JP_ShussekiNo = "jp.ShussekiNo";
        private const string MetaData_JP_PublicFlg = "jp.PublicFlg";

        public static EnrollmentDType Map(OR_Enrollment entity, string fields)
        {
            var enrollment = new EnrollmentDType
            {
                SourcedId = entity.SourcedId.ToString(),
                Status = (BaseStatusEnum)Enum.Parse(typeof(BaseStatusEnum), entity.Status),
                DateLastModified = entity.DateLastModified,
                Metadata = new Dictionary<string, object>
                {
                    { MetaData_JP_ShussekiNo, entity.StudentCode },
                    { MetaData_JP_PublicFlg, 1 }
                },
                User = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.user, entity.User),
                Class = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.@class, entity.Class),                
                School = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.org, entity.School),                
                Role = (EnrolRoleEnum)Enum.Parse(typeof(EnrolRoleEnum), entity.Role),
                Primary = entity.Primary == null ? (TrueFalseEnum?)null : entity.Primary.Value ? TrueFalseEnum.@true : TrueFalseEnum.@false,
                BeginDate = entity.BeginDate,
                EndDate = entity.EndDate,
            };

            return SelectionFieldsHelper.SetNotSelectedFieldsToNull(enrollment, fields);
        }

        public static List<EnrollmentDType> Map(List<OR_Enrollment> entities, string fields) =>
            entities.Select(x => Map(x, fields)).ToList();
    }
}