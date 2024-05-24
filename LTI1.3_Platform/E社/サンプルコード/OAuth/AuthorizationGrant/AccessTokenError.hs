{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

module OAuth.AuthorizationGrant.AccessTokenError where

import Data.Aeson (ToFromJSON)
import Data.OpenApi (ToParamSchema, ToSchema)
import Data.Text (Text)
import GHC.Generics (Generic)
import Network.URI (URI)
import Text.Casing (fromHumps, toSnake)

data Error
  = InvalidRequest
  | InvalidClient
  | InvalidGrant
  | UnauthorizedClient
  | UnsupportedGrantType
  | InvalidScope
  deriving stock (Show)

data ErrorResponse = ErrorResponse
  { error :: Error,
    errorDescription :: Text,
    errorUri :: URI
  }
  deriving stock (Show)
  deriving newtype (ToParamSchema, ToSchema)

instance FromJSON ErrorResponse where
  toJSON (ErrorResponse error desc uri) =
    object
      [ "error" .= error,
        "error_description" .= desc,
        "error_uri" .= (toSnake $ fromHumps $ show uri)
      ]

instance ToJSON ErrorResponse where
  toJSON (ErrorResponse error desc uri) =
    object
      [ "error" .= (toSnake $ fromHumps $ show error),
        "error_description" .= desc,
        "error_uri" .= (show uri)
      ]

-- instance FromForm TokenRequest where
--   fromForm = genericFromForm $ applyForm snakeCase

-- instance ToJSON TokenRequest where
--   toJSON :: TokenRequest -> Value
--   toJSON = genericToJSON $ applyJson snakeCase
