'''
This program builds the SOP document
'''

'''
build_cover reads the coversheet template and custom_xml filename.
It maps certain xml elements form teh custom_xml input to variables
that are used to fill in the template and build 'str_cover', the final
formatted string (in html format) for the coversheet.
'''

def build_cover(template_fn, custom_fn, output_fn):
    # Mapping of xpath to variable names
    # Coding note: the key is a variable name in the template
    # and the value is an xpath if it starts with '.', otherwise it
    # is a variable name with a string value or
    # a constant string value for the template variable
    d_var_val = {
       'title': '2018 Smathers Libraries Strategic Opportunities Grant',
       'due_usa_written_date_time', 'October 16, 2017, 5:00PM',
       'pi_name' : 'Robert V Phillips' ,
       'first_time' : 'X', # hard-code here = I am first time pi
       'department' : 'Smathers Library IT',
       'email' : 'podengo@ufl.edu',
       'phone' : '352-273-8435',
       'additional_name_email_roles': (
          'Chelsea Dinsmore; chedins@uflib.ufl.edu; '
          'Subject Matter Expert and Quality Control'),
       'funds_requested' : '$5,000',
       'abstract_max_100_words': '''Abstract here
       ''',
       'how_cost_share_is_met': '''10% mandatory cost share: Chelsea Dinsmore
       will contribute  1.5% FTE hours at an indirect cost of $1234.56 for a total
       contribution of $500.00.
       '''
    }
    return str_cover
