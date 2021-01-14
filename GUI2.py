import tkinter as tk
# from MailChimpApp import *
import pandas as pd
import os
import linecache
# https://mailchimp.com/help/about-your-contacts/


class NoFileFound(Exception):
    """Raised when a file cannot be found"""
    pass


class DuplicateFilesFound(Exception):
    """Raised when duplicate files of the same file are found within the same directory"""
    pass


class MailChimpApp:
    # Constructor
    def __init__(self):
        arr = []
        ff = os.path.dirname(os.path.abspath(__file__)) + "/config.txt"
        for i in range(1, 5):
            line = linecache.getline(ff, i)
            index = line.find('"')
            extracted = line[index+1:-2]
            arr.append(extracted)
        self.column1 = arr[0]
        self.fname_main = arr[1]
        self.fname_Bouncer = arr[2]
        self.fname_Unsub = arr[3]

    def getPath(self, targetCSV):
        """
        Searches within local directory of where this python file you are reading 
        right now is located for the file(s) with 'targetCSV' string filename.
        """
        dirname = os.path.dirname(__file__)  # alternative : `os.getcwd()`
        count = -1
        fpath2 = None
        for filename in os.listdir(dirname):
            # Will NOT work with case insensitivity; use re.match() instead with regex/wild if client needs
            if filename.startswith(targetCSV) and filename.endswith(".csv"):
                count += 1
                fpath2 = filename  # takes the latest copy
        if count < 0:
            raise NoFileFound("\n" + targetCSV + " file not found.")
        elif count > 0:
            # Program cannot determine latest copy to use, so force the user to store only one copy of a file
            raise DuplicateFilesFound("\nWARNING: More than one " + targetCSV +
                                      " files were found. Please only store the latest copy in folder!")
        return fpath2

    def report(self, data, cleanCount, unsubCount, NoResult):
        """Generates a summary of file cleaning activity; E.g. - the total number of entries removed."""
        clone = data.copy()
        # Marks duplicate values as True or False based on stripped lowercase new column
        clone = clone[clone.duplicated("temp", keep="first")]
        clone.drop(columns="temp", inplace=True)
        clone.drop(clone.columns[4], axis=1, inplace=True)

        nullCount = data[self.column1].isnull().sum()
        # Option 3 Selected
        if cleanCount == None:
            total = nullCount + unsubCount
            cleanCount = 0
            dupeCount = 0

        else:
            dupeCount = clone[self.column1].count()
            total = dupeCount + nullCount + cleanCount + unsubCount

        FoundMsg = """\
        \n----------- SUMMARY -----------\
        Duplicated entries found: {}\
        Null entries found: {}\
        Cleaned members found: {}\
        Unsubscribed members found: {}\
        Total entries removed: {}\
        """.format(dupeCount, nullCount, cleanCount, unsubCount, total)

        if dupeCount == 0 and cleanCount == 0 and unsubCount == 0:
            return "\n\n> Database is already clean!"

        if not NoResult:
            clone.to_csv("Results.csv")
        return FoundMsg

    def cleanDupe(self, data):
        """Deletes duplicate entries from a database"""
        data.drop_duplicates(subset="temp", keep="first", inplace=True)
        data.drop(columns="temp", inplace=True)
        # data.reset_index(inplace=True, drop=True)

    def cleanMembers(self, data, other):
        """Deletes entries from a database that contains specific members from another database"""
        criteria = data[self.column1].isin(other[self.column1])
        beforeCount = data[self.column1].count()
        # inplace = True --> original dataframe is manipulated and nothing is returned; False --> default, returns copy of object...must store/save somewhere
        data.drop(data[criteria].index, inplace=True)

        afterCount = data[self.column1].count()
        diff = beforeCount - afterCount

        if diff == 0:
            print("No deletions made!")
            return diff
        else:
            print("Deleted %d entries" % diff)
            return diff

    # Remove Duplicates & Unsubscribers
    def option1(self, NoResult):
        filesRequired = True
        fnames = [self.fname_main, self.fname_Bouncer, self.fname_Unsub]
        statement = ""
        for name in fnames:
            try:
                self.getPath(name)
            except NoFileFound as msg:
                filesRequired = False
                statement += "\n" + str(msg) + "\n"
            except DuplicateFilesFound as msg2:
                filesRequired = False
                statement += "\n" + str(msg2) + "\n"
        if filesRequired:
            # file MUST be contained in same directory
            fpath = self.getPath(self.fname_main)
            fpath_Bouncer = self.getPath(self.fname_Bouncer)
            fpath_Unsub = self.getPath(self.fname_Unsub)

            data = pd.read_csv(fpath)
            data2 = pd.read_csv(fpath_Bouncer)
            data3 = pd.read_csv(fpath_Unsub)

            # Must create the 'temp' column first
            # Creates a new row that's stripped
            data["temp"] = data[self.column1].str.strip()
            # Converts all cases to be lower for proper duplicate evaluation
            data["temp"] = data["temp"].str.lower()

            # Changes initial index from 0 to 2
            data.index = range(2, len(data)+2)
            cleanCount = self.cleanMembers(data, data2)
            unsubCount = self.cleanMembers(data, data3)

            msg = self.report(data, cleanCount, unsubCount, NoResult)
            self.cleanDupe(data)
            data.drop(data.columns[4], axis=1, inplace=True)
            # Saves dataframe as a .csv file with no default index column added
            data.to_csv("CLEAN_SWdatabase.csv", index=False)
            return msg
        return statement

    # Remove Duplicates ONLY
    def option2(self, NoResult):
        try:
            self.getPath(self.fname_main)
        except NoFileFound as msg:
            return ("\n" + str(msg) + "\n")
        except DuplicateFilesFound as msg2:
            return ("\n" + str(msg2) + "\n")
        else:
            # file MUST be contained in same directory
            fpath = self.getPath(self.fname_main)
            data = pd.read_csv(fpath)

            # Must create the 'temp' column first
            # Creates a new row that's stripped
            data["temp"] = data[self.column1].str.strip()
            # Converts all cases to be lower for proper duplicate evaluation
            data["temp"] = data["temp"].str.lower()

            # Changes initial index from 0 to 2
            data.index = range(2, len(data)+2)

            msg = self.report(data, cleanCount=0,
                              unsubCount=0, NoResult=NoResult)
            self.cleanDupe(data)
            data.drop(data.columns[4], axis=1, inplace=True)
            # Saves dataframe as a .csv file with no default index column added
            data.to_csv("CLEAN_SWdatabase.csv", index=False)
            return msg

    # Remove Unsubscribers ONLY
    def option3(self, NoResult):
        filesRequired = True
        fnames = [self.fname_main, self.fname_Unsub]
        statement = ""
        for name in fnames:
            try:
                self.getPath(name)
            except NoFileFound as msg:
                filesRequired = False
                statement += "\n" + str(msg) + "\n"
            except DuplicateFilesFound as msg2:
                filesRequired = False
                statement += "\n" + str(msg2) + "\n"

        if filesRequired:
            # file MUST be contained in same directory
            fpath = self.getPath(self.fname_main)
            fpath_Unsub = self.getPath(self.fname_Unsub)

            data = pd.read_csv(fpath)
            data3 = pd.read_csv(fpath_Unsub)

            # Must create the 'temp' column first
            # Creates a new row that's stripped
            data["temp"] = data[self.column1].str.strip()
            # Converts all cases to be lower for proper duplicate evaluation
            data["temp"] = data["temp"].str.lower()

            # Changes initial index from 0 to 2
            data.index = range(2, len(data)+2)

            unsubCount = self.cleanMembers(data, data3)
            msg = self.report(data, cleanCount=None,
                              unsubCount=unsubCount, NoResult=NoResult)
            data.drop(data.columns[4], axis=1, inplace=True)
            data.drop(columns="temp", inplace=True)
            # Saves dataframe as a .csv file with no default index column added
            data.to_csv("CLEAN_SWdatabase.csv", index=False)
            return msg
        return statement

    def changeConfig(self, setting, newValue):
        f = open("config.txt", "r")
        filedata = f.read()
        f.close()

        line = linecache.getline("config.txt", setting)
        index = line.find('"')
        extracted = line[index+1:-2]

        newdata = filedata.replace(extracted, newValue)
        f = open("config.txt", "w")
        f.write(newdata)
        f.close()


# --- Testing Environment ; too lazy to use unittest ---
# x = MailChimpApp()

# option = 1 # Manually set options to mimic button selection
# if option == 1:
#     x.option1(False)
# elif option == 2:
#     x.option2()
# elif option == 3:
#     x.option3()
# else:
#     x.option4("newFileName.csv")
# -------------------------------------------------------------------------------
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
