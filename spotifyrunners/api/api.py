"""REST API for spotify-runners."""
import flask
import spotipy
from flask import jsonify
import spotifyrunners


# this sets the scope for our user access token to allow us to view their saved tracks
SCOPE = "user-library-read playlist-modify-public"


@spotifyrunners.app.route("/api/v1/create", methods=["GET", "POST"])
def get_tracks():
    """Return up to 50 tracks from users library that match a given bpm +/- 5 bpm."""
    context = {}
    if flask.request.method == "POST":
        request_info = flask.request.form
        username = (
            request_info["username"]
            if "username" in request_info
            else "d109pti75pqyij348fp3v3ho9"
        )
        bpm = int(request_info["bpm"]) if "bpm" in request_info else 125

        print("Welcome to Spotify Running! Please log in using your browser.")
        token = spotipy.util.prompt_for_user_token(username, SCOPE)

        print("Username:", username)
        print("BPM:", bpm)

        if token:
            sp = spotipy.Spotify(auth=token)

            # get the IDs of all saved tracks for the logged in user
            print("Analyzing your library...")
            ids = []
            current_results = sp.current_user_saved_tracks(limit=50)
            while current_results:
                current_results = sp.next(current_results)
                if current_results:
                    ids.append(
                        [item["track"]["id"] for item in current_results["items"]]
                    )

            # get the audio features (including BPM) for each saved track
            features_list = []
            for id_group in ids:
                features_list.append(sp.audio_features(id_group))

            print("Finding songs that match your BPM...")
            bpm_matches = []
            for lst in features_list:
                for track in lst:
                    # if this is within 5 of our desired BPM on either side, we grab it
                    if -5 <= track["tempo"] - bpm <= 5:
                        bpm_matches.append(track["uri"])
            if bpm_matches:
                print("Creating a playlist for all the songs we've found!")
                new_playlist = sp.user_playlist_create(
                    username, f"Spotify Running at {bpm} BPM"
                )
                bpm_chunks = [
                    bpm_matches[x : x + 100] for x in range(0, len(bpm_matches), 100)
                ]
                for chunk in bpm_chunks:
                    sp.user_playlist_add_tracks(username, new_playlist["id"], chunk)
                print("All done! Check out your new Spotify Running playlist.")
                context = {"status": "created"}
            else:
                print("No songs match. Sorry :/")
                context = {"status": "no matches"}
            return flask.jsonify(**context)

    # if it's a GET request, just redirect them to the index page
    return flask.redirect(flask.url_for("show_index"))
