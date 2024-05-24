using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Course;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public interface ICourseFunction
    {
        Task<CourseSetDType> GetAllCourses(int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields);

        Task<SingleCourseDType> GetCourse(string sourcedId, string fields);
    }
}
