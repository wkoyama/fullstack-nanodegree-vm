import random
import string
import datetime
import json
import httplib2
import requests

from flask import Flask, jsonify, request, url_for, redirect
from flask import session as login_session, g, abort
from flask import make_response, render_template, flash
from flask_httpauth import HTTPBasicAuth
# from flask_wtf.csrf import CSRFProtect
# from flask_seasurf import SeaSurf

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Usuario, Item, Categoria

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from ratelimit import ratelimit, get_view_rate_limit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://grader@localhost:5432/catalogitens'
app.secret_key = "b'\xcaHP\xba\x88\xba\x0c\xd8{m\x14\x99\xf6\xf3Vv'"
app.config['SESSION_TYPE'] = 'filesystem'
# csrf = CSRFProtect(app)
auth = HTTPBasicAuth()
# csrf = SeaSurf(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog Items Application"

# Connect to Database and create database session
engine = create_engine('postgresql://grader@localhost:5432/catalogitens')
Base.metadata.bind = engine

DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()

# todo implementar login com facebook


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


# @app.before_request
# def csrf_protect():
#     if request.method == "POST":
#         token = session.pop('_csrf_token', None)
#         if not token or token != request.form.get('_csrf_token'):
#             abort(403)
#
#
# def generate_csrf_token():
#     if '_csrf_token' not in session:
#         session['_csrf_token'] = get_csrf_token()
#     return session['_csrf_token']
#
#
# app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.route('/login')
def showLogin():

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/')
@app.route('/catalog', methods=["GET"])
@ratelimit(limit=400, per=60 * 1)
def index():
    categorias = session.query(Categoria).all()
    items = session.query(Item).order_by(Item.date.desc()).limit(10).all()
    user = ""

    if 'email' in login_session:
        user = getUserID(login_session['email'])

    return render_template('index.html', categorias=categorias,
                           items=items, user=user)


@app.route('/catalog/new/', methods=['GET', 'POST'])
@auth.verify_password
@ratelimit(limit=300, per=60 * 1)
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    if request.method == 'POST':
        newCategory = Categoria(
            name=request.form['name'], user_id=login_session['user_id'])

        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('addCategory.html')


@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
@ratelimit(limit=30, per=60 * 1)
def editCategory(category_id):

    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    editedCategory = session.query(
        Categoria).filter_by(id=category_id).one()

    if editedCategory.user_id != login_session['user_id']:
        return '''<script>function myFunction() {
                    alert('You are not authorized to edit this category. '
                Please create your own category in order to edit.');}
                </script><body onload='myFunction()'>'''

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('index'))
    else:
        return render_template('editCategory.html', categoria=editedCategory)


# Delete a category
@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
@ratelimit(limit=100, per=60 * 1)
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')

    categoryToDelete = session.query(
        Categoria).filter_by(id=category_id).one()

    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to delete this category. " \
               "Please create your own category in order to delete.');}" \
               "</script><body onload='myFunction()'>"

    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()

        return redirect(url_for('index', category_id=category_id))
    else:
        return render_template('deleteCategory.html',
                               categoria=categoryToDelete)


@app.route('/catalog/JSON', methods=["GET"])
def categoriesJSON():
    categorias = session.query(Categoria).order_by(asc(Categoria.name)).all()
    return jsonify(categorias=[c.serialize for c in categorias])


@app.route('/catalog/<int:category_id>/', methods=["GET"])
@app.route('/catalog/<int:category_id>/items/', methods=["GET"])
def showItems(category_id):
    categorias = session.query(Categoria).all()
    categoria = session.query(Categoria).filter_by(id=category_id).one()
    items = session.query(Item).filter(Item.category_id == Categoria.id)\
        .filter_by(category_id=category_id).all()
    title = categoria.name + " Items (" + str(len(items)) + " items)"

    return render_template('index.html', categorias=categorias, items=items,
                           title=title, category_id=category_id)


@app.route('/catalog/<int:category_id>/items/JSON', methods=["GET"])
def showItemsJSON(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/catalog/items/<int:item_id>/JSON', methods=["GET"])
def showItemJSON(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=item.serialize, category_id=item.categoria.id)


@app.route('/catalog/items/<int:item_id>', methods=["GET"])
def showItem(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('viewItem.html', item=item)


@app.route('/catalog/<int:category_id>/items/add', methods=["GET"])
def addItems(category_id):
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    categoria = session.query(Categoria).filter_by(id=category_id).one()
    if login_session['user_id'] != categoria.user_id:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to add items to this category."\
               "Please create your own category in order to add items.');}"\
               "</script><body onload='myFunction()'>"

    return render_template('addItem.html', category_id=category_id)


@app.route('/catalog/<int:category_id>/items/new', methods=["POST"])
def addItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    categoria = session.query(Categoria).filter_by(id=category_id).one()
    if login_session['user_id'] != categoria.user_id:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to add items to this category." \
               "Please create your own category in order to add items.');}" \
               "</script><body onload='myFunction()'>"

    newItem = Item(date=datetime.datetime.utcnow(),
                   name=request.form['name'],
                   description=request.form['description'],
                   category_id=categoria.id)
    session.add(newItem)
    session.commit()
    flash('New %s Item Successfully Created' % (newItem.name))
    return redirect(url_for('showItems', category_id=category_id))


@app.route('/catalog/items/<int:item_id>/edit', methods=["GET"])
def showEditItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    item = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item.categoria.user_id:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to add items to this category." \
               "Please create your own category in order to add items.');}" \
               "</script><body onload='myFunction()'>"

    return render_template('editItem.html', item=item)


@app.route('/catalog/items/<int:item_id>/edit', methods=["POST"])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    edited_item = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != edited_item.categoria.user_id:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to edit items to this category."\
               "Please create your own category in order to add items.');}" \
               "</script><body onload='myFunction()'>"

    edited_item.name = request.form['name']
    edited_item.description = request.form['description']
    flash('Item Successfully Edited %s' % edited_item.name)
    return redirect(url_for('showItems', category_id=edited_item.categoria.id))


@app.route('/catalog/items/<int:item_id>/delete', methods=["GET"])
def showDeleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    itemToDelete = session.query(Item).filter_by(id=item_id).one()

    if itemToDelete.categoria.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to delete this item." \
               "Please create your own item in order to delete.');}" \
               "</script><body onload='myFunction()'>"

    return render_template('deleteItem.html', item=itemToDelete)


@app.route('/catalog/items/<int:item_id>/delete', methods=['POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')

    checkToken = verify_password(login_session['user_token'], None)
    if checkToken is False:
        flash('Expired time!! Log in again!')
        disconnect()
        return redirect('/login')

    itemToDelete = session.query(Item).filter_by(id=item_id).one()

    if itemToDelete.categoria.user_id != login_session['user_id']:
        return "<script>function myFunction() {" \
               "alert('You are not authorized to delete this item." \
               "Please create your own category in order to delete.');}" \
               "</script><body onload='myFunction()'>"

    categoriaId = itemToDelete.categoria.id
    session.delete(itemToDelete)
    flash('%s Successfully Deleted' % itemToDelete.name)
    session.commit()
    return redirect(url_for('showItems', category_id=categoriaId))


# Login based on provider
@app.route('/oauth/<provider>', methods=['POST'])
def login(provider):
    # STEP 1 - Parse the auth code
    auth_code = request.json.get('code')
    if provider == 'google':
        gconnect(auth_code)
    elif provider == 'facebook':
        return 'Unrecoginized Provider'
    else:
        return 'Unrecoginized Provider'

    flash("You have successfully been logged in.")
    return redirect(url_for('index'))


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    login_session['provider'] = 'google'
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()

        if login_session['provider'] == 'facebook':
            return 'Unrecoginized Provider'

        del login_session['provider']

        flash("You have successfully been logged out.")
        return redirect(url_for('index'))
    else:
        flash("You were not logged in")
        return redirect(url_for('index'))


def gconnect(auth_code):
    # STEP 2 - Exchange for a token
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # STEP 3 - Find User or make a new one

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token

    name = data['name']
    picture = data['picture']
    email = data['email']

    # see if user exists, if it doesn't make a new one
    user = session.query(Usuario).filter_by(email=email).first()
    if not user:
        user = Usuario(username=name, picture=picture, email=email)
        session.add(user)
        session.commit()

    # STEP 4 - Make token
    token = user.generate_auth_token(10000)

    # see if user exists
    user_id = getUserID(email)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['picture'] = data["picture"]
    login_session['user_token'] = token

    response = make_response(redirect(url_for('index')), 302)
    response.headers['Content-Type'] = 'application/json'
    return response


def gdisconnect():
    access_token = login_session['access_token']

    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_token']
        response = make_response(redirect(url_for('index')), 302)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        del login_session['access_token']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_token']
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@auth.verify_password
def verify_password(username_or_token, password):
    # Try to see if it's a token first

    user_id = Usuario.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(Usuario).filter_by(id=user_id).one()
    else:
        user = session.query(Usuario)\
            .filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# def get_csrf_token():
#     state = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                     for x in range(32))
#     return state


def createUser(login_session):
    newUser = Usuario(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Usuario).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(Usuario).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
