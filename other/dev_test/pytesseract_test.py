import os,sys
import datetime
import subprocess
import shutil
from pathlib import Path
import pdf2image
import tempfile

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

r''' well-intentioned noisy blockage messages:
Typical noisy message:
C:\Users\podengo\AppData\Local\Programs\Python\Python36-32\lib\site-packages\
  PIL\Image.py:2575: DecompressionBombWarning:
  Image size (152546079 pixels) exceeds limit of 89478485 pixels,
  could be decompression bomb DOS attack.
  DecompressionBombWarning)

This issues when a pdf page is comprised of a large image, so not usually an
issue.
'''

# Uncomment below to not complain about pdfs with only a jpg image.
#Image.MAX_IMAGE_PIXELS = None

r'''
# This one errors out today 20181106 on UF Office PC, maybe not in linux
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

NOTE: I found a 'better' version of tesseract, and installed on my UF Office
windows 10 PC, referenced below that works
without such error messages.
'''

#see https://pypi.org/project/pytesseract/
# Section USAGE Quickstart has this code to test
MAW_TESSERACT_CMD = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
pytesseract.pytesseract.tesseract_cmd = MAW_TESSERACT_CMD

def ocr_by_pdf(pdf_file_name=None,
    removable_output_folder=None,
    dpi_pdf=320, depth=8,
    lang='eng',
    text_ext='txt', # 'txt' is a natural extension choice
    bounding_box_ext='', # todo: suggest a common extension
    dpi_jpg=300,
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
    me = 'ocr_by_pdf'
    pdftk = os.path.join('C:',os.sep,'Program Files (x86)','PDFtk',
       'bin', 'pdftk',)

    convert = os.path.join('C:',os.sep,'Program Files',
       'ImageMagick-7.0.8-Q16','convert',)

    if log_file is None:
        log_file = sys.stdout
    lf = log_file

    if removable_output_folder is None:
        raise ValueError("No removable_output_folder")

    if verbosity > 0:
        print(
          f"{now()}:{me}: STARTING: dpi_pdf={dpi_pdf}, dpi_jpg={dpi_jpg}",
          file=lf, flush=True)

    searchable_pdf_folder = os.path.join(removable_output_folder,
      'searchable_pdf')
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
        if n_pages > max_pages:
            break

        stem = path.name.split('.')[0]
        abs_stem = f'{cwd}{os.sep}{stem}'
        searchable_stem = (
            f'{searchable_pdf_folder}{os.sep}{stem}_searchable')
        if verbosity > 0:
            print(
              f"\nPage {n_pages}, {now()}: abs_stem={abs_stem},\nsearchable_stem="
              f"{searchable_stem}",
              file=lf, flush=True)

        # Try to get an image from this pdf

        n_images = 0
        abs_tif_name = f'{abs_stem}.tif'
        abs_pdf = f'{abs_stem}.pdf'

        pil_images = pdf2image.convert_from_path(abs_pdf, dpi_pdf=dpi_jpg)

        n_images = 0 if pil_images is None else len(pil_images)

        if n_images > 0:
            image = pil_images[0]
            # Translate embedded images to tif directly.
            # To start - assume a single image if any.
            # Later may encounter multi images per pdf page?
            # imageMagick/convert program creates 200x larger tif images
            # and tesseract never finds any text in those
            if verbosity > 0:
                print(
                  f"\n{now()}:Making tiff 1 of {n_images} in {abs_pdf}.",
                  file=lf, flush=True)
            with open(f'{abs_tif_name}', 'wb') as tif_output:
                image.save(tif_output, format='TIFF')
            if verbosity > 0:
                print(
                  f"\n{now()}:Made tif 1 of {n_images} in {abs_pdf}.",
                  file=lf, flush=True)

        else:
            # give imageMagick/convert a try

            # This is a simple pdf for a page- convert this page pdf to a tif
            cmd = (f'{convert} -density {dpi_pdf} {path.name} -depth '
                   f'{depth} {stem}.tif')

            if verbosity > 0:
                print(
                  f"{now()}:{me}:Running subprocess cmd='{cmd}',\nand cwd='{cwd}'",
                  file=lf)

            convert_proc = subprocess.Popen(cmd, cwd=cwd)
            convert_proc.wait()

            print(f"{now()}:{me}:Done wait on cmd='{cmd}'",
              file=lf)
        # else tried imagemagick convert
        # Now we have the tif

        # Use tesseract method(s) to produce output for this tif
        # file named by abs_tif_name

        if len(text_ext) > 0:
            if verbosity > 0:
                print(f"{now()}:Start image_to_string() on {abs_tif_name}",
                file=lf)
            text = pytesseract.image_to_string(
                Image.open(f'{abs_tif_name}'),lang=lang)
            tlen = len(text)
            if tlen <= 1:
                msg = (f"\nWARNING: file {abs_tif_name} produces 0 bytes of "
                  "text \n")
                print(msg)
            if verbosity > 0:
              print(f"{now()}:image_to_string() outputted {tlen} bytes.",
              flush=True, file=lf)
            output_file_name = f'{cwd}{os.sep}{stem}.{text_ext}'
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
#end  ocr_by_pdf()

def ocr_by_jpg(
    jpg_file_name=None,
    removable_output_folder=None,
    dpi_pdf=300, depth=8,
    lang='eng',
    text_ext='txt', # 'txt' is a natural extension choice
    bounding_box_ext='', # todo: suggest a common extension
    dpi_jpg=200,
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
    Based on ocr_by_pdf - add similar notes here as apt.
    '''

    me = 'ocr_by_jpg'

    convert_exe = os.path.join('C:',os.sep,'Program Files',
       'ImageMagick-7.0.8-Q16','convert',)

    if log_file is None:
        log_file = sys.stdout
    lf = log_file

    if removable_output_folder is None:
        raise ValueError("No removable_output_folder")
    cwd = removable_output_folder

    if verbosity > 0:
        print(
          f"{now()}:{me}: STARTING: cwd={cwd}, dpi_pdf={dpi_pdf}, dpi_jpg={dpi_jpg}",
          file=lf, flush=True)

    searchable_pdf_folder = os.path.join(removable_output_folder,
      'searchable_pdf')

    os.makedirs(removable_output_folder, exist_ok=True)
    os.makedirs(searchable_pdf_folder, exist_ok=True)

    # Copy the pdf_file_name to the removable_output_folder before working with it
    shutil.copy(input_file_name, removable_output_folder)

    n_pages = 0
    # Just one file here for jpg
    #paths = Path(cwd).glob('pg_*.pdf')
    #for path in paths:
    if 1 == 1:
        n_pages += 1

        abs_stem = jpg_file_name.split('.')[0]
        stem = os.path.basename(jpg_file_name).split('.')[0]
        searchable_stem = (
            f'{searchable_pdf_folder}{os.sep}{stem}_searchable')

        if verbosity > 0:
            print(
              f"\nPage {n_pages}, {now()}: abs_stem={abs_stem},"
              f"\nsearchable_stem={searchable_stem}",
              file=lf, flush=True)

        abs_tif_name = f'{abs_stem}.tif'
        abs_pdf = f'{abs_stem}.pdf'

        if 1 == 1:
            # give imageMagick/convert a try

            # This is a simple pdf for a page- convert this page pdf to a tif
            cmd = (f'{convert_exe} -density {dpi_pdf} {jpg_file_name} -depth '
                   f'{depth} {stem}.tif')

            if verbosity > 0:
                print(
                  f"{now()}:{me}:Running subprocess cmd='{cmd}',\nand cwd='{cwd}'",
                  file=lf)

            convert_proc = subprocess.Popen(cmd, cwd=cwd)
            convert_proc.wait()

            print(f"{now()}:{me}:Done wait on cmd='{cmd}'",
              file=lf)
        # tried imagemagick convert

        # Now we should have the tif

        # Use tesseract method(s) to produce output for this tif
        # file named by abs_tif_name

        if len(text_ext) > 0:
            if verbosity > 0:
                print(f"{now()}:Start image_to_string() on {abs_tif_name}",
                file=lf)
            text = pytesseract.image_to_string(
                Image.open(f'{abs_tif_name}'),lang=lang)
            tlen = len(text)
            if tlen <= 1:
                msg = (f"\nWARNING: file {abs_tif_name} produces 0 bytes of "
                  "text \n")
                print(msg)
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
    lang=None,log_file=None, max_pages=10000, remove_tifs=True,
    depth=8,
    input_file_name=None, dpi_pdf=300, dpi_jpg=300,verbosity=1):
    # NOTE lang eng works OK, but lang spa causes similar error output,
    # except error differs:
    # pytesseract.pytesseract.TesseractError: (3221225477, '')

    # print(pytesseract.image_to_string( Image.open(r'c:\rvp\data\0017.jpg'),lang='fra'))

    me = 'run'
    if log_file is None:
        log_file = sys.stdout
    lf = log_file

    print(f"{me}: starting at {now()}, dpi_pdf={dpi_pdf}, dpi_jpg={dpi_jpg}",
      file=lf)

    if input_file_name is None or removable_output_folder is None:
        raise ValueError('Missing argument')

    '''
    Note: had to use 'convert' to convert original pdf to tif first for
    tesseract:
    $ convert -density 300 2_Enero_1921_1.pdf 2_Enero_1921_1.tif
    And that took about a minute on my pc for this 6mb pdf file.
    So may need high cap computing help for large jobs.
    '''

    msg = (f"{me}: Using input_file_name {input_file_name}, "
           f"\n{me}: Using removable_output_folder={removable_output_folder}")
    print(msg, file=lf, flush=True)
    print(msg, file=sys.stdout, flush=True)

    extension = input_file_name.split('.')[1]
    if extension == 'pdf':

        n_pages = ocr_by_pdf(
            depth=depth,
            dpi_pdf=dpi_pdf,
            dpi_jpg=dpi_jpg,
            lang=lang,
            log_file=lf,
            max_pages=max_pages,
            pdf_file_name=input_file_name,
            pdf_or_hocr_ext='pdf',
            removable_output_folder=removable_output_folder,
            remove_tifs=remove_tifs,
            )

        print(f"{now()}:{me}: processed total of {n_pages} pdf pages.",
          file=lf)

    elif extension == 'jpg' or extension == 'jpeg' or extension == 'jp2' :
        n_pages = ocr_by_jpg(jpg_file_name=input_file_name,
            removable_output_folder=removable_output_folder,
            depth=depth,
            dpi_pdf=dpi_pdf,
            dpi_jpg=dpi_jpg,
            lang=lang,
            log_file=lf,
            remove_tifs=remove_tifs,
            max_pages=max_pages,
            pdf_or_hocr_ext='pdf',)

        print(f"{now()}:{me}: processed total of {n_pages} jpg pages."
          , file=lf)
    else:
        msg = (f"{me}:Bad extension. Skipping file {input_file_name}")
        pring(msg, file=log_file, flush=True)
        pring(msg, file=sys.stdout, flush=True)

    print(f"{now()}:{me}: Done!", file=lf)
    print(f"{now()}:{me}: Done!", file=sys.stdout, flush=True)
#end def run()

# RUN

max_pages = 5
remove_tifs = False
verbosity = 1
depth = 8
dpi_pdf = 300
dpi_jpg = 300
lang = 'eng'

input_dir = os.path.join('C:',os.sep,'rvp','data',
         '20181106_alexis_chelsea_pdfs_for_tesseract', 'bohemia_for_robert',
         'bohemia_for_robert',)

base_file_names = [
        '2_Enero_1921_1.pdf', # 0 6mb
        '22_Septiembre_1935.pdf', #1  - 235mb
        '5_Junio_1984.pdf', # 2   xmb
        '8_diciembre_1976_49.pdf', # 3 -
        '21_enero_1966_3.pdf', # 4 -
        '26_marzo_1993.pdf', # 5 -
        'aa00021018_00001_00004.jpg', # 6 -
        'aa00021018_00001_00004.jp2', # 7 -
        ]

base_index= 7
base_file_name = base_file_names[base_index]
base_stem = base_file_name.split('.')[0]

#pdf_file_name = os.path.join(input_dir, f'{pdf_stem}.pdf')
input_file_name = os.path.join(input_dir, f'{base_file_name}')

removable_output_folder = os.path.join(input_dir, 'output',f'{base_stem}',)
print(f"MAIN: Start with removable output_folder={removable_output_folder}")

# Recreate it if needed to remove it... so can see any real errors on removal
# without using rmtree's option to set ignore_errors=True.
os.makedirs(removable_output_folder,  exist_ok=True)
# Remove and recreate the removable output_directory
shutil.rmtree(removable_output_folder)

os.makedirs(removable_output_folder,  exist_ok=True)

with open(f'{removable_output_folder}{os.sep}log.txt',
    mode='w') as lf:

    run(
       depth=depth,
       dpi_pdf=dpi_pdf,
       dpi_jpg=dpi_jpg,
       lang=lang,
       log_file=lf,
       max_pages=max_pages,
       input_file_name=input_file_name,
       removable_output_folder=removable_output_folder,
       remove_tifs=remove_tifs,
       verbosity=verbosity)
