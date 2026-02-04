import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyDBM55pRHOJRkPyE19YlSaIVuREb8VOuhY",
    'authDomain': "spacerider-78a3d.firebaseapp.com",
    "databaseURL": "https://spacerider-78a3d-default-rtdb.europe-west1.firebasedatabase.app/",
    'projectId': "spacerider-78a3d",
    'storageBucket': "spacerider-78a3d.firebasestorage.app",
    'messagingSenderId': "721946961756",
    'appId': "1:721946961756:web:ecb0b1eb8960f888b74399",
    'measurementId': "G-PDYNK4743J"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
