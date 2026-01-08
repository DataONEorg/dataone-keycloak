'''
A simple Flask application demonstrating OpenID Connect (OIDC) authentication
using the flask-oidc library against a keycloak server. The application includes 
routes for logging in and accessing protected resources.
'''

import os
import jwt
import requests

from flask_oidc import OpenIDConnect
from flask import Flask, session, g

app = Flask(__name__)

params = {}
params['FLASK_SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(32).hex())

app.config.update({
    'OIDC_CLIENT_SECRETS': './client_secrets.json',
    'SECRET_KEY': params['FLASK_SECRET_KEY']
})

oidc = OpenIDConnect(app)

@app.route('/kctest')
def index():
    """
    Display a welcome message based on the user's login status.
    """
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['email', 'profile'])
        return f"<h3>Hello, {user_info.get('email')}!</h3> <p>Please visit the <a href='/kctest/info'>user info page</a> to see more details.</p>"
        # return 'Welcome %s' % session["oidc_auth_profile"].get('email')
    else:
        return '<h3>Welcome!</h3> Please <a href="/kctest/login">login</a>.'


@app.route('/kctest/login')
@oidc.require_login
def login():
    """
    Handle user login via OIDC and display a welcome message.
    """
    profile = session["oidc_auth_profile"]
    return f"<h3>Welcome {profile.get('email')}!</h3> <p>Please visit the <a href='/kctest/info'>user info page</a> to see more details.</p>"


@app.route('/kctest/info')
def user_info():
    """
    Display detailed user information if logged in.
    """
    if g.oidc_user.logged_in:
        # Profile from g.oidc_user
        profile_list_1 = "<ul>\n" + "\n".join([f"  <li><strong>{k}:</strong> {v}</li>" for k, v in g.oidc_user.profile.items()]) + "\n</ul>"

        # Profile from session['oidc_auth_profile']
        profile = session["oidc_auth_profile"]
        profile_list_2 = ("<ul>\n" + 
                          "\n".join([f"  <li><strong>{k}:</strong> {v}</li>" for k, v in profile.items()]) + 
                          "\n</ul>")

        name = profile['name']
        access_token = g.oidc_user.access_token
        refresh_token = g.oidc_user.refresh_token
        groups = g.oidc_user.groups
        unique_id = g.oidc_user.unique_id

        access_claims = decode_token(access_token)
        refresh_claims = decode_token(refresh_token, validate=False)

        return f"<h3>Hello, {name}!</h3> <br> <ul> <li><strong>Access token:</strong> {access_token} </li> <li><strong>Access claims:</strong> {access_claims} </li> <li><strong>Refresh token:</strong> {refresh_token} </li> <li><strong>Refresh claims:</strong> {refresh_claims} </li> <li><strong>Groups:</strong> {groups} </li> <li><strong>Unique ID:</strong> {unique_id} </li> </ul> <br> <h3>Profile from g.oidc_user:</h3> {profile_list_1} <br> <h3>Profile from session['oidc_auth_profile']:</h3> {profile_list_2}"
    else:
        return '<h3>Not logged in</h3>'


def get_jwks_url(issuer_url):
    """
    Find the JWKS URL from the OpenID Connect well-known configuration.
    """
    well_known_url = issuer_url + "/.well-known/openid-configuration"
    with requests.get(well_known_url) as response:
        well_known = response.json()
    if not 'jwks_uri' in well_known:
        raise Exception('jwks_uri not found in OpenID configuration')
    return well_known['jwks_uri']


def decode_token(token, validate=True):
    """
    Decode and validate a JWT using the JWKS from the issuer.
    """
    unvalidated = jwt.decode(token, options={"verify_signature": False})
    if not validate:
        return unvalidated
    # TODO: restrict the issuers that are allowed rather than pulling it from the token
    jwks_url = get_jwks_url(unvalidated['iss'])
    jwks_client = jwt.PyJWKClient(jwks_url)
    header = jwt.get_unverified_header(token)
    key = jwks_client.get_signing_key(header["kid"]).key
    return jwt.decode(token, key, [header["alg"]])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("4000"), debug=True)
