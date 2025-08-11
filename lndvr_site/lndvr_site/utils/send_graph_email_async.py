import threading
import base64
from lndvr_site.utils.graph_email import send_graph_email

# this method is being made to handle the delay that was happening while submitting the form

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
                    # Reset file pointer to the start before reading
                    # This is critical because if the file was read previously,
                    # the pointer would be at the end, causing empty content to be read
                    file_obj.seek(0)

                    # Read the full content of the file as bytes
                    content = file_obj.read()

                    # Encode file content in base64 as required by Microsoft Graph API
                    encoded_content = base64.b64encode(content).decode('utf-8')

                    # Prepare the attachment dictionary for the Graph API
                    # Use file_obj.name for the filename
                    # Use file_obj.content_type if available; fallback to 'application/octet-stream'
                    attachment = {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": file_obj.name,
                        "contentType": getattr(file_obj, 'content_type', 'application/octet-stream'),
                        "contentBytes": encoded_content
                    }

                    # Add the attachment dict to the attachments list
                    attachments.append(attachment)

            # Call your existing synchronous email sending function
            # Pass attachments if any, otherwise None
            send_graph_email(subject, body, to_emails, is_html, attachments if attachments else None)

        except Exception as e:
            # Log or print errors occurring during the async email sending
            print(f"[Async Email Error] {e}")

    # Run the email sending logic in a separate thread to avoid blocking the main thread
    threading.Thread(target=run).start()
