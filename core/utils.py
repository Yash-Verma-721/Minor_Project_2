from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(data, key):
    f = Fernet(key)
    return f.decrypt(data)



from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_verification_mail(user_email, username):

    subject = "Verify your Secure Share Account"

    from_email = settings.EMAIL_HOST_USER
    to_email = [user_email]
   
    verification_link = f"http://localhost:8000/verify?vemail={user_email}"

    text_content = f"""
    Welcome to Secure Share.
    Click below link to verify your account:
    {verification_link}
    """

    html_content = f"""
    <html>
    <head></head>
  					<body>
    					<h1>Welcome to Secure Share 😊</h1>
    					<p>You have successfully registered , please click on the link below to verify your account</p>
    					<h2>Username : {username}</h2>
    					<h2>Email : {user_email}</h2>
    					<br>
    					<a href="{verification_link}" >Click here to verify account</a>	
			                       			<p>Thank you for choosing Secure Share, we hope you have a great experience!</p>
						<p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
						<p>for more information visit our official site, Thank you</p>
						<p>Regards,</p>
						<p>Secure Share Team</p>

  					</body>
				</html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    print("Verification mail sent")