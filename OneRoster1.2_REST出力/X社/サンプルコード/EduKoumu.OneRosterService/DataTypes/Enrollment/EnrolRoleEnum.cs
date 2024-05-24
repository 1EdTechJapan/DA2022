using System.Runtime.Serialization;

namespace EduKoumu.OneRosterService.DataTypes.Enrollment
{
    public enum EnrolRoleEnum
    {
        administrator = 1,

        proctor = 2,

        student = 3,

        teacher = 4,

        [EnumMember(Value = "ext:guardian")]
        guardian = 5,
    }
}