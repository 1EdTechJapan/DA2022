module LTI.Claim.ToolPlatform where

import Data.Text (Text)
import Network.URI (URI)
import Data.Vector (Vector)
import Text.EmailAddress(EmailAddress)

data ToolPlatform = ToolPlatform
  { guid :: Text,
    contactEmail :: Maybe EmailAddress,
    description :: Maybe Text,
    name :: Maybe Text,
    url :: Maybe URI,
    productFamilyCode :: Maybe Text,
    version :: Maibe Text
  }
