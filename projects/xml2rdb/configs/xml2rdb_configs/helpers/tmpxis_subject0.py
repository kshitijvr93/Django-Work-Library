# xis_subjects.py
# fairly simple program to read an access innovations 'XIS' file

'''
sample input file has sequence of these 'item' subject term info sections:
---
#Sample XIS-exported input file with subject keywords has sequence of items like this:
-------
<Thesis n="0000002">
<ADD><D>20170214</D>
<IN>DJV</IN>
</ADD>
<CHG><D>20180629</D>
<IN>win</IN>
</CHG>
<TOPIC>Globalization^Sovereignty^Financial markets^Financial transactions^Currency^Information technology^Financial services^International organizations^Flexible spending accounts^Conceptualization</TOPIC>
<OLDLCSH />
<OLDKW>globalization, sovereignty, uk^Political Science^Florida State University^Cocoa High School (Cocoa, Fla.)^Globalization^Sovereignty^Financial markets^Currency^Financial transactions^Financial services^Information technology^Finance^Flexible spending accounts^Conceptualization</OLDKW>
<GEO>Union County (Florida)</GEO>
<FLORIDIANS>Florida State University^Cocoa High School (Cocoa, Fla.)</FLORIDIANS>
<AU><FNAME>Jamie E</FNAME>
<LNAME>Scalera</LNAME>
</AU>
<TI>Challenging the Sovereign</TI>
<DPUB>2007</DPUB>
<ID>UFE0021053_00001</ID>
</Thesis>
-------

and a simple input pre-process program xis_xml.py will read that input file
and only convert the elements with ^-separated terms to
child <I> (item) elements, eg:

<FLORIDIANS>
  <I>Florida State University</I>
  <I>Cocoa High School (Cocoa, Fla.)</I>
</FLORIDIANS>
---
'''

import

def new_xis_subjects(input_file, output_file)
    pass
#end def

run_one = 1

if run_one == 1:
    input_file = 'input.txt'
    output_file ='output.txt'

    # Awkward but this syntax avoids leading white space for nested indents;
    with open(input_file,mode='r') as infile, \
        open(output_file, mode='w') as outfile:
        line = infile.readline

        pass
    #end
