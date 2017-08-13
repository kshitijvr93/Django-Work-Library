import requests
from lxml import etree
from lxml.etree import tostring
import xml.etree.ElementTree as ET
class OAI_Server(object):
    '''
    <synopsis name='OAI_Server'>
    <summary>OAI_Harvester encapsulates information required to make requests to a
    specific OAI server. It also contains
    (1) a generator method named namespaces_node() to read the OAI server listRecords
    and parse it into a node_record xml object that is returned
    </summary>
    <param name="oai_url">The base url for the target OAI Server API
    </param>
    </synopsis>
    <see-also>http://www.openarchives.org/OAI/openarchivesprotocol.html</see-also>
    '''
    def __init__(self, oai_url=None, encoding=None, set_spec=None, metadata_prefix=None
        ,load_sets=0,verbosity=0):

        if oai_url is None:
            raise ValueError("oai_url must be given")
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
        self.encoding = None if encoding is None else encoding
        self.metadata_prefix = None if encoding is None else encoding
        self.set_spec = None if set_spec is None else set_spec

        self.verbosity = verbosity # default verbosity
        # Potential todo - honor an init flag to populate all set names and/or all metadata
        # prefixes here... would take a few seconds,
        # but could then verify and catch errors in attempts to use invalid
        # set names and metadata prefixes in candidate request urls for the OAI server.
        # That time cost would be a waste if you already know the set_spec and/or
        # metadata format that you want... as these lists normally would change
        # infrequently, on the order or months-long periods # or even longer.

        if (load_sets > 0):
            self.d_spec_name = self.get_d_spec_name();
            print("OAI_Server: loading sets, got {} sets".format(len(self.d_spec_name.items())))

        return

        # return the set_spec and metadata_prefix based on supplied args and default self.* values.
    def _get_set_spec(self, set_spec=None):
        if set_spec is None:
            set_spec = self.set_spec
            if set_spec is None:
                raise ValueError("No set_spec is given.")
            #also can add checks here vs all the legal set-specs if they have been pre-loaded per a new
            # constructer param flag, also metadata_prefix name
        else:
            self.set_spec = set_spec

        return(set_spec)

    def _get_metadata_prefix(self, metadata_prefix=None):
        if metadata_prefix is None:
            metadata_prefix = self.metadata_prefix
            if metadata_prefix is None:
                metadata_prefix = "oai_dc" #Set the basic metadata format
                self.metadata_prefix = metadata_prefix
            # also can add checks here vs all legal metadataPrefix values if preloaded
            # However, in my personal experience, many oai servers report set_specs that are
            # rejected by server requests to list records, etc, or metadata_prefix values.
        else:
            self.metadata_prefix = metadata_prefix

        return(metadata_prefix)

    '''
    get_url_list_records(): return the url to list records for the given set_spec
    and metadata_format (or default to current setting).
    If given, also set the current default values for set_spec and metadata_prefix.
    '''

    def get_url_list_records(self, set_spec=None, metadata_prefix=None):
      set_spec = self._get_set_spec(set_spec=set_spec)
      metadata_format = self._get_set_metadata_prefix( metadata_prefix=metadata_prefix)
      url = ("{}?verb=ListRecords&set={}&metadataPrefix={}"
        .format(self.oai_url, set_spec, metadata_prefix))
      return url

    ''' NOTE: even though metadata_prefix is a kwarg, you must set it to None
        rather than not state it at all, else only one record will issue no matter
        how many sets are on the OAI server host
    '''
    def get_url_list_sets(self, metadata_prefix=None):
      metadata_prefix = self._get_metadata_prefix(metadata_prefix=metadata_prefix)
      url = ("{}?verb=ListSets&metadataPrefix={}"
        .format(self.oai_url, metadata_prefix))
      return url

    def get_url_list_identifiers(self,  metadata_prefix=None):
      set_spec = None
      metadata_prefix = self._get_metadata_prefix( metadata_prefix=metadata_prefix)
      url = ("{}?verb=ListIdentifiers&metadataPrefix={}"
        .format(self.oai_url,self.metadata_prefix))
      return url

    '''
    <summary>list_oai_nodes is a generator function that accepts a url
    and a record xpath and expects a 'resumptiontoken', ala oai-pmh standards,
    to indicate multiple 'batches' of responses that comprise a complete
    logical response
    </summary>

    <param name=record_xpath> is the xpath tag name that contains a record of
    interest from the response</param>
    <param name=encoding> must be set to iso-8559-1 for the miami-merrick oai server
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

    note: for miami-merrick oai server, experience shows the caller must give
    encoding "iso-8559-1" explicitly as an argument and not trust the 'chardet'
    default encoding of the requests package.
    '''
    def list_nodes(self, url_list=None, verb=None, metadata_prefix=None, encoding=None
        , verbosity=1):
        me = 'list_nodes'
        rparams = ['url_list','verb']
        if not all(rparams):
            raise ValueError("missing required param from; {}".format(rparams))
        d_return = {}
        d_return['node_record'] = None

        record_xpath = self.d_verb_record_xpath.get(verb,None)
        if record_xpath is None:
            keys = [x for x in self.d_verb_record_xpath.keys()]
            raise ValueError("Error Exit: Given verb={} is not a key in {}"
                .format(repr(verb),keys))

        if record_xpath is None:
            raise ValueError("missing record_xpath value.")

        if (url_list is None):
            raise ValueError("missing url parameter.")
        if verbosity > 0:
            print("{}: Starting with url={}".format(me,url_list))
        n_batch = 0;
        while (url_list is not None):
            n_batch += 1
            d_return['n_batch'] = n_batch
            response = requests.get(url_list)

            if verbosity > 0:
              response_str = requests.utils.get_unicode_from_response(response)
              encodings = requests.utils.get_encodings_from_content(response_str)
              print("using url_list='{}'\nand got response with apparent_encoding='{}', encoding='{}',headers:"
                .format(url_list, response.apparent_encoding, response.encoding))
              for k,v in response.headers.items():
                  print("{}:{}".format(k,v))
              print("encodings from unicode response_str {}='{}'".format(response_str,encodings))

            # re: workaround for miami-merrick oai server - oddity
            # a fundamental python principle is 'explict is better than  implicit', so call encode() here
            # if encoding argument is set (need it for miami-merrick server, possibly others to come)
            # response.encoding = 'iso-8859-1' # that fails! but next call to encode() seems to work.
            if encoding is not None or  1 == 1:
              #xml_bytes = response.text.encode('iso-8859-1')
              encoding = 'utf-8'
              xml_bytes = response.text.encode(encoding)
            else:
              xml_bytes = response.text

            if verbosity > 0:
              print("xml_bytes len={}, response.encoding={}".format(len(xml_bytes), response.encoding))

            try:
              node_root = etree.fromstring(xml_bytes)
              d_return['node_root'] = node_root
            except Exception as e:
              # give detailed diagnostic info
              print("for batch {}, made url request ='{}'.\got batch with parse() exception='{}'"
                    .format(n_batch, url_list, repr(e)))
              #  raise here - no point to continue because we cannot parse/discover the resumptiontoken
              raise

            d_namespaces = {key:value for key,value in dict(node_root.nsmap).items() if key is not None}
            d_return['namespaces'] = d_namespaces

            nodes_record = node_root.findall(record_xpath, namespaces=d_namespaces)
            if (verbosity > 0):
              print("list_nodes:from the xml found {} xml tags for record_xpath={}"
                   .format(len(nodes_record),record_xpath))

            # for every input node/record, yield it to caller
            for node_record in nodes_record:
              d_return['node_record'] = node_record
              yield d_return

            # 'resumption tokens' is the "oai" server way to serve continuation of respsonses
            node_resumption = node_root.find('.//{*}resumptionToken', namespaces=d_namespaces)
            url_list = None
            if node_resumption is not None:
              # This one says generic error message
              url_list = ('{}?verb={}&resumptiontoken={}'
                  .format(self.oai_url,  verb, node_resumption.text))
              # This one says generic error message which does say a verb is needed, so add md prefix?
              url_list = ('{}?resumptiontoken={}'
                  .format(self.oai_url, node_resumption.text))

              url_list = ('{}?verb={}&metadataPrefix=oai_dc&resumptiontoken={}'
                  .format(self.oai_url,  verb, node_resumption.text))
            else:
                print("No resumptionToken found in batch {}".format(n_batch))
            if verbosity > 0:
              print("{}:next url='{}'".format(me,url_list))
        # end while url_list is not None
        return d_return
    # end def list_oai_nodes()

    ''' generator functions for specific oai lists
    '''
    def list_records(self, set_spec=None,metadata_prefix=None):
        url_list = self.get_url_list_records(set_spec=set_spec, metadata_prefix=metadata_prefix)
        for d_record in self.list_nodes(url_list=url_list, verb='ListRecords'):
          yield d_record
        return None

    def list_sets(self, metadata_prefix=None):
        url_list = self.get_url_list_sets(metadata_prefix=metadata_prefix)
        for d_record in self.list_nodes(url_list=url_list, verb='ListSets'):
            yield d_record
        return None

    def list_identifiers(self, metadata_prefix=None):
        url_list = self.get_url_list_identifiers(metadata_prefix=metadata_prefix)
        for d_record in self.list_nodes(url_list=url_list, verb='ListIdentifiers'):
            yield d_record
        return None

    def get_d_spec_name(self):
        d_set_name = {}
        url = self.oai_url
        metadata_prefix = self._get_metadata_prefix()
        n_id = 0
        for d_record in self.list_sets(metadata_prefix=None):
            n_id += 1
            namespaces = d_record['namespaces']
            node_record = d_record['node_record']
            node_set_spec = node_record.find(".//{*}setSpec")
            set_spec = '' if node_set_spec is None else node_set_spec.text
            node_set_name = node_record.find(".//{*}setName")
            set_name = '' if node_set_name is None else node_set_name.text
            d_set_name[set_spec]=set_name
            print("init: {}: got set_spec={}, set_name={}".format(n_id,set_spec,set_name))
            return d_set_name

    #end class OAI_Server

def run_test():
    url_usf = 'http://scholarcommons.usf.edu/do/oai/'
    oai_server = OAI_Server(oai_url=url_usf,verbosity=1)
    metadata_prefix='oai_dc'
    print("run_test using metadata_prefix={}".format(metadata_prefix))

    n_id = 0
    for d_record in oai_server.list_identifiers(metadata_prefix='oai_dc'):
        n_id += 1
        namespaces = d_record['namespaces']
        node_record = d_record['node_record']
        node_identifier = node_record.find(".//{*}identifier")
        identifier_text = '' if node_identifier is None else node_identifier.text
        print("id count={}, id-{}".format(n_id,identifier_text))

def run_test2():
    url_usf = 'http://scholarcommons.usf.edu/do/oai/'
    oai_server = OAI_Server(oai_url=url_usf,load_sets=1,verbosity=1)

    n_id = 0
    for key, val in oai_server.d_spec_name.items():
        n_id += 1
        print("{}: set_spec={}, set_name={}".format(n_id,key,val))
    return
# RUN
#run_test2() #test...
run_test() #test...
