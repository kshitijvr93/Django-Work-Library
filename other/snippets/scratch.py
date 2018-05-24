import re

def testme():
    line = '1	06.11.2017 00:00:00	24.01	0.01	0.00	1493.63'
    rx_star_reading = (
         r"(?P<sn>\d+)\s\s*(?P<dd>.*)/.(?P<mm>.*)/.(?P<y4>.*)"
         r"\s\s*(?P<hr>\d):(?P<min>\d.*):(?P<sec>(\d+(\.\d*)))"
         r"\s+(?P<temperature_c>(\d+(\.\d*)))"
         r"\s+(?P<salinity_psu>(\d+(\.\d*)))"
         r"\s+(?P<conductivity_mS_cm>\d+(\.\d*))"
         r"\s+(?P<sound_velocity_m_sec>(\d+(\.\d*)))"
    )

    rx_test = (
         r"(?P<sn>\d+)\s*(?P<dd>\d+)\.(?P<mm>\d+)\.(?P<y4>\d+)"
         r"\s\s*(?P<hr>\d+):(?P<min>\d+):(?P<sec>(\d+))"
         r"\s+(?P<temperature_c>(\d+(\.\d*)))"
                  r"\s+(?P<salinity_psu>(\d+(\.\d*)))"
            r"\s+(?P<conductivity_mS_cm>(\d+(\.\d*)))"
          r"\s+(?P<sound_velocity_m_sec>(\d+(\.\d*)))"
         )
    rx2= (
         r"\s*(?P<dd>.*)\.(?P<mm>.*)\.(?P<y4>.*)"
         r"\s\s*(?P<hr>\d):(?P<min>\d.*):(?P<sec>(\d+(\.\d*)))"
                 r"\s+(?P<temperature_c>(\d+(\.\d*)))"
                  r"\s+(?P<salinity_psu>(\d+(\.\d*)))"
            r"\s+(?P<conductivity_mS_cm>(\d+(\.\d*)))"
          r"\s+(?P<sound_velocity_m_sec>(\d+(\.\d*)))"
         )

    try:
        data_match = re.search(rx_test, line)
    except Exception as ex:
        line_count = 1
        msg=('line={} rx_test fails'
            .format(line_count))
        raise ValueError(msg)

    print("got line={}, rx={}".format(line, rx_test))
    sn = data_match.group("sn")
    print("sn={}".format(sn))

    dd = data_match.group("dd")
    print("dd={}".format(dd))

    mm = data_match.group("mm")
    print("mm={}".format(mm))

    y4 = data_match.group("y4")
    print("y4={}".format(y4))

    sec = data_match.group("sec")
    print("sec={}".format(sec))

    temp = data_match.group("temperature_c")
    print("temp={}".format(temp))
    svel = data_match.group("sound_velocity_m_sec")
    print("svel={}".format(svel))
    return

#testme()
#20180523 evian tan code from her github... but it does not pass python syntax checks,
#probably experimental.
#
def generate(numRows):
    res = [[1]]
    for i in range(1, numRows):
        res += [map((lambda x,y: x+y), res[-1]+[0], [0]+res[-1])]
    return res[:numRows]

generate(5)
