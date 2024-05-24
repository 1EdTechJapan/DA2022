using System;

namespace EduKoumu.OneRosterService.Exceptions
{
    public class UnknownObjectException : Exception
    {
        public UnknownObjectException(string message) : base(message)
        {
        }
    }
}