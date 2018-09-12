from datetime     import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from . import app, db, bcrypt

class User(db.Document):
    username  = db.StringField(required=True, unique=True)
    password  = db.StringField(required=True); password_hashed = db.BooleanField(default=False)
    moods     = db.ListField(db.ReferenceField('Mood'))

    def clean(self):
        #clean will be called on .save()
        #you can do whatever you want to clean data before saving

        #workaround for already hashed password, mongoengine makes difficult to
        #override the __init__ constructor:
        #https://stackoverflow.com/questions/16881624/mongoengine-0-8-0-breaks-my-custom-setter-property-in-models
        #http://docs.mongoengine.org/guide/document-instances.html#pre-save-data-validation-and-cleaning
        if not self.password_hashed:
            self.password        = bcrypt.generate_password_hash(self.password).decode('utf-8')
            self.password_hashed = True

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def reset_password(self, password):
        self.password        = bcrypt.generate_password_hash(password).decode('utf-8')
        self.password_hashed = True
        return self

    def generate_auth_token(self, expiration=600): #10 mins
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({'username': self.username})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.objects(username=data['username']).first()
        return user

    def add_mood(self, mood):
        if not self.has_mood(mood):
            self.moods.append(mood)
        return self

    def delete_mood(self, mood):
        if self.has_favorite(mood):
            self.moods.remove(mood)
        return self

    def has_mood(self, mood):
        return self.moods.count(mood) > 0

    def moods_filter(self, mood):
        moods = []
        for m in self.moods:
            if m.mood == mood:
                moods.append(m)
        return moods

class Mood(db.Document):
    mood        = db.StringField(required=True, choices=('happy', 'sad', 'neutral'))
    coordinates = db.GeoPointField(required=True)
