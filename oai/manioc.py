def hello():
    print("Hello from manioc!")


def manioc_node_writer(node_record=None, namespaces=None, output_folder=None
  , set_spec=None, metadata_prefix=None, bib_vid='XX00000000_00001'
  , verbosity=0):
    me = 'manioc_node_writer'
    required_params = ['set_spec','metadata_prefix'
        ,'node_record','namespaces','output_folder','bib_vid']
    if not all(required_params):
      raise ValueError("{}:Some params are not given: {}".format(me,required_params))

    bibint = bib_vid[2:10]
    bibid = bib_vid[:10]
    vid = bib_vid[11:16]

    # Consider: also save text from the xml and put in METS notes?
    # <set_spec>,
    # add note for identifier0 vs identifier1... ordering..

    node_type= node_record.find(".//{*}type", namespaces=namespaces)
    genre = '' if node_type is None else node_type.text
    genre = etl.escape_xml_text(genre)

    node_identifier = node_record.find("./{*}header/{*}identifier", namespaces=namespaces)
    header_identifier_text = '' if node_identifier is None else node_identifier.text

    header_identifier_normalized = (header_identifier_text
      .replace(':','_').replace('/','_').replace('.','-'))

    if verbosity > 0:
        print("using bib={}, vid={}, bib_vid={} to output item with "
          "manioc header_identifier_normalized={}"
          .format(bibid,vid,bib_vid, header_identifier_normalized))

    # Parse the input record and save it to a string
    record_str = etree.tostring(node_record, pretty_print=True, encoding='unicode')
    # print("{}:Got record string={}".format(me,record_str))

    output_folder_xml = output_folder + 'xml/'
    # TO CONSIDER: maybe add a class member flag to delete all preexisting
    # files in this directory? maybe dir for mets too?
    os.makedirs(output_folder_xml, exist_ok=True)
    #print("{}:using output_folder_xml={}".format(me,output_folder_xml))

    filename_xml = output_folder_xml + header_identifier_normalized + '.xml'
    with open(filename_xml, mode='w', encoding='utf-8') as outfile:
        #print("{}:Writing filename_xml ='{}'".format(me, filename_xml))
        outfile.write(record_str)

    # Set some variables to potentially output into the METS template
    utc_now = datetime.datetime.utcnow()
    utc_secs_z = utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")

    node_mdf = node_record.find(".//{*}dc", namespaces=namespaces)

    if node_mdf is None:
        # This happens for received 'delete' records
        # Just return None to ignore them pending requirements to process them
        #print ("Cannot find node_mdf for xml tag/node: {*}dc")
        return 0
    else:
      #print("{}: Got node_mdf with tag='{}'",format(node_mdf.tag))
      pass

    #print("{}:got namespaces='{}'".format(me,repr(namespaces)))

    node_creator = node_mdf.find(".//{*}creator", namespaces=namespaces)
    dc_creator = '' if node_creator is None else node_creator.text
    dc_creator = etl.escape_xml_text(dc_creator)
    #print("{}:Got creator={}".format(me,dc_creator))

    node_date = node_mdf.find("./{*}date", namespaces=namespaces)
    dc_date_orig='1969-01-01'
    if node_date is not None:
        dc_date_orig = node_date.text
    # If we get only a year, pad it to year-01-01 to make
    # it valid for this field.
    if len(dc_date_orig) < 5:
        dc_date_orig += "-01-01"
    elif len(dc_date_orig) < 8:
        dc_date_orig += "-01"

    dc_date = '{}T12:00:00Z'.format(dc_date_orig)
    # print("Got dc date orig={}".format(dc_date_orig))
    # Must convert dc_date_orig to valid METS format:
    dc_date = '{}T12:00:00Z'.format(dc_date_orig)
    #print("{}:Got dc_date='{}'".format(me,dc_date))

    node_description = node_mdf.find(".//{*}description",namespaces=namespaces)
    # Make an element tree style tree to invoke pattern to remove inner xml
    #str_description = etree.tostring(node_description,encoding='unicode',method='text').strip().replace('\n','')
    str_description = ''
    if (node_description is not None):
        #str_description = etree.tostring(node_description,encoding='unicode').strip().replace('\n','')
        str_description = etl.escape_xml_text(node_description.text)

    if (1 ==1):
        dc_description = str_description
        # avoid charmap codec windows errors:print("Using dc_description='{}'".format(dc_description))

    nodes_dc_identifier = node_mdf.findall(
      ".//{*}identifier", namespaces=namespaces)

    xml_dc_ids = '\n'

    related_url = ''
    # id type names based on data received in 2017
    # I invented the id_types, based on the data harvested in 2017.
    id_types = ['manioc_set_spec_index', 'manioc_url']
    for i,nid in enumerate(nodes_dc_identifier):
        xml_dc_ids = ('<mods:identifier type="{}">{}</mods:identifier>\n'
          .format(id_types[i], nid.text))
        if (i == 1):
          # per agreement on phone
          related_url = nid.text

    # Create thumbnail src per algorithm provided 20170807 by elliot williams,
    # Digital Initiatives MD Librarian, of Miami-Merrick
    thumbnail_src = 'http://merrick.library.miami.edu/utils/getthumbnail/collection/'
    thumbnail_src += '/'.join(related_url.split('/')[-3:])

    nodes_rights = node_mdf.findall(".//{*}rights",namespaces=namespaces)
    # rights-text per UF email from Laura Perry to rvp 20170713
    rights_text = '''This item was contributed to the Digital Library
of the Caribbean (dLOC) by the source institution listed in the metadata.
This item may or may not be protected by copyright in the country
where it was produced. Users of this work have responsibility for
determining copyright status prior to reusing, publishing or
reproducing this item for purposes other than what is allowed by
applicable law, including any applicable international copyright
treaty or fair use or fair dealing statutes, which dLOC partners
have explicitly supported and endorsed. Any reuse of this item
in excess of applicable copyright exceptions may require
permission. dLOC would encourage users to contact the source
institution directly or dloc@fiu.edu to request more information
about copyright status or to provide additional information about
the item.'''

    # Some list-variable input values
    for node_rights in nodes_rights:
        rights_text += '\n' + node_rights.text
    rights_text = etl.escape_xml_text(rights_text)

    # Subjects
    nodes_subject = node_mdf.findall(".//{*}subject", namespaces=namespaces)
    mods_subjects = '<mods:subject>'
    for node_subject in nodes_subject:
        subjects = node_subject.text.split(';')
        for subject in subjects:
          subject = subject.strip()
          if len(subject) < 1:
            continue
          mods_subjects += '<mods:topic>' + etl.escape_xml_text(subject) + '</mods:topic>\n'
    mods_subjects += ('</mods:subject>\n')

    tnode = node_mdf.find(".//{*}title", namespaces=namespaces)
    dc_title = '(none)' if tnode is None else etl.escape_xml_text(tnode.text)

    tnode = node_mdf.find(".//{*}type", namespaces=namespaces)
    dc_type = '' if tnode is None else etl.escape_xml_text(tnode.text)

    sobekcm_aggregations = ['ALL', 'DLOC1', 'IUM']
    xml_sobekcm_aggregations = ''
    for aggregation in sobekcm_aggregations:
        xml_sobekcm_aggregations += (
            '<sobekcm:Aggregation>{}</sobekcm:Aggregation>'
            .format(aggregation))
    sobekcm_wordmarks = ['UM','DLOC']
    xml_sobekcm_wordmarks = ''
    for wordmark in sobekcm_wordmarks:
        xml_sobekcm_wordmarks += (
            '<sobekcm:Wordmark>{}</sobekcm:Wordmark>\n'
            .format(wordmark))

    # Set some template variable values
    d_var_val = {
        'bib_vid' : bib_vid,
        'create_date' : dc_date,
        'last_mod_date' : utc_secs_z,
        'agent_creator_individual_name': dc_creator,
        'agent_creator_individual_note' : 'Creation via Miami-Merrick OAI  harvest',
        'identifier' : header_identifier_text,
        'mods_subjects' : mods_subjects,
        'rights_text' : rights_text,
        'utc_secs_z' :  utc_secs_z,
        'title' : dc_title,
        'related_url' : related_url,
        'xml_sobekcm_aggregations' : xml_sobekcm_aggregations,
        'xml_sobekcm_wordmarks' : xml_sobekcm_wordmarks,
        'sobekcm_thumbnail_src' : thumbnail_src,
        'xml_dc_ids' : xml_dc_ids,
        'description' : dc_description,
        'creator' : dc_creator,
        'bibid': bibid,
        'vid': vid,
        'type_of_resource' : dc_type,
        'sha1-mets-v1' : '',
        'genre' : '',
        'genre_authority': '',
    }

    # Create mets_str and write it to mets.xml output file
    mets_str = merrick_mets_format_str.format(**d_var_val)
    # Nest filename in folder of the bib_vid,
    # because loads in sobek bulder faster this way
    output_folder_mets = output_folder + 'mets/' + bib_vid + '/'
    os.makedirs(output_folder_mets, exist_ok=True)

    filename_mets = output_folder_mets  + bib_vid + '.mets.xml'
    fn = filename_mets
    with open(fn, mode='w', encoding='utf-8') as outfile:
        #print("{}:Writing METS filename='{}'".format(me,fn))
        #outfile.write(mets_str.encode('utf-8'))
        outfile.write(mets_str)
    return 1
    #end def manioc_node_writer()
