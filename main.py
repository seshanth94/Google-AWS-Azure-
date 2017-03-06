from flask import Flask, render_template, request, session
from pymongo import MongoClient
import base64
from bson.objectid import ObjectId
from imageData import imageData
from userData import userData

app = Flask(__name__)
app.secret_key = "test"

userTable = "user"
filesTable = "userfiles"


@app.route('/')
def hello_world():
    return render_template("home.html")


def createDBConn():
    client = MongoClient('mongodb://146.148.100.237:27017')
    db = client.eideticmemories
    return client, db


@app.route('/register_user', methods=['POST'])
def register_user():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    dict = {}
    dict['name'] = name
    dict['username'] = username
    dict['password'] = password
    client, db = createDBConn()
    usercollection = db[userTable]
    usercollection.insert(dict)
    client.close()
    return render_template('home.html')


@app.route('/login_user', methods=['POST'])
def login_user():
    if request.form['home_button'] == 'Register':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']

        client, db = createDBConn()
        usercollection = db[userTable]

        userdict = {}

        userdict['username'] = username
        userdict['password'] = password
        user = usercollection.find_one(userdict)
        client.close()
        if user is not None:
            session['username'] = username
            session['userid'] = str(user['_id'])
            session['showimagesfor'] = str(user['_id'])
            images = getImages(ObjectId(session['userid']))
            return render_template('user.html', username=username)
        else:
            return render_template('home.html')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    username = session['username']
    client, db = createDBConn()
    file = request.files['upload_2_mongo']
    upload_comments = request.form['upload_comments']

    content = file.read()

    filesDict = {}

    filesDict['userid'] = ObjectId(session['userid'])
    filesDict['upload_comments'] = [upload_comments]
    filesDict['filedata'] = "data:image/jpeg;base64," + base64.b64encode(content)
    filesDict['filesize'] = len(content)

    filecollection = db[filesTable]
    filecollection.insert(filesDict)
    return render_template('user.html', username=username)


def getImages(userid):
    client, db = createDBConn()

    filecollection = db[filesTable]
    filesdict = {}

    filesdict['userid'] = userid
    filesID = filecollection.find(filesdict)
    client.close()

    images = []
    for files in filesID:
        fileID = files['_id']
        comment = files['upload_comments']
        picdata = files['filedata']
        picture = imageData(fileID, comment, picdata)
        images.append(picture)
    return images


@app.route('/view_images', methods=['POST'])
def view_images():
    client, db = createDBConn()

    filecollection = db[filesTable]
    filesdict = {}

    filesdict['userid'] = ObjectId(session['showimagesfor'])
    filesID = filecollection.find(filesdict)
    client.close()

    images = []
    for files in filesID:
        fileID = files['_id']
        comment = files['upload_comments']
        picdata = files['filedata']
        picture = imageData(fileID, comment, picdata)
        images.append(picture)
    return render_template('view_images.html', images=images)


@app.route('/view_other_images', methods=['POST'])
def view_other_images():
    client, db = createDBConn()
    listusers = []
    usercollection = db[userTable]
    users = usercollection.find()

    for user in users:
        if user['username'] != session['username']:
            current_user = userData(user['username'],str(user['_id']))
            listusers.append(current_user)

    return render_template('view_other_images.html', listusers=listusers)


@app.route('/view_images_for', methods=['GET'])
def view_images_for():
    userid = request.args.get('userid')
    session['showimagesfor'] = userid
    return view_images()


@app.route('/delete_file', methods=['POST'])
def delete_file():
    fileid = request.form['delete_button']
    client, db = createDBConn()

    filecollection = db[filesTable]
    file = ObjectId(fileid)
    filesdict = {}
    filesdict['_id'] = file
    filesID = filecollection.find(filesdict)

    for files in filesID:
        filecollection.remove(files['_id'])
    client.close()
    images = getImages(ObjectId(session['showimagesfor']))
    return render_template('view_images.html', images=images)


@app.route('/add_comment',methods=['POST'])
def add_comment():
    new_comment = request.form['new_comment']
    id = request.form['id']
    client, db = createDBConn()

    filecollection = db[filesTable]
    filecollection.update({'_id': ObjectId(id)}, {'$push':{'upload_comments': new_comment}})
    client.close()
    images = getImages(ObjectId(session['showimagesfor']))
    return render_template('view_images.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)