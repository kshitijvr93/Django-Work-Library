
def newfunct(noarg):
    pass
    return

#y = product(a, b)
def test():
        data_elsevier_folder='abc/'
        input_folders = []
        for year in range(2000, 2018):
            input_folders.append('{}/output_ealdxml/{}/'.format(data_elsevier_folder,year))
        print("input_folders={}".format(input_folders))

test()
