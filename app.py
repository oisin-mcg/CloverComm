from flask import Flask, redirect, request, url_for, render_template, flash

#here i will call from the utils class, the defs i will need.
from utils import hash_password, verify_password, encryption, decryption, encryptImage, decryptImage

#https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3
app = Flask(__name__, template_folder="template", static_folder="static")

#https://www.youtube.com/watch?v=mqhxxeeTbu0
#https://www.youtube.com/@TechWithTim

app.secret_key="secret_key"
from flask import Flask, render_template, request, jsonify
import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend




@app.route("/")
def home():
    return render_template("index.html")

#Conor's Page
#array for the stored passwords.
hashed_passwords = []
@app.route("/messenger", methods=["GET", "POST"])
def messenger_view():
    #access password list..
    global hashed_passwords
    #flag to control when to show the stored passwords
    show_passwords_flag = False
    #initialize variable to store hashed password
    hashed_password = None  
    if request.method == 'POST':
        #handle password submission
        if "submit_password" in request.form:
            password = request.form.get("password", "").strip()
            if password:
                hashed_password = hash_password(password)
                hashed_passwords.append(hashed_password)
                flash("Password stored!", "success")
            else:
                flash("Please enter a password.", "error")
        elif "show_passwords" in request.form:
            #simply refresh to show the list
            show_passwords_flag = True
        elif "clear_passwords" in request.form:
            #clear the stored hashed passwords when the "Clear Passwords" button is clicked
            hashed_passwords.clear()
            flash("All passwords cleared.", "info")
        elif "verify_password" in request.form:
            #handle password verification
            input_password = request.form.get("verify_input_password", "").strip()
            if input_password:
                password_verified = False
                #check if the input password matches any stored password
                for stored_password in hashed_passwords:
                    if verify_password(stored_password, input_password):
                        password_verified = True
                        break
                if password_verified:
                    flash("Password is correct.", "success")
                else:
                    flash("Password is incorrect.", "error")
            else:
                flash("Please enter a password to verify.", "error")

    return render_template("messenger.html", hashed_passwords=hashed_passwords)

    return render_template("messenger.html", hashed_passwords=hashed_passwords)

##ois code

# global counter for connection count
connection_count = 0

#here i am generating a unique key for the voice call connection capibilities
def generate_key(call_id, password):
    salt = call_id.encode()  # using Call ID as salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode()


@app.route("/voice", methods=["GET", "POST"])
def voice_view():
    return render_template("voice.html") 

@app.route('/generate_key', methods=['POST'])
def get_key():
    global connection_count
    data = request.get_json()
    call_id = data.get('call_id')
    password = data.get('password')
    if not call_id or not password:
        return jsonify({'error': 'Call ID and password are required.'}), 400

    #increment the connection counter when a key is generated (new connection) or when a call starts (old connection resumed)
    connection_count += 1
    key = generate_key(call_id, password)
    return jsonify({'key': key, 'connection_count': connection_count})

#display user connections to all connected users
@app.route('/get_connection_count', methods=['GET'])
def get_connection_count():
    return jsonify({'connection_count': connection_count})


#Gustavo's Page
@app.route("/gustavo", methods=["GET", "POST"])
def gustavo():
    chat_log = []
    if request.method == "POST":
        if 'user1_send' in request.form:
            user1_message = request.form.get("user1_message")
            if user1_message:
                encrypted_message = encryption(user1_message)
                chat_log.append(("User 1", encrypted_message))
        elif 'user2_send' in request.form:
            user2_message = request.form.get("user2_message")
            if user2_message:
                encrypted_message = encryption(user2_message)
                chat_log.append(("User 2", encrypted_message))

    processed_chat_log = [(user, message, decryption(message)) for user, message in chat_log]

    return render_template("gustavo.html", chat_log=processed_chat_log)
#Vitor's Page
@app.route("/imageEncryption", methods=["GET", "POST"])
def imageEncryption():
   
    image_message = None

    if request.method =="POST":
        if 'encryptImage' in request.form:
            path = request.form.get("path")
            key = request.form.get("key")

            if path and key:
                encryptImage(path, key)
                image_message = "Your Image has been encrypted"
                
        elif 'decryptImage' in request.form:
            path = request.form.get("path")
            key = request.form.get("key")
            
            if path and key:
                decryptImage(path, key)
                image_message = "Your Image has been decrypted"
    
    return render_template("imageEncryption.html", image_message=image_message)

if __name__ == '__main__':
    app.run(debug=True)
