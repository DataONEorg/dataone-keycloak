from flask_oidc import OpenIDConnect
from flask import Flask, session, g

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': '4ac081c6-9e80-11f0-afb5-4e1c2cda7276',  # Replace with a strong secret key
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',  # Path to your OIDC client configuration
    'OIDC_SCOPES': ['openid', 'email', 'profile'],  # Requested OIDC scopes
    'OIDC_REDIRECT_URI': 'https://api.test.dataone.org/kctest', # Your application's redirect URI
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})
oidc = OpenIDConnect(app)

@app.route('/kctest')
def index():
    if oidc.user_loggedin:
        user_info = oidc.user_getinfo(['email', 'profile'])
        return f"Hello, {user_info.get('email')}!"
        # return 'Welcome %s' % session["oidc_auth_profile"].get('email')
    else:
        return 'Welcome! Please <a href="/login">login</a>.'


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
    app.run(host="0.0.0.0", port=int("4000"), debug=True)