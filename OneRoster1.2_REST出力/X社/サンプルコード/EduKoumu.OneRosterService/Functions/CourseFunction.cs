using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Course;
using EduKoumu.OneRosterService.Mappers;
using EduKoumu.OneRosterService.Utils;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public class CourseFunction : ICourseFunction
    {
        private readonly OneRosterDbContext db;

        public CourseFunction()
        {
            this.db = new OneRosterDbContext();
        }

        public async Task<CourseSetDType> GetAllCourses(
            int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields)
        {
            var entities = await QueryHelper
                .Query(this.db.OR_Course, limit, offset, sort, orderBy, filter);

            return new CourseSetDType
            {
                Courses = CourseMapper.Map(entities, fields)
            }; 
        }

        public async Task<SingleCourseDType> GetCourse(string sourcedId, string fields)
        {
            var entity = await QueryHelper.GetBySourcedId(this.db.OR_Course, sourcedId);
                        
            return new SingleCourseDType
            {
                Course = CourseMapper.Map(entity, fields)
            };
        }
    }
}