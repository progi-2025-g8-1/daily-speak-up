import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

class FCMService:

    @staticmethod
    def send_streak_reminder(token: str, title: str, body: str, data: dict = None):
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )

        try:
            response = messaging.send(message)
            print(f"[FCM] Notification sent: {response}")
            return response

        except FirebaseError as e:
            print(f"[FCM] Firebase error: {e.code} - {e.message}")
        
        except Exception as e:
            print(f"[FCM] Unexpected error: {str(e)}")

        return None
