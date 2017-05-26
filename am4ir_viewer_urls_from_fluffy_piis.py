piis= [
    'S0022347613008652',
    'S0094-5765(16)00026-6',#
    'S0370-2693(17)30153-3', #20170301
    'S2405-8963(16)30720-0',
    'S0168-9274(15)00171-3',
    'S2405-4690(16)30107-8',
    'S2352-3964(16)30183-9',
    'S1046-2023(16)30047-0', #20150906+12
    'S0370-2693(16)00088-5', #20160328+0
    'S1473-3099(16)30326-7', #20161215+6
    'S0370-2693(16)30255-6', #20160712+0
    'S0014-4835(14)00175-4', #20160315+12
    'S0022-4804(14)00580-0'  #20160315+12 -Viewer says this page contains errors mismatch (xml errors?)
    'S0003-9993(14)00931-9', #20160501+12mo
    'S0306-4530(13)00241-2', #20150412+12mo- Can not see on 20170524
    'S0022-3476(13)00865-2', #20150522+12mo - CAN NOT SEE on 20170524

    'S2212-0963(14)00023-0',
    'S0160-4120(15)00088-4', #20170131 emb date -
    'S0306-4530(15)00231-0', #20170228 emb date - public could not see on 20170524
    'S0048-9697(15)30256-4', #20170303 emb date - public could not see on 20170524
    'S0014-3057(15)00346-8', #20170305 emb date - public could not see on 20170524
    'S1090944315300132',     # 20170310 - public could not see on 20170524
    'S0048-9697(15)30299-0', # 20170316 end embargo - public could not see on 20170524
    'S2211-9124(15)00022-X', #20170302 end embargo - public *** could *** see on 20170524
    'S0022-3476(15)00815-X', #20170422 end embargo - public could not see on 20170524
    ]

for i in range(len(piis)):
    pii = piis[i]
    normal = (pii.replace('(','').replace(')','').replace('-',''))
    url = ("http://api.elsevier.com/content/article/pii/" + str(normal)
    + "?httpAccept=application/pdf&apiKey=d91051fb976425e3b5f00750cbd33d8b&cdnRedirect=true&amsRedirect=true")
    print(i+1,url)
