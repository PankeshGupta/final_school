from flask import Flask, render_template, request, redirect, jsonify,make_response
from flask_pymongo import PyMongo
import secrets

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'app'
app.config['MONGO_URI'] = 'mongodb://pankesh:11121989@ds153413.mlab.com:53413/app'
mongo = PyMongo(app)

#=================== App Views ==========================
@app.route('/')
def index():
    if get_cookie():
        return (redirect('/user/{}'.format(get_cookie())))
    else:
        return render_template('index.html')

@app.route('/new_user')
def new_user():
    return render_template('new_user.html')
@app.route('/user/<username>')
def user(username):
    student_db = mongo.db.students.find()
    return render_template('user.html',user= username, student_list = [student for student in student_db])
#===================== Cookie methods ===================

def get_cookie():
    secret_hash = request.cookies.get('secret_hash')
    users = mongo.db.users
    login_user = users.find_one({'secret_hash' : '{}'.format(secret_hash)})
    if login_user:
        return login_user['name']
    else :
        return False
@app.route('/api/logout', methods=['GET'])
def logout():
    print("=========inside logout function ===========")
    resp = make_response(jsonify({'messge': "Logout sucessfull"}))
    resp.set_cookie('secret_hash','')
    return resp, 200

def generate_secret_hash():
    return secrets.token_hex(15)


#===================== Api's ============================

@app.route('/api/login', methods=['POST'])
def login():
    users = mongo.db.users
    user_parms = request.form
    login_user = users.find_one({'name' : user_parms['username']})
    if login_user:
        if user_parms['password']== login_user['password']:
            user_secret_hash = login_user['secret_hash']
            message = jsonify({"messsge":"Login sucessful"})
            resp = make_response(message)
            resp.set_cookie('secret_hash',user_secret_hash)
            return resp, 200
    else:
        return jsonify({"message":"Access Denied"}), 401


@app.route('/api/register',methods= ['POST'])
def register():
    try:

        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})
        print("=============={}============".format(existing_user))
        if existing_user is None:
            user_params = request.form
            print("==============User pasrams======{}==============".format(user_params))
            secret_hash = generate_secret_hash()
            users.insert({'name' : user_params['username'], 'password' : user_params['password'], 'secret_hash':'{}'.format(secret_hash)})
            return jsonify({"message":"Registration Sucessfull"}), 200


        else:
            return jsonify({"message":"User already exists"}), 401
    except:
        raise RuntimeError

@app.route('/api/student',methods=['POST','PUT','DELETE'])
def student():
    print("==========inside stuent function ==========")
    students = mongo.db.students
    student_params = request.form
    if request.method == 'POST':
        print("=========== This is a post request====")
        try:
            students.insert({'name' : student_params['name'], 'class' : student_params['class']})
            return jsonify({'status':'student added sucessfully'}), 200
        except:
            raise RuntimeError
    if request.method=='PUT':
        try:
            students.update(
                { 'id': '{}'.format(student_params['id'])  },
                {  'name' : '{}'.format(student_params['name']),
                   'class': '{}'.format(student_params['class'])

                },
                { 'upsert': 'true' }
               )
        except:
            raise RuntimeError
    if request.method == 'DELETE':
        print('========== inside delete=========')
        try:
            students.remove({"name": "{}".format(student_params['name'])}, {'justOne': 'true'})
        except:
            raise RuntimeError

#=======================================================================================

if __name__=='__main__':
    app.run(debug=True)
