"""spotifyrunners index view."""
import flask
import spotifyrunners


@spotifyrunners.app.route("/")
def show_index():
    """Display / route."""
    context = {}
    print("in show_index")
    return flask.render_template("index.html", **context)
