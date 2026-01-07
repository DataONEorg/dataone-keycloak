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

@app.route('/kctest')
def index():
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['email', 'profile'])
        return f"<h3>Hello, {user_info.get('email')}!</h3> <br> <p>Please visit the <a href='/kctest/info'>user info page</a> to see more details.</p>"
        # return 'Welcome %s' % session["oidc_auth_profile"].get('email')
    else:
        return '<h3>Welcome!</h3> Please <a href="/kctest/login">login</a>.'


@app.route('/kctest/login')
@oidc.require_login
def login():
    return 'Welcome %s' % session["oidc_auth_profile"].get('email')


@app.route('/kctest/info')
def user_info():
    # This uses the user instance at g.oidc_user instead
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

        return f"<h3>Hello, {name}!</h3> <br> <ul> <li><strong>Access token:</strong> {access_token} </li> <li><strong>Refresh token:</strong> {refresh_token} </li> <li><strong>Groups:</strong> {groups} </li> <li><strong>Unique ID:</strong> {unique_id} </li> </ul> <br> <h3>Profile from g.oidc_user:</h3> {profile_list_1} <br> <h3>Profile from session['oidc_auth_profile']:</h3> {profile_list_2}"
    else:
        return '<h3>Not logged in</h3>'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("4000"), debug=True)
