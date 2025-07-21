import threading
import base64
from lndvr_site.utils.graph_email import send_graph_email

def send_graph_email_async(subject, body, to_emails, is_html=False, files=None):
    """
    Send email asynchronously with optional file attachments.
    
    :param subject: Email subject string
    :param body: Email body string (HTML or plain text)
    :param to_emails: List of recipient email addresses
    :param is_html: Boolean, True if body is HTML
    :param files: List of Django UploadedFile objects or file-like objects, or None
    """
    def run():
        try:
            attachments = []
            if files:
                for file_obj in files:
                    content = file_obj.read()
                    attachments.append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": file_obj.name,
                        "contentType": file_obj.content_type,
                        "contentBytes": base64.b64encode(content).decode('utf-8')
                    })
            send_graph_email(subject, body, to_emails, is_html, attachments if attachments else None)
        except Exception as e:
            print(f"[Async Email Error] {e}")

    threading.Thread(target=run).start()
