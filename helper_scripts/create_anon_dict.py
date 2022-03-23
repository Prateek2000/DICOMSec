import csv

mydict = {}

with open("reduced_deidentification_table.csv", mode="r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    for rows in reader:
        mydict[rows[0]] = rows[2]

for (k, v) in mydict.items():
    print('"', k, '"', ":", '"', v, '",')
