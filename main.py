from customtkinter import *
from PIL import Image
import pyrebase
import json
import os
import subprocess
import threading
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

with open('misc/firebase.json') as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

main_process = None

def preload_main_application():
    global main_process
    main_process = subprocess.Popen(["python", "record.py"], env={**os.environ, "wait": "1"})

def signal_main_application():
    with open("start_main_signal.txt", "w") as f:
        f.write("start")

def load_config():
    with open("misc/config.json", "r") as file:
        return json.load(file)

def send_email():

    config = load_config()
    EMAIL_ADDRESS = config["EMAIL_ADDRESS"]
    EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
    TO_EMAIL = config["TO_EMAIL"]
    SMTP_SERVER = config["SMTP_SERVER"]
    SMTP_PORT = config["SMTP_PORT"]

    subject = "Login Alert"
    body = "Someone logged into your account from an unknown device. If this was you, you can ignore this email."

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls() 
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def show_signup_page():
    for widget in frame.winfo_children():
        widget.destroy()

    def save_credentials():
        email = email_entry.get()
        password = password_entry.get()
        if email and password:
            try:
                auth.create_user_with_email_and_password(email, password)
                show_login_page()
            except Exception as e:
                error_label.configure(text=f"User already exists")
        else:
            error_label.configure(text="Both fields are required!")

    CTkLabel(master=frame, text="Sign Up", text_color="#000000", font=("Segoe UI", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))

    CTkLabel(master=frame, text="  Email:", text_color="#000000", font=("Segoe UI", 14)).pack(anchor="w", pady=(20, 0), padx=(25, 0))
    email_entry = CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#000000", border_width=2, text_color="#000000")
    email_entry.pack(anchor="w", padx=(25, 0))

    CTkLabel(master=frame, text="  Password:", text_color="#000000", font=("Segoe UI", 14)).pack(anchor="w", pady=(20, 0), padx=(25, 0))
    password_entry = CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#000000", border_width=2, text_color="#000000", show="*")
    password_entry.pack(anchor="w", padx=(25, 0))

    error_label = CTkLabel(master=frame, text="", text_color="red")
    error_label.pack(anchor="w", pady=(10, 0), padx=(25, 0))

    CTkButton(master=frame, text="Sign Up", fg_color="#000000", hover_color="#E44982", font=("Segoe UI", 12), text_color="#ffffff", width=225, command=save_credentials).pack(anchor="w", pady=(20, 0), padx=(25, 0))
    CTkButton(master=frame, text="Back to Login", fg_color="#000000", hover_color="#E44982", font=("Segoe UI", 12), text_color="#ffffff", width=225, command=show_login_page).pack(anchor="w", pady=(10, 0), padx=(25, 0))

def handle_login():
    email = email_entry.get()
    password = password_entry.get()
    if email and password:
        try:
            auth.sign_in_with_email_and_password(email, password)
            status_label.configure(text="Please wait while loading...", text_color="green")
            app.update_idletasks()
            send_email()
            signal_main_application()
            app.destroy()
        except Exception as e:
            error_label.configure(text=f"Invalid Password or Email")
    else:
        error_label.configure(text="Both fields are required!")

def show_login_page():
    for widget in frame.winfo_children():
        widget.destroy()

    CTkLabel(master=frame, text="Welcome Back!", text_color="#000000", font=("Segoe UI", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))
    CTkLabel(master=frame, text="Sign in to your account", text_color="#000000", font=("Segoe UI", 12)).pack(anchor="w", padx=(25, 0))

    CTkLabel(master=frame, text="  Email:", text_color="#000000", font=("Segoe UI", 14), image=email_icon, compound="left").pack(anchor="w", pady=(38, 0), padx=(25, 0))
    global email_entry
    email_entry = CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#000000", border_width=2, text_color="#000000")
    email_entry.pack(anchor="w", padx=(25, 0))

    CTkLabel(master=frame, text="  Password:", text_color="#000000", font=("Segoe UI", 14), image=password_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
    global password_entry
    password_entry = CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#000000", border_width=2, text_color="#000000", show="*")
    password_entry.pack(anchor="w", padx=(25, 0))

    global error_label
    error_label = CTkLabel(master=frame, text="", text_color="red")
    error_label.pack(anchor="w", padx=(25, 0))

    CTkButton(master=frame, text="Login", fg_color="#000000", hover_color="#E44982", font=("Segoe UI", 12), text_color="#ffffff", width=225, command=handle_login).pack(anchor="w", pady=(40, 0), padx=(25, 0))
    CTkButton(master=frame, text="Sign up", fg_color="#000000", hover_color="#E44982", font=("Segoe UI", 12), text_color="#ffffff", width=225, command=show_signup_page).pack(anchor="w", pady=(25, 0), padx=(25, 0))
    global status_label
    status_label = CTkLabel(master=frame, text="", text_color="green", font=("Segoe UI", 12))
    status_label.pack(anchor="w", pady=(5, 0), padx=(25, 0))



app = CTk()
app.title("Welcome")
app.geometry("600x480")
app.resizable(0, 0)

email_icon_data = Image.open("misc/email.png")
password_icon_data = Image.open("misc/password.png")
email_icon = CTkImage(dark_image=email_icon_data, light_image=email_icon_data, size=(20,20))
password_icon = CTkImage(dark_image=password_icon_data, light_image=password_icon_data, size=(17,17))
threading.Thread(target=preload_main_application, daemon=True).start()

side_img_data = Image.open("misc/sidepanel.png")
side_img = CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))

CTkLabel(master=app, text="", image=side_img).pack(expand=True, side="left")

frame = CTkFrame(master=app, width=300, height=480, fg_color="#E2F1E7")
frame.pack_propagate(0)
frame.pack(expand=True, side="right")

show_login_page()

app.mainloop()
