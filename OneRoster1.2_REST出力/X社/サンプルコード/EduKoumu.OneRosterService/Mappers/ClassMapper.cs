using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Class;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;
using System.Linq;

namespace EduKoumu.OneRosterService.Mappers
{
    public class ClassMapper
    {
        private const string MetaData_JP_SpecialNeeds = "jp.specialNeeds";

        public static ClassDType Map(OR_Class entity, string fields)
        {
            var @class = new ClassDType
            {
                SourcedId = entity.SourcedId.ToString(),
                Status = (BaseStatusEnum)Enum.Parse(typeof(BaseStatusEnum), entity.Status),
                DateLastModified = entity.DateLastModified,
                Metadata = new Dictionary<string, object>
                {
                    { MetaData_JP_SpecialNeeds, entity.SpecialNeedsFlg }
                },
                Title = entity.Title,
                ClassCode = entity.ClassCode,
                ClassType = (ClassTypeEnum)Enum.Parse(typeof(ClassTypeEnum), entity.ClassType),
                Location = entity.Location,
                Grades = GetGrades(entity),
                Subjects = entity.Subjects?.Split(',').ToList(),
                Course = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.course, entity.Course),
                School = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.org, entity.School),
                Terms = new List<GUIDRefDType>
                {
                    GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.academicSession, entity.SchoolYear),
                },
                SubjectCodes = entity.SubjectCodes?.Split(',').ToList(),
                Periods = entity.Periods?.Split(',').ToList(),
                Resources = null,
            };

            return SelectionFieldsHelper.SetNotSelectedFieldsToNull(@class, fields);
        }

        public static List<ClassDType> Map(List<OR_Class> entities, string fields ) =>
            entities.Select(x => Map(x, fields)).ToList();

        private static List<string> GetGrades(OR_Class entity)
        {
            List<string> grades = new List<string>();

            if (entity.Taisho1Flg) { grades.Add("P1"); }
            if (entity.Taisho2Flg) { grades.Add("P2"); }
            if (entity.Taisho3Flg) { grades.Add("P3"); }
            if (entity.Taisho4Flg) { grades.Add("P4"); }
            if (entity.Taisho5Flg) { grades.Add("P5"); }
            if (entity.Taisho6Flg) { grades.Add("P6"); }
            if (entity.Taisho7Flg) { grades.Add("J1"); }
            if (entity.Taisho8Flg) { grades.Add("J2"); }
            if (entity.Taisho9Flg) { grades.Add("J3"); }

            return grades;
        }
    }
}