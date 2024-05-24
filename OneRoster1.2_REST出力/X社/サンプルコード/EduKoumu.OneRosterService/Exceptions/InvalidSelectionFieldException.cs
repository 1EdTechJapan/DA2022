using System;

namespace EduKoumu.OneRosterService.Exceptions
{
    public class InvalidSelectionFieldException : Exception
    {
        public InvalidSelectionFieldException(string message) : base(message)
        {
        }
    }
}