"""Quick proof-of-concept for getting BPM for tracks in a user's library."""
import sys
import spotipy  # pylint: disable=import-error

# this sets the scope for our user access token to allow us to view their saved tracks
SCOPE = "user-library-read"


def main():
    """Get the most recent 50 tracks saved by a user and prints their BPMs."""
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: %s username" % (sys.argv[0],))
        sys.exit()

    token = spotipy.util.prompt_for_user_token(username, SCOPE)

    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_saved_tracks(limit=50)
        ids = [item["track"]["id"] for item in results["items"]]
        audio_features = sp.audio_features(ids)
        for track in audio_features:
            print(f"Spotify track URI: {track['uri']}\nBPM: {track['tempo']}\n")
    else:
        print("Can't get token for", username)


if __name__ == "__main__":
    main()
