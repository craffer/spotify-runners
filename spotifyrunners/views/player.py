"""spotifyrunners player view."""
import flask
import spotifyrunners


@spotifyrunners.app.route("/player")
@spotifyrunners.app.route("/player/<playlist_id>")
def show_player(playlist_id=None):
    """Display /player route."""
    embed_link = f"https://open.spotify.com/embed/playlist/{playlist_id}"
    context = { "embed_link": embed_link }
    print("in show_player")
    return flask.render_template("player.html", **context)
