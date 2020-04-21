"""REST API for spotify-runners."""
import flask
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
import json
import os
import random
import spotipy
import spotifyrunners
import spotipy.util as util
import time

# The following are set up to get the REDIRECT_URI, CLIENT_ID, and, CLIENT_SECRET from
# your environment variables. The hardcoded values commented below each variable are
# the credentials from the developer account we created (USR: jshelata15951@gmail.com PWD: spotifyrunners)
# https://developer.spotify.com/dashboard/
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
# REDIRECT_URI = 'http://localhost:8000/api_callback'
# If you want to access the site from a mobile device, change localhost above
# to your local IP address on your home network and register the address with
# our Spotify developer account (USR: jshelata15951@gmail.com PWD: spotifyrunners).
# Once logged in our app is called spotify-runners-dev. Click on it, click edit settings,
# and add your address to Redirect URIs
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
# CLIENT_ID = '50074660d1ea4113bb817049604c3613'
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
# CLIENT_SECRET = '68111ce410784a65a6173d3fe47c9f01'
CACHE = ".cache-"
# this sets the scope for our user access token to allow us to view their saved tracks
SCOPE = "user-library-read user-top-read playlist-modify-public"
# Set this to True for testing but you probaly want it set to False in production.
SHOW_DIALOG = False


@spotifyrunners.app.route("/api/v1/create", methods=["GET", "POST"])
def get_tracks():
    """Return up to 50 tracks from users library that match a given bpm +/- 5 bpm."""
    context = {}
    if flask.request.method == "POST":
        # get data from form request
        request_info = flask.request.form
        username = request_info["username"]
        # save username in session
        session["username"] = username

        # make sure the user is logged in
        session["token_info"], authorized = get_token(session)
        session.modified = True
        # redirect to login if token not valid
        # user can try submit another request once they have authenticated
        if not authorized:
            return redirect("/login")
        sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))
        bpm = int(request_info["bpm"]) if "bpm" in request_info else 125

        print("Username:", username)
        print("BPM:", bpm)

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
                # also checks the track's energy value to keep all songs upbeat
                if -5 <= track["tempo"] - bpm <= 5 and track["energy"] > 0.8:
                    bpm_matches.append(track["uri"])
        # if there are less than 20 matches, recommend some songs
        if len(bpm_matches) < 20:
            # get top 3 tracks from this user's short term time range
            top_tracks = sp.current_user_top_tracks(limit=3, time_range="short_term")
            top_tracks_ids = [top_tracks["items"][index]["id"] for index in range(3)]
            # get top 2 artists from this user's short term time range
            top_artists = sp.current_user_top_artists(limit=2, time_range="short_term")
            top_artists_ids = [top_artists["items"][index]["id"] for index in range(2)]
            # use those to seed recommendations
            recommendations = sp.recommendations(
                seed_artists=top_artists_ids,
                seed_tracks=top_tracks_ids,
                limit=20 - len(bpm_matches),
                min_tempo=bpm - 5,
                max_tempo=bpm + 5,
                min_energy=0.8,
            )
            rec_track_ids = [
                recommendations["tracks"][index]["id"]
                for index in range(len(recommendations["tracks"]))
            ]
            # add recommended songs to the list
            bpm_matches.extend(rec_track_ids)
        # if we have songs, continue
        if bpm_matches:
            # added random shuffle to make the playlist look better since artists
            # were being grouped together
            random.shuffle(bpm_matches)
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
            playlist_id = new_playlist["uri"].split(":")[2]
            context = {"status": "created"}
        else:
            # TODO: make an error page or display some better text
            # probably not actually necessary for our full demo
            print("No songs match. Sorry :/")
            context = {"status": "no matches"}
            return context
        return flask.redirect(flask.url_for("show_player", playlist_id=playlist_id))
    else:
        # if it's a GET request, just redirect them to the index page
        return flask.redirect(flask.url_for("show_index"))


# route for user login
@spotifyrunners.app.route("/login")
def verify():
    """Route for initial user login."""
    username = session.get("username")
    # Don't reuse a SpotifyOAuth object because they store token info
    # and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE + username,
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@spotifyrunners.app.route("/api_callback")
def api_callback():
    """Handle redirect from Spotify authentication server and grab code."""
    username = session.get("username")
    # Don't reuse a SpotifyOAuth object because they store token info
    # and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE + username,
    )
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info

    return flask.redirect(flask.url_for("show_index"))


def get_token(session):
    """Check to see if token is valid and get a new token if not."""
    username = session.get("username")
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    # if not, we cannot refresh so user must authenticate
    if not session.get("token_info", False):
        token_valid = False
        return token_info, token_valid
    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get("token_info").get("expires_at") - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        return token_info, False
        # Don't reuse a SpotifyOAuth object because they store token
        # info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE + username,
        )
        token_info = sp_oauth.refresh_access_token(
            session.get("token_info").get("refresh_token")
        )

    token_valid = True
    return token_info, token_valid
