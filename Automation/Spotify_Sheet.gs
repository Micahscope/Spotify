const SS = SpreadsheetApp.getActiveSheet();

const MONTHS_OWED_COLUMN = 5;
const MONEY_OWED_COLUMN = 6;
const MONTHS_PAID_COLUMN = 7;
const MONEY_PAID_COLUMN = 8;

const PEOPLE_START_ROW = 4;
const MONTHLY_COST = SS.getRange('A5').getValue();
const UPDATE_MONTHS_VALUE = 'C17';
const MEMBERS_CELL = 'A3';
const NUM_MEMBERS = SS.getRange(MEMBERS_CELL).getValue();
const LAST_PAYMENT_CELL = 'A7';


//RUNS EVERY 6th of EVERY MONTH. IDRK WHAT TIME I DONT REMEMBER
function monthlyUpdate() {
  incrementCell(LAST_PAYMENT_CELL);

  //test this
  //SS.getRange(LAST_PAYMENT_CELL).setValue(SS.getRange(LAST_PAYMENT_CELL).getValue() % 12);

  updateOwedMonths();
}

//LOOPS THROUGH ALL MONTHLY MEMBERS TO UPDATE MONTHLY DUES
function updateOwedMonths() {
  var row = PEOPLE_START_ROW;

  while (row < NUM_MEMBERS + PEOPLE_START_ROW - 2) {
    updateRow(row++, -MONTHLY_COST);
  }

  //temporary: for testing of py script
    row = 9;

    while (row < 13) {
      updateRow(row++, -MONTHLY_COST);
    }
}

//UPDATES THE MEMBERS' ROWS ON THEIR PAYMENT INFO
function updateRow(row, payment) {
  var owed = SS.getRange(row, MONEY_OWED_COLUMN).getValue();
  var oldPayment = SS.getRange(row, MONEY_PAID_COLUMN).getValue();
  var monthsPrepaid = SS.getRange(row, MONTHS_PAID_COLUMN).getValue();
  var monthsOwed = SS.getRange(row, MONTHS_OWED_COLUMN).getValue();
  //row: landis
  //payment: 30
  //owed: 0
  //oP:0
  //mP: 0
  //mO: 0

  if (payment >= owed) {
    payment -= owed;
    owed = 0;
    monthsOwed = 0;

  } else {
    owed -= payment;
    payment = 0;
    monthsOwed = owed / MONTHLY_COST;
  }
  payment += oldPayment;

  if (payment != 0 || owed != 0) {


    if (payment == owed) {
      payment = owed = 0;
      monthsPrepaid = 0;
      monthsOwed = 0;
    }
    else if (payment > owed) {
      payment -= owed;
      owed = 0;
      monthsPrepaid = payment / MONTHLY_COST;
      monthsOwed = 0;
    }
    else {
      owed -= payment;
      payment = 0;
      monthsPrepaid = 0;
      monthsOwed = owed / MONTHLY_COST;
    }
  }

  SS.getRange(row, MONEY_PAID_COLUMN).setValue(payment);
  SS.getRange(row, MONEY_OWED_COLUMN).setValue(owed);
  SS.getRange(row, MONTHS_PAID_COLUMN).setValue(monthsPrepaid);
  SS.getRange(row, MONTHS_OWED_COLUMN).setValue(monthsOwed);

}

function incrementCell(cell) {
  SS.getRange(cell).setValue(SS.getRange(cell).getValue() + 1);
}

/***************
BUTTON FUNCTIONS
***************/


//DO I NEED THESE? MAYBE KEEP THESE TO ENSURE I DON'T MANUALLY EDIT VALUES??


//
function increment() {
 SS.getRange(UPDATE_MONTHS_VALUE).setValue(SS.getRange(UPDATE_MONTHS_VALUE).getValue() + 1);
}

function decrement() {
 SS.getRange(UPDATE_MONTHS_VALUE).setValue(SS.getRange(UPDATE_MONTHS_VALUE).getValue() - 1);
}

function reset() {
  SS.getRange(UPDATE_MONTHS_VALUE).setValue(0);
}

function update() {
  var row = SS.getActiveCell().getRow();

  if (row > NUM_MEMBERS + 2 || row < 4)
    // temporary
    if (row > 8 && row < 13)
        updateRow(row, SS.getRange(UPDATE_MONTHS_VALUE).getValue());
    return;
  
  updateRow(row, SS.getRange(UPDATE_MONTHS_VALUE).getValue());

}
