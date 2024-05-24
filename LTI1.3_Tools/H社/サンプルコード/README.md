# LANGX LTI Server Sample
---

## 1. Overall
### 1.1 src directry
- ``app.py``: main code of LTI server using PyLTI1p3
    - ``login()``: validate init. login request, create auth. request and redirect target link uri.
    - ``launch()``: receive and validate auth. response and dender the tool.<br><br>
- ``validation.py``: validation program of token_id
    - ``validate_token_id(token_id: dict)``: validate sub, role, context, target_link_uri, tool_platform and custom parameters.
        - ``validate_sub(sub: str)``: check whether sub is valid uuid4
        - ``validate_role(role: List[str])``: check whether role is valid
        - ``validate_context(context: dict)``: check whether context id is not empty
        - ``validate_target_link_uri(target_link_uri: str)``: check whether target_link_uri is not empty
        - ``validate_tool_platform(tool_platform: dict)``: check whether guid is valid if there is tool_platform parameters in an auth. response.
        - ``validate_custom(custom: dict)``: check whether grade value is valid if there is custom grade parameter in an auth. response.

### 1.2 configs directry
- ``config.json``: setting of platforms
    ```json
    {   
        // key name should be iss (platform_id)
        "iss_example": [{
            "default": true, // This config value is used if cliend_id is not passed on the login step
            "client_id": "example_client", // client_id
            "auth_login_url": "https://example.com/login", // auth_login_url
            "auth_token_url": "https://example.com/auth", // auth_token_url
            "key_set_url": "https://example.com/jwks", // url of platform's jwks
            "key_set": null, // platform's public key as jwks style
            "private_key_file": "tool_private.key", // path of tool's private key
            "public_key_file": "tool_public.key", // path of tool's public key
            "deployment_ids": ["example_deploymet"] // deployment_ids
        }]
    }
    ```

## 2. System requirements

- Python version
```
Python v3.9.6
```

- Modules
```
Flask==2.2.2
Flask-Caching==2.0.1
Flask-Session2==1.3.1
PyLTI1p3==2.0.0
```

## 3. Project setup

```sh
$ pip install -r requirements.txt
$ cd src
$ python app.py
```