from Database import Database
import getpass

print("Welcome! \n")

master = getpass.getpass("Enter Master Password Here: ")

database = Database(master, "Information.db")

choice = input("Would You Like To Read (R), Insert (I), Update (U), Delete (D), List (L), Additional (A), Or Exit (E)? ").upper()

while(choice != "E"):

    if(choice == "R"):
        database.read()

    elif(choice == "I"):
        database.insert()
    
    elif(choice == "U"):
        database.update()

    elif(choice == "D"):
        database.delete()

    elif(choice == "L"):
        database.list()

    elif(choice == "A"):
        database.readAdd()

    elif(choice == "E"):
        exit()
    
    else:
        print("Invalid Choice \n")

    choice = input("Would You Like To Read (R), Insert (I), Update (U), Delete (D), List (L), Additional (A), Or Exit (E)? ").upper()

