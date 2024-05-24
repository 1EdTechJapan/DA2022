{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.AuthorizationCode.Authorization where

import Data.OpenApi (ToParamSchema, ToSchema)
import Network.URI (URI)

data Request = Request
  { responseType :: Text,
    clientId :: Text,
    redirectUri :: Maybe URI,
    scope :: Maybe Text,
    state :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (FromHttpApiData, ToHttpApiData, ToParamSchema, ToSchema)

data AuthorizedResponse = AuthorizedResponse
  { code :: Text,
    state :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (FromHttpApiData, ToHttpApiData, ToParamSchema, ToSchema)

data AuthorizationError
  = InvalidRequest
  | UnauthorizedClient
  | AccessDenied
  | UnsupportedResponceType
  | InvalidScope
  | ServerError

data UnauthorizedResponse = UnauthorizedResponse
  { error :: AuthorizationError,
    errorDescription :: Text,
    errorUri :: URI,
    state :: Maybe Text
  }
