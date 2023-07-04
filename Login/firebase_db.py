import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("Login\credentials.json")

firebase_admin.initialize_app(cred, {'databaseURL' : "https://kaki-db097-default-rtdb.asia-southeast1.firebasedatabase.app/"})


#Creating data into the realtime database

# data = {
#     "First Name": "Jun Ming",
#     "Last Name": "Ng", 
#     "Birthdate": "20/07/2005",
#     "Email": "mrngjunming@gmail.com"
# }

data = {
    "First Name": "Pin Shien",
    "Last Name": "Seah", 
    "Birthdate": "14/07/2005",
    "Email": "seahpinshien@gmail.com"
}

ref = db.reference("Users/Staff/Account Details")
ref.set(data)