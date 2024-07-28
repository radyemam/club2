import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

# تحديد المسار الكامل إلى ملف club-1667e-firebase-adminsdk-b4pu1-b72e3dc1d4.json
cred_path = os.path.join(os.path.dirname(__file__), 'club-1667e-firebase-adminsdk-b4pu1-b72e3dc1d4.json')

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'club-1667e.appspot.com'  # تحديد اسم الحاوية هنا
})

db = firestore.client()
