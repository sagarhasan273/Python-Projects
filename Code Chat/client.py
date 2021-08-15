from mysql.connector import errorcode
import mysql.connector
from logging import exception
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import socket
import threading
from tkinter import font
from tkinter import ttk
from win32api import GetSystemMetrics
import pygame


PORT = 80
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

# Create a new client socket
# and connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDRESS)


firstName = ""
lastName = ""
username = ""
email = ""
password = ""
re_password = ""
screen_width = int((GetSystemMetrics(0) / 2) - 425)

is_on_b1 = False
is_on_b2 = False
log_pass_eys_is_on = True


class GUI:
    # constructor method
    def __init__(self, uname):
        self.Window = Tk()
        self.Window.withdraw()
        self.goAhead(uname)
        self.Window.mainloop()

    def goAhead(self, name):
        self.layout(name)

        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

    # The main layout of the chat
    def layout(self, name):
        self.name = name
        self.client_name = set()
        self.Window.deiconify()
        self.Window.title("Code Chat")
        self.Window.resizable(width=False, height=False)
        self.Window.geometry(f'850x600+{screen_width}+150')
        self.main_bg_image = ImageTk.PhotoImage(
            Image.open("chatroom/chat_bg.png"))
        self.main_label = Label(
            self.Window, image=self.main_bg_image).pack(fill=BOTH)

        Label(self.Window, text=name, background='white',
              font='Helvetica 25 bold').place(relx=0.41, rely=0.028)

        self.online_frame = Frame(
            self.Window, bg='blue', height=486, width=264)
        self.chat_box_frame = Frame(
            self.Window, bg="red", height=426, width=553)
        self.text_box_frame = Frame(
            self.Window, bg='green', height=47, width=432)

        self.online_frame.place(relx=0.01, rely=0.165)
        self.chat_box_frame.place(
            relheight=0.7, relwidth=0.652, relx=0.335, rely=0.165)
        self.text_box_frame.place(relx=0.335, rely=0.8959)

        self.online_box_image = ImageTk.PhotoImage(
            Image.open("chatroom/online.png"))
        self.online_box_image_label = Label(
            self.online_frame, image=self.online_box_image)
        self.online_box_image_label.pack()

        self.textCons = Text(self.chat_box_frame, font="Helvetica 14",
                             foreground='black', background='#D7D2ED')
        self.textCons.pack(fill=BOTH, expand=False)

        # demo text

        self.text_box_image = ImageTk.PhotoImage(
            Image.open("chatroom/text_box.png").resize((432, 47)))
        self.text_box_image_label_field = Label(
            self.text_box_frame, image=self.text_box_image)
        self.text_box_image_label_field.pack()

        self.entryMsg = Entry(self.text_box_frame,
                              bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.959, relheight=0.7,
                            relx=0.022, rely=0.15)
        self.entryMsg.focus()
        self.entryMsg.bind(
            '<Return>', lambda event: self.sendButton(self.entryMsg.get(),))

        self.send_button_image = ImageTk.PhotoImage(
            Image.open("chatroom/send.png"))
        self.buttonMsg = Button(self.Window, image=self.send_button_image, height=47, width=111,
                                command=lambda: self.sendButton(self.entryMsg.get())).place(relx=0.855, rely=0.8959)
        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
        scrollbar.place(relheight=1, relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        pygame.mixer.init()  # initialise the pygame
        pygame.mixer.music.load("sound/codechat.mp3")
        pygame.mixer.music.play(loops=0)
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.sendMessage)
        snd.start()

    # function to receive messages
    def receive(self):
        while True:
            try:
                message = client.recv(1024).decode(FORMAT)

                msg = str(message)
                if ":" in msg:
                    get_index = msg.index(":")
                    self.client_name.add(msg[:get_index])
                    y_name = 0.318
                    y_bar = 0.37
                    self.horizontal_bar = ImageTk.PhotoImage(
                        Image.open("chatroom/line.png"))
                    for name in self.client_name:
                        Label(self.Window, text=name, font=("Arial Bold", 16), pady=0).place(
                            relx=0.0185, rely=y_name, relwidth=0.3)
                        y_name += 0.07
                        Label(self.Window, image=self.horizontal_bar).place(
                            relx=0.02, rely=y_bar, relwidth=0.3)
                        y_bar += 0.07

                # if the messages from the server is NAME send the client's name
                if message == 'NAME':
                    client.send(self.name.encode(FORMAT))
                else:
                    # insert messages to text box
                    def reset_tabstop(event):
                        event.widget.configure(tabs=(event.width-8, "right"))

                    if self.name in message:
                        if self.name+' has joined' in message:
                            self.textCons.config(state=NORMAL)
                            line_number, column = self.textCons.index(
                                'end').split('.')
                            line_number = int(line_number)
                            self.textCons.insert(END, " \t{}                           \n\n".format(msg))
                            self.textCons.tag_add('me', "{}.1".format(
                                line_number-1), "{}.1000".format(line_number-1))
                            self.textCons.tag_config(
                                'me', background="#C4FFBE", foreground="black")

                        else:
                            self.textCons.config(state=NORMAL)
                            line_number, column = self.textCons.index(
                                'end').split('.')
                            line_number = int(line_number)
                            msg = message.replace(self.name+":", "")
                            self.textCons.insert(END, " \t{}   \n".format(msg))
                            self.textCons.bind("<Configure>", reset_tabstop)
                            self.textCons.tag_add('me', "{}.2".format(
                                line_number-1), "{}.1000".format(line_number-1))
                            self.textCons.tag_config(
                                'me', background="#C4FFBE", foreground="black")

                    else:
                        if ' has joined the chat!' in message:
                            self.textCons.config(state=NORMAL)
                            line_number, column = self.textCons.index(
                                'end').split('.')
                            line_number = int(line_number)
                            self.textCons.insert(
                                END, "                          {} \n\n".format(message))

                        else:
                            self.textCons.config(state=NORMAL)
                            line_number, column = self.textCons.index(
                                'end').split('.')
                            line_number = int(line_number)
                            self.textCons.insert(
                                END, "{} \t\n\n".format(message))
                            self.textCons.tag_add('you', "{}.0".format(
                                line_number-1), "{}.{}".format(line_number-1, len(message)))
                            self.textCons.tag_config(
                                'you', background="white", foreground="black")
                            self.textCons.bind("<Configure>", reset_tabstop)

                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)
            except:
                print("An error occured!")
                client.close()
                break

    def sendMessage(self):
        self.textCons.config(state=DISABLED)
        while True:
            message = (f"{self.name}: {self.msg}")
            client.send(message.encode(FORMAT))
            break


class SampleApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Code Chat")
        self.resizable(width=False, height=False)
        icon = ImageTk.PhotoImage(Image.open("image/logo.png"))
        self.iconphoto(False, icon)
        self.geometry(f'850x600+{screen_width}+150')
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    def destroy_all(self, username, password):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin2968",
            database="python_project"
        )
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT username FROM users WHERE username = %s", (username, ))
        myresult_username = mycursor.fetchall()
        mydb.commit()

        mycursor.execute(
            "SELECT userpass FROM users WHERE userpass = %s", (password, ))
        myresult_userpass = mycursor.fetchall()
        mydb.commit()

        myResult_un = False
        myResult_up = False
        for result in myresult_username:
            if username == str(*result):
                myResult_un = True
                break
        for result in myresult_userpass:
            if password == str(*result):
                myResult_up = True
                break
        if myResult_un and myResult_up:
            print("login successfull...")
            super().destroy()
            mycursor.execute(
                "SELECT FirstName, LastName FROM users WHERE username = %s", (username, ))
            name = mycursor.fetchall()
            name = list(*name)
            name = str(name[0] + ' ' + name[1])
            GUI(name)
        else:
            messagebox.askretrycancel(
                "ERROR!", "user-name or password incorrect!")
            pass


class StartPage(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.imag = ImageTk.PhotoImage(Image.open(
            "image/front_bg.jpg").resize((850, 600)))
        self.image_log_bg = Label(self, image=self.imag)
        self.image_log_bg.pack()

        self.image_login_button = ImageTk.PhotoImage(
            Image.open("image/login.png").resize((280, 40)))
        Button(self, image=self.image_login_button, background="#142632", border=0,
               command=lambda: master.switch_frame(LoginClass)).place(anchor="n", relx=0.5, rely=0.55)

        self.image_registration_button = ImageTk.PhotoImage(
            Image.open("image/registration.png").resize((280, 40)))
        Button(self, image=self.image_registration_button, background="#142632", border=0,
               command=lambda: master.switch_frame(RegistrationClass)).place(anchor="n", relx=0.5, rely=0.64)


class LoginClass(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        Frame.configure(self, bg='blue')

        self.image_log = ImageTk.PhotoImage(Image.open(
            "signin/background.png").resize((850, 600)))
        self.image_log_bg = Label(self, image=self.image_log)
        self.image_log_bg.pack()

        def username_click(*args):
            if self.entryUserName.get() == "user-name":
                self.entryUserName.delete(0, 'end')

        self.entryUserName = Entry(
            self, font="Helvetica 14", foreground='#666666', borderwidth=10, relief=FLAT)
        self.entryUserName.place(
            relwidth=0.305, relheight=0.05, relx=0.45, rely=0.379)
        self.entryUserName.insert(0, "user-name")
        self.entryUserName.bind('<Button-1>', username_click)
        self.entryUserName.focus()

        def log_pass_click(*args):
            if self.entrypass.get() == "Password":
                self.entrypass.delete(0, 'end')
            global log_pass_eys_is_on
            if log_pass_eys_is_on:
                pass
            else:
                self.entrypass.config(show='')
                Button(self, image=self.on, background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_log_password).place(relheight=0.05, relx=0.715, rely=0.466)
                log_pass_eys_is_on = True
                pass_eye_btn_text_fromlogin.set("Show")

        self.entrypass = Entry(self, font="Helvetica 14", borderwidth=10,
                               show="*", foreground='#666666', relief=FLAT)
        self.entrypass.place(relwidth=0.28, relheight=0.05,
                             relx=0.45, rely=0.466)
        self.entrypass.insert(0, "Password")
        self.entrypass.bind("<Button-1>", log_pass_click)
        self.entrypass.focus()

        def toggle_log_password():
            if pass_eye_btn_text_fromlogin.get() == 'Show':
                self.entrypass.config(show='*')
                Button(self, image=self.off, background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_log_password).place(relheight=0.05, relx=0.715, rely=0.466)
                pass_eye_btn_text_fromlogin.set("Hide")
            else:
                Button(self, image=self.on, background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_log_password).place(relheight=0.05, relx=0.715, rely=0.466)
                self.entrypass.config(show='')
                pass_eye_btn_text_fromlogin.set("Show")

        self.on = PhotoImage(file="registration/eye_on.png")
        self.off = PhotoImage(file="registration/eye_off.png")
        pass_eye_btn_text_fromlogin = StringVar()
        pass_eye_btn_text_fromlogin.set("Hide")
        Button(self, image=self.off, textvariable=pass_eye_btn_text_fromlogin, background="WHITE", border=0,
               font="Helvetica 10", command=toggle_log_password).place(relheight=0.05, relx=0.715, rely=0.466)

        self.image_back_button = ImageTk.PhotoImage(
            Image.open("signin/back.png"))
        self.image_getin_button = ImageTk.PhotoImage(
            Image.open("signin/getin.png"))
        Button(self, image=self.image_back_button, text="Go back", font="Helvetica 14", border=0,
               command=lambda: master.switch_frame(StartPage)).place(relwidth=0.143, relheight=0.05, relx=0.279, rely=0.6)
        Button(self, image=self.image_getin_button, text="Get In", font="Helvetica 14", border=0, command=lambda: self.master.destroy_all(
            self.entryUserName.get(), self.entrypass.get())).place(relwidth=0.143, relheight=0.05, relx=0.576, rely=0.6)


class RegistrationClass(Frame):
    def __init__(self, master):
        def first_click(*args):
            if self.entryFirstName.get() == "First Name":
                self.entryFirstName.delete(0, 'end')

        def last_click(*args):
            if self.entryLastName.get() == "Last Name":
                self.entryLastName.delete(0, 'end')

        def user_click(*args):
            if self.entryUserName.get() == "Username:- example123":
                self.entryUserName.delete(0, 'end')

        def email_click(*args):
            if self.entryEmail.get() == "Email: example@gmail.com":
                self.entryEmail.delete(0, 'end')

        def pass_click(*args):
            if self.entryPassword.get() == "Password":
                self.entryPassword.delete(0, 'end')
            global is_on_b1
            if is_on_b1:
                pass
            else:
                self.entryPassword.config(show='*')
                Button(self, image=self.off, background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_password).place(relheight=0.055, relx=0.7, rely=0.465)
                is_on_b1 = True
                pass_btn_text.set("Show")

        def repass_click(*args):
            if self.entryRePassword.get() == "Confirm Password":
                self.entryRePassword.delete(0, 'end')
            global is_on_b2
            if is_on_b2:
                pass
            else:
                self.entryRePassword.config(show='*')
                Button(self, image=self.off,  background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_repassword).place(relheight=0.055, relx=0.7, rely=0.561)
                repass_btn_text.set("Show")
                is_on_b2 = True

        Frame.__init__(self, master)
        Frame.configure(self)

        self.image_log = ImageTk.PhotoImage(Image.open(
            "registration/registrationbg.png").resize((850, 600)))
        self.image_log_bg = Label(self, image=self.image_log)
        self.image_log_bg.pack()

        self.entryFirstName = Entry(
            self, font="Helvetica 14", borderwidth=10, relief=FLAT, foreground='#666666')
        self.entryFirstName.place(
            relwidth=0.228, relheight=0.055, relx=0.263, rely=0.28)
        self.entryFirstName.insert(0, "First Name")
        self.entryFirstName.bind("<Button-1>", first_click)
        self.entryFirstName.focus()

        self.entryLastName = Entry(
            self, font="Helvetica 14", borderwidth=10, relief=FLAT, foreground='#666666')
        self.entryLastName.place(
            relwidth=0.228, relheight=0.055, relx=0.528, rely=0.28)
        self.entryLastName.insert(0, "Last Name")
        self.entryLastName.bind("<Button-1>", last_click)
        self.entryLastName.focus()

        self.entryUserName = Entry(
            self, font="Helvetica 14", borderwidth=10, relief=FLAT, foreground='#666666')
        self.entryUserName.place(
            relwidth=0.494, relheight=0.055, relx=0.263, rely=0.373)
        self.entryUserName.insert(0, "Username:- example123")
        self.entryUserName.bind("<Button-1>", user_click)
        self.entryUserName.focus()

        self.entryPassword = Entry(
            self, font="Helvetica 14", borderwidth=10, relief=FLAT, foreground='#666666')
        self.entryPassword.place(
            relwidth=0.494, relheight=0.055, relx=0.263, rely=0.465)
        self.entryPassword.insert(0, "Password")
        self.entryPassword.bind("<Button-1>", pass_click)
        self.entryPassword.focus()

        self.entryRePassword = Entry(
            self, font="Helvetica 14", borderwidth=10, relief=FLAT, foreground='#666666')
        self.entryRePassword.place(
            relwidth=0.494, relheight=0.055, relx=0.263, rely=0.561)
        self.entryRePassword.insert(0, "Confirm Password")
        self.entryRePassword.bind("<Button-1>", repass_click)
        self.entryRePassword.focus()

        self.entryEmail = Entry(self, font="Helvetica 14",
                                borderwidth=10, relief=FLAT, foreground='#666666')
        self.entryEmail.place(
            relwidth=0.494, relheight=0.055, relx=0.263, rely=0.655)
        self.entryEmail.insert(0, "Email: example@gmail.com")
        self.entryEmail.bind("<Button-1>", email_click)
        self.entryEmail.focus()

        def toggle_password():
            if pass_btn_text.get() == 'Show':
                self.entryPassword.config(show='')
                Button(self, image=self.on, background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_password).place(relheight=0.055, relx=0.7, rely=0.465)
                pass_btn_text.set("Hide")
            else:
                Button(self, image=self.off, background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_password).place(relheight=0.055, relx=0.7, rely=0.465)
                self.entryPassword.config(show='*')
                pass_btn_text.set("Show")

        def toggle_repassword():
            if repass_btn_text.get() == 'Show':
                self.entryRePassword.config(show='')
                repass_btn_text.set("Hide")
                Button(self, image=self.on,  background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_repassword).place(relheight=0.055, relx=0.7, rely=0.561)
            else:
                Button(self, image=self.off,  background="WHITE", border=0, font="Helvetica 10",
                       command=toggle_repassword).place(relheight=0.055, relx=0.7, rely=0.561)
                repass_btn_text.set("Show")
                self.entryRePassword.config(show='*')

        self.on = PhotoImage(file="registration/eye_on.png")
        self.off = PhotoImage(file="registration/eye_off.png")
        pass_btn_text = StringVar()
        repass_btn_text = StringVar()
        Button(self, image=self.on, textvariable=pass_btn_text, background="WHITE", border=0,
               font="Helvetica 10", command=toggle_password).place(relheight=0.055, relx=0.7, rely=0.465)
        Button(self, image=self.on, textvariable=repass_btn_text,  background="WHITE", border=0,
               font="Helvetica 10", command=toggle_repassword).place(relheight=0.055, relx=0.7, rely=0.561)

        self.image_back_button = ImageTk.PhotoImage(
            Image.open("registration/back.png").resize((122, 34)))
        Button(self, image=self.image_back_button, border=0, command=lambda: master.switch_frame(
            StartPage)).place(relwidth=0.143, relheight=0.055, relx=0.263, rely=0.77)
        self.image_create_account_button = ImageTk.PhotoImage(
            Image.open("registration/createaccount.png").resize((198, 34)))
        Button(self, image=self.image_create_account_button, text="Create Account", border=0,
               command=self.create_account).place(relwidth=0.22, relheight=0.055, relx=0.536, rely=0.769)

    def create_account(self):
        global firstName
        firstName = self.entryFirstName.get()
        global lastName
        lastName = self.entryLastName.get()
        global username
        username = self.entryUserName.get()
        global email
        email = self.entryEmail.get()
        global password
        password = self.entryPassword.get()
        global re_password
        re_password = self.entryRePassword.get()

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin2968",
            database="python_project"
        )

        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT username FROM users WHERE username = %s", (self.entryUserName.get(), ))
        myresult_username = mycursor.fetchall()
        print(myresult_username)
        mydb.commit()

        mycursor.execute(
            "SELECT useremail FROM users WHERE useremail = %s", (self.entryEmail.get(), ))
        myresult_useremail = mycursor.fetchall()
        print(myresult_useremail)
        mydb.commit()

        myResult_un = False
        myResult_ue = False
        for result in myresult_username:
            if self.entryUserName.get() == str(*result):
                myResult_un = True
        for result in myresult_useremail:
            if self.entryEmail.get() == str(*result):
                myResult_ue = True

        if (firstName == "First Name" or lastName == "Last Name" or username == "Username:- example123" or email == "Email: example@gmail.com"):
            messagebox.askretrycancel("Form!", "No empty box allows!")
            self.master.switch_frame(RegistrationClass)
        elif (password != re_password):
            messagebox.askretrycancel("Password!", "Use same password, please")
            self.master.switch_frame(RegistrationClass)
        elif myResult_un:
            messagebox.askretrycancel(
                "Username!", "Sorry, Username already exists!")
            self.master.switch_frame(RegistrationClass)
        elif myResult_ue:
            messagebox.askretrycancel(
                "Email!", "Sorry, Already have an account with this email!")
            self.master.switch_frame(RegistrationClass)
        else:
            messagebox.showinfo("login", "Successfully Login!")
            self.insert_into_db()
            self.master.switch_frame(LoginClass)

    def insert_into_db(self):
        print("Using database to insert table values...")
        mydb1 = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin2968"
        )
        mycursor = mydb1.cursor()
        mycursor.execute("USE {}".format(DB_NAME))
        fn, ln, un, ue, up = self.entryFirstName.get(), self.entryLastName.get(
        ), self.entryUserName.get(), self.entryEmail.get(), self.entryPassword.get()
        mycursor.execute(
            "INSERT INTO users (FirstName, LastName, username, useremail, userpass) VALUES (%s, %s, %s, %s, %s)", (fn, ln, un, ue, up))
        print("Insertion done!")
        mydb1.commit()
        pass


DB_NAME = 'python_project'


def connect_database():
    def create_database(myCursor):
        try:
            myCursor.execute("CREATE DATABASE {}".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    print("Connecting database... ")
    print(DB_NAME)

    mydb = mysql.connector.connect(
        user='root',
        password='admin2968',
        host='localhost'
    )
    myCursor = mydb.cursor()

    try:
        myCursor.execute("USE {}".format(DB_NAME))
        print("Using database....")
        use_database(myCursor)
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(myCursor)
            print("Database {} created successfully.".format(DB_NAME))
            myCursor.execute("USE {}".format(DB_NAME))
            use_database(myCursor)
        else:
            print(err)
            exit(1)
    myCursor.close()
    del myCursor


def use_database(myCursor):
    try:
        print("Creating table {}: ".format("users"), end='')
        myCursor.execute("CREATE TABLE users (user_ID int NOT NULL AUTO_INCREMENT PRIMARY KEY, FirstName varchar(25),LastName varchar(25),username varchar(25),useremail varchar(255), userpass varchar(25));")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


if __name__ == "__main__":
    connect_database()
    app = SampleApp()
    app.mainloop()
