"""spotifyrunners package initializer."""
import flask

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (spotifyrunners/config.py)
app.config.from_object("spotifyrunners.config")

app.config.from_envvar("SPOTIFYRUNNERS_SETTINGS", silent=True)

app.secret_key = b'_5#y2L"F4185\n\xec]/'
# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.
import spotifyrunners.api  # noqa: E402  pylint: disable=wrong-import-position
import spotifyrunners.views  # noqa: E402  pylint: disable=wrong-import-position

# import spotifyrunners.views  # noqa: E402  pylint: disable=wrong-import-position
# import spotifyrunners.model  # noqa: E402  pylint: disable=wrong-import-position
