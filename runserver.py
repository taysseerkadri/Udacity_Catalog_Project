from flask import Flask, render_template, request, redirect,jsonify, url_for, flash, make_response
from flask import session as login_session
import random, string
app = Flask(__name__)

import httplib2
import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Brand, BrandAddress, ClothingItem

engine = create_engine('sqlite:///clothing.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/index')
def Index():
    return render_template('index.html')

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return "The current session state is %s" % login_session['state']

# see all brands
@app.route('/brands')
def brands():
    brands = session.query(Brand)
    return render_template('brands.html', brands=brands)


# create new brand
@app.route('/brand/new/', methods=['GET', 'POST'])
def brandnew():
    if request.method == 'POST':
        try:
            brandname = request.form['brandname']
            logourl = request.form['logourl']
            description = request.form['description']
            newbrand = Brand(name=brandname, picture=logourl, description=description)
            session.add(newbrand)
            session.commit()
            return redirect(url_for('brands'))
        except Exception:
            return Exception
    else:
        return render_template('brandnew.html')


# edit selected brand
@app.route('/brand/<int:brand_id>/edit', methods=['GET', 'POST'])
def brandedit(brand_id):
    editedbrand = session.query(Brand).filter_by(id=brand_id).one()
    if request.method == 'POST':
        if request.form['brandname']:
            editedbrand.name = request.form['brandname']
        if request.form['brandname']:
            editedbrand.picture = request.form['logourl']
        if request.form['brandname']:
            editedbrand.description = request.form['description']
        return redirect(url_for('brands'))
    else:
        return render_template('brandedit.html', brand=editedbrand)


# delete selected brand
@app.route('/brand/<int:brand_id>/delete')
def branddelete(brand_id):
    brandToDelete =  session.query(Brand).filter_by(id=brand_id).one()
    if request.method == 'POST':
        session.delete(brandToDelete)
        session.commit()
        return redirect(url_for(brands))
    else:
        return render_template('branddelete.html', brand=brandToDelete)


# next two routes are logically transitory and synonymous - see all items in brand
@app.route('/brand/<int:brand_id>/')
@app.route('/brand/<int:brand_id>/items')
def brand(brand_id):
    items = session.query(ClothingItem).filter_by(brand_id=brand_id).all()
    return render_template('brand.html', brand_id=brand_id, items=items)


# create a new item under selected brand
@app.route('/brand/<int:brand_id>/item/new', methods=['GET','POST'])
def itemnew(brand_id):
    brand = session.query(Brand).filter_by(id = brand_id).one()
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

        newItem = ClothingItem(
            name=request.form['clothingname'],
            picture=request.form['picurl'],
            description=request.form['description'],
            price=float(finalprice),
            stockamount=int(finalstock),
            brand_id=brand_id
        )
        session.add(newItem)
        session.commit()
        return redirect(url_for('brand', brand_id=brand_id))
    else:
        return render_template('itemnew.html', brand_id=brand_id)

# see selected item under selected brand
@app.route('/brand/<int:brand_id>/item/<int:clothingitem_id>/')


# edit selected clothing item under selected brand
@app.route('/brand/<int:brand_id>/item/<int:clothingitem_id>/edit')
def itemedit(brand_id, clothingitem_id):

    editedItem = session.query(ClothingItem).filter_by(id=clothingitem_id).one()
    brand = session.query(Brand).filter_by(id=brand_id).one()

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
        return render_template('itemedit.html', brand_id=brand_id, clothingitem_id=clothingitem_id, item=editedItem)

# delete selected clothing item under selected brand
@app.route('/brand/<int:brand_id>/item/<int:clothingitem_id>/delete')
def itemdelete(brand_id, clothingitem_id):
    itemToDelete = session.query(ClothingItem).filter_by(id=clothingitem_id).one()
    brand = session.query(Brand).filter_by(id=brand_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('brand', brand_id=brand.id))
    else:
        return render_template('itemdelete.html', brand_id=brand.id, item=itemToDelete)



if __name__ == '__main__':
    app.secret_key = "secret_key_1"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

