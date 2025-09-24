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
    print(token)
    session["refresh_token"] = token["refresh_token"]
    session["JWT"] = token["access_token"]
    session["user_info"] = keycloak_openid.userinfo(token["access_token"])
    print(session["user_info"])
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
    return render_template("logged.html", 
                           email=session["user_info"]["email"],
                           name=session["user_info"]["given_name"], 
                           lastname=session["user_info"]["family_name"], 
                           realmrole=session["user_info"]["sub"],
                           token=session["JWT"],
                           refreshtoken=session["refresh_token"])


@app.route("/logout")
def logout():
    return "The logout page is not implemented yet"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
