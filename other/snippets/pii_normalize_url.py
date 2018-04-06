# good -- am4ir.html does display:
pii = "S0001-8791(10)00161-2" #bad
pii = "S2405-6030(15)30049-2" #bad
pii = "S0370-2693(17)30100-4" #bad
pii = "S0370-2693(17)3010018-7" # bad
# bad pii = "S0001-8791(10)00021-7"

#Trial and error, find good ones that am4ir.html will display from letitias 20170512 excel file
piis_good = []

pii = "S0160412015000884" # good http://manuscript.elsevier.com/S0160412015000884/am4ir.html
piis_good.append(pii)


pii = "S0001-8791(16)30023-9" # good http://manuscript.elsevier.com/S0001879116300239/am4ir.html
piis_good.append(pii)


pii="S2210670715000219" # good: brisbane energy use http://manuscript.elsevier.com/S2210670715000219/am4ir.html
piis_good.append(pii)

pii = "S0001-706X(15)30021-8" # good http://manuscript.elsevier.com/S0001706X15300218/am4ir.html
piis_good.append(pii)

for i in range(len(piis_good)):
    pii = piis_good[i]
    pii = pii.replace('(','').replace(')','').replace('-','')

    url ="http://manuscript.elsevier.com/{}/am4ir.html".format(pii)
    print(url)

print("Done")
#
