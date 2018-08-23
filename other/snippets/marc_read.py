from pymarc import MARCReader
with open('c:/rvp/data/Kendra.dat', 'rb') as fh:
    reader = MARCReader(fh)
    for record in reader:
        print(record.title())
#
#
#
