from flask import Flask, render_template, redirect, request, session
from keycloak import KeycloakOpenID
import os

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_URL"),
    realm_name=os.getenv("KEYCLOAK_REALM"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET"),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logged")
def logged():
    return render_template("logged.html")


@app.route("/callback")
def callback():
    token = keycloak_openid.token(
        # Code fourni en query parameter lors de la redirection vers /callback
        code=request.args.get("code"),
        grant_type="authorization_code",
        redirect_uri="http://localhost:8081/callback"
    )
    session["JWT"] = keycloak_openid.userinfo(token["access_token"])
    print(session["JWT"])
    return redirect("/account")



@app.route("/login")
def login():
    return redirect(
        keycloak_openid.auth_url(
            # URL vers laquelle Keycloak doit rediriger l'utilisateur après la connexion
            redirect_uri="http://localhost:8081/callback",
            scope="openid profile email"
        )
    )


@app.route("/account")
def account():
    return "The account page is not implemented yet"


@app.route("/logout")
def logout():
    return "The logout page is not implemented yet"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
