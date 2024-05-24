using System;

namespace EduKoumu.OneRosterService.Exceptions
{
    public class UnauthorisedException : Exception
    {
        public UnauthorisedException(string message) : base(message)
        {
        }
    }
}