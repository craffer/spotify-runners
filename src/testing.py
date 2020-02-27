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

        # get the IDs of all saved tracks for the logged in user
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

        for lst in features_list:
            for track in lst:
                print(f"Spotify track URI: {track['uri']}\nBPM: {track['tempo']}\n")
    else:
        print("Can't get token for", username)


if __name__ == "__main__":
    main()
