value = 11
value = 32
value = 'aus_la_trobe'
kparts = value.split('_')
country = kparts[0]
institution = '_'.join(kparts[1:])
print(value, country, institution)
