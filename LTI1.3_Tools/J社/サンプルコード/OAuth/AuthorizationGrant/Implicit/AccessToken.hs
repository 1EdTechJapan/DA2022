{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.Implicit.AccessToken where

import Data.OpenApi (ToParamSchema, ToSchema)
import Network.URI (URI)

data SuccessResponse = SuccessResponse
  { accessToken :: Text,
    tokenType :: Text,
    expiresIn :: Maybe Int,
    scope :: Maybe Text,
    state :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (ToParamSchema, ToSchema)

data Error
  = InvalidRequest
  | InvalidClient
  | AccessDenied
  | UnsupportedResponseType
  | InvalidScope
  | ServerError

data ErrorResponse = ErrorResponse
  { error :: Error,
    errorDescription :: Text,
    errorUri :: URI,
    state :: Maybe Text
  }
