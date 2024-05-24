using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Class;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public interface IClassFunction
    {
        Task<ClassSetDType> GetAllClasses(int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields);

        Task<SingleClassDType> GetClass(string sourcedId, string fields);
    }
}
