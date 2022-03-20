import pandas as pd

df = pd.read_csv('tabula-part15-deidentification-table.csv', index_col='Tag')
df = df.drop(['Retd. (from PS3.6)', 'In Std. Comp. IOD (from PS3.3)'], axis=1)
print(df)

df.to_csv('reduced_deidentification_table.csv')







#tried basic csv library, it wasnt good enough. dict.pop was wiping the whole thing 
"""
fp = open('tabula-part15-deidentification-table.csv', newline='', encoding="utf-8")

reader = csv.DictReader(fp)

for row in reader:
    print(row)
    #row.pop('Retd. (from PS3.6)')
    #row.pop('In Std. Comp. IOD (from PS3.3)')

print("<=================================Rows Removed=================================>")

for row in reader:
    print(row)
"""