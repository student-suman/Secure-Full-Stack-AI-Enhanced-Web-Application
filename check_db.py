from app import app, db
from models import Certificate

def check_certificates():
    print("--- SCRIPT STARTED: Checking for certificates... ---")
    try:
        with app.app_context():
            all_certs = Certificate.query.all()
            if not all_certs:
                print("RESULT: No certificates found in the database.")
            else:
                id_list = [c.certificate_id for c in all_certs]
                print("RESULT: Found the following certificate IDs:")
                print(id_list)
    except Exception as e:
        print(f"An error occurred: {e}")
    print("--- SCRIPT FINISHED ---")

if __name__ == '__main__':
    check_certificates()