# TODO: Imports

def create_app():
    app = FLASK(__name__)
    app.config["SQLAlchemy_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["ENV"] = config("ENV")
    DB.init-app(app)

    @app.route('/')
    def root():
        bird = Bird.query.all()
        return render_template('base.html', title = home, birds = 'birds')

    #TODO
