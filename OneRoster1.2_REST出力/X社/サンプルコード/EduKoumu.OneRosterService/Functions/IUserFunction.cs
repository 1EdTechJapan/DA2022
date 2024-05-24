using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.User;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public interface IUserFunction
    {
        Task<UserSetDType> GetAllUsers(int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields, RoleEnum? role = null);

        Task<SingleUserDType> GetUser(string sourcedId, string fields, RoleEnum? role = null);
    }
}