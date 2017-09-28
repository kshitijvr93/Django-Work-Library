# coding: utf-8
# Make change of address letters using weasyprint
# python 3 code
import os
######################################
# Set some correspondent variable values.
# They may also include html tags if desired, that must be well-formed
# and fit in the context of the template, of course.
correspondents = [
    {'correspondent_name': 'American Century Brokerage, Division of American Century Investment Services, Inc'
    ,'co_addr1': 'P.O. Box 419146'
    ,'co_addr2': 'Kansas City,  MO '
    ,'co_zip': '64141-6146'
    ,'co_account_name': 'Account Number'
    ,'co_account_id': '4MV-044929'
    ,'outfile_prefix': 'amcent'
    },
    {'correspondent_name': 'todo: Avaya Savings'
    ,'co_addr1': ('x')
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    {'correspondent_name': 'todo:Alerus?'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    {'correspondent_name': 'x'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    {'correspondent_name': 'x'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    ]
#################more to do 20161209 ##############################
#
# Set some correspondent variable values.
# They may also include html tags if desired, that must be well-formed
# and fit in the context of the template, of course.
correspondents = [
    {'correspondent_name': 'Merrill Edge'
    ,'co_addr1': 'P.O. Box 1580'
    ,'co_addr2': 'Pennington, NJ '
    ,'co_zip': '08534-1580'
    ,'co_account_name': 'Account Number'
    ,'co_account_id': '5F5-85586'
    ,'outfile_prefix': 'merrill'
    },
    {'correspondent_name': 'Hawthorne Reserve Condominium Assoc'
    ,'co_addr1': ('c/o Bosshardt Property Mgt<br>''5522-B NW 43rd Street')
    ,'co_addr2': 'Gainesville, FL'
    ,'co_zip': '32653'
    ,'co_account_name': 'Unit Number'
    ,'co_account_id': '151'
    ,'outfile_prefix': 'hawthorne_reserve'
    },
    {'correspondent_name': 'x'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    ]
correspondents = [
    {'correspondent_name': 'todo:Alerus?'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    {'correspondent_name': 'x'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
    {'correspondent_name': 'x'
    ,'co_addr1': 'x'
    ,'co_addr2': 'x'
    ,'co_zip': 'x'
    ,'co_account_name': 'x'
    ,'co_account_id': 'x'
    ,'outfile_prefix': 'x'
    },
]
###############################################
'''
very simple program.
define a formattable string that was based on an html file first generated
with libre-writer - that is say a letter - a change of address lettter.
Variable list 'correspondents', above, just defines a list recipients,
each list item being a dictionary
where the keys are the variable names used in the formattable-html-string.
Next, for each item in the list use python's string
format() method to make an output file x.html
Next, call weasyprint to process each outputted new html file to generate
a pdf file for it.
Next, print the pdf files.
'''
# This format string is based on html output of libre-writer, hand edited a bit
# to host python format-style variabls where I want them to be.
############ CHANGE OF ADDRESS ###################
doc_string='''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title></title>
  <meta name="generator" content="LibreOffice 4.2.8.2 (Linux)">
  <meta name="created" content="20161009;183812439632025">
  <meta name="changed" content="20161009;184217117305396">
  <style type="text/css">
  <!--
    @page {{ margin: 0.79in }}
    p {{ margin-bottom: 0.1in; line-height: 120% }}
  -->
  </style>
</head>
<body lang="en-US" dir="ltr">
{correspondent_name}<br>
{co_addr1}<br>
{co_addr2} {co_zip}<br>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0in; line-height: 100%">Dear
{correspondent_name},</p>
<p style="margin-bottom: 0in; line-height: 100%">
My {co_account_name} is {co_account_id}.<br>
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0in; line-height: 100%">Please be advised
that I have changed my legal mailing address.</p>
<p style="margin-bottom: 0in; line-height: 100%">My former address
was:</p>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
Robert V. Phillips<br>
507 NW 39<sup>th</sup>
Rd Unit 151<br>
Gainesville, FL 32607<br>
<p style="margin-bottom: 0in; line-height: 100%">Please be advised that my new address
is:</p>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
Robert V. Phillips<br>
308 SW 40<sup>th</sup>Street<br>
Gainesville, FL 32607<br></p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
<p style="margin-bottom: 0in; line-height: 100%">Thank you,</p>
<p style="margin-bottom: 0in; line-height: 100%">Robert V Phillips</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
<p style="margin-bottom: 0in; line-height: 100%">October 10, 2016</p>
</body>
</html>
'''
#end older letters
############################ GAINESVILLE HEALTH AND FITNESS ###########################
d_correspondents = {
    'ghf' : {
    ,'correspondent_name' : 'Sally in Accounts Receivable'
    ,'salutation' : 'Dear Sally'
    ,'co_addr1': '4820 Newberry Road'
    ,'co_addr2': 'Gainesville, FL'
    ,'co_zip': '32607'
    ,'co_account_name': 'Membership Agreement'
    ,'co_account_id': '283756'
    ,'today': 'June 10, 2017'
    ,'outfile_prefix': 'ghf20170610'
    },
    'test' : {
    'representative_name' : 'Sally in Accounts Receivable'
    ,'correspondent_name': 'Gainesville Health and Fitness'
    ,'salutation' : 'Dear Sally'
    ,'co_addr1': '4820 Newberry Road'
    ,'co_addr2': 'Gainesville, FL'
    ,'co_zip': '32607'
    ,'co_account_name': 'Membership Agreement'
    ,'co_account_id': '283756'
    ,'today': 'June 10, 2017'
    ,'outfile_prefix': 'test20170610'
    },
}
letter_non_renew = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title></title>
  <meta name="generator" content="LibreOffice 4.2.8.2 (Linux)">
  <meta name="created" content="20161009;183812439632025">
  <meta name="changed" content="20161009;184217117305396">
  <style type="text/css">
  <!--
    @page {{ margin: 0.79in }}
    p {{ margin-bottom: 0.1in; line-height: 120% }}
  -->
  </style>
</head>
<body lang="en-US" dir="ltr">
{correspondent_name}<br>
{co_addr1}<br>
{co_addr2} {co_zip}<br>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0in; line-height: 100%">
{salutation}</p>
<p style="margin-bottom: 0in; line-height: 100%">
This regards our {co_account_name}, #{co_account_id}.<br>
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
I have decided to not renew the {co_account_name} with you.
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
<p style="margin-bottom: 0in; line-height: 100%">Also, please be advised
that I have changed my legal mailing address.</p>
<p style="margin-bottom: 0in; line-height: 100%">My former address
was:</p>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
Robert V. Phillips<br>
507 NW 39<sup>th</sup>
Rd Unit 151<br>
Gainesville, FL 32607<br>
<p style="margin-bottom: 0in; line-height: 100%">Please be advised that my new address
is:</p>
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
Robert V. Phillips<br>
308 SW 40<sup>th</sup>Street<br>
Gainesville, FL 32607<br></p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
I regret to inform you that I have lost my membership card, and I
understand that there is a replacement fee of $10, however, since I
am not renewing, I will no longer need a card.
Please advise whether you require payment of this $10, and direct all future
correspondence related to this Membership Agreement to my new U.S. Mail address,
given above.
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
<p style="margin-bottom: 0in; line-height: 100%">Thank you,</p>
<p style="margin-bottom: 0in; line-height: 100%">Robert V Phillips</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
<p style="margin-bottom: 0in; line-height: 100%">May 27, 2017</p>
</body>
</html>
'''
letter_ghf_20170610= '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title></title>
  <meta name="generator" content="LibreOffice 4.2.8.2 (Linux)">
  <meta name="created" content="20161009;183812439632025">
  <meta name="changed" content="20161009;184217117305396">
  <style type="text/css">
  <!--
    @page {{ margin: 0.79in }}
    p {{ margin-bottom: 0.1in; line-height: 120% }}
  -->
  </style>
</head>
<body lang="en-US" dir="ltr">
308 SW 40th Street</br>
Gainesville, FL 32607</br>
<p style="margin-bottom: 0in; line-height: 100%"><br>
{today}
<p style="margin-bottom: 0in; line-height: 100%"><br>
<p style="margin-bottom: 0in; line-height: 100%"><br>
{correspondent_name}<br>
{co_addr1}<br>
{co_addr2} {co_zip}<br>
</p>
<p style="margin-bottom: 0in; line-height: 100%">
<p>{salutation}</p>
Thank you for your reminder about the final payment on my former account
with you that my credit card company
dishonored to you. They canceled that card (that was used monthly to pay you)
before its expiration date  without my express order.
<p style="margin-bottom: 0in; line-height: 100%">
Please find my check enclosed for $36.85 as payment in full under our
former {co_account_name} #{co_account_id}.<br>
</p>
I apologize for the inconvenience.
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
Thank you,
<p style="margin-bottom: 0in; line-height: 100%">
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
Robert V. Phillips
<p style="margin-bottom: 0in; line-height: 100%">{today}</p>
</body>
</html>
'''
letter_business_test_20170610= '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title></title>
  <meta name="generator" content="LibreOffice 4.2.8.2 (Linux)">
  <meta name="created" content="20161009;183812439632025">
  <meta name="changed" content="20161009;184217117305396">
  <style type="text/css">
  <!--
    @page {{ margin: 0.79in }}
    p {{ margin-bottom: 0.1in; line-height: 120% }}
  -->
  </style>
</head>
<body lang="en-US" dir="ltr">
308 SW 40th Street</br>
Gainesville, FL 32607</br>
<p style="margin-bottom: 0in; line-height: 100%"><br>
{today}
<p style="margin-bottom: 0in; line-height: 100%"><br>
<p style="margin-bottom: 0in; line-height: 100%"><br>
{representative_name}<br>
{correspondent_name}<br>
{co_addr1}<br>
{co_addr2} {co_zip}<br>
</p>
<p style="margin-bottom: 0in; line-height: 100%">
<p>{salutation}</p>
Thank you for your reminder about the final payment on my former account
with you that my credit card company
dishonored to you. They canceled that card (that was used monthly to pay you)
before its expiration date  without my express order.
<p style="margin-bottom: 0in; line-height: 100%">
Please find my check enclosed for $36.85 as payment in full under our
former {co_account_name} #{co_account_id}.<br>
</p>
I apologize for the inconvenience.
<p style="margin-bottom: 0in; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
Thank you,
<p style="margin-bottom: 0in; line-height: 100%">
</p>
<p style="margin-bottom: 0in; line-height: 100%"><br></p>
Robert V. Phillips
<p style="margin-bottom: 0in; line-height: 100%">{today}</p>
</body>
</html>
'''
'''
Method out_html_letters()
<param name='template_html'>The html letter template that formats correspondent
parameters into an html letter</param>
<param>d_correspondents is a dict keyd by correspondent initial/short name, and the value of
each is a dictionary, keyed with template variable names and values are values to plug into the ouput
letter template for that corerspondent.
<param>correspondents is a list of dicts, each with the parameter values for
filling out the template to create an html file that represents a letter to send to the correspondent</param>
<param>output_folder is the output folder into which to write the letter.
Note that the output folder is NOT cleared out of files first, by design </param>
'''
def out_html_letters(template_html=None, nicknames=None ,d_correspondents=None, output_folder=None):
    me = 'out_html_letters'
    if not (template_html and correspondents and output_folder):
        raise ValueError('Args template_html and correspondents are required.')
    print("{}: Creating html letters for {} correspondents:".format(me,repr(len(nicknames))))

    for i, d_correspondent in enumerate([d_correspondents[nickname] for nickname in nicknames ]):
        out_str = template_html.format(**d_correspondent)
        outfile_prefix = d_correspondent.get(
            'outfile_prefix','coa_mail_{}'.format(i))
        output_filename='{}/{}.html'.format(output_folder,outfile_prefix)
        print("{}: Outputting filename='{}'".format(me,output_filename))
        with open(output_filename, mode='w',encoding='utf-8') as fwutf8:
            fwutf8.write(out_str)

from subprocess import run
from pathlib import Path
'''method weasyprint_html_to_pdfs()
Given parameter head_folder, find all .html files there, and for each,
create an output file in the same folder, ending .pdf
'''
def weasyprint_html_to_pdfs(head_folder=None):
    me = 'weasyprint_html_to_pdfs'
    if head_folder is None:
        raise ValueError('Missing required argument: head_folder')
    head_path = Path(head_folder)
    path_list = list(head_path.glob('**/*.html'))
    print("{}: Printing from {} html files in head_folder='{}'".format(me,len(path_list),head_folder))
    for i, path in enumerate(path_list):
        filename = path.name
        print("Using FILE PATH NAME='{}'".format(filename))
        parts = filename.split('.')
        #Parse the filename except final .html
        filebase = '.'.join(parts[:-1])
        call_args = ['weasyprint', '{}/{}'.format(head_folder,filename)
            , '{}/{}.pdf'.format(head_folder,filebase)]
        print("{}: Submitting subprocess.run({})...".format(me,repr(call_args)))
        ran = run(call_args)
        print("Ran with returncode={}".format(ran.returncode))
def print_pdfs(head_folder=None):
    if not head_folder:
        raise ValueError('Missing required argument: head_folder')
    head_path = Path(head_folder)
    path_list = list(head_path.glob('**/*.pdf'))
    for i, path in enumerate(path_list):
        call_args = ['lpr', '{}/{}'.format(head_folder,path.name)]
        print("Submitting subprocess.run({})...".format(repr(call_args)))
        ran = run(call_args)
        print("Ran with returncode={}".format(ran.returncode))
# ################## Run Parameters and RUN #####################
def main_run(d_args):
    fshome = d_args['file_system_home']
    output_folder = d_args['output_folder']
    os.makedirs(output_folder, exist_ok=True)
    print("main_run: output_folder={}".format(output_folder))

    whether_make_pdfs_now = d_args['make_pdfs_now']
    whether_print_now = d_args['print_now']
    d_correspondents = d_args['d_correspondents']
    nicknames = d_args['nicknames']
    template_letter = d_args['template_letter']
    #
    # Note: before running this, if you want delete contents in the output folder,
    # you must do it manually.
    # Create the formatted html files
    print("Start: calling out_html_letters() with template_letter='{}'\n,"
          " correspondents='{}'\n, output_folder='{}'\n"
          .format(template_letter,correspondents,output_folder))

    out_html_letters(template_html=template_letter, nicknames=nicknames, d_correspondents=d_correspondents,
        output_folder=output_folder)

    if whether_make_pdfs_now:
        #invoke weasyprint at subprocess levelto create a pdf for every html letter
        print("Calling weasyprint_html_to_pdfs")
        weasyprint_html_to_pdfs(output_folder)
    if whether_print_now:
        #print pdfs in a folder
        print_pdfs(head_folder=output_folder)
############## CONFIGURE MAIN PARAMETERS  AND RUN ######################################
fshome = '/home/robert'
d_args = {
    'file_system_home':fshome,
    'output_folder': '{}/tmpdir/letters'.format(fshome),
    'make_pdfs_now': True,
    'print_now': False,
    'template_letter': letter_ghf_20170610,
    'd_correspondents': d_correspondents,
    'nicknames': ['ghf']
};
print("Starting calling main_run...")
main_run(d_args)
print("Back from main_run. Done!")

#################################################################################################################
## END -- THAT PRINTED THE HTML FILES IN THE OUTPUT FOLDER. NEXT USES WEASYPRINT TO CREATE PDF FILES
import weasyprint
doc1 = '''<p style="page-break-before:always;">
  </br>
  <strong>IN TESTIMONY</strong> whereof, the name of the GRANTOR(S) is hereunto
  affixed,
  </br> this _____ day of _____________, 2015.
  </br>
  ___________________________
  </br>
  {{grantor.name}}, Grantor
  </div>
  <!-- ACKNOWLEDGEMENT SECTION  -->
  <h5 align='center' style="font-size:200%;" ><strong>ACKNOWLEDGEMENT</strong></h5>
  <!-- COUNTY  OF NOTARIZATION DIV -->
<div style="font-size:150%;line-height:145%;font-family:'Times New Roman', Times, serif;">
<strong>STATE OF</strong> ____________________)
</br>
<strong>COUNTY OF</strong> __________________) ss
</div>
  <!-- NOTARY DIV -->
  <div style="font-size:150%;line-height:125%;font-family:'Times New Roman', Times, serif;">
  <p><span><strong>BE IT REMEMBERED</strong><span>, That on this day, before the undersigned, a Notary Public
  within and for the State and County aforesaid, duly commissioned and acting, personally appeared,
  {{grantor.name}}, to me well known as (or satisfactorily proven to be) the person
  whose name is subscribed to the foregoing instrument and acknowledged that
  {{grantor.nominative_pronoun}}
  had executed the same for the consideration and purposes therein mentioned and set forth.
  </p><p>
  <strong>WITNESS</strong> my hand and official seal on this _____ day of _____________, 2015.
  </p>
    <div style="display:block; margin-left:8cm; line-height:205%">
    ___________________________
    </br>
    <strong>Notary Public</strong>
    </br>Print name: _________________________
    </br>My commission expires: ________________
    </div>
  </div>
  <!-- END NOTARY DIV AND SECTION -->
'''
'''
doc = HTML(doc1)
try:
    import StringIO
    StringIO = StringIO.StringIO
except Exception:
    from io import StringIO
import cgi
def index(request):
    # return the html render returns
    return render(request, 'x2p_test1.html', {'variable': 'value'})
def download(request):
    if request.POST:
        result = StringIO()
        pdf = pisa.CreatePDF(
            StringIO(request.POST["data"]),
            result
            )
        #==============README===================
        #Django < 1.7 is content_type is mimetype
        #========================================
        if not pdf.err:
            return http.HttpResponse(
                result.getvalue(),
                content_type='application/pdf')
    return http.HttpResponse('We had some errors')
def render_to_pdf(request, template_src, context_dict):
    template = get_template(template_src)
    context = RequestContext(request, context_dict)
    html  = template.render(context)
    result = StringIO()
    pdf = pisa.pisaDocument(StringIO( "{0}".format(html) ), result)
    if not pdf.err:
        #==============README===================
        #Django < 1.7 is content_type is mimetype
        #========================================
        return http.HttpResponse(result.getvalue(), content_type='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
# In[ ]:'''
