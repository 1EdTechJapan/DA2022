module Lti.ResourceLinkRequest where

import Data.UnixTime(UnixTIme)
import Data.Text(Text)
import Network.URI(URI)
import Text.EmailAddress(EmailAddress)
import qualified Lti.Claim.Context as Context
import qualified Lti.Claim.ResourceLink as ResourceLink
import qualified Lti.Claim.ToolPlatform as ToolPlatform
import qualified Lti.Claim.LaunchPresentation as LaunchPresentation
import qualified Lti.Claim.Lis as Lis

data Message = Massage
  {
    iss :: Text,
    sub :: Maybe Text,
    aud :: Text,
    ext :: UnixTime,
    iat :: UnixTime,
    azp :: Text,
    none :: Text,
    name :: Text,
    givennName :: Text,
    middleName :: Text,
    picture :: URI,
    email :: EmailAddress,
    locale :: Text,
    deploymentId :: Text,
    message_type :: Text,
    version :: Text,
    roles :: Vector URI,
    role_scope_mentor :: Maybe Vector URI,
    context :: Maybe Context.Context,
    resourceLink :: ResourceLink.ResourceLink,
    toolPlatform :: Maybe ToolPlatform.ToolPlatform,
    targetLinkUri :: URI,
    launchPresentation :: Maybe LaunchPresentation.LaunchPresentation,
    lis :: Maybe Lis.Lis
  }
