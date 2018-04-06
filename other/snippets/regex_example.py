import re

# From stack overflow - a nice query string regex
query_string_regex = "^\?([\w-]+(=[\w-]*)?(&[\w-]+(=[\w-]*)?)*)?$"

query_strings=["?a=1&b=2&c=4"
         ,'?f=ZZ,%3dZZ,+AU,+TO,LA'
         ,'?f=ZZ, ZZ,%2bAU,%2bTO,LA'

         ]

for qs in query_strings:
    print("qs='{}'".format(qs))
    if re.search(query_string_regex, qs):
        print("OK found a match.")
    else:
        print("That was bad! String does not match!")

    pass
