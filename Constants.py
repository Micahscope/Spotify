# These could be read from the spreadsheet, but eh.
NUM_MEMBERS = 6
TOTAL_COST = 15
MONTHLY_COST = TOTAL_COST / NUM_MEMBERS

# Venmo user IDs for members of plan.
MICAH_USER_ID = 2623650196881408414
ABBEY_USER_ID = 2778767613231104481
ELLIOT_USER_ID = 2813627916615680461
JACK_USER_ID = 2777990702301184896
LANDIS_USER_ID = 3077913033310208184

# Local storage files.
DEBT_FILE = "Local_Files/Member_List.txt"
DEBT_HIST_FILE = "Local_Files/Member_List_Backup.txt"
TRANSACTION_FILE = "Local_Files/Pending_Transactions.txt"
TRANSACTION_HIST_FILE = "Local_Files/Pending_Transactions_Backup.txt"
ERROR_LOG_FILE = "Local_Files/Error_Log.txt"
DATA_LOG_FILE = "Local_Files/Log.txt"

# THE ID and specified range to access our Google Sheet data.
SPOTIFY_SPREADSHEET_ID = '1kcdbFgniYEnsaoiGPkRPmQIR3hitxA7YbbYIR3DJg0M'
SPREADSHEET_RANGE = 'D4:H8'


# Lists of recognized users:
# their names, usernames, and IDs
NAMES = ['Abbey', 'Elliot', 'Jack', 'Landis']
USERNAMES = ['Abbey-Grosvenor', 'Elliot-Cooper-7', 'Jack-Myers-46', 'Land1s']
USER_IDS = [ABBEY_USER_ID, ELLIOT_USER_ID, JACK_USER_ID, LANDIS_USER_ID]
