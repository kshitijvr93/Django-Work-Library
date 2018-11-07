import os,sys
import datetime
import subprocess
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

r''' disable well-intentioned work blockage messages:
Typical interfering message:
C:\Users\podengo\AppData\Local\Programs\Python\Python36-32\lib\site-packages\
  PIL\Image.py:2575: DecompressionBombWarning:
  Image size (152546079 pixels) exceeds limit of 89478485 pixels,
  could be decompression bomb DOS attack.
  DecompressionBombWarning)1G
'''
Image.MAX_IMAGE_PIXELS = None


r'''
# This one errors out today 20181106
MAW_TESSERACT_CMD= r'c:\rvp\bin\tesseract4_tdhintz_win64_20181106.exe'

Traceback (most recent call last):
  File "C:\rvp\git\marshal\other\tmpdir\pytesseract_test.py", line 12, in <module>
    print(pytesseract.image_to_string(Image.open(r'c:\rvp\data\0017.jpg')))
  File "C:\Users\podengo\AppData\Local\Programs\Python\Python36-32\lib\site-packages\pytesseract\pytesseract.py", line 294, in image_to_string
    return run_and_get_output(*args)
  File "C:\Users\podengo\AppData\Local\Programs\Python\Python36-32\lib\site-packages\pytesseract\pytesseract.py", line 202, in run_and_get_output
    run_tesseract(**kwargs)
  File "C:\Users\podengo\AppData\Local\Programs\Python\Python36-32\lib\site-packages\pytesseract\pytesseract.py", line 178, in run_tesseract
    raise TesseractError(status_code, get_errors(error_string))
pytesseract.pytesseract.TesseractError: (3221225781, '')
'''

#see https://pypi.org/project/pytesseract/
# Section USAGE Quickstart has this code to test
MAW_TESSERACT_CMD = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
pytesseract.pytesseract.tesseract_cmd = MAW_TESSERACT_CMD

def ocr_by_pdf(pdf_file_name=None,
    removable_output_folder=None,
    dpi=300, depth=8,
    lang='eng',
    text_ext='txt', # 'txt' is a natural extension choice
    bounding_box_ext='', # todo: suggest a common extension
    verbose_ext='', # todo: suggest a common extension
    orientation_ext='', # 'osd' is suggested
    # Next param: use 'pdf' for searchable_pdf,
    # or 'hocr' for HOCR output (per tesseract docs)
    pdf_or_hocr_ext='pdf', #'pdf' or 'hocr'. Others ok?
    max_pages=2,
    remove_tifs=True,
    log_file=None,
    verbosity=1):
    '''
    IMPORTANT NOTE: The removable_output_folder will be completely removed of
    all its contents! This method will write its output files will there.

    Given input pdf_file_name, use 'pdftk my.pdf burst' to split/burst it into
    individual page-based pdf files (0001.pdf, ... NNNN.pdf) in the
    removable folder.

    For each resulting pdf page file create a 'tif' page file (0001.tif,
    ... NNNN.tif) and run tesseract ocr on each page tif to create tif
    page output files (0001.txt ... NNNN.txt)
    and hocr output files 0001.hocr... NNNN.hocr.

    See tesseract docs for the *_ext use cases:
    https://pypi.org/project/pytesseract/

    todo: accept list of extensions, each type mapped to a tesseract method,
    and if an extension maps to a method, run that and produce file with
    that extension. Easier than setting many vars and also provides
    new support that allows both
    production of searchable pdf and hocr file in one call to this method.
    '''
    me = 'ocr_by_multipdf'
    pdftk = os.path.join('C:',os.sep,'Program Files (x86)','PDFtk',
       'bin', 'pdftk',)

    convert = os.path.join('C:',os.sep,'Program Files',
       'ImageMagick-7.0.8-Q16','convert',)

    if log_file is None:
        log_file = sys.stdout
    lf = log_file

    if removable_output_folder is None:
        raise ValueError("No removable_output_folder")

    # Remove and recreate the output_directory
    try:
        shutil.rmtree(removable_output_folder)
    except Exception as exc:
        print(f"shutil.rmtree(): Ignoring exc={exc}", file=lf)
        pass

    os.makedirs(removable_output_folder, exist_ok=True)

    searchable_pdf_folder = os.path.join(removable_output_folder,
      'searchable_pdf')

    os.makedirs(removable_output_folder, exist_ok=True)
    os.makedirs(searchable_pdf_folder, exist_ok=True)

    # Copy the pdf_file_name to the removable_output_folder before working with it
    shutil.copy(pdf_file_name, removable_output_folder)

    # Create the bursted or split pages in separate pdfs for the input pdf
    cmd = f'{pdftk} {pdf_file_name} burst'
    cwd = removable_output_folder
    if verbosity > 0:
        print(f"{now()}:{me}",file=lf,flush=True)
        print(f"{now()}:{me}:searchable_pdf_folder {searchable_pdf_folder}",
          file=lf)
        print(
          f"{now()}:{me}:Bursting/splittng '{pdf_file_name}' "
          "to multiple pdf page files.", file=lf)
        print(f"{now()}:{me}:Running subprocess cmd='{cmd}',\nand cwd='{cwd}'",
          file=lf, flush=True)
    pdftk_proc = subprocess.Popen(cmd, cwd=cwd)
    pdftk_proc.wait()

    if verbosity > 0:
        print(f"{now()}:{me}:{now()}: pdftk_proc done splitting pdf pages....",
          file=lf, flush=True)

    # Now for each pdf file, convert it to tif and run tesseract on the tif
    if verbosity > 0:
        print(f"{now()}:Created temporary pdf page files.",file=lf, flush=True)

    n_pages = 0
    paths = Path(cwd).glob('pg_*.pdf')
    for path in paths:
        n_pages += 1
        stem = path.name.split('.')[0]
        abs_stem = f'{cwd}{os.sep}{stem}'
        searchable_stem = (
            f'{searchable_pdf_folder}{os.sep}{stem}_searchable')
        if verbosity > 0:
            print(
              f"\nPage {n_pages}, abs_stem={abs_stem},\nsearchable_stem="
              f"{searchable_stem}",
              file=lf, flush=True)

        if n_pages > max_pages:
            break

        # convert this page pdf to a tif
        cmd = (f'{convert} -density {dpi} {path.name} -depth '
               f'{depth} {stem}.tif')

        if verbosity > 0:
            print(
              f"{now()}:{me}:Running subprocess cmd='{cmd}',\nand cwd='{cwd}'",
              file=lf)

        convert_proc = subprocess.Popen(cmd, cwd=cwd)
        convert_proc.wait()

        print(f"{now()}:{me}:Done wait on cmd='{cmd}'",
          file=lf)

        #Use tesseract method(s) to produce output for this tif
        abs_tif_name = f'{abs_stem}.tif'

        if len(text_ext) > 0:
            if verbosity > 0:
                print(f"{now()}:Start image_to_string() on {abs_tif_name}",
                file=lf)
            text = pytesseract.image_to_string(
                Image.open(f'{abs_tif_name}'),lang=lang)
            tlen = len(text)
            if verbosity > 0:
              print(f"{now()}:image_to_string() outputted {tlen} bytes.",
              flush=True, file=lf)
            output_file_name = f'{abs_stem}.{text_ext}'
            with open(\
                output_file_name, mode='w', encoding='utf-8') as output_file:
                output_file.write(text)

        if len(bounding_box_ext) > 0:
            if verbosity > 0:
              print(
                f"{now()}:Doing bounding box calcs on tif page file {abs_tif_name}",
                file=lf)
            output = pytesseract.image_to_boxes(
                Image.open(f'{abs_tif_name}'),lang=lang)
            print(f"{now()}:Done.", flush=True, file=lf)
            output_file_name = f'{abs_stem}.{bounding_box_ext}'
            with open(output_file_name,'w') as output_file:
                output_file.write(output)

        if len(verbose_ext) > 0:
            output = pytesseract.image_to_data(
                Image.open(f'{abs_tif_name}'),lang=lang)
            output_file_name = f'{abs_stem}.{verbose_ext}'
            with open(output_file_name,'w') as output_file:
                output_file.write(output)

        if len(orientation_ext) > 0:
            output = pytesseract.image_to_osd(
                Image.open(f'{abs_tif_name}'),lang=lang)
            output_file_name = f'{abs_stem}.{orientation_ext}'
            with open(output_file_name,'w') as output_file:
                output_file.write(output)

        if ( len(pdf_or_hocr_ext) > 0
            and pdf_or_hocr_ext == 'pdf' ):
            output_file_name = f'{searchable_stem}.{pdf_or_hocr_ext}'

            if verbosity > 0:
                print(
                f"{now()}:Doing pdf_or_hocr() on tif page file {abs_tif_name} "
                f"\nto create output_file '{output_file_name}'",file=lf)
            output = pytesseract.image_to_pdf_or_hocr(
                Image.open(f'{abs_tif_name}'),lang=lang)
            if verbosity > 0:
                print(
                f"{now()}:Done pdf or hocr calcs", flush=True,file=lf)
            with open(output_file_name,'wb') as output_file:
                output_file.write(output)
        if remove_tifs == True:
            os.remove(abs_tif_name)
        lf.flush()
    #end for path in paths (pdf page files)
    return n_pages
#end  ocr_by_pdf(pdf_file_name=None,

def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def run(input_dir=None, removable_output_folder=None,
    log_file=None, max_pages=10000, remove_tifs=True,
    pdf_file_name=None, verbosity=1):
    # NOTE lang eng works OK, but lang spa causes similar error output,
    # except error differs:
    # pytesseract.pytesseract.TesseractError: (3221225477, '')

    # print(pytesseract.image_to_string( Image.open(r'c:\rvp\data\0017.jpg'),lang='fra'))
    me = 'run'
    if log_file is None:
        log_file = sys.stdout
    lf = log_file

    print(f"{me}: starting at {now()}",file=lf)

    if pdf_file_name is None or removable_output_folder is None:
        raise ValueError('Missing argument')

    '''
    Note: had to use 'convert' to convert original pdf to tif first for
    tesseract:
    $ convert -density 300 2_Enero_1921_1.pdf 2_Enero_1921_1.tif
    And that took about a minute on my pc for this 6mb pdf file.
    So may need high cap computing help for large jobs.
    '''

    print(f"{me}:Using pdf_file_name {pdf_file_name}, and calling "
      "ocr_by_pdf()", file=lf)

    n_pages = ocr_by_pdf(pdf_file_name=pdf_file_name,
      removable_output_folder=removable_output_folder,
      log_file=lf,
      remove_tifs=remove_tifs,
      max_pages=max_pages,
      pdf_or_hocr_ext='pdf',)

    print(f"{now()}:{me}: processed total of {n_pages} pdf pages.", file=lf)
    print(f"{now()}:{me}: Done!", file=lf)
#end def run()

# RUN

input_dir = os.path.join('C:',os.sep,'rvp','data',
         '20181106_alexis_chelsea_pdfs_for_tesseract', 'bohemia_for_robert',
         'bohemia_for_robert',)

removable_output_folder = os.path.join(
         'C:',os.sep,'rvp','data',
         '20181106_alexis_chelsea_pdfs_for_tesseract', 'bohemia_for_robert',
         'bohemia_for_robert','output_dir2',)

pdf_file_names = [
        '2_Enero_1921_1.pdf', #6mb
        '22_Septiembre_1935.pdf', #235mb
        ]

pdf_file_name = os.path.join(input_dir, pdf_file_names[1])

max_pages = 1
remove_tifs = False
verbosity = 1

with open(r'C:\\rvp\\data\\tesseract\\test_log.txt', mode='w') as lf:
   run(log_file=lf,
       max_pages=max_pages,
       pdf_file_name=pdf_file_name,
       removable_output_folder=removable_output_folder,
       remove_tifs=remove_tifs,
       verbosity=verbosity)
