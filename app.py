from flask import Flask, jsonify, request
from flask_mail import Mail, Message
import random
import string
import ssl
import certifi
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

client = MongoClient("mongodb+srv://myAtlasDBUser:Sai123@myatlasclusteredu.qifwasp.mongodb.net/UserPython?retryWrites=true&w=majority",
                     tlsCAFile=certifi.where())
db = client['UserPython']

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'saikrishnanaiudub@gmail.com'
app.config['MAIL_PASSWORD'] = 'rvvo vkfi hepj ytfl'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

@app.route("/", methods=['GET'])
def home():
    return jsonify("Hello World")

@app.route("/register", methods=["POST"])
def Register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    user = db.users.find_one({'email': email})
    
    if user:
        return jsonify({'message': "User already exists, please log in"}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    otp = ''.join(random.choices(string.digits, k=6))
    
    
    db.users.insert_one({
        'email': email,
        'password': hashed_password,
        'otp': otp,
        'is_verified': False
    })
    
    msg = Message('Your OTP Code', sender="saikrishnanaiudub@gmail.com", recipients=[email])
    msg.body = f"Your OTP Code is {otp}, please verify your email"
    mail.send(msg)
    
    return jsonify({'message': "OTP sent to your email"}), 200


@app.route("/verify",methods=['POST'])
def Verify():
    data = request.json
    email=data.get("email")
    otp=data.get("otp")
    
    user = db.users.find_one({'email':email})
    if not user :
        return jsonify({'message':"user not register,please register"}),404
    
    if user['otp'] == otp:
         db.users.update_one({'email':email,},{'$set':{'is_verified':True,'otp':None}})
         return jsonify({"message":"Email Verified Succesfully"})
    else:
         return jsonify({"message":"Invalid Otp"}),400

if __name__ == "__main__":
    app.run(debug=True)
