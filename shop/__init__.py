from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_cors import CORS
import os




basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/test'
app.config['SECRET_KEY']='GanpatiBappaMorya'
app.config['UPLOADED_PHOTOS_DEST']=os.path.join(basedir, 'static/images')



app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search(app, db=db)
search.init_app(app)
search.create_index(update=True)
MSEARCH_INDEX_NAME =  os.path.join(app.root_path,'msearch')
MSEARCH_PRIMARY_KEY = 'id'
MSEARCH_ENABLE = True

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message=  u"Please login first"

from shop import routes


