from __future__ import division
from flask import jsonify, request, make_response
import jwt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import *
from base64 import b64encode
from datetime import date, datetime
import base64, binascii
import requests, json

from sqlalchemy import cast
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_httpauth import HTTPBasicAuth
from models import *

auth = HTTPBasicAuth()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/user/info/<username>', methods=['GET'])
def get_one_user(username):
    # if not current_user.admin:

    #     return jsonify({'message' : 'Cannot perform that function!'})
    user = User.query.filter_by(username=username).first()

    if not user:
        return make_response('no user found!')
    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['password'] = user.password
    user_data['first_name'] = user.first_name
    user_data['last_name'] = user.last_name
    user_data['contact_number'] = user.contact_number
    user_data['birth_date'] = user.birth_date
    user_data['gender'] = user.gender
    user_data['profpic'] = base64.b64encode(user.profpic)
    print(user_data)    
    return jsonify(user_data)


@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(username=data['username'], password=hashed_password, first_name=data['first_name'],
                    last_name=data['last_name'], contact_number=data['contact_number'], birth_date=data['birth_date'],
                    gender=data['gender'], latitude=data['latitude'], longitude=data['longitude'], profpic='')

    user = User.query.filter_by(username=data['username']).first()
    if user is None:
        db.session.add(new_user)
        db.session.commit()
        bookshelf = Bookshelf(new_user.id, new_user.username)
        db.session.add(bookshelf)
        db.session.commit()

        token = jwt.encode({'id': new_user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')}, {'message': 'added successful'})
    else:
        return make_response('username already used')

@app.route('/user/edit', methods=['POST'])
def edit_user():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.birth_date = data['birth_date']
    user.gender = data['gender']
    user.contact_number = data['contact_num']
    db.session.commit()
    return make_response('Change successful')

# @app.route('/user/<user_id>', methods=['PUT'])
# @token_required
# def promote_user(current_user, public_id):
#
#     # if not current_user.admin:
#     #     return jsonify({'message' : 'Cannot perform that function!'})
#
#     user = User.query.filter_by(public_id=public_id).first()
#
#     if not user:
#         return jsonify({'message' : 'No user found!'})
#
#     user.admin = True
#     db.session.commit()
#
#     return jsonify({'message' : 'The user has been promoted!'})
#
# @app.route('/user/<user_id>', methods=['DELETE'])
# @token_required
# def delete_user(current_user, public_id):
#
#     # if not current_user.admin:
#     #     return jsonify({'message' : 'Cannot perform that function!'})
#
#     user = User.query.filter_by(public_id=public_id).first()
#
#     if not user:
#         return jsonify({'message': 'No user found!'})
#
#     db.session.delete(user)
#     db.session.commit()
#
#     return ({'message' : 'The user has been deleted!'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth['password']):
        user
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8'), 'username': user.username})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

# @app.route('/user/<int:id>/bookshelf/', methods=['GET'])
# def viewbooks(id):
#
# <<<<<<< HEAD
#     books = ContainsAssociation.query.join(Bookshelf).filter_by(bookshelf_id = id).all()
# =======

@app.route('/user/set/coordinates', methods=['GET', 'POST'])
def set_coordinates():
    data = request.get_json()
    user = User.query.filter_by(username=data['current_user']).first()
    user.latitude = data['latitude']
    user.longitude = data['longitude']
    db.session.commit()
    return jsonify({'message': "Added successful"})

@app.route('/user/bookshelf/search', methods=['GET', 'POST'])
@token_required
def searchbookshelf(current_user):
    data = request.get_json()

    item = '%' + data['item'] + '%'

    books = Bookshelf.query.filter_by(bookshef_owner=current_user).first()
    shelf_id = books.bookshelf_id

    books = ContainsAssociation.query.join(Books).filter(
        (cast(shelf_id, sqlalchemy.String).like(item)) & ((Books.title.like(item)) | (
            Books.year_published.like(item)) | (Books.types.like(item)) | cast(Books.edition, sqlalchemy.String).like(
            item) | (Books.isbn.like(item)))).all()

    if books is None:
        return jsonify({'message': 'No book found!'})

    output = []

    for book in books:
        user_data = {}
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['year_published'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)

    return jsonify({'book': output})


@app.route('/user/bookshelf', methods=['GET'])
def viewbook():
    data = request.get_json()
    books = Bookshelf.query.filter_by(bookshef_owner= data['current_user']).first()
    shelf_id = books.bookshelf_id

    contains = ContainsAssociation.query.filter_by(shelf_id=shelf_id).first()
    if contains is None:
        return make_response('no books found')
    shelf_id = contains.shelf_id
    Book = Books.query.join(ContainsAssociation).filter_by(shelf_id=shelf_id).all()

    # q = (db.session.query(Books, Bookshelf, ContainsAssociation, Author)
    #      .filter(Bookshelf.bookshef_owner == id)
    #      .filter(ContainsAssociation.shelf_id == Bookshelf.bookshelf_id)
    #      .filter(Books.book_id == ContainsAssociation.book_id)
    #      .filter(Author.author_id == Books.publisher_id)
    #      .all())

    output = []
    if (Book is None) or (contains is None) or (books is None):
        return make_response('no books found')

    for book in Book:
        user_data = {}
        book_contains = ContainsAssociation.query.filter_by(book_id=book.book_id).first()
        user_data['title'] = book.title
        user_data['book_id'] = book.book_id
        genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
        genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
        user_data['genre'] = genre_final.genre_name
        user_data['book_cover'] = book.book_cover
        book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
        author = Author.query.filter_by(author_id=book_author.author_id).first()
        user_data['owner_bookshelfid'] = books.bookshelf_id
        user_data['author_name'] = author.author_name
        user_data['description'] = book.description
        user_data['edition'] = book.edition
        user_data['year'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)

    return jsonify({'book': output})

@app.route('/user/bookshelf/<book_id>', methods=['GET'])
def view_one_book(book_id):
    data = request.get_json()
    book = Books.query.filter_by(book_id=book_id).first()

    output = []
    if book is None:
        return make_response('no books found')

    book = Books.query.filter_by(book_id=book_id).first()
    user = User.query.filter_by(username=data['username']).first()
    viewer = User.query.filter_by(username=data['current_user']).first()
    bookshelf = Bookshelf.query.filter_by(bookshef_owner=user.username).first()
    contains = ContainsAssociation.query.filter((ContainsAssociation.book_id == book_id) &
                                                 (ContainsAssociation.shelf_id == bookshelf.bookshelf_id)).first()
    publisher = Publisher.query.filter_by(publisher_id=book.publisher_id).first()

    user_data = {}
    user_data['owner'] = user.first_name+" "+ user.last_name
    user_data['username'] = user.username
    user_data['viewer_name'] = viewer.first_name+" "+ viewer.last_name
    user_data['viewer_profpic'] = base64.b64encode(viewer.profpic)
    user_data['viewer_username'] = viewer.username
    user_data['owner_bookshelfid'] = bookshelf.bookshelf_id
    user_data['title'] = book.title
    user_data['book_id'] = book.book_id
    user_data['year'] = book.year_published
    user_data['availability'] = contains.availability
    user_data['quantity'] = contains.quantity
    user_data['book_cover'] = book.book_cover
    user_data['edition'] = book.edition
    user_data['year'] = book.year_published
    genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
    genre_name = Genre.query.filter_by(id_genre=genre.genreId).first()
    user_data['genre'] = genre_name.genre_name
    book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
    author = Author.query.filter_by(author_id=book_author.author_id).first()
    user_data['author_name'] = author.author_name
    user_data['description'] = book.description
    user_data['price'] = contains.price
    user_data['methods'] = contains.methods
    user_data['contains_id'] = contains.contains_id
    user_data['isbn'] = book.isbn
    user_data['types'] = book.types
    user_data['publisher_id'] = publisher.publisher_name
    yourRating = BookRateAssociation.query.filter((BookRateAssociation.book_id == contains.contains_id) & (BookRateAssociation.user_id == viewer.id)).first()
    if yourRating is not None:
        user_data['rating'] = yourRating.rating
    else:
        user_data['rating'] = int('1')
    totalRate = BookRateTotal.query.filter_by(bookRated=contains.contains_id).first()
    if totalRate is not None:
        user_data['totalRate'] = ((totalRate.totalRate/totalRate.numofRates))
        user_data['numofRates'] = totalRate.numofRates
        book_rate = BookRateAssociation.query.filter_by(book_id=contains.contains_id).all()
        num5 = 0
        num4 = 0
        num3 = 0
        num2 = 0
        num1 = 0
        for book in book_rate:
            print(book.rating)
            if book.rating == 1:
                num1 = num1 + 1
            elif book.rating == 2:
                num2 = num2 + 1
            elif book.rating == 3:
                num3 = num3 + 1
            elif book.rating == 4:
                num4 = num4 + 1
            else:
                num5 = num5 + 1
        print(num1)
        print(num2)
        print(num3)
        print(num4)
        print(num5)

        user_data['num1'] = (num1 / int(totalRate.numofRates))*100
        user_data['num2'] = (num2 / int(totalRate.numofRates))*100
        user_data['num3'] = (num3 / int(totalRate.numofRates))*100
        user_data['num4'] = (num4 / int(totalRate.numofRates))*100
        user_data['num5'] = (num5 / int(totalRate.numofRates))*100
    else:
        user_data['totalRate'] = 0.0
        user_data['numofRates'] = 0

    output.append(user_data)
    print(output)
    return jsonify({'book': output})

@app.route('/bookshelf/comments/book', methods=['GET'])
def get_comments():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    book = Books.query.filter_by(book_id=data['book_id']).first()
    bookshelf = Bookshelf.query.filter_by(bookshef_owner=user.username).first()
    contains = ContainsAssociation.query.filter((ContainsAssociation.book_id == book.book_id) &
                                                (ContainsAssociation.shelf_id == bookshelf.bookshelf_id)).first()
    comments = BookCommentAssociation.query.filter_by(bookshelf_id=contains.contains_id).all()
    output=[]
    numofcomments=0
    for comment in comments:
        comments1={}
        comments1['comment'] = comment.comment
        fmt = "%a, %d %b %Y %H:%M:%S GMT"
        now = comment.date.strftime('%a, %d %b %Y %H:%M')
        comments1['date'] = now
        user_commenter = User.query.filter_by(id=comment.user_id).first()
        comments1['user_fname'] = user_commenter.first_name
        comments1['user_lname'] = user_commenter.last_name
        comments1['user_username'] = user_commenter.username
        comments1['profpic'] = base64.b64encode(user_commenter.profpic)
        numofcomments=numofcomments+1
        output.append(comments1)

    return jsonify({'comments': output})


@app.route('/user/edit/book', methods=['POST'])
def edit_book():
    data = request.get_json()
    book = Books.query.filter_by(book_id=data['book_id']).first()
    bookshelf = Bookshelf.query.filter_by(bookshef_owner=data['username']).first()
    contains = ContainsAssociation.query.filter((ContainsAssociation.book_id == book.book_id) &
                                                (ContainsAssociation.shelf_id == bookshelf.bookshelf_id)).first()
    contains.quantity = data['quantity']
    contains.methods = data['methods']
    contains.price = data['price']
    db.session.commit()
    return make_response('Successful')

@app.route('/user/bookshelf/remove/book', methods=['POST', 'GET'])
def remove_book():
    data = request.get_json()
    book = Books.query.filter_by(book_id=data['book_id']).first()
    bookshelf = Bookshelf.query.filter_by(bookshef_owner=data['username']).first()
    contains = ContainsAssociation.query.filter((ContainsAssociation.book_id == book.book_id)&
                                                 (ContainsAssociation.shelf_id == bookshelf.bookshelf_id)).first()
    db.session.delete(contains)
    db.session.commit()
    return make_response('Successful')

# COMMENT (BOOK)
@app.route('/comment-book', methods=['GET', 'POST'])
def commentbook():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    contains = ContainsAssociation.query.filter_by(contains_id=data['contains_id']).first()
    if contains is None:
        return make_response('Could not comment!')
    else:
        comment = BookCommentAssociation(comment=data['comment'], user_id=user.id, bookshelf_id=contains.contains_id)
    db.session.add(comment)
    db.session.commit()
    return make_response('Comment posted!')

@app.route('/rate-book', methods=['GET', 'POST'])
def ratebook():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    contains = ContainsAssociation.query.filter_by(contains_id=data['contains_id']).first()
    if contains is None:
        return make_response('Could not rate!')
    else:
        rate_check = BookRateAssociation.query.filter((BookRateAssociation.book_id == contains.contains_id) & (BookRateAssociation.user_id == user.id)).first()
        if rate_check is None:
            rate = BookRateAssociation(comment="", rating=data['ratings'], user_id=user.id, book_id=contains.contains_id)
            db.session.add(rate)
            db.session.commit()
            totalRate = BookRateTotal.query.filter_by(bookRated=contains.contains_id).first()
            if totalRate is None:
                total_rate = BookRateTotal(bookRated=contains.contains_id, numofRates=1, totalRate=data['ratings'])
                db.session.add(total_rate)
                db.session.commit()
                print('new rate')
            else:
                totalRate.numofRates = totalRate.numofRates + 1
                totalRate.totalRate = totalRate.totalRate + float(data['ratings'])
                db.session.commit()
                print('added!!')
        else:
            totalRate2 = BookRateTotal.query.filter_by(bookRated=contains.contains_id).first()
            totalRate2.totalRate = totalRate2.totalRate - rate_check.rating
            rate_check.rating = data['ratings']
            totalRate2.totalRate = totalRate2.totalRate + float(data['ratings'])
            db.session.commit()


    return make_response('Rate posted!')

# addbook 
@app.route('/user/addbook', methods=['POST'])
@token_required
def addbook(self):

    data = request.get_json()
    print(data['publisher_name'])
    book = Books.query.filter((Books.title == data['title']) &
                              (Books.year_published == data['year']) & (Books.isbn == data['isbn'])
                              & (Books.description == data['description'])).first()
    publisher = Publisher.query.filter(Publisher.publisher_name == data['publisher_name']).first()
    author = Author.query.filter((Author.author_name == data['author_name'])).first()
    if (book is None) or (publisher is None) or (author is None):
        if publisher is None:
            newPublisher = Publisher(publisher_name= data['publisher_name'])
            db.session.add(newPublisher)
            db.session.commit()
            publisher_id = Publisher.query.filter((Publisher.publisher_name == data['publisher_name'])).first()
            if author is None:
                author = Author(author_name=data['author_name'])
                db.session.add(author)
                db.session.commit()
            elif author is not None:
                author = Author.query.filter((Author.author_name == data['author_name'])).first()
        elif publisher is not None:
            publisher_id = Publisher.query.filter((Publisher.publisher_name == data['publisher_name'])).first()
            if author is None:
                author = Author(data['author_name'])
                db.session.add(author)
                db.session.commit()
            elif author is not None:
                author = Author.query.filter(Author.author_name == data['author_name']).first()

        publisher = Publisher.query.filter(Publisher.publisher_name == data['publisher_name']).first()
        publisher_id = publisher.publisher_id
        bookshelf = Bookshelf.query.filter_by(bookshef_owner=data['current_user']).first()
        book_check = Books.query.filter_by(isbn=data['isbn']).first()
        author = Author.query.filter((Author.author_name == data['author_name'])).first()
        if book_check is not None and (author is not None):
            author1 = WrittenByAssociation.query.filter((WrittenByAssociation.book_id == book_check.book_id) & (WrittenByAssociation.author_id == author.author_id)).first()
        if book_check is not None and (author1 is not None):
            book_check1 = ContainsAssociation.query.filter((ContainsAssociation.shelf_id == bookshelf.bookshelf_id) and
                                                           (ContainsAssociation.book_id == book_check.book_id)).first()
            if book_check1 is not None:
                #book_check1 = gi check if ga exist ba ang libro sa bookshelf sa user
                return make_response('The book is already in your bookshelf!')

        print(book_check)
        book = Books(title = data['title'], year_published = data['year'], isbn =data['isbn'], types=None, edition=None, publisher_id= publisher_id, description=data['description'], book_cover=data['book_cover'])
        db.session.add(book)
        db.session.commit()
        get_category = Category.query.filter_by(category_name=data['category']).first()
        if get_category is None:
            set_category = Category(category_name=data['category'])
            db.session.add(set_category)
            db.session.commit()

        get_category = Category.query.filter_by(category_name=data['category']).first()
        category = CategoryAssociation(book_id=book.book_id, category_id=get_category.category_id)
        db.session.add(category)
        db.session.commit()

        get_genre = Genre.query.filter_by(genre_name=data['genre']).first()
        if get_genre is None:
            set_genre = Genre(genre_name=data['genre'])
            db.session.add(set_genre)
            db.session.commit()

        get_genre = Genre.query.filter_by(genre_name=data['genre']).first()
        genre = HasGenreAssociation(genreId=get_genre.id_genre, bookId=book.book_id)
        db.session.add(genre)
        db.session.commit()

        author = Author.query.filter_by(author_name=data['author_name']).first()
        written = WrittenByAssociation(author.author_id, book.book_id)
        db.session.add(written)
        db.session.commit()

        bookshelf = Bookshelf.query.filter_by(bookshef_owner=data['current_user']).first()
        shelf_id = bookshelf.bookshelf_id
        book1 = Books.query.filter_by(isbn=data['isbn']).first()
        print(data['quantity'])
        contain = ContainsAssociation(shelf_id=shelf_id, book_id=book.book_id, quantity= data['quantity'], availability='YES', methods=data['method'], price=data['price'])
        check = ContainsAssociation.query.filter((ContainsAssociation.shelf_id == shelf_id) and
                                                  (ContainsAssociation.book_id == book1.book_id)).first()
        db.session.add(contain)
        db.session.commit()

        return jsonify({'message': 'New book created!'})

    else:

        bookshelf = Bookshelf.query.filter_by(bookshef_owner=data['current_user']).first()
        shelf_id = bookshelf.bookshelf_id

        bookquantity = ContainsAssociation.query.filter((ContainsAssociation.shelf_id == shelf_id) & (ContainsAssociation.book_id == book.book_id)).first()
        if bookquantity is None:
            contain = ContainsAssociation(shelf_id=shelf_id, book_id=book.book_id, quantity= data['quantity'], availability='YES', methods=data['method'], price=data['price'])
            db.session.add(contain)
            db.session.commit()
            print('book quantity is None')
        else:
            curQuant = bookquantity.quantity
            print('book quantity is not None')
            bookquantity.quantity = int(curQuant)
            db.session.commit()

    return jsonify({'message': 'New book counted!'})


# addbook check by ISBN
@app.route('/mobile/user/isbn_check/<isbn>', methods=['GET'])
@token_required
def mobile_isbn_check(self, isbn):

    #data = request.get_json()

    book = Books.query.filter_by(isbn=isbn).first()
    print(book)
    if book is not None:
        output = []
        user_data = {}
        user_data['title'] = book.title
        user_data['book_id'] = book.book_id
        user_data['book_cover'] = book.book_cover
        user_data['description'] = book.description
        book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
        author = Author.query.filter_by(author_id=book_author.author_id).first()
        publisher = Publisher.query.filter_by(publisher_id=book.publisher_id).first()
        user_data['publishers'] = publisher.publisher_name
        user_data['author_name'] = author.author_name
        user_data['year'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        output.append(user_data)
        return jsonify({'data': output}) #naa kay libro nakit.an sa db
    else:
        url = "https://openlibrary.org/api/books?bibkeys=ISBN:{0}&jscmd=data&format=json".format(isbn)
        url2 = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0}&key=AIzaSyAOeYMvF7kPJ7ZcAjOVWiRA8PjCk5E_TsM".format(isbn)
        output = []
        book = {}
        response2 = requests.get(url2)
        resp2 = json.loads(response2.text) #ga requests ka sa API sa google
        response = requests.get(url)
        resp = json.loads(response.text) #ga requests ka sa API sa OPENLibrary
        book['isbn'] = isbn
        if (resp2['totalItems'] == 0) and (not resp): #walay kay nakuha sa API sa duha
            return make_response('No books found!')
        elif not resp: #wala kay nakuha sa API sa OpenLibrary so ang google imo gamiton
            book['title'] = resp2['items'][0]['volumeInfo']['title'] #gikuha nimong title
            if 'publisher' in resp2['items'][0]['volumeInfo']: #usahay walay publisher gikan sa google
                book['publishers'] = resp2['items'][0]['volumeInfo']['publisher'] #gi store nimo ang publisher kay naa
            else:
                book['publishers'] = '' #pag wala
            book['book_cover'] = resp2['items'][0]['volumeInfo']['imageLinks']['thumbnail']
            book['author_name'] = resp2['items'][0]['volumeInfo']['authors'][0]
            book['description'] = resp2['items'][0]['volumeInfo']['description']
            book['year'] = resp2['items'][0]['volumeInfo']['publishedDate']
        else: #pag naa kay makuha sa duha
            index = "ISBN:{0}".format(isbn)
            book['title'] = resp[index]['title'] #gikan na ni sa OpenLibrary
            book['publishers'] = resp[index]['publishers'][0]['name']
            if 'cover' in resp[index]: #usahay way cover sad ma return
                book['book_cover'] = resp[index]['cover']['large']
            else:
                book['cover'] = '#'
            book['author_name'] = resp[index]['authors'][0]['name']
            date1 = resp[index]['publish_date']
            book['year'] = date1
            if resp2['totalItems'] != 0: #pag naa sad sa googlebooks
                book['title'] = resp2['items'][0]['volumeInfo']['title'] #gistore ang title gikan sa GoogleBooks kay mas tarong ilang title, publisher, authorname og publishedDate
                if 'publisher' in resp2['items'][0]['volumeInfo']:
                    book['publishers'] = resp2['items'][0]['volumeInfo']['publisher']
                else:
                    book['publishers'] = ''
                if 'authors' in resp2['items'][0]['volumeInfo']:
                    book['author_name'] = resp2['items'][0]['volumeInfo']['authors'][0]
                book['description'] = resp2['items'][0]['volumeInfo']['description']
                book['year'] = resp2['items'][0]['volumeInfo']['publishedDate']
        output.append(book)
        print(output[0])
    return jsonify(output)


#addbook check by TITLE
@app.route('/mobile/user/title_check/<title>', methods=['GET'])
@token_required
def mobile_title_check(self, title):
    print(title)
    url = "https://www.googleapis.com/books/v1/volumes?q=intitle:{0}&key=AIzaSyAOeYMvF7kPJ7ZcAjOVWiRA8PjCk5E_TsM&maxResults=40".format(title)
    response = requests.get(url)
    resp = json.loads(response.text)
    books = Books.query.filter(Books.title.like(title)).all()
    if int(resp['totalItems']) == 0 and books is None:
        return make_response('No books found')
    elif books is not None: 
        output = []
        for book in books:
            books1 = {}
            books1['title'] = book.title
            books1['book_id'] = book.book_id
            books1['book_cover'] = book.book_cover
            books1['description'] = book.description
            book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            publisher = Publisher.query.filter_by(publisher_id=book.publisher_id).first()
            books1['publishers'] = publisher.publisher_name
            books1['author_name'] = author.author_name
            books1['year'] = book.year_published
            books1['isbn'] = book.isbn
            books1['types'] = book.types
            output.append(books1)

        if int(resp['totalItems']) == 0: #way libro gikan sa google
            return jsonify(output)
        else:
            print(response.text) #ani ang itsura sa results gikan google
            for book_item in resp['items']:
                books = {}
                if((('publisher' in book_item['volumeInfo']) and ('industryIdentifiers' in book_item['volumeInfo']))
                and (('imageLinks' in book_item['volumeInfo']) and ('authors' in book_item['volumeInfo'])))\
                and ('description' in book_item['volumeInfo'] and 'publishedDate' in book_item['volumeInfo']):
                    books['title'] = book_item['volumeInfo']['title']
                    books['publishers'] = book_item['volumeInfo']['publisher']
                    books['isbn'] = book_item['volumeInfo']['industryIdentifiers'][0]['identifier']
                    books['book_cover'] = book_item['volumeInfo']['imageLinks']['thumbnail']
                    books['author_name'] = book_item['volumeInfo']['authors'][0]
                    books['description'] = book_item['volumeInfo']['description']
                    books['year'] = book_item['volumeInfo']['publishedDate']
                    output.append(books)
                else:
                    continue
            return jsonify(output)


#search by authorname
@app.route('/mobile/user/author_check/<author_name>', methods=['GET'])
@token_required
def mobile_author_check(self, author_name):
    author = author_name
    url = "https://www.googleapis.com/books/v1/volumes?q=inauthor:{0}&key=AIzaSyAOeYMvF7kPJ7ZcAjOVWiRA8PjCk5E_TsM&maxResults=40".format(
        author)
    response = requests.get(url)
    resp = json.loads(response.text)
    print(resp)
    author = Author.query.filter_by(author_name=author_name).first()
    if int(resp['totalItems']) == 0 and author is None:
        return make_response('No books found')
    
    elif int(resp['totalItems']) == 0:  # way libro gikan sa google
        output=[]
        if author is not None:
            written = WrittenByAssociation.query.filter_by(author_id=author.author_id).all()
            for writtenbook in written:  # mga libro sa author gikan sa db
                book = Books.query.filter_by(book_id=writtenbook.book_id).first()
                books1 = {}
                books1['title'] = book.title
                books1['book_id'] = int(book.book_id)
                books1['book_cover'] = book.book_cover
                books1['description'] = book.description
                book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
                author = Author.query.filter_by(author_id=book_author.author_id).first()
                publisher = Publisher.query.filter_by(publisher_id=book.publisher_id).first()
                books1['publishers'] = publisher.publisher_name
                books1['author_name'] = author.author_name
                books1['year'] = book.year_published
                books1['isbn'] = book.isbn
                books1['types'] = book.types
                output.append(books1)
    else:
        output = []
        print(response.text)  # ani ang itsura sa results gikan google
        for book_item in resp['items']:
            books = {}
            if ((('publisher' in book_item['volumeInfo']) and ('industryIdentifiers' in book_item['volumeInfo']))
                and (('imageLinks' in book_item['volumeInfo']) and ('authors' in book_item['volumeInfo']))) \
                    and ('description' in book_item['volumeInfo'] and 'publishedDate' in book_item[
                        'volumeInfo']):  # usahay mag ka kulang mga result gikan sa google,
                # way publisher, isbn or picture and etc.
                # so if kulang kay iskip siya, mao pulos sa 'continue'
                books['title'] = book_item['volumeInfo']['title']
                books['publishers'] = book_item['volumeInfo']['publisher']
                books['isbn'] = book_item['volumeInfo']['industryIdentifiers'][0]['identifier']
                books['book_cover'] = book_item['volumeInfo']['imageLinks']['thumbnail']
                books['author_name'] = book_item['volumeInfo']['authors'][0]
                books['description'] = book_item['volumeInfo']['description']
                books['year'] = book_item['volumeInfo']['publishedDate']
                output.append(books)
            else:
                continue
                
        if author is not None:
            written = WrittenByAssociation.query.filter_by(author_id=author.author_id).all()
            for writtenbook in written:  # mga libro sa author gikan sa db
                book = Books.query.filter_by(book_id=writtenbook.book_id).first()
                books1 = {}
                books1['title'] = book.title
                books1['book_id'] = int(book.book_id)
                books1['book_cover'] = book.book_cover
                books1['description'] = book.description
                book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
                author = Author.query.filter_by(author_id=book_author.author_id).first()
                publisher = Publisher.query.filter_by(publisher_id=book.publisher_id).first()
                books1['publishers'] = publisher.publisher_name
                books1['author_name'] = author.author_name
                books1['year'] = book.year_published
                books1['isbn'] = book.isbn
                books1['types'] = book.types
                output.append(books1)

        return jsonify(output)


# {"title": "new book","edition": "20", "year": "2018", "isbn": "SEVENTEEN", "types": "HARD" , "publisher_name":"DK", "author_fname": "SEANNE", "author_lname": "CANOY"}

@app.route('/user/bookshelf/availability', methods=['GET'])
def viewbooks():
    data = request.get_json()
    books = ContainsAssociation.query.join(Bookshelf).filter_by(bookshef_owner=data['current_user']).all()

    if books == []:
        return jsonify({'message': 'No book found!'})

    else:

        output = []
        for book in books:
            user_data = {}
            user_data['shelf_id'] = book.shelf_id
            user_data['book_id'] = book.book_id
            user_data['quantity'] = book.quantity
            user_data['availability'] = book.availability
            output.append(user_data)

        return jsonify({'book': output})

@app.route('/category/<string:category>/', methods=['GET'])
def category(category):

    books = Books.query.join(Category).filter(Category.categories == category).filter(Books.book_id == Category.book_id).all()
    # filter_by(firstname.like(search_var1),lastname.like(search_var2))
    #
    # q = (db.session.query(Category, Books)
    #      .join(Books)
    #      .join(Category)
    #      .filter(Category.categories == category)
    #      .filter(Books.book_id == Category.book_id)
    #      .all())

    output = []

    for book in books:
        user_data = {}
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['edition'] = book.edition
        user_data['year'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        output.append(user_data)


    return jsonify({'book': output})

@app.route('/interests/<genre_name>', methods=['POST'])
def add_interest(genre_name):
    data = request.get_json()
    user = User.query.filter_by(username=data['current_user']).first()

    genre = Genre.query.filter_by(genre_name=genre_name).first()
    if genre is None:
        genre = Genre(genre_name=genre_name)
        db.session.add(genre)
        db.session.commit()

    genre = Genre.query.filter_by(genre_name=genre_name).first()
    interests = InterestAssociation(user_Id=user.id, genreId=genre.id_genre)
    db.session.add(interests)
    db.session.commit()
    return jsonify({'message': "added successful"})

@app.route('/interests/view/<genre_name>', methods=['GET'])
def view_genre(genre_name):

    genre = Genre.query.filter_by(genre_name=genre_name).first()
    if genre is None:
        genre = Genre(genre_name=genre_name)
        db.session.add(genre)
        db.session.commit()
        return jsonify({'message': 'No book found!'})

    genre = Genre.query.filter_by(genre_name=genre_name).first()

    books = Books.query.join(HasGenreAssociation).filter(HasGenreAssociation.genreId == genre.id_genre).filter(
        Books.book_id == HasGenreAssociation.bookId).order_by(Books.edition.desc()).limit(40).all()
    if books is None:
        return jsonify({'message': 'No book found!'})
    output = []

    for book in books:
        print(book)
        book_ = Books.query.filter_by(book_id=book.book_id).first()
        owner_contains = ContainsAssociation.query.filter_by(book_id=book_.book_id).first()
        if owner_contains is None:
            continue
        else:
            owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contains.shelf_id).first()
            user_data = {}
            user_data['genre'] = genre_name
            user_data['title'] = book_.title
            bookrate = BookRateTotal.query.filter_by(bookRated=owner_contains.contains_id).first()
            if bookrate is not None:
                user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
            else:
                user_data['totalRate'] = 0.0
            user_data['book_id'] = book_.book_id
            book_author = WrittenByAssociation.query.filter_by(book_id=book_.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            user_data['author_name'] = author.author_name
            owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
            user_data['book_cover'] = book.book_cover
            user_data['owner_fname'] = owner.first_name
            user_data['owner_lname'] = owner.last_name
            user_data['owner_username'] = owner.username
            output.append(user_data)

    return jsonify({'book': output})

@app.route('/category/view/<category_name>', methods=['GET'])
def view_category(category_name):

    category = Category.query.filter_by(category_name=category_name).first()
    if category is None:
        category = Category(category_name=category_name)
        db.session.add(category)
        db.session.commit()
        return jsonify({'message': 'No book found!'})

    category = Category.query.filter_by(category_name=category_name).first()

    books = Books.query.join(CategoryAssociation).filter(CategoryAssociation.book_id == Books.book_id).filter(
        category.category_id == CategoryAssociation.category_id).order_by(Books.year_published.desc()).limit(12).all()
    if books is None:
        return jsonify({'message': 'No book found!'})
    output = []

    for book in books:
        print(book)
        book_ = Books.query.filter_by(book_id=book.book_id).first()
        owner_contains = ContainsAssociation.query.filter_by(book_id=book_.book_id).first()
        if owner_contains is None:
            continue
        else:
            owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contains.shelf_id).first()
            bookrate = BookRateTotal.query.filter_by(bookRated=owner_contains.contains_id).first()
            user_data = {}
            if bookrate is not None:
                user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
            else:
                user_data['totalRate'] = 0.0
            genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
            get_genre = Genre.query.filter_by(id_genre=genre.genreId).first()
            user_data['genre'] = get_genre.genre_name
            user_data['title'] = book_.title
            user_data['book_id'] = book_.book_id
            book_author = WrittenByAssociation.query.filter_by(book_id=book_.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            user_data['author_name'] = author.author_name
            owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
            user_data['book_cover'] = book.book_cover
            user_data['owner_fname'] = owner.first_name
            user_data['owner_lname'] = owner.last_name
            user_data['owner_username'] = owner.username
            output.append(user_data)

    return jsonify({'book': output})

@app.route('/interests/view2/<genre_name>', methods=['GET'])
def view_genre2(genre_name):

    genre = Genre.query.filter_by(genre_name=genre_name).first()
    if genre is None:
        genre = Genre(genre_name=genre_name)
        db.session.add(genre)
        db.session.commit()
        return jsonify({'message': 'No book found!'})

    genre = Genre.query.filter_by(genre_name=genre_name).first()

    books = Books.query.join(HasGenreAssociation).filter(HasGenreAssociation.genreId == genre.id_genre).filter(
        Books.book_id == HasGenreAssociation.bookId).order_by(Books.year_published.desc()).limit(12).all()
    if books is None:
        return jsonify({'message': 'No book found!'})
    output = []

    for book in books:
        print(book)
        book_ = Books.query.filter_by(book_id=book.book_id).first()
        owner_contains = ContainsAssociation.query.filter_by(book_id=book_.book_id).first()
        if owner_contains is None:
            continue
        else:
            owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contains.shelf_id).first()
            user_data = {}
            user_data['genre'] = genre_name
            user_data['title'] = book_.title
            user_data['book_id'] = book_.book_id
            bookrate = BookRateTotal.query.filter_by(bookRated=owner_contains.contains_id).first()
            if bookrate is not None:
                user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
            else:
                user_data['totalRate'] = 0.0
            book_author = WrittenByAssociation.query.filter_by(book_id=book_.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            user_data['author_name'] = author.author_name
            owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
            user_data['book_cover'] = book.book_cover
            user_data['owner_fname'] = owner.first_name
            user_data['owner_lname'] = owner.last_name
            user_data['owner_username'] = owner.username
            output.append(user_data)

    return jsonify({'book': output})

@app.route('/bookshelf/books', methods=['GET'])
def get_all_book():
    output = []
    books = Books.query.order_by(Books.title.desc()).all()
    for book in books:
        owner_contains = ContainsAssociation.query.filter_by(book_id=book.book_id).all()

        for owner_contain in owner_contains:
            user_data = {}
            owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contain.shelf_id).first()
            owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
            bookrate = BookRateTotal.query.filter_by(bookRated=owner_contain.contains_id).first()
            user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
            user_data['owner_fname'] = owner.first_name
            user_data['owner_lname'] = owner.last_name
            user_data['owner_username'] = owner.username
            user_data['owner_bookshelfid'] = owner_bookshelf.bookshelf_id
            user_data['title'] = book.title
            user_data['book_id'] = book.book_id
            user_data['book_cover'] = book.book_cover
            genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
            genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
            user_data['genre'] = genre_final.genre_name
            book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            user_data['author_name'] = author.author_name
            output.append(user_data)

    return jsonify({'book': output})

@app.route('/bookshelf/books/latest', methods=['GET'])
def get_latest_books():
    output = []
    books = Books.query.order_by(Books.year_published.desc()).limit(12).all()
    for book in books:
        owner_contains = ContainsAssociation.query.filter_by(book_id=book.book_id).all()
        for owner_contain in owner_contains:
            user_data = {}
            user_data['title'] = book.title
            user_data['book_id'] = book.book_id
            bookrate = BookRateTotal.query.filter_by(bookRated=owner_contain.contains_id).first()
            if bookrate is not None:
                user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
            else:
                user_data['totalRate'] = 0.0
            genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
            genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
            user_data['genre'] = genre_final.genre_name
            book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            user_data['author_name'] = author.author_name
            user_data['book_cover'] = book.book_cover
            owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contain.shelf_id).first()
            owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
            user_data['owner_fname'] = owner.first_name
            user_data['owner_lname'] = owner.last_name
            user_data['owner_username'] = owner.username
            user_data['owner_bookshelfid'] = owner_bookshelf.bookshelf_id
            output.append(user_data)

    return jsonify({'book': output})

@app.route('/bookshelf/books/toprated', methods=['GET'])
def get_toprated_books():
    output = []
    ratedbooks = BookRateTotal.query.order_by(BookRateTotal.totalRate.asc()).limit(12).all()
    for ratedbook in ratedbooks:
        owner_contains = ContainsAssociation.query.filter_by(book_id=ratedbook.bookRated).first()
        book = Books.query.filter_by(book_id=owner_contains.book_id).first()
        user_data = {}
        user_data['title'] = book.title
        user_data['book_id'] = book.book_id
        user_data['totalRate'] = ((ratedbook.totalRate/ratedbook.numofRates))
        genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
        genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
        user_data['genre'] = genre_final.genre_name
        book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
        author = Author.query.filter_by(author_id=book_author.author_id).first()
        user_data['author_name'] = author.author_name
        user_data['book_cover'] = book.book_cover
        owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contains.shelf_id).first()
        owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
        user_data['owner_fname'] = owner.first_name
        user_data['owner_lname'] = owner.last_name
        user_data['owner_username'] = owner.username
        user_data['owner_bookshelfid'] = owner_bookshelf.bookshelf_id
        output.append(user_data)

    return jsonify({'book': output})

@app.route('/bookshelf/books/recent', methods=['GET'])
def get_recent_books():
    output = []
    contains = ContainsAssociation.query.order_by(ContainsAssociation.date.desc()).limit(12).all()
    for contain in contains:
        book = Books.query.filter_by(book_id=contain.book_id).first()
        user_data = {}
        user_data['title'] = book.title
        user_data['book_id'] = book.book_id
        bookrate = BookRateTotal.query.filter_by(bookRated=contain.contains_id).first()
        if bookrate is not None:
            user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
        else:
            user_data['totalRate'] = 0.0
        genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
        genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
        user_data['genre'] = genre_final.genre_name
        book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
        author = Author.query.filter_by(author_id=book_author.author_id).first()
        user_data['author_name'] = author.author_name
        user_data['book_cover'] = book.book_cover
        owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=contain.shelf_id).first()
        owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
        user_data['owner_fname'] = owner.first_name
        user_data['owner_lname'] = owner.last_name
        user_data['owner_username'] = owner.username
        user_data['owner_bookshelfid'] = owner_bookshelf.bookshelf_id
        output.append(user_data)

    return jsonify({'book': output})

#### WISHLIST ###
@app.route('/bookshelf/wishlist', methods=['POST'])
def add_wishlist():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()
    bookshelf = Bookshelf.query.filter_by(bookshef_owner=user.username).first()
    bookshelf_id = data['bookshelf_id']
    print(bookshelf.bookshelf_id)
    print(bookshelf_id)
    if int(bookshelf_id) == int(user.id):
        return jsonify({'message': "You can't add your own book to your wishlist"})
    else:
        wishlist = Wishlist.query.filter((Wishlist.user_id==user.id) & (Wishlist.shelf_id==data['bookshelf_id']) & (Wishlist.bookId==data['book_id'])).first()
        print(wishlist)
        if wishlist is not None:
            return jsonify({'message': "Book is already in wishlist"})

        wishlist1 = Wishlist(user_id=user.id, shelf_id=data['bookshelf_id'], bookId=data['book_id'])
        if wishlist1 is None:
            return jsonify({'message': "Failed to add"})

        db.session.add(wishlist1)
        db.session.commit()
        return jsonify({'message': "Added successful"})

@app.route('/bookshelf/remove_wishlist', methods=['POST'])
def remove_wishlist():
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()
    bookshelf = Bookshelf.query.filter_by(bookshef_owner=data['bookshelf_owner']).first()
    book = Books.query.filter_by(book_id=data['book_id']).first()
    wishlist = Wishlist.query.filter((Wishlist.user_id == user.id) & (Wishlist.shelf_id == bookshelf.bookshelf_id) &
                                     (Wishlist.bookId == book.book_id)).first()
    db.session.delete(wishlist)
    db.session.commit()
    return jsonify({'message': "Added successful"})

@app.route('/bookshelf/wishlist/user', methods=['GET'])
def show_wishlist():
    data = request.get_json()
    output = []
    user = User.query.filter_by(username=data['current_user']).first()
    wishlist_books = Wishlist.query.filter_by(user_id=user.id).all()
    for book in wishlist_books:
        user_data = {}
        get_book = Books.query.filter_by(book_id=book.bookId).first()
        owner_contains = ContainsAssociation.query.filter_by(book_id=get_book.book_id).first()
        if owner_contains is None:
            continue
        else:
            owner_bookshelf = Bookshelf.query.filter_by(bookshelf_id=owner_contains.shelf_id).first()
            bookrate = BookRateTotal.query.filter_by(bookRated=owner_contains.contains_id).first()
            if bookrate is not None:
                user_data['totalRate'] = ((bookrate.totalRate/bookrate.numofRates))
            else:
                user_data['totalRate'] = 0.0
            user_data['title'] = get_book.title
            user_data['book_id'] = get_book.book_id
            genre = HasGenreAssociation.query.filter_by(bookId=get_book.book_id).first()
            genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
            user_data['genre'] = genre_final.genre_name
            book_author = WrittenByAssociation.query.filter_by(book_id=get_book.book_id).first()
            author = Author.query.filter_by(author_id=book_author.author_id).first()
            user_data['author_name'] = author.author_name
            owner = User.query.filter_by(username=owner_bookshelf.bookshef_owner).first()
            user_data['book_cover'] = book.book_cover
            user_data['owner_fname'] = owner.first_name
            user_data['owner_lname'] = owner.last_name
            user_data['owner_username'] = owner.username
            output.append(user_data)

    return jsonify({'book': output})
### END OF WISHLIST ###

### ADD PROFILE PICTURE ###

@app.route('/profile/picture', methods=['POST'])
def add_profile():
    data = request.get_json()
    print('file')
    print(data['filename'])
    print('binary')
    file = binascii.a2b_base64(data['filename'])
    print(file)
    user = User.query.filter_by(username=data['current_user']).first()
    user.profpic = file
    db.session.commit()
    return jsonify({'message': "successful"})
### END OF PROFILE PICTURE ###

### ADD BOOK COVER PICTURE ###

# COMMENT (USER)
# @app.route('/profile/comment-user/', methods=['GET', 'POST'])
@app.route('/profile/comment-user/<int:user_id>', methods=['GET', 'POST'])
def comment(current_user, user_id):
    if user_id == current_user.id:
        comments = UserCommentAssociation.query.filter((UserCommentAssociation.user_idCommentee == current_user.id))
        x = []
        for c in comments:
            s = User.query.filter_by(id=c.user_idCommenter).first()
            x.append(s.first_name + ' ' + s.last_name)
        return jsonify({'message': 'ok', 'comments': comments, 'name': x, 'currrent_user': current_user})
    else:
        user = User.query.filter_by(id=user_id).first()
        otheruserId = user_id
        comments = UserCommentAssociation.query.filter((UserCommentAssociation.user_idCommentee == user_id))
        xs = []
        for c in comments:
            s = User.query.filter_by(id=c.user_idCommenter).first()
            xs.append(s.first_name + ' ' + s.last_name)
        if request.method == 'POST':
            comment = request.form['comment']
            commentOld = UserCommentAssociation.query.filter(
                (UserCommentAssociation.user_idCommentee == otheruserId) & (
                        UserCommentAssociation.user_idCommenterter == current_user.id)).first()

            if commentOld is not None:
                commentOld.comment = comment
                db.session.commit()

            else:
                newCommenter = UserCommentAssociation(current_user.id, otheruserId, comment)
                db.session.add(newCommenter)
                db.session.commit()
            return jsonify({'message': 'ok', 'user_id': user_id})
        return jsonify({'message': 'ok', 'user': user, 'comments': comments, 'name': xs, 'currrent_user': current_user})

@app.route('/users/coordinates', methods=['GET'])
def coordinates():
    data = request.get_json()
    user = User.query.filter_by(username=data['current_user']).first()
    users = User.query.filter(User.username!=data['current_user']).all()
    output = []
    for user in users:
        user_data = {}
        user_data['other_username'] = user.username
        user_data['other_userfname'] = user.first_name
        user_data['other_userlname'] = user.last_name
        user_data['other_user_lat'] = user.latitude
        user_data['other_user_lng'] = user.longitude
        user_data['other_profpic'] = base64.b64encode(user.profpic)
        output.append(user_data)
    return jsonify({'users': output})

@app.route('/user/coordinates', methods=['GET'])
def own_coordinates():
    data = request.get_json()
    user = User.query.filter_by(username=data['current_user']).first()
    output = []
    user_data = {}
    user_data['username'] = user.username
    user_data['firstname'] = user.first_name
    user_data['lastname'] = user.last_name
    user_data['latitude'] = user.latitude
    user_data['longitude'] = user.longitude
    user_data['profpic'] = base64.b64encode(user.profpic)
    output.append(user_data)
    return jsonify({'user': output})

@app.route('/search', methods=['GET', 'POST'])
def search():

    data = request.get_json()
    item = '%' + data['item'] + '%'

    books = Books.query.filter(((Books.title.like(item)) | (Books.year_published.like(item)) | (
    Books.types.like(item)) | cast(Books.edition, sqlalchemy.String).like(str(item)) | (
                                Books.isbn.like(item)))).all()

    if books is None:
        return jsonify({'message': 'No book found!'})

    output = []

    for book in books:
        user_data = {}
        contains = ContainsAssociation.query.filter_by(book_id=book.book_id).first()
        owner = Bookshelf.query.filter_by(bookshelf_id=contains.shelf_id).first()
        user_owner = User.query.filter_by(username=owner.bookshef_owner).first()
        genre = HasGenreAssociation.query.filter_by(bookId=book.book_id).first()
        genre_final = Genre.query.filter_by(id_genre=genre.genreId).first()
        user_data['genre'] = genre_final.genre_name
        book_author = WrittenByAssociation.query.filter_by(book_id=book.book_id).first()
        author = Author.query.filter_by(author_id=book_author.author_id).first()
        user_data['author_name'] = author.author_name
        user_data['owner_username'] = user_owner.username
        user_data['owner_fname'] = user_owner.first_name
        user_data['owner_lname'] = user_owner.last_name
        user_data['book_id'] = book.book_id
        user_data['title'] = book.title
        user_data['description'] = book.description
        user_data['year_published'] = book.year_published
        user_data['isbn'] = book.isbn
        user_data['types'] = book.types
        user_data['publisher_id'] = book.publisher_id
        user_data['book_cover'] = book.book_cover
        output.append(user_data)

    return jsonify({'book': output})

# @app.route('/addbok/<int:id>')
# def addbook(id):
