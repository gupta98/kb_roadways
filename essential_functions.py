import os
import pandas as pd
from datetime import datetime as dt
from math import ceil


def nameGenerator(prefix="", divider="", suffix=""):
    name = str(dt.now())
    name = name.replace("-", divider)
    name = name.replace(" ", divider)
    name = name.replace(":", divider)
    name = name.replace(".", divider)
    return prefix + name + suffix


def createExcelFile(filename, columns, index, sheet_name):
    df = pd.DataFrame(columns=columns)
    df.to_excel(filename, index=index, sheet_name=sheet_name)


def monthNoToMonthStr(month: int) -> str:
    month_to_str_dict = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }
    return month_to_str_dict[month]


def monthStrToMonthNo(month: str) -> int:
    month_to_no_dict = {
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'Jun' : 6,
        'Jul' : 7,
        'Aug' : 8,
        'Sep' : 9,
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12
    }
    return month_to_no_dict[month.title()]


def dateToInt(date: str) -> int:
    day, month, year = map(str, date.split('-'))
    month = str(monthStrToMonthNo(month))
    return int(f"{year.zfill(4)}{month.zfill(2)}{day.zfill(2)}")


def twoDigitsNumberToString(number: int) -> str:
    number = abs(number)

    if not number:
        return "ZERO"

    one_to_nineteen = ['', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN',
                      'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN', 'SEVENTEEN', 'EIGHTEEN', 'NINETEEN']
    twenty_to_ninety = ['', '', 'TWENTY', 'THIRTY', 'FORTY', 'FIFTY', 'SIXTY', 'SEVENTY', 'EIGHTY', 'NINETY']

    if number < 20:
        return one_to_nineteen[number]
    else:
        return f"{twenty_to_ninety[number // 10]} {one_to_nineteen[number % 10]}".strip()


def numberToText(number: int) -> str:
    number = str(abs(number))
    decimal = "00"
    if '.' in number:
        number = number.split('.')
        decimal = number[1].ljust(2, '0')
        number = number[0]

    number = number.zfill(7 * ceil(len(number) / 7))

    number_parts = []
    for i in range(0, len(number), 7):
        number_parts.append(number[i: i+7])

    result = ""
    final_print_flag = False
    for num in number_parts[:-1]:
        print_flag = False
        num = int(num)
        if num // 10 ** 5:
            print_flag = True
            final_print_flag = True
            result += twoDigitsNumberToString(num // 10 ** 5) + " LAKH "
            num = num % 10 ** 5
        if num // 10 ** 3:
            print_flag = True
            final_print_flag = True
            result += twoDigitsNumberToString(num // 10 ** 3) + " THOUSAND "
            num = num % 10 ** 3
        if num // 10 ** 2:
            print_flag = True
            final_print_flag = True
            result += twoDigitsNumberToString(num // 10 ** 2) + " HUNDRED "
            num = num % 10 ** 2
        if num:
            if print_flag:
                result += " AND "
            print_flag = True
            final_print_flag = True
            result += twoDigitsNumberToString(num)

        if print_flag:
            result += " CRORE "

    num = int(number_parts[-1])
    print_flag = False
    num = int(num)
    if num // 10 ** 5:
        print_flag = True
        result += twoDigitsNumberToString(num // 10 ** 5) + " LAKH "
        num = num % 10 ** 5
    if num // 10 ** 3:
        print_flag = True
        result += twoDigitsNumberToString(num // 10 ** 3) + " THOUSAND "
        num = num % 10 ** 3
    if num // 10 ** 2:
        print_flag = True
        result += twoDigitsNumberToString(num // 10 ** 2) + " HUNDRED "
        num = num % 10 ** 2
    if num:
        if print_flag or final_print_flag:
            result += " AND "
        result += twoDigitsNumberToString(num)

    if decimal:
        if result:
            result += " RUPEES AND "
        result += twoDigitsNumberToString(int(decimal)) + " PAISA "

    return " ".join(result.split())


def formatNumber(number):
    number = str(number)
    decimal = "00"
    if '.' in number:
        number = number.split('.')
        decimal = number[1].ljust(2, '0')
        number = number[0]
    last_digit = number[-1]
    number = number[:-1]
    number = number.zfill(2 * ceil(len(number) / 2))
    number_parts = []
    for i in range(0, len(number), 2):
        number_parts.append(number[i: i + 2])

    result = f"{','.join(number_parts)}{last_digit}.{decimal}".lstrip('0')
    if result.startswith('.'):
        result = "0" + result
    if result.endswith('.0'):
        result = result + "0"

    return result

if __name__ == '__main__':
    number = 35
    print(numberToText(number))
    print(formatNumber(number))