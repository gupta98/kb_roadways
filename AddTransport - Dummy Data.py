import sys
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import sqlite3
import json
import random
import string

import essential_functions as ef

database_path = ".\\__Database\\"
database_name = "kb_roadways.db"
database = database_path + database_name
db_con = sqlite3.connect(database)
cursor = db_con.cursor()


cursor.execute("SELECT * FROM COMPANIES")
companies = cursor.fetchall()
companies = [[entry[0], entry[1]] for entry in companies]

cursor.execute("SELECT * FROM VEHICLE_OWNERS")
vehicle_owners = cursor.fetchall()
vehicle_owners = [[entry[0], entry[1]] for entry in vehicle_owners]

cursor.execute("SELECT * FROM CARS")
cars = cursor.fetchall()
cars_and_vehicle_owners = {}
for entry in cars:
    cars_and_vehicle_owners[entry[2]] = cars_and_vehicle_owners.get(entry[2], []) + [entry[0]]
cars = {entry[0]:entry[1] for entry in cars}

cursor.execute("SELECT * FROM DRIVERS")
drivers = cursor.fetchall()
drivers = [[-1, '']] + [[entry[0], entry[1]] for entry in drivers]

days = [i for i in range(1, 29)]
months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
months = [[key, months[key]] for key in months]
years = [2019, 2020, 2021, 2022, 2023]

districts = [
    "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri",
    "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Medinipur",
    "Paschim Burdwan", "Purba Burdwan", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur", "Sunderban",
    "Ichhemati", "Ranaghat", "Bishnupur", "Jangipur", "Behrampur"
]
districts.sort(key=lambda state: state.upper())

for _ in range(200):

    source_company = random.choice(companies)
    source_id = source_company[0]
    source = source_company[1]
    destination_company = random.choice(companies)
    while destination_company == source_company:
        destination_company = random.choice(companies)
    destination_id = destination_company[0]
    destination = destination_company[1]
    
    # today = int(f"{dt.now().year}{str(dt.now().month).zfill(2)}{str(dt.now().day).zfill(2)}")
    today = date.today()
    day_ago = today - timedelta(days=5)
    day_ago = int(f"{day_ago.year}{str(day_ago.month).zfill(2)}{str(day_ago.day).zfill(2)}")
    while True:
        year = random.choice(years)
        day = random.choice(days)
        month_item = random.choice(months)
        month = month_item[0]
        month_str = month_item[1]
        full_date = int(f"{year}{str(month).zfill(2)}{str(day).zfill(2)}")
        if full_date < day_ago:
            full_date_str = f"{str(day).zfill(2)}-{month_str}-{year}"
            break
    
    vehicle_owner_item = random.choice(vehicle_owners)
    vehicle_owner_id = vehicle_owner_item[0]
    vehicle_owner_name = vehicle_owner_item[1]
    
    car_id = random.choice(cars_and_vehicle_owners.get(vehicle_owner_id, [-1]))
    car_no = cars.get(car_id, '')
    
    driver_item = random.choice(drivers)
    driver_id = driver_item[0]
    driver_name = driver_item[1]
    
    no_of_debits = random.randint(1, 5)
    debitList = []
    debit_total = 0
    for _ in range(no_of_debits):
        key = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 15)))
        value = float(f"{random.randint(0, 10000)}.{random.randint(0, 99)}")
        debitList.append([_+1, key, value])
        debit_total += value
    
    creditList = []
    credit_total = 0
    counter = 1
    while credit_total < debit_total:
        key = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 15)))
        value = float(f"{random.randint(0, 10000)}.{random.randint(0, 99)}")
        creditList.append([counter, key, value])
        credit_total += value
        counter += 1
    
    contract_amount_with_vehicle_owner = credit_total + random.randint(1, 10000)
    profit = float(f"{random.randint(1000, 5000)}.{random.randint(0, 99)}")
    contract_amount_with_company = contract_amount_with_vehicle_owner + profit
    
    goods_unit = random.choice(["Piece", "Litre", "Ton"])
    no_of_unit = random.randint(1, 50)
    while not contract_amount_with_company // no_of_unit:
        no_of_unit = random.randint(1, 50)
    cost_per_unit = contract_amount_with_company / no_of_unit
    total_cost = no_of_unit * cost_per_unit
    
    bill_generation = random.randint(0, 1)
    bill_generated = 0
    bill_generated_year = 0
    bill_generated_day = 0
    bill_generated_month = 0
    bill_generated_full_date = 0
    bill_generated_full_date_str = '-'
    
    source_district = random.choice(districts)
    destination_district = random.choice(districts)

    insert_query = f"""
        INSERT INTO TRANSPORTS(
            SOURCE_ID, SOURCE, DESTINATION_ID, DESTINATION, DATE_STRING, FULL_DATE, YEAR, MONTH, 
            DAY, VEHICLE_OWNER_ID, VEHICLE_OWNER_NAME, CAR_ID, CAR_NO, DRIVER_ID, DRIVER_NAME, 
            CONTRACT_AMOUNT_WITH_COMPANY, CONTRACT_AMOUNT_WITH_VEHICLE_OWNER, PROFIT, GOODS_UNIT, NO_OF_UNIT, 
            COST_PER_UNIT, TOTAL_COST, DEBITS, CREDITS, DEBIT_AMOUNT, CREDIT_AMOUNT, NOTES, BILL_GENERATION, 
            BILL_GENERATED, SOURCE_ROAD, SOURCE_CITY, SOURCE_DISTRICT, SOURCE_PIN, DESTINATION_ROAD, 
            DESTINATION_CITY, DESTINATION_DISTRICT, DESTINATION_PIN, INVOICE_NO, LR_NO, 
            BILL_GENERATED_DATE_STRING, BILL_GENERATED_FULL_DATE, BILL_GENERATED_YEAR, BILL_GENERATED_MONTH, 
            BILL_GENERATED_DAY
        )
        VALUES(
            {source_id},
            '{source}',
            {destination_id},
            '{destination}',
            '{full_date_str}',
            {full_date},
            {year},
            {month},
            {day},
            {vehicle_owner_id},
            '{vehicle_owner_name}',
            {car_id},
            '{car_no}',
            {driver_id},
            '{driver_name}',
            {contract_amount_with_company},
            {contract_amount_with_vehicle_owner},
            {profit},
            '{goods_unit}',
            {no_of_unit},
            {cost_per_unit},
            {total_cost},
            '{json.dumps(debitList)}',
            '{json.dumps(creditList)}',
            {debit_total},
            {credit_total},
            '{''.join(random.choices(string.ascii_letters, k=random.randint(10, 100)))}',
            {bill_generation},
            {bill_generated},
            '{''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))}',
            '{''.join(random.choices(string.ascii_letters, k=random.randint(5, 15)))}',
            '{source_district}',
            '{random.randint(111111, 999999)}',
            '{''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))}',
            '{''.join(random.choices(string.ascii_letters, k=random.randint(5, 15)))}',
            '{destination_district}',
            '{random.randint(111111, 999999)}',
            '{''.join(random.choices(string.ascii_letters, k=random.randint(10, 20)))}',
            'LR-{''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))}',
            '{bill_generated_full_date_str}',
            {bill_generated_full_date},
            {bill_generated_year},
            {bill_generated_month},
            {bill_generated_day}
        );
    """
    cursor.execute(insert_query)
    db_con.commit()