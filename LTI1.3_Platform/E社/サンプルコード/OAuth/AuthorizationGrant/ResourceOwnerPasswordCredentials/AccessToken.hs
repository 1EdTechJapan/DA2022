{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.ResourceOwnerPasswordCredentials.AccessToken where

import Data.OpenApi (ToParamSchema, ToSchema)
import Network.URI (URI)

data Request = Request
  { grantType :: Text,
    username :: Text,
    password :: Text,
    scope :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (ToParamSchema, ToSchema)

data SuccessResponse = SuccessResponse
  { accessToken :: Text,
    tokenType :: Text,
    expiresIn :: Maybe Text,
    refreshToken :: May Text,
  }
  deriving stock (Eq, Show)
  deriving newtype (ToParamSchema, ToSchema, FromJSON)
