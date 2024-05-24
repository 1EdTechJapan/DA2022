{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.ClientCredentials.AccessToken where

import Data.OpenApi (ToParamSchema, ToSchema)
import Network.URI (URI)

data Request = Request
  { grantType :: Text,
    scope :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (ToParamSchema, ToSchema)

data SuccessResponse = SuccessResponse
  { accessToken :: Text,
    tokenType :: Text,
    expiresIn :: Int,
  }
  deriving stock (Eq, Show)
  deriving newtype (ToParamSchema, ToSchema)
