'''
am4ir_txt2db

read a utf-8 text file where column 1 is a pii, column 2 is it embargo-free date
and output:

(1) a new txt file that has normalized pii values in column 1 and column 2 has the same embargo free date (yyyy-mm-dd)
(2) file am4ir_create.sql with sql server code to insert the lines of file 1 into a new table named els_am


Example SQL to insert into rvp_test_sobekdb

use [rvp_test_sobekdb];

begin transaction;
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'els_am4ir') TRUNCATE TABLE els_am4ir
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'els_am4ir') drop table els_am4ir

create table els_am4ir(
pii nvarchar(100)
,embargo_free_date nvarchar(100)
CONSTRAINT pk_els_am4ir PRIMARY KEY(pii)
);

COMMIT transaction;

begin transaction;

BULK INSERT els_am4ir
FROM 'c:/rvp/data/test_am4ir/outputs/am4ir_txt2db/els_am4ir.txt'
WITH (FIELDTERMINATOR ='\t', ROWTERMINATOR = '\n');

COMMIT transaction;

'''
def am4ir_txt2db(input_folder='c:/rvp/data/test_am4ir', output_folder='c:/rvp/data/test_am4ir/outputs/am4ir_txt2db'):

    output_file_name = '{}/els_am4ir.txt'.format(output_folder)
    input_file_name = '{}/am4ir_pii_embargodate.txt'.format(input_folder)

    with open(str(output_file_name),encoding="latin1",mode="w") as output_file:
        # output will be inserted into sql server 2008 which does not support utf-8,
        # so output encoding is latin1
        # NOTE: save EXCEL file as "UNICODE text" file
        with open (str(input_file_name),encoding="utf-8",mode="r") as input_file:
            # NOTE: one may use VIM or other tools to change input file encoding to required
            # utf-8 here if not already in utf-8 format, eg vim command...
            # :set fileencoding=utf-8
            lines = input_file.readlines()
            for i,line in enumerate(lines):
                #print("Got line='{}'.,eline='{}'".format(line,eline))

                parts = line.split('\t')
                nparts = len(parts)
                pii = parts[0].replace('(','').replace(')','').replace('-','')
                # Note use end='' in print else get double-spacing problem
                print('{}\t{}'.format(pii,parts[1]),file=output_file,end="")

    return i
#end def am4ir_txt2db

i = am4ir_txt2db()
print(i)
