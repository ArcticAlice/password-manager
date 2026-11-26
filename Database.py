import sqlite3
from Encrypt import Encrypt
from Generate import Generate
from prettytable import PrettyTable
import json

class ExitToMenu(Exception):
    pass

# This class interacts with the SQLite database
class Database:
    
    def __init__(self, master_password: str, database_name):
        self.path = database_name
        self.connect()
        self.ensure_table()
        self.encrypt = Encrypt(master_password)

        if not self.validate():
            print("Master password is incorrect for this database.")
            self.close()
            exit()
        else:
            print("Master password validated successfully.\n")

    def connect(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def _input(self, prompt: str) -> str:
        value = input(prompt)
        if value.upper() == "EXIT":
            print("Returning to menu... \n")
            raise ExitToMenu()
        return value

    def ensure_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Pass_v2 (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Service TEXT NOT NULL,
                Email BLOB,
                Label TEXT,
                Username BLOB,
                Additional BLOB,
                Salt BLOB NOT NULL,
                Password BLOB NOT NULL
            )
        """)
        self.conn.commit()

    def validate(self):
        try:
            self.cursor.execute(
            "SELECT Salt, Password FROM Pass_v2 WHERE Service = ? AND Label = ?",
            ("Validate", "Validate"))

            row = self.cursor.fetchone()

            if not row:
                salt = self.encrypt.getSalt()
                encrypted_password, = self.encrypt.toEncrypt(salt, ["Validate"])

                self.cursor.execute("""
                Insert INTO Pass_v2 (Service, Email, Label, Username, Salt, Password) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, ("Validate", "Validate@gmail.com", "Validate", "Validate", salt, encrypted_password))

                self.conn.commit()
                return True 

            salt, encrypted_password = row
            raw_password, = self.encrypt.toDecrypt(salt, [encrypted_password])

            if (raw_password == "Validate"):
                return True
        except:
            return False

    def read(self):
        try:
            service = self._input("Which Service Would You Like To Read From? ").upper()

            self.cursor.execute("SELECT ID, Salt, Password, Email, Username, Label FROM Pass_v2 WHERE Service = ?", (service,))

            rows = self.cursor.fetchall()

            if (len(rows) > 1):
                table = PrettyTable()
                table.align = 'l'
                table.field_names = ["ID", "Service", "Email", "Label"]
                for row in rows:
                    raw_email, = self.encrypt.toDecrypt(row[1], [row[3]])
                    table.add_row([row[0], service, raw_email, row[5]])
                print(f"{table} \n")
                label = self._input("Please Filter By Label: ").upper()
                self.cursor.execute("SELECT ID, Salt, Password, Email, Username FROM Pass_v2 WHERE Service = ? AND Label = ?", (service, label))
                rows = self.cursor.fetchone()
            else:
                self.cursor.execute("SELECT ID, Salt, Password, Email, Username FROM Pass_v2 WHERE Service = ?", (service,))
                rows = self.cursor.fetchone()

            if (rows):
                id, salt, encypted_password, encrypted_email, encypted_username = rows
                raw_password, raw_email, raw_username = self.encrypt.toDecrypt(salt, [encypted_password, encrypted_email, encypted_username])
            else:
                print("No Service Found")
                return

            table = PrettyTable()
            table.align = 'l'
            table.field_names = ["ID", "Email", "Username", "Password"]
            table.add_row([id, raw_email, raw_username, raw_password])
            print(f"{table} \n")

        except ExitToMenu:
            return

    def list(self):

        self.cursor.execute("SELECT Service, Email, Label, Username, Salt FROM Pass_v2")

        rows = self.cursor.fetchall()

        if not rows:
            print("Nothing Found \n")
            return
        
        rows.sort(key=lambda row: row[0])

        table = PrettyTable()
        table.align = "l"

        table.field_names = ["Service", "Email", "Label", "Username"]

        # Print each row with formatting
        for row in rows:
            service, encrypted_email, label, encypted_username, salt = row
            if service == "Validate" and label == "Validate":
                continue
            else:
                raw_email, raw_username = self.encrypt.toDecrypt(salt, [encrypted_email, encypted_username])
                table.add_row([service, raw_email, label, raw_username])

        print()
        print(table)
        print()

    def insert(self):
        try:
            service = self._input("Enter Website Name Here: ").upper()
            raw_email = self._input("Enter Email Here: ")
            label = self._input("Enter Label Here: ").upper()
            raw_username = self._input("Enter Username Here: ")
            raw_password = self._input("Enter Password Here: ")
            if (len(raw_password) <= 5):
                raw_password = Generate(20).main()
                print(f"Password too short. Generated a secure password: {raw_password} \n")

            salt = self.encrypt.getSalt()
            encrypted_password, encrypted_email, encrypted_username = self.encrypt.toEncrypt(salt, [raw_password, raw_email, raw_username])

            self.cursor.execute("""
            INSERT INTO Pass_v2 (Service, Email, Label, Username, Salt, Password)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (service, encrypted_email, label, encrypted_username, salt, encrypted_password))

            self.conn.commit()

            print("Password Added Successfully \n")

        except ExitToMenu:
            return

    def update(self):
        try:
            index = self._input("Enter Index Here: ")

            if not index.isdigit():
                print("Index must be a number \n")
                return

            change = self._input("What Would You Like To Change? Service (S), Email (E), Label (L), Username (U), Additional (A), Or Password (P) ").upper()
            
            self.cursor.execute("SELECT Salt FROM Pass_v2 WHERE ID = ?", (index,))
            row = self.cursor.fetchone()

            if not row:
                print("Index does not exits\n")
                return  

            salt = row[0]

            if change == "S":
                service = self._input("Enter New Service Here: ").upper()
                self.cursor.execute("UPDATE Pass_v2 SET Service = ? WHERE ID = ?", (service, index))
            elif change == "E":
                raw_email = self._input("Enter New Email Here: ")
                encrypted_email, = self.encrypt.toEncrypt(salt, [raw_email])
                self.cursor.execute("UPDATE Pass_v2 SET Email = ? WHERE ID = ?", (encrypted_email, index))
            elif change == "L":
                label = self._input("Enter New Label Here: ").upper()
                self.cursor.execute("UPDATE Pass_v2 SET Label = ? WHERE ID = ?", (label, index))
            elif change == "U":
                raw_username = self._input("Enter New Username Here: ")
                encrypted_username, = self.encrypt.toEncrypt(salt, [raw_username])
                self.cursor.execute("UPDATE Pass_v2 SET Username = ? WHERE ID = ?", (encrypted_username, index))
            elif change == "A":
                self.insertAdd(index, salt)
            elif change == "P":
                raw_password = self._input("Enter New Password Here: ")
                if (len(raw_password) <= 5):
                    raw_password = Generate(20).main()
                    print(f"Password too short. Generated a secure password: {raw_password} \n")
                encrypted_password, = self.encrypt.toEncrypt(salt, [raw_password])
                self.cursor.execute("UPDATE Pass_v2 SET Password = ? WHERE ID = ?", (encrypted_password, index))
            else:
                print("Option Not Valid \n")
                return

            self.conn.commit()

            print("Table Updated Successfully \n")

        except ExitToMenu:
            return

    def delete(self):
        try:
            index = self._input("Enter Index Here: ")

            if not index.isdigit():
                print("Index must be a number \n")
                return

            if(int(index) == 1):
                print("Cannot Delete Validation Entry \n")
                return

            self.cursor.execute("SELECT Salt, Service, Email, Label, Username FROM Pass_v2 WHERE ID = ?", (index,))
            row = self.cursor.fetchone()

            if not row:
                print("No Service Found \n")
                return
            
            raw_email, raw_username = self.encrypt.toDecrypt(row[0], [row[2], row[4]])

            table = PrettyTable()
            table.field_names = ["Service", "Email", "Label", "Username"]
            table.add_row([row[1], raw_email, row[3], raw_username])
            table.align = 'l'
            print(table)
            choice = self._input(f"Are You Sure You Want To Delete the following entry? Yes (Y) Or No (N) ").upper()

            if choice == "Y":
                self.cursor.execute("DELETE FROM Pass_v2 WHERE ID = ?", (index,))
                self.conn.commit()
                print("Password Deleted Successfully \n")
            elif choice == "N":
                print("You Changed Your Mind \n")
            else:
                print("Not Valid Option \n")
                return

        except ExitToMenu:
            return
    
    def insertAdd(self, index, salt):
        try:
            self.cursor.execute("SELECT Additional FROM Pass_v2 WHERE ID = ?", (index,))
            row = self.cursor.fetchone()

            if row and row[0]:
                encrypted_info = row[0]
                json_string, = self.encrypt.toDecrypt(salt, [encrypted_info])
                raw_info = json.loads(json_string)
            else:
                raw_info = {}

            finished = "Y"

            while finished == "Y":
                question = self._input("Enter Question, Pin, Or Custom Here: ")
                answer = self._input("Enter Answer Here: ")
                raw_info[question] = answer
                finished = self._input("Would You Like To Continue? Yes (Y) Or No (N) ").upper()

            json_string = json.dumps(raw_info)
            encrypted_info, = self.encrypt.toEncrypt(salt, [json_string])

            self.cursor.execute("UPDATE Pass_v2 SET Additional = ? WHERE ID = ?", (encrypted_info, index))

        except ExitToMenu:
            return
        
    def readAdd(self):
        try:
            service = self._input("Which Service Would You Like To Read From? ").upper()

            self.cursor.execute("SELECT Salt, Additional, Label FROM Pass_v2 WHERE Service = ?", (service,))
            rows = self.cursor.fetchall()

            if not rows:
                print("No Service Exists \n")
                return
            
            table = PrettyTable()
            table.field_names = ["Service", "Label"]
            table.align = 'l'
            count = 0
            labels = []

            for row in rows:
                if row[1]:
                    count += 1
                    table.add_row([service, row[2]])
                    labels.append(row[2])

            if count == 0:
                print("No Account For This Service Has Additional Information \n")
                return
            
            if count > 1:
                print(f"{table} \n")
                label = self._input("Please Filter By Label: ").upper()

                self.cursor.execute("SELECT Salt, Additional FROM Pass_v2 WHERE Service = ? AND Label = ?", (service, label))
                row = self.cursor.fetchone()

                if not row:
                    print("No Service Has This Label \n")
                    return
            else:
                self.cursor.execute("SELECT Salt, Additional FROM Pass_v2 WHERE Service = ? AND Label = ?", (service, labels[0]))
                row = self.cursor.fetchone()
                
            table.clear()
            table.align = 'l'

            salt = row[0]
            encrypted_info = row[1]

            json_string, = self.encrypt.toDecrypt(salt, [encrypted_info])
            raw_info = json.loads(json_string)
            headings = ["Service"]
            values = [service]

            for key, value in raw_info.items():
                headings.append(key)
                values.append(value)

            table.field_names = headings
            table.add_row(values)

            print(f"{table} \n")

        except ExitToMenu:
            return


    def close(self):
        self.conn.close()