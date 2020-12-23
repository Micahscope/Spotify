from APIs import Venmo as vm
import Local_Data as loc

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


def monthly_update(members, debt_count):

    # This should be redundant, but ensures
    # the program does not update incorrectly.
    # If no members owe money, do not attempt
    # to send requests (on which there is further
    # protection) or save any to a file.
    # However, we still want to increment each
    # member's debt. In this case, all members
    # have prepaid for the subscription.
    if debt_count == 0:
        loc.write_debt_file(members)
        return None

    # Otherwise, at least 1 member owes
    # money. Initialize the (my) Venmo
    # client account, request money from
    # each debtor, and save the payment
    # note and amount in a local file.
    else:
        # Initialize Venmo client.
        client = vm.initialize_venmo_api()

        # Request money from debtors, and
        # store the transaction information.
        pending_notes, pending_amounts = vm.collect_debts(client, members)

        # Append the transactions to a local file.
        loc.write_transaction_file(pending_notes, pending_amounts, 'a')

        # Update the debts in the local file.
        loc.write_debt_file(members)

        return client
