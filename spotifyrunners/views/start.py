"""spotifyrunners index view."""
import flask
import spotifyrunners


@spotifyrunners.app.route("/start")
def show_start():
    """Display /start route."""
    context = {}
    print("in show_start")
    return flask.render_template("start.html", **context)
