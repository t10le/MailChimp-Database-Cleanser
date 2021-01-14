import tkinter as tk
from MailChimpApp import *

# GLOBAL VARIABLES
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 500
CONST_X = 0.06
CONST_WIDTH = 0.88
GREETMSG = "MailChimp Email Cleanser\nBy Tommy Le\n\nWelcome!\nBefore starting, ensure all files are within the same directory.\n\nTo get started, click on the options below."

root = tk.Tk()
root.title("MailChimp Email Cleanser")
root.iconbitmap("email.ico")
root.geometry("%dx%d" % (WINDOW_WIDTH, WINDOW_HEIGHT))

#add new comment test
class UserInterface(MailChimpApp):
    # Constructor
    def __init__(self, root):
        super().__init__()
        self.preMsg = "> Analyzing '%s' database ...\n\n" % (self.fname_main)

        # Output Box
        frm_output = tk.Frame(root, bg="grey", bd=2)
        frm_output.place(relx=CONST_X, rely=0.04,
                         relwidth=CONST_WIDTH, relheight=0.44)
        self.lbl_output = tk.Label(
            frm_output,
            text=GREETMSG,
            fg="white",
            bg="#282a37",
            font=("Courier", 13),
            anchor="nw",
            justify="left",
            wraplength=250
        )
        # error message: lbl_output.config(fg="red")
        self.lbl_output.place(relwidth=1, relheight=1)

        # Check Button - Results
        frm_results = tk.Frame(root)
        frm_results.place(relx=CONST_X, rely=0.49,
                          relwidth=CONST_WIDTH, relheight=0.05)
        tk.Grid.columnconfigure(frm_results, 0, weight=1)
        tk.Grid.rowconfigure(frm_results, 0, weight=1)
        # Default checkbox is value=1 pre-checked mark
        self.flag = tk.IntVar(value=1)
        check = tk.Checkbutton(frm_results, text="No Results", variable=self.flag).grid(
            row=0, column=0, sticky="ns")

        # Buttons
        frm_buttons = tk.Frame(root)
        frm_buttons.place(relx=CONST_X, rely=0.55,
                          relwidth=CONST_WIDTH, relheight=0.3)
        tk.Grid.columnconfigure(frm_buttons, 0, weight=1)
        for row in range(3):
            tk.Grid.rowconfigure(frm_buttons, row, weight=1)
        btn_1 = tk.Button(frm_buttons, text="Remove Duplicates & Unsubscribers",
                          command=self.Action1).grid(row=0, column=0, sticky="nswe")
        btn_2 = tk.Button(frm_buttons, text="Remove Duplicates ONLY",
                          command=self.Action2).grid(row=1, column=0, sticky="nswe")
        btn_3 = tk.Button(frm_buttons, text="Remove Unsubscribers ONLY",
                          command=self.Action3).grid(row=2, column=0, sticky="nswe")

        # New Email
        frm_email = tk.Frame(root)
        frm_email.place(relx=0.2, rely=0.87, relwidth=0.59, relheight=0.1)
        tk.Grid.columnconfigure(frm_email, 0, weight=1)
        tk.Grid.rowconfigure(frm_email, 0, weight=1)
        newName = tk.Label(frm_email, text="New Email Database Name").grid(
            row=0, column=0, sticky="ns")
        self.entry = tk.Entry(frm_email)
        self.entry.bind("<Return>", self.Action4)
        # Note: had to separate .grid, else .bind won't work
        self.entry.grid(row=1, column=0, sticky="nswe")

    # Remove Duplicates & Unsubscribers
    def Action1(self):
        # Converts 0 or 1 into True or False to avoid (if NoResult == 1 or 0)
        NoResult = bool(self.flag.get())
        if NoResult:
            self.lbl_output["text"] = "%s> No Result.csv%s" % (
                self.preMsg, self.option1(NoResult))
        else:
            self.lbl_output["text"] = "%s> Producing Result.csv%s" % (
                self.preMsg, self.option1(NoResult))

    # Remove Duplicates ONLY
    def Action2(self):
        # Converts 0 or 1 into True or False to avoid (if NoResult == 1 or 0)
        NoResult = bool(self.flag.get())
        if NoResult:
            self.lbl_output["text"] = "%s> No Result.csv%s" % (
                self.preMsg, self.option2(NoResult))
        else:
            self.lbl_output["text"] = "%s> Producing Result.csv%s" % (
                self.preMsg, self.option2(NoResult))

    # Remove Unsubscribers ONLY
    def Action3(self):
        # Converts 0 or 1 into True or False to avoid (if NoResult == 1 or 0)
        NoResult = bool(self.flag.get())
        if NoResult:
            self.lbl_output["text"] = "%s> No Result.csv%s" % (
                self.preMsg, self.option3(NoResult))
        else:
            self.lbl_output["text"] = "%s> Producing Result.csv%s" % (
                self.preMsg, self.option3(NoResult))

    # New Email Database Name Change
    def Action4(self, event):
        value = self.entry.get()
        self.entry.delete(0, "end")
        self.changeConfig(2, value)
        self.lbl_output["text"] = "%s file has been registered!\n\nPlease restart the application now for the changes to apply completely." % value


test = UserInterface(root)

root.mainloop()
