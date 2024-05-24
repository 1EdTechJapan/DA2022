using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Course;
using EduKoumu.OneRosterService.Utils;
using System;
using System.Collections.Generic;
using System.Linq;

namespace EduKoumu.OneRosterService.Mappers
{
    public class CourseMapper
    {
        public static CourseDType Map(OR_Course entity, string fields)
        {
            var course = new CourseDType
            {
                SourcedId = entity.SourcedId.ToString(),
                Status = (BaseStatusEnum)Enum.Parse(typeof(BaseStatusEnum), entity.Status),
                DateLastModified = entity.DateLastModified,
                Title = entity.Title,
                SchoolYear = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.academicSession, entity.SchoolYear),
                CourseCode = entity.CourseCode,
                Grades = GetGrades(entity),
                Subjects = entity.Subjects?.Split(',').ToList(),
                Org = GUIDRefDTypeHelper.GetGUIDRefDType(GUIDRefTypeEnum.org, entity.Org),
                SubjectCodes = entity.SubjectCodes?.Split(',').ToList(),
                Resources = null,
            };

            return SelectionFieldsHelper.SetNotSelectedFieldsToNull(course, fields);

        }

        public static List<CourseDType> Map(List<OR_Course> entities, string fields) =>
            entities.Select(x => Map(x, fields)).ToList();

        private static List<string> GetGrades(OR_Course entity)
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