import os
import email
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Directories and API
MAIL_DIR = "/var/mail/Maildir/new"
API_URL = "http://127.0.0.1:5000/detect"
ENRICHED_LOG = "/var/log/mail_ml.log"

# ------------------------------------------------------
#  DELETE OLD LOG FILE SAFELY BEFORE STARTING WATCHER
# ------------------------------------------------------
def reset_log_file():
    try:
        if os.path.exists(ENRICHED_LOG):
            os.remove(ENRICHED_LOG)
            print("Old mail_ml.log deleted.")
        else:
            print("mail_ml.log does not exist — nothing to delete.")
    except Exception as e:
        print("Error deleting log file:", e)

class NewMailHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        try:
            with open(event.src_path, 'r') as f:
                msg = email.message_from_file(f)
                sender = msg.get('From', '')
                recipient = msg.get('To', '')
                subject = msg.get('Subject', '')
                date = msg.get('Date', '')
                
                # Extract body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                
                # REMOVE ALL NEWLINES AND EXTRA WHITESPACE
                body = body.replace('\n', ' ').replace('\r', ' ').strip()
                # Optional: Replace multiple spaces with single space
                body = ' '.join(body.split())
                
                # Send to ML server
                response = requests.post(API_URL, json={"content": body})
                ml_result = response.json()
                label = ml_result.get("label", "unknown")
                score = ml_result.get("score", 0.0)
                
                # Format log entry
                log_line = (
                    f"{datetime.utcnow().isoformat()} "
                    f"ML_Label={label} ML_Score={score:.6f} "
                    f"From=\"{sender}\" To=\"{recipient}\" "
                    f"Subject=\"{subject}\" Date=\"{date}\" "
                    f"Body=\"{body}\""
                )
                
                # Write log — file will auto-create if missing
                with open(ENRICHED_LOG, 'a') as log_file:
                    log_file.write(log_line + "\n")
                    log_file.write("#**END**#\n")
                
                print("Processed email:", subject)
                print("Enriched log:", log_line)
                
        except Exception as e:
            print("Error processing email:", e)

if __name__ == "__main__":
    # SAFE LOG RESET
    reset_log_file()
    
    event_handler = NewMailHandler()
    observer = Observer()
    observer.schedule(event_handler, MAIL_DIR, recursive=False)
    observer.start()
    
    print(f"Watching {MAIL_DIR} for new emails...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
