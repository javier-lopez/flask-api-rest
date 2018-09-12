from flask import redirect, url_for, request, g, abort
from flask_httpauth import HTTPBasicAuth

from .       import app
from .models import User, Mood

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.objects(username=username_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return {'token': token.decode('ascii')}

@app.route('/api/user', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.objects(username=username).first() is not None:
        # existing user
        return {'username': username}, 201, {'Location': url_for('get_user', username=username, _external = True)}

    new_user = User(
                username=username,
                password=password,
                ).save()

    return {'username': username}, 201, {'Location': url_for('get_user', username=username, _external = True)}

@app.route('/api/user/<username>')
def get_user(username):
    user = User.objects(username=username).first()
    if not user:
        abort(404)

    moods  = user.moods
    states = []
    for mood in moods:
        if not states.count(mood['mood']) > 0:
            states.append(mood['mood'])

    states_with_percentages = {}
    for state in states:
        state_percentage = (100 * len(user.moods_filter(state))) / len(moods)
        states_with_percentages[state] = state_percentage

    return states_with_percentages

@app.route('/api/user/<username>/<mood>')
def get_user_locations_in_mood(username,mood):
    user = User.objects(username=username).first()
    if not user:
        abort(400)

    moods  = user.moods_filter(mood)
    coords = []
    for mood in moods:
        if not coords.count(mood['coordinates']) > 0:
            coords.append(mood['coordinates'])

    return coords

@app.route('/api/mood', methods = ['POST'])
@auth.login_required
def new_mood():
    user = User.objects(username=g.user.username).first()

    mood = request.json.get('mood')
    lot  = float(request.json.get('lot'))
    lat  = float(request.json.get('lat'))

    if mood is None or lot is None or lat is None:
        abort(400) # missing arguments

    new_mood = Mood.objects(mood=mood, coordinates=[lot,lat]).first()

    if new_mood is None:
        new_mood = Mood(
                    mood=mood,
                    coordinates=[lot,lat],
                    ).save()

    user.add_mood(new_mood).save()

    return {
            'username': user.username,
            'mood': new_mood.mood,
            'coordinates': new_mood.coordinates,
        }, 201, {'Location': url_for('get_user', username=user.username, _external = True)}

@app.route('/api/whoami')
@auth.login_required
def get_resource():
    return {'whoami': 'Hello, %s!' % g.user.username}
