from flask import Flask, render_template, request , session ,redirect
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import pyrebase
import time

app = Flask(__name__)
app.secret_key = 'who420is420in12paris'

cred = credentials.Certificate("Account_management/credentials.json")
firebase_admin.initialize_app(cred)

config = {
    "apiKey": "AIzaSyBTdJ-q5cuHwkH7iZ9Np2fyFJEeCujN0Jg",
    "authDomain": "kaki-db097.firebaseapp.com",
    "projectId": "kaki-db097",
    "databaseURL": "https://kaki-db097-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "kaki-db097.appspot.com",
    "messagingSenderId": "521940680838",
    "appId": "1:521940680838:web:96e15f16f11bb306c91107",
    "measurementId": "G-QMBGXFXJET"
}

firebase = pyrebase.initialize_app(config)
pyredb = firebase.database()
pyreauth = firebase.auth()
pyrestorage = firebase.storage()

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Validate reCAPTCHA response
        recaptcha_response = request.form['g-recaptcha-response']
        secret_key = "6LcVAHgnAAAAADAjOy6d57YNiSnviQnkqJxuv9KG"  
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"

        data = {
            'secret': secret_key,
            'response': recaptcha_response
        }

        response = requests.post(captcha_url, data=data)
        result = response.json()

        if not result['success']:
            unsuccessful = 'Please complete the reCAPTCHA verification.'
            return render_template('account_management/login.html', umessage=unsuccessful)

        # Rest of your login logic (similar to your existing code)
        email = request.form['user_email']
        password = request.form['user_pwd']
        try:
            user = pyreauth.sign_in_with_email_and_password(email, password)
            # Get the Firebase token ID
            token_id = user['idToken']
            # Save the token ID in the session
            session['user_token'] = token_id

            firebase_user = auth.get_user(user['localId'])
            email_verified = firebase_user.email_verified
            if not email_verified:
                # Update user's custom claims to indicate pending email verification
                auth.set_custom_user_claims(user['localId'], {'emailVerified': False})

                # Send the email verification
                pyreauth.send_email_verification(user['idToken'])
                print("Verification email sent. Waiting for email verification...")
                # Wait until the email is verified
                while True:
                    firebase_user = auth.get_user(user['localId'])
                    email_verified = firebase_user.email_verified
                    if email_verified:
                        # Update user's custom claims to indicate email verification completed
                        auth.set_custom_user_claims(user['localId'], {'emailVerified': True})
                        print("Email verified.")
                        break
                    else:
                        print("Email not verified. Waiting...")
                        time.sleep(5)  # Add a 5-second delay before checking again
            else:
                print("Email already verified.")

            return redirect('/staff/users')
            # return redirect('/dashboard')
        except:
            unsuccessful = 'Please check your credentials'
            return render_template('account_management/login.html', umessage=unsuccessful)

    return render_template('account_management/login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_token' in session:
        # Retrieve the token ID from the session
        token_id = session['user_token']

        # Use the token ID to get the user's UID from Firebase authentication
        user = pyreauth.get_account_info(token_id)

        uid = user['users'][0]['localId']
        
        print(f'user: {user}')

        # Use the UID as the key in the database to get the user data
        user_data = pyredb.child("Users").child("Consumer").child(uid).get().val()
        print(user_data)
        return render_template('account_management/update_usercred.html', user_data=user_data)
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    # Clear the session on logout
    session.pop('user_email', None)
    return redirect('/')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        pwd0 = request.form['user_pwd0']
        pwd1 = request.form['user_pwd1']
        if pwd0 == pwd1:
            email = request.form['user_email']
            try:
                user = auth.create_user(
                    email=email,
                    password=pwd0
                )
                # Save the email in the session
                session['user_email'] = email

                session['user_token'] = user

                session['pwd'] = pwd0

                # Get the Firebase token ID (use user.uid instead of user['idToken'])
                token_id = user.uid
                # Save the token ID in the session
                session['user_token'] = token_id
                return render_template('account_management/user_cred.html')
            except auth.EmailAlreadyExistsError:
                existing_account = "An account with this email already exists."
                return render_template('account_management/login.html', exist_message=existing_account)
    return render_template('account_management/login.html')



@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    user_email = request.form.get('user_email')
    try:
        pyreauth.send_password_reset_email(user_email)
        return 'Password reset email sent successfully.'
    except:
        r_email = 'Error sending password reset email'
        return render_template('account_management/forget_password.html', exist_message=r_email)
    


@app.route('/add_user_credentials', methods=['GET', 'POST'])
def add_user_credentials():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        birthdate = request.form['birthdate']
        town = request.form['town']

        # Save the username in the session
        session['username'] = username

        # Retrieve the email from the session
        email = session.get('user_email', None)
        # Retrieve the token ID from the session
        token_id = session.get('user_token', None)  

        password = session.get('pwd', None)

        if email is None:
            return "User email not found. Please create an account first."

        if token_id is None:
            return "User token ID not found. Please log in first."
        # Add the "status" field with the value "User" to the data
        data = {
            "email": email,
            "name": name,
            "username": username,
            "birthdate": birthdate,
            "town": town,
            "status": "User"  # Add the "status" field with the value "User"
        }
        # Use the token ID as the key in the database
        pyredb.child("Users").child("Consumer").child(token_id).set(data)
        try:
            user = pyreauth.sign_in_with_email_and_password(email, password)
            # Get the Firebase token ID
            token_id = user['idToken']
            # Save the token ID in the session
            session['user_token'] = token_id

            firebase_user = auth.get_user(user['localId'])
            email_verified = firebase_user.email_verified
            if not email_verified:
                # Update user's custom claims to indicate pending email verification
                auth.set_custom_user_claims(user['localId'], {'emailVerified': False})

                # Send the email verification
                pyreauth.send_email_verification(user['idToken'])
                print("Verification email sent. Waiting for email verification...")
                # Wait until the email is verified
                while True:
                    firebase_user = auth.get_user(user['localId'])
                    email_verified = firebase_user.email_verified
                    if email_verified:
                        # Update user's custom claims to indicate email verification completed
                        auth.set_custom_user_claims(user['localId'], {'emailVerified': True})
                        session.pop('pwd',None)  
                        print("Email verified.")
                        break
                    else:
                        print("Email not verified. Waiting...")
                        time.sleep(5)  # Add a 5-second delay before checking again
            else:
                print("Email already verified.")
        except Exception as e:
            print(f"Authentication failed: {e}")
        return redirect('/staff/users')
        

@app.route('/update_user_cred', methods=['POST'])
def update_user_credentials():
    if 'user_token' in session:
        # Retrieve the token ID from the session
        token_id = session['user_token']

        # Use the token ID to get the user's UID from Firebase authentication
        user = pyreauth.get_account_info(token_id)
        uid = user['users'][0]['localId']

        # Get the updated data from the form
        name = request.form['fullName']
        email = request.form['eMail']
        username = request.form['username']
        birthdate = request.form['birthdate']
        town = request.form['town']

        # Update the user data in Firebase
        data = {
            "name": name,
            "email": email,
            "username": username,
            "birthdate": birthdate,
            "town": town
        }

        pyredb.child("Users").child("Consumer").child(uid).update(data)

        # Redirect to the dashboard with updated data
        return redirect('/dashboard')

    else:
        return "User token ID not found. Please log in first."


@app.route('/delete_account', methods=['POST'])
def delete_account():
    try:
        # Get the user's token ID from the session
        token_id = session.get('user_token', None)
        
        if token_id:
            session.pop('user_email', None)            
            # Delete the user from Firebase Authentication
            decoded_token = pyreauth.get_account_info(token_id)
            user_id = decoded_token['users'][0]['localId']
            auth.delete_user(user_id)

            # Delete user data from the Realtime Database (assuming the user's data is stored in 'Users/Consumer' node)
            pyredb.child("Users").child("Consumer").child(user_id).remove()
            
            # After deleting the account and data, redirect the user to the login page
            return redirect('/')
        else:
            # Handle the case where the token_id is not available in the session
            return redirect('/error-page')
    except Exception as e:
        # Handle any errors that may occur during account deletion
        print('Error deleting account:', str(e))
        # You can choose to show an error message or redirect the user to an error page
        return redirect('/error-page')


@app.route('/staff/users')
def show_all_users():
    try:
        # Get all user data from the Realtime Database (assuming the user's data is stored in 'Users/Consumer' node)
        all_users_data = pyredb.child("Users").child("Consumer").get().val()

        return render_template('account_management/show_all_users.html', all_users_data=all_users_data)
    except Exception as e:
        # Handle any errors that may occur
        print('Error:', str(e))
        # You can choose to show an error message or redirect the user to an error page
        return redirect('/error-page')


@app.route('/update_user', methods=['POST'])
def update_user():
    try:
        # Get the user_id and user_data from the request's JSON payload
        request_data = request.get_json()
        user_id = request_data.get('user_id')
        user_data = request_data.get('user_data')

        # Update the user data in Firebase
        pyredb.child("Users").child("Consumer").child(user_id).update(user_data)

        # Return a success message (if needed)
        return "User data updated successfully"
    except Exception as e:
        # Handle any errors that may occur during the update process
        print('Error updating user data:', str(e))
        # You can choose to show an error message or return an error response
        return "Error updating user data", 500


@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        data = request.get_json()
        user_id = data['user_id']

        # Delete the user data from the database
        auth.delete_user(user_id)
        pyredb.child("Users").child("Consumer").child(user_id).remove()
        pyrebase.child("Users").child("Consumer").child(user_id).child('birthdate-placeholder').remove()
        pyrebase.child("Users").child("Consumer").child(user_id).child('town-placeholder').remove()
        pyrebase.child("Users").child("Consumer").child(user_id).child('username-placeholder').remove()

        return "User data deleted successfully!"
    except Exception as e:
        # Handle any errors that may occur
        print('Error deleting user data:', str(e))
        return "Error deleting user data."


if __name__ == '__main__':
    app.run(debug=True, port=5000)