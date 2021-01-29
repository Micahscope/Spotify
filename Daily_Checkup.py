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
        loc.update_log_file("All transactions completed.")
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
        loc.write_transaction_files(pending_note_list, pending_amount_list, 'w')

        # Loop through each completed transaction
        # and the list of recognized user's names.
        for i in range(len(completed_note_list)):

            loc.update_log_file("Payment received with note: " + completed_note_list[i])

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

    else:
        loc.update_log_file("No requests completed at this time.")

    return


'''
MONTHLY UPDATE:
    - Called by daily checkup, once each month.
      Occurs when our online information has
      automatically been updated through Google
      Apps Script code, but our local data has not.
    - Sends a Venmo request to all members with a
      positive debt. The message and amount are saved
      in a local file, as "keys" to access this
      payment later.
    - Updates the local data to reflect the online
      data. In essence, we increase each person's
      debt by the service's monthly cost.
'''


def monthly_update(members_list_gs, debt_count):

    # This should be redundant, but ensures
    # the program does not update incorrectly.
    # If no members owe money, do not attempt
    # to send requests (on which there is further
    # protection) or save any to a file.
    # However, we still want to increment each
    # member's debt. In this case, all members
    # have prepaid for the subscription.
    if debt_count == 0:
        # @todo ensure this works. was write_...
        loc.update_debt_file(members_list_gs)
        return None

    # Otherwise, at least 1 member owes
    # money. Initialize the (my) Venmo
    # client account, request money from
    # each debtor, and save the payment
    # note and amount in a local file.
    else:
        # Initialize Venmo client.
        client = vm.initialize_venmo_api()

        # Initialize list variables for the currently
        # awaiting transactions.
        previous_notes = []
        previous_amounts = []

        # @todo ensure this works
        # Read all transactions that are still unpaid.
        previous_notes, previous_amounts, loc.read_transaction_file()

        # Cancel all unpaid requests.
        # We do this so there aren't repeated
        # requests if someone does not fulfill their
        # payment from the previous month.
        for i in range(len(previous_notes)):
            # If a request is not able to be cancelled, write an error to the log file.
            if not vm.cancel_payment_request(client, previous_notes[i], previous_amounts[i]):
                error_message = "Old transaction with note ''" + previous_notes[i]
                error_message += "'' was unable to be removed. A double charge has occurred."
                loc.update_error_log_file(error_message)

        # Request money from debtors, and
        # store the transaction information.
        pending_notes, pending_amounts = vm.collect_debts(client, members_list_gs)

        # Append the transactions to a local file.
        loc.write_transaction_files(pending_notes, pending_amounts, 'a')

        # Update the debts in the local file.
        # @todo ensure this works. was write_...
        loc.update_debt_file(members_list_gs)

        return client


if __name__ == '__main__':
    main()
