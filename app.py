from flask import Flask, redirect, request, url_for, render_template, flash

#here i will call from the utils class, the defs i will need.
from utils import hash_password, verify_password, encryption, decryption, encryptImage, decryptImage

#https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3
app = Flask(__name__, template_folder="template", static_folder="static")

#https://www.youtube.com/watch?v=mqhxxeeTbu0
#https://www.youtube.com/@TechWithTim

@app.route("/")
def home():
    return render_template("index.html")

#Conor's Page
@app.route("/messenger", methods=["GET", "POST"])
def messenger_view():
    #Initialize variable to store hashed password
    hashed_password = None  
    if request.method == 'POST':
        #Get the password from the form input
        password = request.form['password']
        #Call hash_password to hash the entered password
        hashed_password = hash_password(password)
    #Render the template with the hashed password (if available)
    return render_template("messenger.html", hashed_password=hashed_password)


@app.route("/voice")
def voice_view():
    return render_template("voice.html") 

@app.route("/video")
def video_view():
    return render_template("video.html") 
#Gustavo's Page
@app.route("/gustavo", methods=["GET", "POST"])
def gustavo():
    encrypted_message = None
    decrypted_message = None

    if request.method == "POST":
        if 'encrypt' in request.form:
            print("Encrypting message...")
            message = request.form.get("message")
            if message:
                encrypted_message = encryption(message) 
        elif 'decrypt' in request.form:
            print("Decrypting message...")
            token = request.form.get("encrypted_message")
            if token:
                decrypted_message = decryption(token) 
                
    return render_template("gustavo.html", encrypted_message=encrypted_message, decrypted_message=decrypted_message)

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
