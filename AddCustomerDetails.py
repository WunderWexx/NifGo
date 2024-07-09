# This is where the reports are modified to include customer details

from ELT import Extract
import Utilities as util
from os import listdir
from os.path import isfile, join

customerdata_df = Extract().customer_data()
customerdata_df = customerdata_df.rename(columns={0:'sample_id',1:'initials',2:'lastname',3:'birthdate',4:'status'})
customerdata_df = customerdata_df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
customerdata_df.sort_values(by='sample_id', ascending=True, inplace=True)
customerdata_df.reset_index(inplace=True, drop=True)

util.printEntire(customerdata_df)

path = 'Output\Reports'
reports = [file for file in listdir(path) if isfile(join(path, file))]

non_filled_files = []
for file in reports:
    if file.split('_')[1] .split('.')[0] in list(customerdata_df['sample_id']):
        print(file)
    else:
        non_filled_files.append(file)

print(non_filled_files)