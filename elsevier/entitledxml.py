def get_entitlement_xml_for_piis(piis, output_folder_name=None):

    sep = ''
    str_piis = ''
    for pii in piis:
        str_piis += str(pii)
        sep = ','

    url = (('http://api.elsever.com/article/entitlement/pii/{}'
            'apiKey'=d91051fb976425e3b5f00750cbd33d8b)
           .format(piis))

    input_xml_str = etl.get_response_by_url(url, json_loads=False)
    node_root_input = etree.fromstring(input_xml_str)
    d_ns = {key:value
            for key,value in dict(node_root_input.nsmap).items()
            if key is not None}
    nodes_entitlement = node_root_input.findall(
        'document-entitlement', namespaces=d_ns)

    for node_entitlement in nodes_entitlement:
        with output ("pii_{}.xml".format(pii), 'wb' as outfile:
            outfile.write(etree.tostring(node_entitlement, pretty_print=True))

def get_pii_info(input_file_name=None):

    d_pii_info = {}
    rows = [
        ['a' ,  'infoa']
        ,['b' :  'infob']
        ]
    for pii,info in rows_pii_info:
        key = d_pii_info.get('key', None)
        if key is not None:
            print("Warning: pii {} is a duplicate with info={}"
                  .format(pii,info))
            continue;
        d_pii_info[pii] = info

    return d_pii_info()

def run(output_folder_name=None):
    d_pii_info = get_pii_info()

    for pii,info in piis:
        save_entitled_xml_for_pii(pii, output_folder_name)

#
