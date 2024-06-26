# LTI 1.3 Tool

This is a small LTI 1.3 tool that can be installed.

## TLS Setup

To setup TLS in a development environment it's recommended that you
install [mkcert](https://github.com/FiloSottile/mkcert) which will install a trusted root certificate and then allow a
certificate to be generated for localhost. Once installed run this in the root of the project:

    mkcert -pkcs12 -p12-file config/keystore.p12 localhost

Then start the application with the ssl profile enabled and the LTI tool should be accessible on https://localhost:8443/

## LTI 1.3 Setup

For LTI 1.3 a public/private keypair is needed. To generate one for development use:

    keytool -genkeypair \
      -alias jwt \
      -keyalg RSA \
      -keystore config/jwk.jks \
      -storepass store-pass \
      -dname CN=development

## LTI Reference Implementation Setup

There is a reference implementation for testing LTI integrations available at https://lti-ri.imsglobal.org
which allows you to create a Platform to perform test launches with. These instructions assume you are running the tool
on https://localhost:8443/

### Step 1: Generate public / private key pair for platform

* Open [Generate Keys](https://lti-ri.imsglobal.org/keygen/index) in a new tab and keep this tab open.

### Step 2: Create a Platform (LMS)

* Open [Manage Platforms](https://lti-ri.imsglobal.org/platforms) in a new tab
* Click Add Platform.
* Add a unique name for your Platform.
* Provide a OAuth2 client id. (ex: 12345)
* Add a audience (ex: https://lti-ri.imsglobal.org)
* Set Tool Deep Link Service Endpoint to https://localhost:8443/
* Copy Public key from Generate Keys tab and paste into Platform Public Key field
* Copy Private key from Generate Keys tab and paste into Platform Private Key field
* Run `keytool -list -rfc -keystore config/jwk.jks -alias jwt -storepass store-pass` at the root of the project and copy
  the certificate into to Tool Public Key field.
* Click Save

### Step 3: Add Deployment to Platform

* Find your Platform in the list of Platforms
* View your Platform
* Click Platform Keys
* Click Add Platform Key.
* Create a name for your Platform Key (ex: Key 1)
* Add Deployment ID (ex: 1, you may set up multiple later)
* Click Save

### Step 4: Configure our tool

* Add a oauth registration/provider for the LTI RI platform to `config/application.properties`:

      spring.security.oauth2.client.registration.ims-ri.client-id=oauth-12345
      spring.security.oauth2.client.registration.ims-ri.client-secret=unused
      spring.security.oauth2.client.registration.ims-ri.authorization-grant-type=implicit
      spring.security.oauth2.client.registration.ims-ri.scope=openid
      spring.security.oauth2.client.registration.ims-ri.redirect-uri={baseUrl}/lti/login
      
      spring.security.oauth2.client.provider.ims-ri.authorization-uri=https://lti-ri.imsglobal.org/platforms/343/authorizations/new
      spring.security.oauth2.client.provider.ims-ri.token-uri=https://lti-ri.imsglobal.org/platforms/343/access_tokens
      spring.security.oauth2.client.provider.ims-ri.jwk-set-uri=https://lti-ri.imsglobal.org/platforms/343/platform_keys/333.json
      spring.security.oauth2.client.provider.ims-ri.user-name-attribute=sub

* Update OAuth2 client id (`spring.security.oauth2.client.registration.ims-ri.client-id`), same value as Platform
  above (ex: 12345)

* In Platform tab, navigate to your platform
* Click View Platform
* Click Platform Keys
* Copy well-known/jwks URL endpoint
* Update JWT URI (`spring.security.oauth2.client.provider.ims-ri.jwk-set-uri`) with the copied value.

* In Platform tab, navigate to your platform
* Copy the OAuth2 Access Token URL value
* Update Token URI (`spring.security.oauth2.client.provider.ims-ri.token-uri`) with the copied value.
* Copy the OIDC Auth URL from Platform Page
* Update Authorization URI (`spring.security.oauth2.client.provider.ims-ri.authorization-uri`) with the copied value.

Step 5: In Platform tab, view your Platform

* Click Courses
* Click Add Course
* Populate course values in form
* Click save

* Navigate back and view your Platform
* Click Resource Links
* Populate resource link values in form
* For Tool link url, use https://localhost:8443/
* For Login initiation url, use https://localhost:8443/lti/login_initiation/ims-ri
* Click Save

* Navigate and view your Platform
* Click Resource Links
* Click Select User for Launch
* Click on Launch Resource Link (OIDC) for a user
* Click on Post request
* Click on Launch Resource Link
* Click on Perform Launch
* If configuration is setup correctly, you should see Successful Launch at top of page

Deploy in server

```text
docker build -t lti-dev .
docker run --name lti-server-dev -p 443:8443 lti-dev -d
```
