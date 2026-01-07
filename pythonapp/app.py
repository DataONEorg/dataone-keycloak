'''
A simple Flask application demonstrating OpenID Connect (OIDC) authentication
using the flask-oidc library against a keycloak server. The application includes 
routes for logging in and accessing protected resources.
'''

import os
from flask_oidc import OpenIDConnect
from flask import Flask, session, g


app = Flask(__name__)

params = {}
params['FLASK_SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(32).hex())

app.config.update({
    'OIDC_CLIENT_SECRETS': './client_secrets.json',
    # 'OIDC_OVERWRITE_REDIRECT_URI': 'https://api.test.dataone.org/kctest/authorize',
    # 'OIDC_CALLBACK_ROUTE': '/kctest/authorize',
    'SECRET_KEY': params['FLASK_SECRET_KEY']
})

oidc = OpenIDConnect(app)

# Works: https://auth.test.dataone.org/auth/realms/DataONE/protocol/openid-connect/auth?client_id=ogdc&response_type=code&redirect_uri=https://api.test.dataone.org/kctest/authorize
# Returns code to: https://api.test.dataone.org/kctest/authorize?session_state=b2161565-3560-4805-b514-12ff88377301&iss=https%3A%2F%2Fauth.test.dataone.org%2Fauth%2Frealms%2FDataONE&code=7abdbc78-6202-4e9d-bf59-ab228ed5f17f.b2161565-3560-4805-b514-12ff88377301.8483d161-ff76-4eb1-9d98-5cfe424e6458

@app.route('/kctest')
def index():
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['email', 'profile'])
        return f"Hello, {user_info.get('email')}!"
        # return 'Welcome %s' % session["oidc_auth_profile"].get('email')
    else:
        return 'Welcome! Please <a href="/kctest/login">login</a>.'


@app.route('/kctest/login')
@oidc.require_login
def login():
    return 'Welcome %s' % session["oidc_auth_profile"].get('email')


@app.route('/kctest/alt')
def alternative():
    # This uses the user instance at g.oidc_user instead
    if g.oidc_user.logged_in:
        return 'Welcome %s' % g.oidc_user.profile.get('email')
    else:
        return 'Not logged in'

if __name__ == "__main__":
    print(oidc.client_secrets)
    print(oidc.accept_token)
    print(params['FLASK_SECRET_KEY'])
    app.run(host="0.0.0.0", port=int("4000"), debug=True)
