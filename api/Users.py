from flask import Flask, request
from flask_restplus import Namespace, Resource, fields, reqparse, inputs
from .SharedModel import db
from .Notes import Notes, NotesDAO, NotesDbModel

userparser = reqparse.RequestParser()
userparser.add_argument('name', type=str)
userparser.add_argument('notified', type=inputs.boolean)
userparser.add_argument('email', type=str)



noteparser = reqparse.RequestParser()
noteparser.add_argument('book_id', type=int)
noteparser.add_argument('notes', type=str)

updatenoteparser = reqparse.RequestParser()
updatenoteparser.add_argument('note_id', type=int, required = True)
updatenoteparser.add_argument('book_id', type=int, required = True)
updatenoteparser.add_argument('notes', type=str)

deletenoteparser = reqparse.RequestParser()
deletenoteparser.add_argument('note_id', type=int, required = True)

api = Namespace('Users', description='Operations related to users')

user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'name': fields.String(required=True, description='The name of a user'),
    'notified': fields.Boolean(required=False, description='notified or not'),
    'email': fields.String(required=True, description='The email associated with a user')
})


# Database model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    notified = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(80))


# User class
class User(object):
    def __init__(self, id, name, notified, email):
        self.id = id
        self.name = name
        self.notified = False
        self.email = email


# User DAO
class UserDAO(object):
    def __init__(self):
        self.counter = 0

    def to_dic(self, sql_object):
        my_list = []
        for i in sql_object:
            my_list.append({"id": i.id, "name": i.name, "notified": i.notified, "email": i.email})
        return my_list

    def to_dic_note(self, notes):
        my_list = []
        for note in notes:
            my_list.append({"book_id":note['book_id'], "notes":note['notes']})
        return my_list

    def get_all_users(self):
        all_record = Users.query.all()
        return self.to_dic(all_record)

    def store(self, new_user):
        while db.session.query(Users.id).filter_by(id=self.counter).scalar() is not None:
            self.counter = self.counter + 1

        new_user.id = self.counter
        query = Users(id=new_user.id, name=new_user.name, notified=new_user.notified, email=new_user.email)
        db.session.add(query)
        db.session.commit()
        return new_user

    def get_a_user(self, user_id):
        a_user = Users.query.filter_by(id=user_id).first()
        return a_user

    def update_notes(self, user_id, updated_notes):
        old_record = NotesDbModel.query.filter_by(id=updated_notes['note_id'], user_id=user_id, book_id=updated_notes['book_id']).first()
        if not old_record:
            api.abort(404, description = "Users notes could not be updated")
        old_record.notes = updated_notes['notes']
        db.session.commit()


    def update(self, id, updated_user):
        old_record = self.get_a_user(id)
        if not old_record:
            api.abort(404, description = "Could not update current user")
        if updated_user['name'] is not None:
            old_record.name = updated_user['name']
        if updated_user['notified'] is not None:
            old_record.notified = updated_user['notified']
        if updated_user['email'] is not None:
            old_record.email = updated_user['email']
        db.session.commit()


    def delete(self, id):
        deleted_user = self.get_a_user(id)
        if not deleted_user:
            api.abort(404, description = "User could not be deleted")
        db.session.delete(deleted_user)
        db.session.commit()


    def delete_notes(self, id):
        a_user = self.get_a_user(id)
        if not a_user:
            api.abort(404, description = "Users notes could not be deleted")
        db.session.commit()

DAO = UserDAO()
Notes_DAO = NotesDAO()

@api.response(202, 'users successfully obtained')
@api.response(404, 'Could not find any users')
@api.route('/')
class UserCollection(Resource):
    def get(self):
        ''' Return a list of users'''
        return DAO.get_all_users(), 202

    @api.response(202, 'User successfully created')
    @api.response(404, 'Could not create a new user')
    @api.expect(userparser)
    def post(self):
        '''Creates a new user.'''
        data = userparser.parse_args()
        new_user = User(0, data['name'], data['notified'], data['email'])
        DAO.store(new_user)
        return 'success', 202


@api.route('/<int:id>')
class UserOperations(Resource):
    @api.response(200, 'User successfully obtained')
    @api.response(404, 'Could not get that specific user')
    @api.marshal_with(user_model)
    def get(self, id):
        '''Return a certain user by id'''
        user = DAO.get_a_user(id)
        if not user:
            api.abort(404, description = "could not get that specific user")
        else:
            return user, 200

    @api.response(200, 'User successfully updated')
    @api.response(404, 'Could not update current user')
    @api.expect(userparser)
    def put(self, id):
        ''' Updates a current user'''
        a_updated_user = userparser.parse_args()
        DAO.update(id, a_updated_user)
        return 'User successfully updated', 200

    @api.response(200, 'User successfully deleted')
    @api.response(404, 'User could not be deleted')
    def delete(self, id):
        '''Deletes a user'''
        DAO.delete(id)
        return 'User successfully deleted', 200

    book_id_parser = reqparse.RequestParser()
    book_id_parser.add_argument('book_id', type=int)
    book_id_parser.add_argument('notes', type=str)



@api.route('/<int:user_id>/note')
class UserNoteController(Resource):
    @api.response(200, 'Users notes successfully created')
    @api.response(404, 'Users notes could not be created')
    @api.expect(noteparser)
    def post(self, user_id):
        '''creates a note from a user about a book using a book id'''
        data = noteparser.parse_args()
        book_id = data['book_id']
        notes = data['notes']
        new_note = Notes(id=0,book_id=book_id, user_id=user_id, notes=notes)
        Notes_DAO.store(new_note)
        return 'Users notes successfully created', 200

    @api.response(200, 'Users notes successfully updated')
    @api.response(404, 'Users notes could not be updated')
    @api.expect(updatenoteparser)
    def put(self, user_id):
        '''updates a note by a user with a given required parameters'''
        data = updatenoteparser.parse_args()
        DAO.update_notes(user_id, data)
        return 'Users notes successfully updated', 200


    @api.response(200, 'Notes successfully deleted')
    @api.response(404, 'Users notes could not be deleted')
    @api.expect(deletenoteparser)
    def delete(self, user_id):
        '''deletes a users note with a given note id'''
        data = deletenoteparser.parse_args()
        note_id = data['note_id']
        Notes_DAO.delete_by_user(user_id,note_id)
        return 'Notes successfully deleted', 200


@api.route('/<int:user_id>/NoteCollection')
@api.response(202, 'Accepted')
@api.response(404, 'Could not get a list of notes about the book')
class NoteCollectionController(Resource):
    def get(self, user_id):
        '''
        Returns list of notes by a specific user.
        '''
        notes = Notes_DAO.get_notes_by_user(user_id)
        new_format_notes = DAO.to_dic_note(notes)
        if not new_format_notes:
            api.abort(404, description='Could not get a list of notes about the book')
        return new_format_notes, 202