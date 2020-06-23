from flask import Flask, request
from flask_restplus import Resource, Namespace, fields, reqparse, inputs
from .SharedModel import db
from .Notes import NotesDAO
api = Namespace('Books', description='Operations related to books')

books = []

# Api model
book_api_model = api.model('Book', {
    'title': fields.String(description='Book title'),
    'author': fields.String(description='Book author'),
    'id': fields.Integer(description='Book ID'),
    'genre': fields.String(description='Book genre'),
    'year_released': fields.String(description='year released'),
    'checked_out': fields.Boolean(description ='Is the book checked out')
})

#parser to make a book
parser = reqparse.RequestParser()
parser.add_argument('title', required=False)
parser.add_argument('author', required=False)
parser.add_argument('genre', required=False)
parser.add_argument('year_released', required=False)
parser.add_argument('checked_out', required=False, type=inputs.boolean)


#searchparser to find a book
searchparser = reqparse.RequestParser()
searchparser.add_argument('title', required=False)
searchparser.add_argument('author', required=False)
searchparser.add_argument('genre', required=False)
searchparser.add_argument('year_released', required=False)
searchparser.add_argument('checked_out', default = False, required=False, type=inputs.boolean)



#Book class for python
class Book(object):
    def __init__(self, title, author, id, genre, year_released, checked_out):
        self.title = title
        self.author = author
        self.id = id
        self.genre = genre
        self.year_released = year_released
        self.checked_out = checked_out


#Database model for books
class BookDbModel (db.Model):
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(100))
    year_released = db.Column(db.String(100))
    checked_out = db.Column(db.Boolean, default=False)

#Book DAO
class BookDAO(object):
    def __init__(self):
        self.counter = 0

    def to_dic(self, sql_object):
        my_list = []
        for book in sql_object:
            my_list.append({"title": book.title, "author": book.author, "id": book.id, "genre": book.genre, "year_released": book.year_released, "checked_out": book.checked_out})
        return my_list

    def to_dic_note(self, notes):
        my_list = []
        for note in notes:
            my_list.append({"user_id":note['user_id'], "notes":note['notes']})
        return my_list

    def get_all_books(self):
        all_books = BookDbModel.query.all()
        return self.to_dic(all_books)

    def store(self, new_book):
        while db.session.query(BookDbModel.id).filter_by(id=self.counter).scalar() is not None:
            self.counter = self.counter + 1

        new_book.id = self.counter
        query = BookDbModel(title=new_book.title, author=new_book.author, id= new_book.id, genre=new_book.genre,year_released=new_book.year_released, checked_out= new_book.checked_out)
        db.session.add(query)
        db.session.commit()
        return new_book

    def get_a_book(self, book_id):
        a_book = BookDbModel.query.filter_by(id=book_id).first()
        return a_book

    def update(self, book_id, updated_book):
        old_book = self.get_a_book(book_id)
        if not old_book:
            api.abort(404, description = "could not update book")
        if updated_book['title'] is not None:
            old_book.title = updated_book['title']
        if updated_book['author'] is not None:
            old_book.author = updated_book['author']
        if updated_book['genre'] is not None:
            old_book.genre = updated_book['genre']
        if updated_book['year_released'] is not None:
            old_book.year_released = updated_book['year_released']
        if updated_book['checked_out'] is not None:
            old_book.checked_out = updated_book['checked_out']
        db.session.commit()

    def delete(self, book_id):
        deleted_book = self.get_a_book(book_id)
        if not deleted_book:
            api.abort(404, description = "could not delete a book")
        db.session.delete(deleted_book)
        db.session.commit()

    def changeCheckOut(self, book_id, status):
        single_book = BookDbModel.query.filter_by(id=book_id).first()
        single_book.checked_out = status
        db.session.commit()



DAO = BookDAO()









@api.route('/')
@api.response(202, 'Accepted')
@api.response(404, 'Could not get a list of books')
class BooksCollection(Resource):

    # @api.expect(parser)
    def get(self):
        '''
        Returns list of books from given parameter.
        '''
        return DAO.get_all_books(), 202

    @api.response(202, 'book successfully created')
    @api.response(404, 'Could not create a new book')
    @api.expect(parser)
    def post(self):
        '''
        Creates a new book.
        '''
        data = parser.parse_args()
        new_book= Book(title=data['title'],author= data['author'],id= 0,genre= data['genre'],year_released=data['year_released'],checked_out=data['checked_out'])
        DAO.store(new_book)
        return 'book successfully created', 202



@api.response(202, 'Accepted')
@api.response(404,'ID does not exist')
@api.route('/book/<int:id>')
class BookOperation(Resource):
    @api.response(202, 'Book was successfully found')
    @api.response(404, 'Could not get specific book')
    @api.marshal_with(book_api_model)
    #@api.expect(parser)
    def get(self, id):
        '''
        Returns a specific book.
        '''
        book = DAO.get_a_book(id)
        if not book:
            api.abort(404, description = 'Could not get specific book')
        else:
            return book

    @api.response(404, "could not update book")
    @api.response(202, 'Book successfully updated')
    @api.expect(parser)
    def put(self, id):
        '''
        Updates a book
        '''
        data = parser.parse_args()
        updated_book = data
        DAO.update(id, updated_book)
        return 'Book successfully updated', 202

    @api.response(404, "could not delete a book")
    @api.response(200, 'Book has been deleted')
    def delete(self, id):
        '''
        Deletes a book.
        '''
        DAO.delete(id)
        return 'Book deleted successfully', 200

@api.response(404, "could not find a book")
@api.response(202, 'Book has been found')
@api.route('/AdvancedSearch')
class SearchController(Resource):
    @api.expect(parser)
    def get(self):
        '''
        An advanced search engine
        '''
        search = searchparser.parse_args()
        title = search['title']
        author = search['author']
        genre = search['genre']
        year_released = search['year_released']
        print(year_released)
        checked_out = search['checked_out']
        q = BookDbModel.query
        if title:
            q = q.filter_by(title = title)
        if author:
            q = q.filter_by(author = author)
        if genre:
            q = q.filter_by(genre = genre)
        if year_released:
            q = q.filter_by(year_released = year_released)
            print(DAO.to_dic(q.all()))
        if checked_out == True or checked_out == False:
            q = q.filter_by(checked_out = checked_out)



        return DAO.to_dic(q.all()), 202

Notes_DAO = NotesDAO()

@api.route('/book/<int:book_id>/notes')
@api.response(202, 'Accepted')
@api.response(404, 'Could not get a list of notes about the book')
class NoteCollectionController(Resource):
    def get(self, book_id):
        '''
        Returns list of notes for a book.
        '''
        notes = Notes_DAO.get_notes_by_book(book_id)
        new_format_notes = DAO.to_dic_note(notes)
        return new_format_notes, 202