import Constants as c
from Member import Member
from emoji import demojize
from sys import stderr
import datetime

'''
This function writes all transactions from
the list parameters to the file that stores the
pending transactions.
Note that it can be called with append mode or
write mode.
'''


def write_transaction_file(note_list, amount_list, mode, file):
    # Open transaction file in either write
    # or append mode.
    with open(file, mode) as wf:

        # If writing to the history file, add a timestamp.
        if file == c.TRANSACTION_HIST_FILE:
            # Use datetime to get the current time and date.
            # This is used in the note to create a unique note
            # for each history log note.
            time = getTime()

            # Write the note
            wf.write(time + " :\n")

        # Loop through items in the transaction lists.
        for i in range(len(note_list)):
            # Write each transaction.
            # Note and amount, tab delimited.
            wf.write(demojize(note_list[i]) + "\t" + str(amount_list[i]) + "\n")
    return


"""

"""


def write_transaction_files(note_list, amount_list, mode):
    write_transaction_file(note_list, amount_list, mode, c.TRANSACTION_FILE)
    write_transaction_file(note_list, amount_list, 'a', c.TRANSACTION_HIST_FILE)


'''
This function reads all transactions
stored in the local file. It parses
them into a list of their notes and
the amount requested, and returns them.
'''


def read_transaction_file():
    # Initialize lists.
    note_list = []
    amount_list = []

    # Open transaction file in read mode.
    with open(c.TRANSACTION_FILE, 'r') as rf:
        # Loop through each line
        for line in rf:
            # Separate each line by
            # tab delimiter.
            data = line.strip().split("\t")

            # Store the separated data to a
            # note list and an amount list.
            note_list.append(data[0])
            amount_list.append(float(data[1]))

    return note_list, amount_list


"""
This reads the debt file and parses its
contents into a Member object's data for
each line of the file. Then, it compiles
a list of the Members and returns it.
"""


def get_members():
    # Initialize list.
    members = []

    # Open debt file in read mode.
    with open(c.DEBT_FILE, 'r') as rf:
        # Loop through each line of the file.
        for line in rf:
            # Split each line into its components
            data = line.strip().split()
            # Create a member object from the
            # components and add it to a list.
            members.append(Member(data[0], float(data[1]), int(data[2])))

    return members


"""
This function writes a list of
members to the debt file. This
can either be the current debt
file or the backup, which stores
the current and all previous data
stored in this file.
"""


def write_debt_file(new_members, mode, file):

    # Open specified debt file in specified mode.
    with open(file, mode) as wf:
        # If writing to the history file, add a timestamp.
        if file == c.DEBT_HIST_FILE:

            # Use datetime to get the current time and date.
            # This is used in the note to create a unique note
            # for each history log note.
            time = getTime()

            # Write the note
            wf.write(time + " :\n")

        # Loop through all members in the list.
        for member in new_members:
            # Print each member's toString function
            # on each line.
            wf.write(member.toString() + "\n")
    return


"""
The function below updates the debt file with
a new member list to compare to the current list
stored by the file. Likewise, a history file is
written to that stores all current and prior data.
If the lists are not different, the function does
not waste time overwriting the same information.
"""


def update_debt_file(new_member_list):
    # Read the file into a list of Members.
    old_member_list = get_members()

    # Loop through the new list of Members.
    for i in range(len(new_member_list)):
        # If any differences are found,
        if not new_member_list[i].equals(old_member_list[i]):
            # Write the new Member list to the file.
            write_debt_file(new_member_list, 'w', c.DEBT_FILE)

            # Append the new Member list to the history file.
            write_debt_file(new_member_list, 'a', c.DEBT_HIST_FILE)
            return True

    return False


"""
This function formats a Member list to
be presented in a spreadsheet. It turns
the list into a 2D array of information.
"""


def format_data_for_gs(member_list):
    # Initialize outside array.
    spreadsheet = []

    # Loop through Members.
    for member in member_list:
        # Initialize inside array.
        member_data = []

        # Our inside array should follow this pattern:
        # [name, months owed, $ owed, months paid, $ paid]

        # Append the name to the inside array.
        member_data.append(member.name)

        debt = member.money_owed

        # If the Member owes money,
        if debt > 0:
            # Owed months is owed money / monthly cost.
            member_data.append(int(debt / c.MONTHLY_COST))
            member_data.append(debt)

            # Prepaid months and money are 0.
            member_data.append(0)
            member_data.append(0)
        # Otherwise, do the opposite:
        else:
            # Owed months and money are 0.
            member_data.append(0)
            member_data.append(0)

            # Prepaid months is owed money / monthly cost.
            member_data.append(abs(int(debt / c.MONTHLY_COST)))
            member_data.append(abs(debt))

        # Add the inside array to the outside array
        spreadsheet.append(member_data)

    return spreadsheet


"""
This function writes information to a log file.
It writes the given message formatted with the
date and time of the write.
"""


def update_log_file(message):
    # Use datetime to get the current time and date.
    # This is used in the note to create a unique note
    # for each log note.
    time = getTime()

    # Open log file in append mode.
    with open(c.DATA_LOG_FILE, 'a') as wf:
        # Write the note to the log file.
        wf.write("\n" + time + " :\n" + demojize(message) + "\n")
    return


"""
This function writes information to an error log file.
It writes the given message formatted with the date
and time of the write.
"""


def update_error_log_file(message):
    # Use datetime to get the current month and year.
    # This is used in the note to create a unique note
    # for each error log note.
    time = getTime()

    # Defines the note that will be written to the log
    # and written in console as an error.
    error_note = time + " :\n" + message + "\n\n"

    # Open error log file in append mode.
    with open(c.ERROR_LOG_FILE, 'a') as wf:
        # Write the error to the error log file.
        wf.write(error_note)

    # Write the error to the console log.
    stderr.write(error_note)

    return


"""
This function returns the formatted
time and date necessary for any logging
information. This data will be used in
the log files, and anytime one of the
data files are changed, their backup files
containing the history will be added to, with
this datetime stamp.
Formatting: MM/DD/YY HH:MM:SS
"""


def getTime():
    # Gets the current datetime data
    now = datetime.datetime.now()

    # Formats the data as specified
    # by the function.
    time = now.strftime("%x %X")

    return time
