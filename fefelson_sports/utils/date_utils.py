from datetime import date, datetime, timedelta

today = date.today()
twoWeeks = today - timedelta(14)
oneMonth = today - timedelta(31)
twoMonths = today - timedelta(62)

compDates = {
    "2Weeks": twoWeeks,
    "1Month": oneMonth,
    "2Months": twoMonths
}

def calculate_start_date(label):
    return compDates.get(label)