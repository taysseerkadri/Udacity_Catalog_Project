from flask import Flask, render_template, request, redirect, \
    jsonify, url_for, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Brand, BrandAddress, ClothingItem
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests

app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').
                       read())['web']['client_id']

engine = create_engine('sqlite:///clothing.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def createToken():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
  return state

@app.route('/')
@app.route('/index')
def Index():
    """
    Routes to the index page while prepping a state token for potential
    login session.
    """    
    login_session['state'] = createToken()
    return render_template('index.html', STATE=login_session['state'])


@app.route('/login')
def showLogin():
    """
    Routes to a dedicated login page that has a single Google login link.
    Prepares a state token in the process.
    """
    state = createToken()
    login_session['state'] = state
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Gathers data from Google Sign In API and places it inside a
    session variable.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state param'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the '
                                            'authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                            ' already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    return render_template('loginredirect.html')


@app.route('/gdisconnect')
def gdisconnect():
    """
    Disconnects from the Google login session by deleting headers,
    reviking access tokens, and deleting all references for the local
    login session .
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user'
                                            ' not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']

    # Execute HTTP GET request to revoke current token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    print 'result is '
    print result

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        return redirect('/')

    else:
        response = make_response(json.dumps('Failed to revoke token'
                                            ' for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/brands')
def brands():
    brands = session.query(Brand)
    return render_template('brands.html',
                           brands=brands,
                           login_session=login_session,
                           STATE=login_session['state'])


@app.route('/brands/json/')
def brandsjson():
    brands = session.query(Brand).all()
    return jsonify(Brands=[b.serialize for b in brands])


# create new brand
@app.route('/brand/new/', methods=['GET', 'POST'])
def brandnew():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        try:
            brandname = request.form['brandname']
            logourl = request.form['logourl']
            description = request.form['description']
            creator = login_session['username']
            newbrand = Brand(name=brandname, picture=logourl,
                             description=description, creator=creator)
            session.add(newbrand)
            session.commit()
            return redirect(url_for('brands'))
        except Exception:
            return Exception
    else:
        return render_template('brandnew.html', login_session=login_session)


# edit selected brand
@app.route('/brand/<int:brand_id>/edit', methods=['GET', 'POST'])
def brandedit(brand_id):
    if 'username' not in login_session:
        return redirect('/login')
    if 'username' in login_session:
        editedbrand = session.query(Brand).filter_by(id=brand_id).one()
        if login_session['username'] == editedbrand.creator:
            if request.method == 'POST':
                if request.form['brandname']:
                    editedbrand.name = request.form['brandname']
                if request.form['brandname']:
                    editedbrand.picture = request.form['logourl']
                if request.form['brandname']:
                    editedbrand.description = request.form['description']
                return redirect(url_for('brands'))
            else:
                return render_template('brandedit.html',
                                       brand=editedbrand, login_session=login_session)
        else:
            return redirect(url_for('brands'))


# delete selected brand
@app.route('/brand/<int:brand_id>/delete')
def branddelete(brand_id):
    if 'username' not in login_session:
        return redirect('/login')
    if 'username' in login_session:
        brandToDelete = session.query(Brand).filter_by(id=brand_id).one()
        if login_session['username'] == brandToDelete.creator:
            if request.method == 'POST':
                session.delete(brandToDelete)
                session.commit()
                return redirect(url_for(brands))
            else:
                return render_template('branddelete.html',
                                       brand=brandToDelete,
                                       login_session=login_session)
        else:
            return redirect(url_for('brands'))


# next two routes are logically transitory
# and synonymous - see all items in brand
@app.route('/brand/<int:brand_id>/')
@app.route('/brand/<int:brand_id>/items')
def brand(brand_id):
    items = session.query(ClothingItem). \
        filter_by(brand_id=brand_id).all()
    return render_template('brand.html',
                           brand_id=brand_id,
                           items=items)


@app.route('/brand/<int:brand_id>/items/json')
def branditemsjson(brand_id):
    branditems = session.query(ClothingItem). \
        filter_by(brand_id=brand_id).all()
    return jsonify(BrandItems=[b.serialize for b in branditems])


# create a new item under selected brand
@app.route('/brand/<int:brand_id>/item/new', methods=['GET', 'POST'])
def itemnew(brand_id):
    if 'username' not in login_session:
        return redirect('/login')
    brand = session.query(Brand).filter_by(id=brand_id).one()
    if request.method == 'POST':
        price = request.form['price']

        if price == '':
            finalprice = 0
        else:
            finalprice = price

        stock = request.form['stockamount']
        if stock == '':
            finalstock = 0
        else:
            finalstock = stock
        creator = login_session['username']
        newItem = ClothingItem(
            name=request.form['clothingname'],
            picture=request.form['picurl'],
            description=request.form['description'],
            price=float(finalprice),
            stockamount=int(finalstock),
            brand_id=brand_id,
            creator=creator
        )
        session.add(newItem)
        session.commit()
        return redirect(url_for('brand', brand_id=brand_id))
    else:
        return render_template('itemnew.html',
                               brand_id=brand_id, login_session=login_session)


# see selected item under selected brand
@app.route('/brand/<int:brand_id>/item/<int:clothingitem_id>/')
# edit selected clothing item under selected brand
@app.route('/brand/<int:brand_id>/item/<int:clothingitem_id>/edit')
def itemedit(brand_id, clothingitem_id):
    if 'username' not in login_session:
        return redirect('/login')
    if 'username' in login_session:

        editedItem = session.query(ClothingItem). \
            filter_by(id=clothingitem_id).one()
        brand = session.query(Brand).filter_by(id=brand_id).one()
        if login_session['username'] == editedItem.creator:
            if request.method == 'POST':
                if request.form['name']:
                    editedItem.name = request.form['name']
                if request.form['picture']:
                    editedItem.picture = request.form['picture']
                if request.form['description']:
                    editedItem.description = request.form['description']
                if request.form['price']:
                    editedItem.price = request.form['price']
                if request.form['stockamount']:
                    editedItem.stockamount = request.form['stockamount']
                session.add(editedItem)
                session.commit()
                return redirect(url_for('brand', brand_id=brand_id))

            else:
                return render_template('itemedit.html', brand_id=brand_id,
                                       clothingitem_id=clothingitem_id,
                                       item=editedItem,
                                       login_session=login_session)
        else:
            return redirect(url_for('brand', brand_id=brand_id))


# delete selected clothing item under selected brand
@app.route('/brand/<int:brand_id>/item/<int:clothingitem_id>/delete')
def itemdelete(brand_id, clothingitem_id):
    if 'username' not in login_session:
        return redirect('/login')
    if 'username' in login_session:
        itemToDelete = session.query(ClothingItem). \
            filter_by(id=clothingitem_id).one()
        brand = session.query(Brand).filter_by(id=brand_id).one()
        if login_session['username'] == itemToDelete.creator:
            if request.method == 'POST':
                session.delete(itemToDelete)
                session.commit()
                return redirect(url_for('brand', brand_id=brand.id))
            else:
                return render_template('itemdelete.html',
                                       brand_id=brand.id,
                                       item=itemToDelete,
                                       login_session=login_session)
        else:
            return redirect(url_for('brand', brand_id=brand_id))


if __name__ == '__main__':
    app.secret_key = "secret_key_1"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
