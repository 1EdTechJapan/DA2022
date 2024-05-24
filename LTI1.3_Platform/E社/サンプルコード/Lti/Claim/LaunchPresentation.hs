module LTI.Claim.LaunchPresentation where

import Data.Text (Text)
import Network.URI (URI)
import Data.Vector (Vector)

data LaunchPresentation = LaunchPresentation
  { documentTarget :: Text,
    height :: Int,
    width :: Int,
    return_url :: URI
  }
