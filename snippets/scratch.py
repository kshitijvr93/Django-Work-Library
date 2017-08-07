related_url='http://///a/b/c/d/e/f/g'
thumbnail_src = 'http://merrick.library.miami.edu/utils/getthumbnail/'

thumbnail_src += '/'.join(related_url.split('/')[-3:])
print(thumbnail_src)
