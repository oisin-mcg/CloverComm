import hashlib
#generates secure random numbers
#random is not cyrptographically secure
import secrets
#Start of Conors Code. This is a seperate "utils" class to organise our code better. It will be seperate form main flask class.
#We can call on the defs from this class in our main Flask class of "app.py".
def hash_password(password: str) -> str:
    #Generate a random 16-byte salt
    #Step 1
    #Salt is a random value added to a password before it is hashed
    salt = secrets.token_hex(16)
    #Step 2
    #Combines the salt and password to create a salted password
    salted_password = salt + password
    #Step 3:
    #Create a SHA-256 hash of the salted password
    #Provides a secure hash function that gives fixed size output
    #however string must be encoded to bytes as haslib only works with byte data
    hash_object = hashlib.sha256(salted_password.encode())
    #Step4:
    #Convert the hash to a hexadecimal format
    #hexdigest() returns has in hexadecimal format, easier to store & read.
    hashed_password = hash_object.hexdigest()
    #Step 5:
    #Return the salt and hashed password in the format: "salt$hashed_password"
    return f"{salt}${hashed_password}"

def verify_password(stored_password: str, input_password: str) -> bool:
   #Step 1:
    #Split the stored password to get the salt and hash
    salt, hashed_password = stored_password.split('$')
    #Step 2:
    #combine salt with input password to retrieve the salt and the hash.
    #allows for the inpu tto be hashed with the same salt used originally
    salted_input_password = salt + input_password
    #Step 3:
    #Hash the salted input password
    hash_object = hashlib.sha256(salted_input_password.encode())
    hashed_input_password = hash_object.hexdigest()
    #Step 4:
    #Compare the hashed input password with the stored hash
    #assuming they match it means the input password is correct
    return hashed_password == hashed_input_password

#Example Usage 1:
#Hash a user's password (e.g., during registration)
hashed_pw = hash_password("user_password123")
print("Hashed Password:", hashed_pw)

#Verify the password (e.g., during login)
is_valid = verify_password(hashed_pw, "user_password123")
print("Password is valid:", is_valid)
#will need to incorporate 'Flask' to ensure the frontend info is passed to the python backend. Wwill also have to use some form of JavaScript.
#End of Conors Code.

#Gustavo's code
from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)

def encryption(message):
    token = f.encrypt(message.encode())
    return token.decode()

def decryption(token):
    decrypted_message = f.decrypt(token.encode())
    return decrypted_message.decode()
# end of Gustavo's