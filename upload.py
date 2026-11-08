"""Publication YouTube (API Data v3).

Première fois (une seule fois) :
    python3 upload.py auth            -> affiche un lien ; ouvre-le, accepte,
                                         puis colle l'adresse de la page finale
Ensuite :
    python3 upload.py video.mp4 meta.json   -> envoie la vidéo, renvoie son ID

Fichiers secrets (jamais publiés en public) :
    secrets/client_secret.json   (téléchargé depuis Google Cloud)
    secrets/token.json           (créé par « auth »)
meta.json : {"title", "description", "tags", "publishAt" (ISO, optionnel),
             "thumbnail" (optionnel)}
"""
import json, sys, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

HERE = os.path.dirname(os.path.abspath(__file__))
SECRET = os.path.join(HERE, "secrets", "client_secret.json")
TOKEN = os.path.join(HERE, "secrets", "token.json")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]


def auth():
    flow = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES, redirect_uri="http://localhost:8765/")
    url, _ = flow.authorization_url(access_type="offline", prompt="consent")
    print("Ouvre ce lien, accepte, puis colle ici l'adresse complète de la page d'arrivée :\n" + url)
    resp = input("> ").strip()
    flow.fetch_token(authorization_response=resp.replace("http://", "https://"))
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    open(TOKEN, "w").write(flow.credentials.to_json())
    print("OK, jeton enregistré.")


def service():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds.valid:
        creds.refresh(Request())
        open(TOKEN, "w").write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload(path, meta):
    yt = service()
    status = {"privacyStatus": "private" if meta.get("publishAt") else "public",
              "selfDeclaredMadeForKids": True, "embeddable": True}
    if meta.get("publishAt"):
        status["publishAt"] = meta["publishAt"]
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:5000],
                        "tags": meta.get("tags", []), "categoryId": "10",  # Musique
                        "defaultLanguage": "fr", "defaultAudioLanguage": "fr"},
            "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(path, chunksize=8 << 20, resumable=True))
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            print(f"envoi {int(st.progress() * 100)} %")
    vid = resp["id"]
    if meta.get("thumbnail"):
        try:
            yt.thumbnails().set(videoId=vid, media_body=meta["thumbnail"]).execute()
        except Exception as e:
            print("miniature non posée :", e)
    print("VIDEO_ID", vid, resp["status"].get("privacyStatus"), resp["status"].get("uploadStatus"))
    return vid


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    if sys.argv[1] == "auth":
        auth()
    else:
        upload(sys.argv[1], json.load(open(sys.argv[2])))
