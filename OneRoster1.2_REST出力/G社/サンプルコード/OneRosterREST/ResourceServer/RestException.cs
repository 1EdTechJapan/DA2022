using System;
using System.Net;

namespace ResourceServer
{
    public class RestException : Exception
    {
        public HttpStatusCode statusCode;
        public string exceptionName;
        public string exceptionValue;

        public RestException(HttpStatusCode statusCode, string exceptionName, string exceptionValue)
        {
            this.statusCode = statusCode;
            this.exceptionName = exceptionName;
            this.exceptionValue = exceptionValue;
        }
    }
}