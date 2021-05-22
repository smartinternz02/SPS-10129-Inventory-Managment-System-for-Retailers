import smtplib
import os

def sendmail(user,TEXT):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    subject = "Stock Alert"
    s.starttls()
    s.login("lpbasavaraj17@gmail.com", "basu@1234")
    message  = 'Subject: {}\n\n{}'.format(subject, TEXT)
    s.sendmail("lpbasavaraj17@gmail.com", user, message)
    s.quit()

    

