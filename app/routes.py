"""
    Определение маршрутов приложения
"""


def route(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return "404"

    @app.route("/")
    def index():
        return "Index"

    @app.route("/authorize/", methods=["GET", "POST"])
    def authorize():
        return "Authorize"

    @app.route("/quit/", methods=["POST"])
    def quit():
        return "Quit"

    @app.route("/stat/")
    def stat():
        return "Stat"

    @app.route("/list/")
    @app.route("/list/<number>/", methods=["GET", "POST"])
    def list(number=None):
        return "List"

    @app.route("/retr/<number>/", methods=["GET", "POST"])
    def retr(number):
        return "Retr"

    @app.route("/dele/<number>/", methods=["GET", "POST"])
    def dele(number):
        return "Dele"

    @app.route("/rset/")
    def rset(number):
        return "Rset"

    @app.route("/top/<number>/<count>/", methods=["GET", "POST"])
    def top(number, count):
        return "Top"
