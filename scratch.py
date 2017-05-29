import etl
rv = etl.get_tmp_folder_name(relative_output_folder='tmptest')
print(rv)
rv = etl.get_local_output_folder_name(relative_output_folder='test')
print(rv)
