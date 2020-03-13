"""REST API for spotify-runners."""
import flask
import spotipy
from flask import jsonify
import spotifyrunners


# this sets the scope for our user access token to allow us to view their saved tracks
SCOPE = "user-library-read playlist-modify-public"


@spotifyrunners.app.route("/api/v1/", methods=["GET"])
def get_tracks(username):
    """
    Return up to 50 tracks from users library that match a given bpm +/-
    5 bpm.
    """
    print("Welcome to Spotify Running! Please log in using your browser.")
    token = spotipy.util.prompt_for_user_token(username, SCOPE)

    if token:
        sp = spotipy.Spotify(auth=token)

        desired_bpm = int(input("Please enter your desired BPM: "))

        # get the IDs of all saved tracks for the logged in user
        print("Analyzing your library...")
        ids = []
        current_results = sp.current_user_saved_tracks(limit=50)
        while current_results:
            current_results = sp.next(current_results)
            if current_results:
                ids.append([item["track"]["id"] for item in current_results["items"]])

        # get the audio features (including BPM) for each saved track
        features_list = []
        for id_group in ids:
            features_list.append(sp.audio_features(id_group))

        print("Finding songs that match your BPM...")
        bpm_matches = []
        for lst in features_list:
            for track in lst:
                # if this is within 5 of our desired BPM on either side, we grab it
                if -5 <= track["tempo"] - desired_bpm <= 5:
                    bpm_matches.append(track["uri"])
        context = {"tracks": bpm_matches}
        if bpm_matches:
            print("Creating a playlist for all the songs we've found!")
            new_playlist = sp.user_playlist_create(username, "Spotify Running")
            bpm_chunks = [
                bpm_matches[x : x + 100] for x in range(0, len(bpm_matches), 100)
            ]
            for chunk in bpm_chunks:
                sp.user_playlist_add_tracks(username, new_playlist["id"], chunk)
            print("All done! Check out your new Spotify Running playlist.")
        else:
            print("No songs match. Sorry :/")

        return flask.jsonify(**context)

    print("Can't get token for", username)
    context = {"message": "Bad Request", "info": "Can't get token", "status_code": 400}
    resp = flask.jsonify(**context)
    resp.status_code = 400
    return resp
