{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.AuthorizationCode.AccessToken where

import Data.Aeson (FromJSON, ToJSON)
import Data.OpenApi (ToParamSchema, ToSchema)
import Network.URI (URI)

data Request = Request
  { grantType :: Text,
    code :: Text,
    redirectUri :: Maybe Text,
    clientId :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (FromJSON, ToParamSchema, ToSchema)

data SuccessResponse = SuccessResponse
  { accessToken :: Text,
    tokenType :: Text,
    expiresIn :: Maybe Int,
    scope :: Maybe Text
  }
  deriving stock (Eq, Show)
  deriving newtype (ToJSON, ToParamSchema, ToSchema)
