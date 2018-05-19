import sys, os
import math

'''salinity_calculator_douglass_2010
Calculate salinity with params, with formulae and constant value Defaults
given by spreadsheet link sent by Joe Aufmuth 20180510.
'''
class SalinityPsuCalculatorDouglass2010():
    '''

    '''
    def __init__(self,verbosity=0
        ):
        self.me = 'SalinityPsuCalculatorDouglass2010'
        self.verbosity = verbosity
        #  may make a param later - resusing referenced cell names as var
        # names here too
        self.temperature_c = None  # will be set from a10 value later
        self.conductivity_mS_cm= None  # will be set from b10 value later

        self.c10 = 42.9
        self.ref_cond_at_35psu_15c = self.c10


        if verbosity > 0:
            print("{}: Initializing salinity_calculator:"
              .format(self.me))
        #end if
    # End def __init__

    def from_temperature_c_conductivity_mS_cm(self,temperature_c=None,
        conductivity_mS_cm=None
    ):
        # Calculate and return salinity in Practical Salinity Unit value
        # First calculate sub-terms to clarify the formula
        self.a10 = temperature_c
        self.b10 = conductivity_mS_cm

        #conductivity_ratio is measured conductivity/reference conductivity
        self.d10 = self.b10/self.c10

        #self.g10 is rt calculation based on a10
        self.g10 = ( 0.6766097 + 0.0200564*self.a10
          + 0.0001104259 * self.a10 ** 2
          + (-6.9698*10**-7) * self.a10**3
          + (1.0031*10**-9) * self.a10**4
        )

        # self.e10 is Conductivity ratio/rt
        self.e10 = self.d10/self.g10

        #self.f10 is dS
        self.f10 = (
          ((self.a10 -15)/(1 + 0.0162 * (self.a10-15)))
          * (0.0005
            + (-0.0056) * self.e10**0.5
            + (-0.0066) * self.e10
            + (-0.0375) * self.e10**1.5
            + (0.0636)  * self.e10**2
            + (-0.0144) * self.e10**2.5
          )
        )

        #self.h10 is calculated salnity in psu (practical salinity units)
        self.h10 = ( 0.008
          + (-0.1692  * self.e10**0.5)
          + 25.3851   * self.e10
          + 14.0941   * self.e10**1.5
          + (-7.0261) * self.e10**2
          + 2.7081    * self.e10**2.5
          + self.f10
        )
        return self.h10
    # end def from_temperature_c_conductivity_mS_cm
# end class salinity_calculator1

def get_salinity_psu(SalinityPsu=None,temperature_c=None, conductivity_mS_cm=None):
    #Check that args are not none Later
    salinity_psu = SalinityPsu.from_temperature_c_conductivity_mS_cm(
        temperature_c=temperature_c,
        conductivity_mS_cm=conductivity_mS_cm
    )
    return salinity_psu

#end def get_salinity_psu

def test_run():
    # List of test tuples of temperature_c and conductivity_mS_cm values
    l_tuple_tc = [ (19.8, 22.6)
    ]

    SalinityPsu = SalinityPsuCalculatorDouglass2010(verbosity=1)
    for tuple_tc in l_tuple_tc:
        temperature_c = tuple_tc[0]
        conductivity_mS_cm = tuple_tc[1]
        print("Using values temp={}, cond={}"
          .format(temperature_c, conductivity_mS_cm))

        salinity_psu = get_salinity_psu(SalinityPsu=SalinityPsu,
          temperature_c=temperature_c,
          conductivity_mS_cm=conductivity_mS_cm)
        print("For temp={}, cond={}, salnity_psu={}"
          .format(temperature_c, conductivity_mS_cm,salinity_psu))
#end def test_run
for x in range(10000):
    print(x)
    test_run()
