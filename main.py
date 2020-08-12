import csv
import sys
import time

save_location = None
second_option = None

# Each of these will become nested dictionaries
accounts = {}
incomes = {}
expenses = {}
transfers = {}


# First code that gets executed
def main():
    print("Welcome to Andrew's Budgeting Software!\n"
          "If you find yourself stuck on an input prompt, press ENTER to exit to summary.\n")
    ask_for_previous_save()


# Repeated error message for invalid input
def not_valid():
    print("Not valid, try again.\n")


def already_exists():
    print("Already exists, try again")


# Directs to find_save or add_account depending on user input if previous save exists
def ask_for_previous_save():
    save_exists = input("Do you have a previous save for this program? (Y/N)\n").lower()
    if save_exists == "y":
        find_previous_save()
    elif save_exists == "n":
        print("Starting new save...")
        print("What is the first account you would like to add?")
        add_account()
    else:
        not_valid()
        ask_for_previous_save()


# Asks user for file path, locates file, and saves data in nested dictionaries
def find_previous_save():
    global save_location
    try:
        save_location = input("Save File Path: ")
        with open(save_location, "r") as save_file:
            save_reader = csv.reader(save_file)
            for row in save_reader:
                # Reads each row in the file and attributes each entry to dictionary depending on first value
                if row[0] == "account":
                    accounts[row[1]] = {"Starting_Amount": float(row[2]), "Ending_Amount": float(row[3])}
                elif row[0] == "income":
                    incomes[row[1]] = {"Destination": row[2], "Amount": float(row[3])}
                elif row[0] == "expense":
                    expenses[row[1]] = {"Origin": row[2], "Amount": float(row[3])}
                elif row[0] == "transfer":
                    transfers[row[1]] = {"Origin": row[2], "Destination": row[3], "Amount": float(row[4])}
    except (FileNotFoundError, PermissionError, OSError):
        not_valid()
        find_previous_save()
    summary()


# Adds an account to nested dictionary
def add_account():
    account_name = input("\nAccount Name: ").title()
    if account_name == "":
        summary()
    elif account_name in accounts:
        already_exists()
        add_account()
    while True:
        try:
            starting_amount = float(input(f"Starting Amount in {account_name}: $"))
            accounts[account_name] = {"Starting_Amount": starting_amount, "Ending_Amount": starting_amount}
            break
        except ValueError:
            not_valid()
    continue_choice(add_account)


# Adds income to nested dictionary and ties it to a specific account
def add_income():
    income_name = input("\nIncome Name: ").title()
    if income_name == "":
        summary()
    elif income_name in incomes:
        already_exists()
        add_income()
    try:
        income_amount = float(input("Amount: $"))
        incomes[income_name] = income_amount
        print("Destination Account?")
        for name in accounts:
            print(f"*{name}")
        destination = input().title()
        if destination in accounts:
            incomes[income_name] = {"Destination": destination, "Amount": income_amount}
            accounts[destination]["Ending_Amount"] += incomes[income_name]["Amount"]
        else:
            not_valid()
            add_income()
    except (ValueError, TypeError, KeyError):
        not_valid()
        add_income()
    continue_choice(add_income)


# Adds expense to nested dictionary and ties it to a specific account
def add_expense():
    expense_name = input("\nExpense Name: ").title()
    if expense_name == "":
        summary()
    elif expense_name in expenses:
        already_exists()
        add_expense()
    try:
        expense_amount = float(input("Amount: $"))
        expenses[expense_name] = expense_amount
        print("Originating Account?")
        for name in accounts:
            print(f"*{name}")
        origin = input().title()
        if origin in accounts:
            expenses[expense_name] = {"Origin": origin, "Amount": expense_amount}
            accounts[origin]["Ending_Amount"] -= expenses[expense_name]["Amount"]
        else:
            not_valid()
            add_expense()
    except (ValueError, TypeError, KeyError):
        not_valid()
        add_expense()
    continue_choice(add_expense)


# Adds transfer to nested dictionary and ties it to a specific account
def add_transfer():
    transfer_name = input("\nTransfer Name: ").title()
    if transfer_name == "":
        summary()
    elif transfer_name in transfers:
        already_exists()
        add_transfer()
    try:
        transfer_amount = float(input("Amount: $"))
        print("Originating Account?")
        for name in accounts:
            print(f"*{name}")
        origin = input().title()
        if origin not in accounts:
            not_valid()
            add_transfer()
        print("Destination Account?")
        for name in accounts:
            print(f"*{name}")
        destination = input().title()
        if destination not in accounts:
            not_valid()
            add_transfer()
        transfers[transfer_name] = {"Origin": origin, "Destination": destination, "Amount": transfer_amount}
        accounts[origin]["Ending_Amount"] -= transfers[transfer_name]["Amount"]
        accounts[destination]["Ending_Amount"] += transfers[transfer_name]["Amount"]
    except (ValueError, TypeError, KeyError):
        not_valid()
        add_transfer()
    continue_choice(add_transfer)


# Directs to the correct entry deletion
def delete_directory():
    global second_option
    if second_option == "_account":
        delete_entry("account", accounts)
    elif second_option == "_income":
        delete_entry("income", incomes)
    elif second_option == "_expense":
        delete_entry("expense", expenses)
    elif second_option == "_transfer":
        delete_entry("transfer", transfers)


# Deletes entry in specified dictionary
def delete_entry(category, dictionary):
    print(f"\nWhich {category} would you like to delete? ")
    for entry in dictionary:
        print(f"*{entry}")
    entry = input().title()
    if entry == "":
        summary()
    elif entry in dictionary:
        if category == "account":
            # If the category is account, it will search each income, expense, and transfer
            # Any income, expense, or transfer connected to the entry will be deleted
            for income in list(incomes):
                if entry in incomes[income]["Destination"]:
                    del incomes[income]
            for expense in list(expenses):
                if entry in expenses[expense]["Origin"]:
                    del expenses[expense]
            for transfer in list(transfers):
                if (entry in transfers[transfer]["Destination"]) or (entry in transfers[transfer]["Origin"]):
                    del transfers[transfer]
        # The amount of the entry being deleted will be debited/credited back to the original accounts
        elif category == "income":
            destination = dictionary[entry]["Destination"]
            accounts[destination]["Ending_Amount"] -= dictionary[entry]["Amount"]
        elif category == "expense":
            origin = dictionary[entry]["Origin"]
            accounts[origin]["Ending_Amount"] += dictionary[entry]["Amount"]
        elif category == "transfer":
            origin = dictionary[entry]["Origin"]
            destination = dictionary[entry]["Destination"]
            accounts[origin]["Ending_Amount"] += dictionary[entry]["Amount"]
            accounts[destination]["Ending_Amount"] -= dictionary[entry]["Amount"]
        del dictionary[entry]
        continue_choice(delete_directory)
    else:
        not_valid()
        delete_entry(category, dictionary)


# Provides the user the choice to continue the current module
def continue_choice(func):
    cont = input("Continue? (Y/N)\n").lower()
    if cont == "y":
        func()
    elif cont == "n":
        summary()
    else:
        not_valid()
        continue_choice(func)


# Creates file at given file path and writes dictionary data
def save_and_exit():
    global save_location
    save_location = input("\nSave Folder Path: ")
    if save_location == "":
        summary()
    save_location = save_location + "\\budget.csv"
    try:
        with open(save_location, "w", newline="") as save_file:
            save_writer = csv.writer(save_file)
            # Takes each dictionaries' entries and writes them to the file
            for account in accounts:
                starting_amount = accounts[account]["Starting_Amount"]
                ending_amount = accounts[account]["Ending_Amount"]
                save_writer.writerow(["account", account, starting_amount, ending_amount])
            for income in incomes:
                destination = incomes[income]["Destination"]
                amount = incomes[income]["Amount"]
                save_writer.writerow(["income", income, destination, amount])
            for expense in expenses:
                origin = expenses[expense]["Origin"]
                amount = expenses[expense]["Amount"]
                save_writer.writerow(["expense", expense, origin, amount])
            for transfer in transfers:
                origin = transfers[transfer]["Origin"]
                destination = transfers[transfer]["Destination"]
                amount = transfers[transfer]["Amount"]
                save_writer.writerow(["transfer", transfer, origin, destination, amount])
    except FileNotFoundError:
        not_valid()
        save_and_exit()
    print("\nThank you for using Andrew's Budgeting Software!")
    time.sleep(3)
    sys.exit()


# Provides a formatted list of all dictionaries
def summary():
    line_break = f"{'-' * 60}"
    print(f"\n{'Accounts':^20} | {'Starting Amount':^17} | {'Ending Amount':^17}")
    print(line_break)
    for account in accounts:
        starting_amount = accounts[account]["Starting_Amount"]
        ending_amount = accounts[account]["Ending_Amount"]
        print(f"{account:<20} | ${starting_amount:<16,.2f} | ${ending_amount:<16,.2f}")
    if len(incomes) > 0:
        print(f"\n{'Incomes':^20} | {'Destination':^17} | {'Amount':^17}")
        print(line_break)
        for income in incomes:
            destination = incomes[income]["Destination"]
            amount = incomes[income]["Amount"]
            print(f"{income:<20} | {destination:<17} | ${amount:<16,.2f}")
    if len(expenses) > 0:
        print(f"\n{'Expenses':^20} | {'Origin':^17} | {'Amount':^17}")
        print(line_break)
        for expense in expenses:
            origin = expenses[expense]["Origin"]
            amount = expenses[expense]["Amount"]
            print(f"{expense:<20} | {origin:<17} | ${amount:<16,.2f}")
    if len(transfers) > 0:
        print(f"\n{'Transfers':^20} | {'Origin':^17} | {'Destination':^17} | {'Amount':^17}")
        print(f"{'-' * 80}")
        for transfer in transfers:
            origin = transfers[transfer]["Origin"]
            destination = transfers[transfer]["Destination"]
            amount = transfers[transfer]["Amount"]
            print(f"{transfer:<20} | {origin:<17} | {destination:<17} | ${amount:<16,.2f}")
    choose_next()


# Asks for user input on what function to execute next
def choose_next():
    global second_option
    try:
        first_choice = int(input("\nWhat would you like to do?\n"
                                 "1. Add Entry\n"
                                 "2. Delete Entry\n"
                                 "3. Save and Exit\n"))
        first_option = str(first_switcher.get(first_choice))
        if first_option == "save_and_exit":
            save_and_exit()
        second_choice = int(input(f"Where would you like to {first_option} an entry?\n"
                                  "1. Accounts\n"
                                  "2. Incomes\n"
                                  "3. Expenses\n"
                                  "4. Transfers\n"))
        second_option = str(second_switcher.get(second_choice))
        func_choice = first_option + second_option
        func = function_switcher.get(func_choice)
        return func()
    except (ValueError, TypeError):
        not_valid()
        choose_next()


# Switch statements that act as a function directory
first_switcher = {
    1: "add",
    2: "delete",
    3: "save_and_exit"
}
second_switcher = {
    1: "_account",
    2: "_income",
    3: "_expense",
    4: "_transfer"
}
function_switcher = {
    "add_account": add_account,
    "delete_account": delete_directory,
    "add_income": add_income,
    "delete_income": delete_directory,
    "add_expense": add_expense,
    "delete_expense": delete_directory,
    "add_transfer": add_transfer,
    "delete_transfer": delete_directory,
}

# Start of program
main()
