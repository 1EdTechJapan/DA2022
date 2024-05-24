using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.AcademicSession;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;
using System.Linq;

namespace EduKoumu.OneRosterService.Mappers
{
    public class AcademicSessionMapper
    {
        public static AcademicSessionDType Map(OR_AcademicSession entity, string fields)
        {
            var academicSession = new AcademicSessionDType
            {
                SourcedId = entity.SourcedId.ToString(),
                Status = (BaseStatusEnum)Enum.Parse(typeof(BaseStatusEnum), entity.Status),
                DateLastModified = entity.DateLastModified,
                Title = entity.Title,
                Type = (SessionTypeEnum)Enum.Parse(typeof(SessionTypeEnum), entity.Type),
                StartDate = entity.StartDate,
                EndDate = entity.EndDate,
                Parent = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.academicSession, entity.Parent),
                SchoolYear = entity.SchoolYear,
                Children = GUIDRefDTypeHelper.GetGUIDRefDTypeList(GUIDRefTypeEnum.academicSession, entity.OR_Children.Select(x => x.SourcedId).ToArray()),
            };

            return SelectionFieldsHelper.SetNotSelectedFieldsToNull(academicSession, fields);
        }

        public static List<AcademicSessionDType> Map(List<OR_AcademicSession> entities, string fields) =>
            entities.Select(x => Map(x, fields)).ToList();  
    }
}