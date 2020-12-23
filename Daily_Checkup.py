from Monthly_Update import monthly_update
import Local_Data as loc
from APIs import Venmo as vm, Google_Sheets as gs
from venmo_api import PaymentStatus
from Constants import NAMES

'''
DAILY CHECK:
    - Read Google Sheets member information.
    - if debts don't match local copy,
      we know the GS data has updated and
      a new month payment is required:
        * RUN MONTHLY_UPDATE
        --> requests money from indebted members
        --> saves payment request information locally
        --> saves online debts to a local copy
        
    Whether or not the process above has run, we expect
    that our local and online information about each member's
    debt are consistent. Now,
        
    - Check pending transactions from our local file:
        * Read a list of all relevant :
            - remove from transaction list and rewrite it
            - update DEBT local copy
            - update spreadsheet
'''


def main():
    # Read the data from the Google Sheets spreadsheet.
    data = gs.read_sheet()

    # Initialize the Venmo client as None.
    client = None

    # Parse the data into a list of family plan
    # members and their debts.
    member_list_gs, debt_count = gs.read_members(data)

    # Read the locally stored data about the
    # members and debts.
    member_list_loc = loc.get_members()

    # Loop through each member. If any have
    # a difference in debt between the GS
    # and local data, call monthly update.
    # Note that this occurs only after the
    # initial Spotify payment on the 6th.
    # @todo if anything doesnt work, its this
    for i in range(len(member_list_gs)):
        if not member_list_loc[i].equals(member_list_gs[i]):
            client = monthly_update(member_list_gs, debt_count)
            break

    '''
    Now, check for any completed payments.
    This code will run daily through Task
    Scheduler. The above code will only call
    the monthly update function once per month.
    Here, it is guaranteed that the local debt
    data is equal to the online debt data.
    '''

    # Read the pending transactions list.
    pending_note_list, pending_amount_list = loc.read_transaction_file()

    # If no transactions are awaiting payment,
    # halt the program.
    if len(pending_note_list) == 0:
        print("Nothing to do")
        return

    # Initialize the client if it had
    # not been done so yet.
    if client is None:
        client = vm.initialize_venmo_api()

    # Read the list of relevant charge payments
    # from Venmo.
    venmo_note_list, venmo_amount_list, venmo_status_list = vm.read_previous_charges(client)

    # Initializing variables
    completed_note_list = []
    completed_amount_list = []
    offset = 0

    # Loop through each pending transaction from the local
    # file and the transactions found from Venmo, searching
    # for any matches. Any transaction recognized by Venmo
    # and the local file that has been settled will be removed
    # from the pending transactions list and added to a
    # completed transactions list.
    for i in range(len(venmo_note_list)):
        for j in range(len(pending_note_list)):
            # Match is found.
            if venmo_note_list[i] == pending_note_list[j - offset]:
                # The matched transaction has been completed.
                if venmo_status_list[i] == PaymentStatus.SETTLED:
                    # Move the transaction from pending list to completed list.
                    completed_note_list.append(pending_note_list[j - offset])
                    completed_amount_list.append(pending_amount_list[j - offset])
                    pending_note_list.remove(pending_note_list[j - offset])
                    pending_amount_list.remove(pending_amount_list[j - offset])

                    # Increment list index offset counter.
                    offset += 1

    # If there are any completed transactions,
    # update the local transaction file to no longer
    # store this transaction. Also, write to the debt
    # file any user who has zeroed their balance.
    # Finally, push the new debt information to
    # the Google Sheets spreadsheet.
    if len(completed_amount_list) != 0:
        # Update pending transaction file.
        loc.write_transaction_file(pending_note_list, pending_amount_list, 'w')

        # Loop through each completed transaction
        # and the list of recognized user's names.
        for i in range(len(completed_note_list)):
            for name in NAMES:
                # If the transaction note contains the user's name,
                if completed_note_list[i].count(name) > 0:
                    # Loop through the members to find the user.
                    for member in member_list_gs:
                        # When user is found,
                        if member.name == name:
                            # Decrease their debt by the transaction
                            # amount from Venmo.
                            member.money_owed -= completed_amount_list[i]

        # Write the new debt information to
        # the local debt file.
        loc.update_debt_file(member_list_gs)

        # Format the data for a spreadsheet.
        data = loc.format_data_for_gs(member_list_gs)

        # Push the formatted data to Google Sheets.
        gs.write_sheet(data)

    return


if __name__ == '__main__':
    main()
