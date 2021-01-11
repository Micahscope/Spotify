// Save the spreadsheet for easy access
const SS = SpreadsheetApp.getActiveSheet();

// Store relevant columns as variables as to
// not hardcode them. Corresponds to columns
// e, f, g, and h, respectively.
const MONTHS_OWED_COLUMN = 5;
const MONEY_OWED_COLUMN = 6;
const MONTHS_PAID_COLUMN = 7;
const MONEY_PAID_COLUMN = 8;

// Store the first row that stores information for
// the members. This is row 4 in the spreadsheet.
const PEOPLE_START_ROW = 4;

// Reads the monthly cost from the spreadsheet.
// Here, we hardcode the cell (A5) because we do not
// need any information about the cell besides its value.
// The value is found by: total cost / number of members.
const MONTHLY_COST = SS.getRange('A5').getValue();

// This cell will hold a value to manually update members'
// debts and prepays. This is how the spreadsheet was
// originally used. Now, it is currently only necessary
// (AS OF 1/10/21) to update when members prepay for the service.
const UPDATE_MONTHS_VALUE = 'C17';

// This cell's value is the number of members on
// the Spotify plan. It is calculated by determining
// the number of columns used below the first starting
// member information column.
const NUM_MEMBERS = SS.getRange('A3').getValue();

// This cell holds the month integer (1-12) of
// the most recent payment cycle that has occurred.
const LAST_PAYMENT_CELL = 'A7';


// This function runs on the 6th of every month,
// coinciding when the Spotify payment is due.
// (Occurs between 8 and 9 am, using Google Apps Script
// triggers - https://script.google.com/home/triggers).
// It causes an update of all values that change each month.
function monthlyUpdate() {

  // Increment the month payment cell.
  incrementCell(LAST_PAYMENT_CELL);

  // test this
  // Ensure that the cell is between 1 and 12.
  // SS.getRange(LAST_PAYMENT_CELL).setValue(SS.getRange(LAST_PAYMENT_CELL).getValue() % 12);

  // Updates each member's new debts or prepays.
  updateOwedMonths();
}


// This function loops through each member listed in
// the spreadsheet, and calls updateRow for each one.
function updateOwedMonths() {

  // Set the starting row.
  var row = PEOPLE_START_ROW;

  // Increment the row until all members have been updated.
  while (row < NUM_MEMBERS + PEOPLE_START_ROW - 2) {
    // Update each member's row of data.
    updateRow(row++, -MONTHLY_COST);
  }

  // temporary: for testing of py script
  row = 9;

  while (row < 13) {
    updateRow(row++, -MONTHLY_COST);
  }
  // end temporary part.
}


// The majority of the work is done by this function.
// It increments each member's balances by the payment parameter.
// Because there are columns for debts and prepayments, it
// must ensure that either one or the other is 0, while
// correcting the value of the other.

//@param row: the member's row that is being edited.
//@param payment: the amount payment due. If this is
// called by the monthly cycle, the payment is the
// monthly cost, negated; if manually called, it is
// whatever value resides in the UPDATE_MONTHS_VALUE cell.
function updateRow(row, payment) {
  // Read all of the current information:
  // owed -> the money previously owed
  // oldPayment -> the money previously prepaid.
  // At least one of these values is expected to be 0.
  // ...
  var owed = SS.getRange(row, MONEY_OWED_COLUMN).getValue();
  var oldPayment = SS.getRange(row, MONEY_PAID_COLUMN).getValue();
  var monthsPrepaid = SS.getRange(row, MONTHS_PAID_COLUMN).getValue();
  var monthsOwed = SS.getRange(row, MONTHS_OWED_COLUMN).getValue();

  // If the person pays more than they currently owe,
  if (payment >= owed) {

    // There may be an abundance in payment,
    // which will be dealt with soon.
    payment -= owed;

    // The person owes nothing.
    owed = 0;
    monthsOwed = 0;

  // Otherwise, the person pays less than currently owed,
  // or, they are charged more money.
  } else {

    // Subtract the payment from what is already owed.
    // Note that being charged the monthly cost is
    // a negative payment, leading to an increase in
    // what the person owes.
    owed -= payment;

    // There will be no excess payment.
    payment = 0;

    // Update the months owed variable with
    // the new money the person owes.
    monthsOwed = owed / MONTHLY_COST;
  }

  // Add the excess payment to any
  // currently prepaid surplus.
  // (One of these is usually 0, BUT
  // if someone has prepaid, but pays
  // more, this is necessary).
  payment += oldPayment;

  // If the member still has excess money
  // that they paid, or they owe an excess
  // of money, we still must update some values.
  // This set of code ensures that at least
  // one of (debts, prepayments) are 0.
  if (payment != 0 || owed != 0) {

    // If the person's excess money matches what
    // they previously owed, they have paid exactly
    // what is due, with no debts or prepayments.
    if (payment == owed) {

      // Set all columns to 0.
      // No money currently stored or owed.
      payment = owed = 0;
      monthsPrepaid = 0;
      monthsOwed = 0;
    }

    // Otherwise, if the person's excess money
    // is more than what they owed previously,
    // they should no longer owe money, and now
    // have prepaid for the service.
    else if (payment > owed) {

      // Reduce the payment surplus by what is
      // still owed.
      payment -= owed;

      // Set the money owed and months owed to 0.
      owed = 0;
      monthsOwed = 0;

      // Set the months prepaid to the money prepaid
      // (payment) divided by the monthly cost.
      monthsPrepaid = payment / MONTHLY_COST;

    }
    // Otherwise, the person has made a payment,
    // or has been charged, and continues to owe
    // money. They should have no excess money here.
    else {

      // Reduce the money owed by the new payment.
      // Again, if the payment is negative (charged),
      // this raises the money owed.
      owed -= payment;

      // Set the money and months prepaid to 0.
      payment = 0;
      monthsPrepaid = 0;

      // Set the months owed to the new money owed
      // divided by the monthly cost.
      monthsOwed = owed / MONTHLY_COST;
    }
  }

  // Set each of the new values in their respective columns.
  SS.getRange(row, MONEY_PAID_COLUMN).setValue(payment);
  SS.getRange(row, MONEY_OWED_COLUMN).setValue(owed);
  SS.getRange(row, MONTHS_PAID_COLUMN).setValue(monthsPrepaid);
  SS.getRange(row, MONTHS_OWED_COLUMN).setValue(monthsOwed);

}


// This function increments any cell that is inputted's value
// by 1.
// @param cell - the cell to be incremented.
function incrementCell(cell) {
  SS.getRange(cell).setValue(SS.getRange(cell).getValue() + 1);
}


/***************
BUTTON FUNCTIONS
***************/

// This function resets the update months cell.
// This is used in the reset button on the spreadsheet.
function reset() {
  SS.getRange(UPDATE_MONTHS_VALUE).setValue(0);
}

// This function updates the selected member's
// row with the inputted payment given by the
// update months cell.
function update() {

  // Get the row that is currently highlighted by the mouse.
  var row = SS.getActiveCell().getRow();

  // If the row number is not one that has member data, return.
  if (row > NUM_MEMBERS + 2 || row < PEOPLE_START_ROW)
    // temporary
    if (row > 8 && row < 13)
        updateRow(row, SS.getRange(UPDATE_MONTHS_VALUE).getValue());
    // end temp
    return;

  // Otherwise, update the row with the new payment value.
  updateRow(row, SS.getRange(UPDATE_MONTHS_VALUE).getValue());

}
