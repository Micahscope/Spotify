import venmo_api as vm
from emoji import emojize, demojize
from Constants import USER_IDS, NAMES, USERNAMES
import datetime
import Local_Data as loc

'''
Accesses (my) client Venmo account credentials.
'''


def initialize_venmo_api():
    # Sets access token to my Venmo account.
    # @todo Add encryption for account protection.
    access_token = vm.Client.get_access_token("Micahscope", "Microcarrot8",
                                              "70081150-12F5-8K84-19G2-5EK87U192AH2")
    # Initializes my Venmo account.
    client = vm.Client(access_token)

    if client is None:
        loc.update_error_log_file("Unable to access Venmo servers.")

    return client


'''
Log out of the Venmo account.
Will require 2FA to sign in again.
'''


def logout(client):
    client.logout()


'''
Request a payment, using the client Venmo
account, from the recipient, a Member object,
which stores the name, Venmo account ID, and
the amount of money they owe.
'''


def request_payment(client, recipient):
    # Ensure that each recognized recipient's ID
    # matches their first name and username.
    # @todo throw exception

    if not test_user_ids(client):
        error_message = "User data in Constants.py does not match data from Venmo server."
        error_message += " A Venmo request is needed but has not been completed."
        error_message += " Likely an user's username has changed."

        loc.update_error_log_file(error_message)
        return None, None

    # Use datetime to get the current month and year.
    # This is used in the note to create a unique note
    # for each transaction.
    now = datetime.datetime.now()
    month = now.strftime("%B %Y")

    # Customize the note, and add the recipient's name
    # to separate each member's transaction "IDs".
    note = "Automatic Request for " + recipient.name + " " + emojize(":musical_note: ") + month + "."

    # Requests a payment through the Venmo API,
    # using the defined note, the amount owed,
    # and the recipient's Venmo account ID.
    # These transactions are set to private.
    client.payment.request_money(amount=recipient.money_owed,
                                 note=note,
                                 target_user_id=recipient.id,
                                 callback=None,
                                 privacy_setting=vm.PaymentPrivacy.PRIVATE)

    # Write the request to the log file.
    loc.update_log_file("Request sent with note: " + note)

    # The note and amount owed by the recipient
    # are returned, to store in a file.
    return note, recipient.money_owed


'''
This function utilizes the request_payment function
above. It passes in a list of Member objects to
send Venmo requests. Only members who owe money
are sent a request. The request note and amount
are returned to store and save in a file.
'''


def collect_debts(client, member_list):
    # Initialize variables.
    payment_notes = []
    payment_amounts = []

    # Loop through each member in the inputted list.
    for member in member_list:
        # Request a payment if the member owes money
        # and save the payment request in a list.
        if member.money_owed > 0:
            note, amount = request_payment(client, member)
            payment_notes.append(note)
            payment_amounts.append(amount)

    return payment_notes, payment_amounts


'''
This function reads the client (my) Venmo
account's list of charge payments. This
includes completed, pending, and cancelled
requests. We return the note, amount, and
status of each request that belongs to a
recognized member of this program.
'''


def read_previous_charges(client):
    # Initialize list variables.
    note_list = []
    amount_list = []
    status_list = []

    # Loop through all payments that the client
    # Venmo account has charged others for.
    for payment in (client.payment.get_charge_payments()):
        # Any request that corresponds to a recognized
        # member is stored.
        if USER_IDS.count(int(payment.target.id)) > 0:
            note_list.append(demojize(payment.note))
            amount_list.append(payment.amount)
            status_list.append(payment.status)

    return note_list, amount_list, status_list


'''
This function uses the Venmo client
to ensure the saved constants are correct.
It runs through each first name, username,
and user ID of each recognized Venmo member.
'''


def test_user_ids(client):
    # Loop through the number of names.
    # Also number of IDs and usernames.
    for i in range(len(NAMES)):
        # Use Venmo client to get the User object.
        user = client.user.get_user(user_id=USER_IDS[i])
        # Ensure that both username and first name
        # match what we expect them to be.
        if user.username != USERNAMES[i]:
            return False
        if user.first_name != NAMES[i]:
            return False

    return True


"""
This function cancels a payment request made
by the program. It detects the payment based
on its note and amount, and ensures that it
is a pending request. If the request is cancelled,
the function returns True. Otherwise, it returns false.
"""


def cancel_payment_request(client, payment_note, payment_amount):
    # Loop through all payments that the client
    # Venmo account has charged others for.
    for payment in (client.payment.get_charge_payments()):
        # Ensure the online payment object matches the
        # parameter's note, amount, and is a pending request.
        # If so, cancel and return true.
        if payment.note == payment_note:
            if payment.amount == payment_amount:
                if payment.status == vm.PaymentStatus.PENDING:
                    client.payment.cancel_payment(payment=payment)
                    return True

    return False
