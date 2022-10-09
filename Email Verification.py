import smtplib,random

def genhash():
    hash = random.getrandbits(128)
    return hash

def vemail():
    user="flaskbook1@gmail.com"
    passwd="amitpandey123121"
    receiver_address = {{current_user.email}}
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(user, passwd) #login with mail_id and password
    hash1=genhash()
    link = "localhost:5000/emailverify/hash="+str(hash1)
    text="Verify FlaskBook acc By clicking the link :-  localhost:5000/emailverify/hash="+str(hash1)
    session.sendmail(user, receiver_address, link)
    session.quit()

vemail()