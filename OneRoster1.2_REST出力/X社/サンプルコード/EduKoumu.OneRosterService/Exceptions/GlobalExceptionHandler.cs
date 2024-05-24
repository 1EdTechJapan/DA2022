using EduKoumu.OneRosterService.DataTypes.Imsx;
using log4net;
using System;
using System.Net;
using System.Net.Http;
using System.Reflection;
using System.Web.Http.ExceptionHandling;
using System.Web.Http.Results;

namespace EduKoumu.OneRosterService.Exceptions
{
    public class GlobalExceptionHandler : ExceptionHandler
    {
        private static readonly ILog logger = LogManager.GetLogger(MethodBase.GetCurrentMethod().DeclaringType);


        public override void Handle(ExceptionHandlerContext context)
        {
            HttpStatusCode httpStatusCode;

            var imsxStatusInfoDType = new Imsx_StatusInfoDType
            {
                Imsx_description = GetExceptionMessage(context.Exception),
                Imsx_codeMajor = Imsx_StatusInfoDTypeImsx_codeMajor.failure,
                Imsx_severity = Imsx_StatusInfoDTypeImsx_severity.error,
            };

            // Access Exception using context.Exception;
            switch (context.Exception.GetType().Name)
            {
                case nameof(InvalidSelectionFieldException):
                case nameof(InvalidFilterFieldException):
                    httpStatusCode = HttpStatusCode.BadRequest; // 400
                    break;  

                case nameof(UnauthorisedException):
                    httpStatusCode = HttpStatusCode.Unauthorized; // 401
                    break;

                case nameof(ForbiddenException):
                    httpStatusCode = HttpStatusCode.Forbidden; // 403
                    break;

                case nameof(UnknownObjectException):
                    httpStatusCode = HttpStatusCode.NotFound; //404
                    break;

                case nameof(UnprocessableEntityException):
                    httpStatusCode = (HttpStatusCode)422; //422
                    break;

                case nameof(TooManyRequestException):
                    httpStatusCode = (HttpStatusCode)429; //429
                    break;
                    
                default:
                    httpStatusCode = HttpStatusCode.InternalServerError; // 500
                    break;
            }

            var response = context.Request.CreateResponse(httpStatusCode, imsxStatusInfoDType);
            context.Result = new ResponseMessageResult(response);

            logger.Error(imsxStatusInfoDType.Imsx_description);
        }

        private string GetExceptionMessage(Exception e)
        {
            if (e.InnerException == null)
            {
                return e.Message;
            }

            return e.Message + GetExceptionMessage(e.InnerException);
        }
    }
}