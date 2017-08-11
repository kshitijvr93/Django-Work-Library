class OAI_Server(object):
  '''
  <synopsis name='OAI_Harvester'>
  <summary>OAI_Harvester encapsulates information required to make requests to a
  specific OAI server. It also contains
  (1) a generator method named namespaces_node() to read the OAI server listRecords
  and parse it into a node_record xml object that is returned
  </summary>
  <param name="node_writer">A function that takes arguments of (1) node_record and
  (2) namespaces (eg, the return values from a call to namespaces_node() ,
  (3) output_folder, and for other params, see calls to it in this source code.
  </param>
  </synopsis>
  <see-also>http://www.openarchives.org/OAI/openarchivesprotocol.html</see-also>
  '''
  def __init__(self, oai_url=None, verbosity=0):

    self.oai_url = oai_url
    self.d_verb_record_xpath = {
        "GetRecord" : ".//{*}record",
        "ListIdentifiers" : ".//{*}header",
        "ListMetadataFormats" : ".//{*}metadataFormat",
        "ListRecords" : ".//{*}record",
        "ListSets"    : ".//{*}set",
        "Identify" : ".//{*}Identify"
        }

    # namespaces will be reset by each xml file inputted by the api()
    self.namespaces = None #will be overwritten when each xml file is input by the list_oai_nodes
    self.set_spec = ''
    self.metadata_format = "oai_dc"


    self.verbosity = verbosity # default verbosity
    # Potential todo - honor an init flag to populate all set names and/or all metadata
    # prefixes here... would take a few seconds,
    # but could then verify and catch errors in attempts to use invalid
    # set names and metadata prefixes in candidate request urls for the OAI server.
    # That time cost would be a waste if you already know the set_spec and/or
    # metadata format that you want... as these lists normally would change
    # infrequently, on the order or months-long periods # or even longer.
    return

# return the set_spec and metadata_prefix based on supplied args and default self.* values.
def _get_set_spec_metadata_prefix(self,set_spec=None, metadata_prefix=None):
    if set_spec is None:
        set_spec = self.set_spec
        if set_spec is None:
            raise ValueError("No set_spec is given.")
    else:
        self.set_spec = set_spec

    if metadata_prefix is None:
        metadata_prefix = self.metadata_prefix
        if metadata_prefix is None:
            raise ValueError("No metadata_format is given.")

        if metadata_prefix is None:
            metadata_prefix = "oai_dc" #Set the basic metadata format
    else:
        self.metadata_prefix = metadata_prefix
    return(set_spec, metadata_prefix)


  ''' get_url_list_records(): return the url to list records for the given set_spec
  and metadata_format (or default to current setting).
  If given, also set the current default values.
  '''
  def get_url_list_records(self, set_spec=None, metadata_prefix=None):
    set_spec, metadata_format = _get_set_spec_metadata_prefix(self,set_spec, metadata_prefix)

    url = ("{}?verb=ListRecords&set={}&metadataPrefix={}"
      .format(self.oai_url,self.set_spec,self.metadata_prefix))
    return url

  def get_url_list_sets(self, metadata_prefix=None):
    if metadata_prefix is not None:
        self.metadata_prefix = metadata_prefix
    url = ("{}?verb=ListSets&metadataPrefix={}"
      .format(self.oai_url,self.metadata_prefix))
    return url

  def get_url_list_identifiers(self, set_spec=None, metadata_prefix=None):
    set_spec, metadata_prefix = _get_set_spec_metadata_prefix(self,set_spec, metadata_prefix)

    url = ("{}?verb=ListIdentifiers&set={}&metadataPrefix={}"
      .format(self.oai_url,self.set_spec,self.metadata_prefix))
    return url

  '''
  <summary>list_oai_nodes is a generator function that accepts a url
  and a record xpath and expects a 'resumptionToeken', ala OAI-PMH standards,
  to indicate multiple 'batches' of responses that comprise a complete
  logical response
  </summary>

  <param name=record_xpath> is the xpath tag name that contains a record of
  interest from the response</param>
  <param name=encoding> must be set to ISO-8559-1 for the miami-merrick oai server
  (and possible others) because the normal character encoding detection
  (that usually works for other oai servers) does not work for miami-merric
  </param>
  <return> a dictionary with:
  'record': node_record - the lxml doc node of the this record
  'namespaces': node_record - dictionary of the namespaces of the
                response/batch containing this record
  'n_batch' : the batch number count, or query response count for the response
              containing the node record
  'root'    : the lxml root node of the response page of of this batch of records
  </return>

  NOTE: for miami-merrick oai server, experience shows the caller must give
  encoding "ISO-8559-1" explicitly as an argument and not trust the 'chardet'
  default encoding of the requests package.
  '''
  def list_oai_nodes(self, url_list=None, verb=None, encoding=None
        , verbosity=0):

    d_return = {}
    d_return['node_record'] = None

    record_xpath = self.d_verb_record_path[verb]

    if record_xpath is None:
      raise ValueError("Missing record_xpath value.)

    if (url is None):
      raise ValueError("Missing url parameter.")

    n_batch = 0;
    while (url_list is not None):
      n_batch += 1
      d_return['n_batch'] = n_batch
      response = requests.get(url_list)

      if verbosity> 0:
          response_str = requests.utils.get_unicode_from_response(response)
          encodings = requests.utils.get_encodings_from_content(response_str)
          print("Using url_list='{}'\nand got response with apparent_encoding='{}', encoding='{}',headers:"
            .format(url_list, response.apparent_encoding, response.encoding))
          for k,v in response.headers.items():
              print("{}:{}".format(k,v))
          print("Encodings from unicode response_str {}='{}'".format(response_str,encodings))

      # RE: Workaround for miami-merrick oai server - oddity
      # A fundamental python principle is 'explict is better than  implicit', so call encode() here
      # if encoding argument is set (need it for miami-merrick server, possibly others to come)
      # response.encoding = 'ISO-8859-1' # that fails! But next call to encode() seems to work.
      if encoding is not None:
          #xml_bytes = response.text.encode('ISO-8859-1')
          xml_bytes = response.text.encode(encoding)
      else:
          xml_bytes = response.text

      if verbosity > 0:
          print("xml_bytes len={}, response.encoding={}".format(len(xml_bytes), response.encoding))

      try:
          node_root = etree.fromstring(xml_bytes)
          d_return['node_root'] = node_root
      except Exception as e:
          # Give detailed diagnostic info
          print("For batch {}, made url request ='{}'.\Got batch with Parse() exception='{}'"
                .format(n_batch, url_list, repr(e)))
          #  Raise here - no point to continue because we cannot parse/discover the resumptionToken
          raise

      d_namespaces = {key:value for key,value in dict(node_root.nsmap).items() if key is not None}
      d_return['namespaces'] = d_namespaces

      nodes_record = node_root.findall(record_xpath, namespaces=d_namespaces)
      if (verbosity > 0):
          print("From the xml found {} xml tags for records".format(len(nodes_record)))
          print ("ListRecords request found root tag name='{}', and {} records"
             .format(node_root.tag, len(nodes_record)))

      # For every input node/record, yield it to caller
      for node_record in nodes_record:
          d_return['node_record'] = node_record
          yield d_return

      # 'Resumption Tokens' is the "OAI" server way to serve continuation of respsonses
      node_resumption = node_root.find('.//{*}resumptionToken', namespaces=d_namespaces)
      url_list = None
      if node_resumption is not None:
          url_list = ('{}?verb=ListRecords&resumptionToken={}'
              .format(self.oai_url,  node_resumption.text))
      if verbosity > 0:
          print("{}:Next url='{}'".format(me,url_list))
    # end while url_list is not None
    return d_return
  # end def list_oai_nodes()

  def output_sets(self, verbosity=1):
    num_records = 0
    output_filename = '{}/{}/list_sets.xml'.format(self.output_folder, self.metadata_format)
    url_sets = "{}?verb=ListSets&metadataFormat={}".format(self.oai_url)

    for (d_record) in oai.list_oai_nodes(url_list=url_sets):
        node_record = d_record['node_record']
        if node_record is None:
              break;
        sets_str = etree.tostring(node_record, pretty_print=True)
        print(sets_str, file=output_file)
        num_records += 1

    if verbosity > 0:
      print("Outputted xml for {} OAI set_specs to filename {}...".format(num_records,output_filename))
    return num_records, num_deleted
  # end def output_sets()

  def output_records(self):
    num_records = num_deleted = 0
    bibvid = self.bib_prefix + str(self.bib_last).zfill(self.bib_zfills[0]) + '00001' #may implement vid later
    output_folder_format = '{}/{}/'.format(self.output_folder, self.metadata_format)

    # increment the candiate bib_last integer to offer for the output of the next mets
    self.bib_last += 1

    for (namespaces, node_record) in oai.list_oai_nodes():
      bib_vid = self.bib_prefix + str(self.bib_last).zfill(8) + '_00001' #may implement vid later

      # Call crosswalk this xml node's record content to output the record to a file
      # zw = self.node_writer()
      if node_record is None:
            break;
      # save the xml in its own output ... folder ***
      #
      # Call the crosswalk function to read the node_record and write mets file output
      rv = self.node_writer(node_record=node_record ,namespaces=namespaces
          ,output_folder=output_folder_format, bib_vid=bib_vid)

      if rv == 0:
          num_deleted += 1
      # Increment the integer bib_last id candidate for the next mets record.
      # NOTE: some received OAI node_records are for 'delete' ,
      # Later - change the node_writer to return true if it wrote a mets
      # and false if it detected a delete record and so did not write a mets.
      # if rv == 1: # uncomment after finishing testing other things to keep bibids the same in meantime
      self.bib_last += 1
      num_records += 1

    return num_records, num_deleted
  # end def output_records()


# end class OAI_Harvester
