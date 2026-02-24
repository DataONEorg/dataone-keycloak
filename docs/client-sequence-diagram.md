# OIDC Client Sequence Diagrams

Typical sequence diagrams for client authentication and authorization using Keycloak as an OIDC service, with ORCID configured as a 3rd-party Identity Provider.

## Authentication: Confidential clients

This sequence is for confidential clients, e.g., server applications that can securely store a client identifier and client secret and transmit those to Keycloak without exposing them to the user.

This sequence shows a browser app requesting to login at a server application, which redirects the browser first to the keycloak login page, and then to the ORCID login page when the user requests that IdP. The user then logs into ORCID, which redirects the user to the Keycloak redirect endpoint, and Keycloak retrieves the associated orcid tokens, registers the user in LDAP if needed, and then redirects the user back to the server app redirect endpoint. At this point the user sends the code to the server redirect endpoint, which collects the access_token and refresh token from Keycloak, and returns them to the browser to use in subsequent requests.

```mermaid
sequenceDiagram
    
    participant Browser
    participant server_app
    participant keycloak
    participant ORCID
    participant d1_account

    Browser->>+server_app: GET /login
    server_app->>-Browser: 302 Redirect to keycloak login page
    
    Browser->>+keycloak: GET /realms/dataone/protocol/openid-connect/auth (response_type, client_id, redirect_uri, scope, state, nonce)
    keycloak->>-Browser: 302 Redirect to ORCID login page

    rect rgb(191, 223, 255)

    Browser->>+ORCID: GET /oauth/authorize (scope=/read-limited, state, response_type=code, client_id, redirect_uri)
    ORCID->>-Browser: 302 Redirect to keycloak

    Browser->>+keycloak: GET /realms/dataone/broker/orcid/endpoint (code, state)
    
    keycloak->>+ORCID: GET /token
    ORCID->>-keycloak: access_token, refresh_token

    keycloak->>+d1_account: registerAccount(person)
    d1_account->>-keycloak: response

    keycloak->>-Browser: 302 Redirect to server_app

    end
    
    Browser->>+server_app: GET /authorize (codestate, session_state, iss, code)
    server_app->>+keycloak: GET /token
    keycloak->>-server_app: access_token, refresh_token
    server_app->>-Browser: access_token, refresh_token
```

## Authorization with OIDC tokens

Once we have an OIDC token, we can send it to any DataONE service that knows how to validate OIDC tokens. If the access token is expired or is about to expire, we can use the refresh token to get a new access token.


```mermaid
sequenceDiagram
        
    Browser->>+server_app: Get /oidc_protected (access_token)
    server_app->>-Browser: : 200 Return resource

    Browser->>+keycloak: GET /realms/dataone/protocol/openid-connect/token (refresh_token)
    keycloak->>-Browser: access_token, refresh_token

    Browser->>+server_app: Get /oidc_protected (access_token)
    server_app->>-Browser: : 200 Return resource

```


## Exchange OAuth access token for D1Token

Once we have an OIDC token, we can use that to exchaneg it for a historical DataONE token, which can be sent to any DataONE service that does not know how to use OIDC tokens. If the DataONE token is expired, we can use a valid OIDC access_token to retrieve a new DataONE token.

```mermaid
sequenceDiagram
    
    Browser->>+d1_portal: GET /token (access_token)
    d1_portal->>d1_portal: validateAccessToken(access_token)
    d1_portal-->>-Browser: 200 DataONE_JWT
    
    Browser->>+server_app: Get /protected (DataONE_JWT)
    server_app->>-Browser: : 200 OK
```

## Authentication: Public clients

Authentication for public clients proceeds similarly to confidential clients, but instead of a client id and secret, the application uses a PKCE challenge to establish continuity of identity.


