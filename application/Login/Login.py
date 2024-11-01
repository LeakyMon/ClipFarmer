import customtkinter
from Login.Auth import Authentication
from tkinter import messagebox

class AuthPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.auth_instance = Authentication()

        self.title_container = customtkinter.CTkLabel(self, text="Sign In or Create an Account", font=('Arial', 32))
        self.title_container.pack(pady=20)

        self.login_container = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.createAuthPage()

    def user_login(self):
        email = self.user_entry.get()
        password = self.user_pass.get()
        result = self.auth_instance.sign_in(email, password)
        if result:
            self.parent.show_home_page()  # Transition to home page after login
        else:
            messagebox.showerror("Login Failed", "Invalid email or password. Please try again.")

    def register_account(self):
        email = self.user_entry.get()
        password = self.user_pass.get()
        if email and password:
            result = self.auth_instance.signUp(email, password)
            if result:
                messagebox.showinfo("Account Created", "Account created successfully. Please log in.")
                self.parent.show_home_page()  # Optionally go directly to home page after account creation
            else:
                messagebox.showerror("Registration Failed", "Failed to create account. Try again.")

    def skip(self):
        # Use a default account to skip login
        email = "default_user@example.com"
        password = "default_password"
        result = self.auth_instance.sign_in(email, password)
        if result:
            self.parent.show_home_page()

    def createAuthPage(self):
        self.label1 = customtkinter.CTkLabel(master=self.login_container, text='Login Below')
        self.label1.pack(pady=12, padx=10)

        self.user_entry = customtkinter.CTkEntry(master=self.login_container, placeholder_text="Email")
        self.user_entry.pack(pady=12, padx=10)

        self.user_pass = customtkinter.CTkEntry(master=self.login_container, placeholder_text="Password", show="*")
        self.user_pass.pack(pady=12, padx=10)

        self.button = customtkinter.CTkButton(master=self.login_container, text='Login', command=self.user_login)
        self.button.pack(pady=12, padx=10)

        #self.button1 = customtkinter.CTkButton(master=self.login_container, text='Register', command=self.register_page)
        #self.button1.pack(pady=12, padx=10)

        self.button2 = customtkinter.CTkButton(master=self.login_container, text='Skip', command=self.skip)
        self.button2.pack(pady=12, padx=10)
