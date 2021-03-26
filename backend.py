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
