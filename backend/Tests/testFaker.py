from faker import Faker
import csv
data =Faker()
header  =   ["name","job"]
users   =   [[data.name(),data.job()]   for x in range(10)]
print(users)
with open("Data/csvfiles/addUser.csv","w",encoding="UTF-8",newline="") as csv_file:
    csv_writer=csv.writer(csv_file)
    csv_writer.writerow(header)
    csv_writer.writerows(users)
    