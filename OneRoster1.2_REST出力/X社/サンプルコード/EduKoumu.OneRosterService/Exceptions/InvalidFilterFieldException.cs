using System;

namespace EduKoumu.OneRosterService.Exceptions
{
    public class InvalidFilterFieldException : Exception
    {
        public InvalidFilterFieldException(string message) : base(message)
        {
        }
    }
}