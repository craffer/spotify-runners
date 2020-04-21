"""spotifyrunners bpm generator view."""
import flask
import spotifyrunners


@spotifyrunners.app.route("/bpm")
def show_bpm():
    """Display /bpm route."""
    print("in show_bpm")
    return flask.render_template("bpm.html")
