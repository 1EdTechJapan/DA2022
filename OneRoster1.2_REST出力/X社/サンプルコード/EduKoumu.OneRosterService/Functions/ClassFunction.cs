using EduKoumu.OneRosterService.DataModels;
using EduKoumu.OneRosterService.DataTypes;
using EduKoumu.OneRosterService.DataTypes.Class;
using EduKoumu.OneRosterService.Mappers;
using EduKoumu.OneRosterService.Utils;
using System.Threading.Tasks;

namespace EduKoumu.OneRosterService.Functions
{
    public class ClassFunction : IClassFunction
    {
        private readonly OneRosterDbContext db;

        public ClassFunction()
        {
            this.db = new OneRosterDbContext();
        }

        public async Task<ClassSetDType> GetAllClasses(
            int? limit, int? offset, string sort, OrderByEnum? orderBy, string filter, string fields)
        {
            var entities = await QueryHelper
                .Query(this.db.OR_Class, limit, offset, sort, orderBy, filter);

            return new ClassSetDType
            {
                Classes = ClassMapper.Map(entities, fields)
            };
        }

        public async Task<SingleClassDType> GetClass(string sourcedId, string fields)
        {
            var entity = await QueryHelper.GetBySourcedId(this.db.OR_Class, sourcedId);

            return new SingleClassDType
            {
                Class = ClassMapper.Map(entity, fields)
            };
        }
    }
}