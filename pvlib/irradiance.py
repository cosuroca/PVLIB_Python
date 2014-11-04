

import numpy as np
import pvl_tools 
import pandas as pd 
import pdb

def extraradiation(doy):
  '''
  Determine extraterrestrial radiation from day of year

  Parameters
  ----------

  doy : int or pandas.index.dayofyear
        Day of the year

  Returns
  -------

  Ea : float or DataFrame

        the extraterrestrial radiation present in watts per square meter
        on a surface which is normal to the sun. Ea is of the same size as the
        input doy.


  References
  ----------
  <http://solardat.uoregon.edu/SolarRadiationBasics.html>, Eqs. SR1 and SR2

  SR1       Partridge, G. W. and Platt, C. M. R. 1976. Radiative Processes in Meteorology and Climatology.
  
  SR2       Duffie, J. A. and Beckman, W. A. 1991. Solar Engineering of Thermal Processes, 2nd edn. J. Wiley and Sons, New York.

  See Also 
  --------
  pvl_disc

  '''
  Vars=locals()
  Expect={'doy': ('array','num','x>=1','x<367')}

  var=pvl_tools.Parse(Vars,Expect)

  B=2 * np.pi * var.doy / 365
  Rfact2=1.00011 + 0.034221*(np.cos(B)) + 0.00128*(np.sin(B)) + 0.000719*(np.cos(2 * B)) + 7.7e-05*(np.sin(2 * B))
  Ea=1367 * Rfact2
  return Ea

def globalinplane(SurfTilt,SurfAz,AOI,DNI,In_Plane_SkyDiffuse, GR):
  '''
  Determine the three components on in-plane irradiance

  Combines in-plane irradaince compoents from the chosen diffuse translation, ground 
  reflection and beam irradiance algorithms into the total in-plane irradiance.    

  Parameters
  ----------

  SurfTilt : float or DataFrame
          surface tilt angles in decimal degrees.
          SurfTilt must be >=0 and <=180. The tilt angle is defined as
          degrees from horizontal (e.g. surface facing up = 0, surface facing
          horizon = 90)

  SurfAz : float or DataFrame
          Surface azimuth angles in decimal degrees.
          SurfAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, south=180, East = 90, West = 270).

  AOI : float or DataFrame
          Angle of incedence of solar rays with respect
          to the module surface, from :py:mod:`pvl_getaoi`. AOI must be >=0 and <=180.

  DNI : float or DataFrame
          Direct normal irradiance (W/m^2), as measured 
          from a TMY file or calculated with a clearsky model. 
  
  In_Plane_SkyDiffuse :  float or DataFrame
          Diffuse irradiance (W/m^2) in the plane of the modules, as
          calculated by a diffuse irradiance translation function

  GR : float or DataFrame
          a scalar or DataFrame of ground reflected irradiance (W/m^2), as calculated
          by a albedo model (eg. :py:mod:`pvl_grounddiffuse`)

  Returns
  -------

  E : float or DataFrame
          Total in-plane irradiance (W/m^2)
  Eb : float or DataFrame 
          Total in-plane beam irradiance (W/m^2)
  Ediff : float or DataFrame
          Total in-plane diffuse irradiance (W/m^2)

  See also
  --------

  pvl_grounddiffuse
  pvl_getaoi
  pvl_perez
  pvl_reindl1990
  pvl_klucher1979
  pvl_haydavies1980
  pvl_isotropicsky
  pvl_kingdiffuse

  '''
  Vars=locals()
  Expect={'SurfTilt':('num','x>=0'),
      'SurfAz':('num','x>=0'),
      'AOI':('x>=0'),
      'DNI':('x>=0'),
      'In_Plane_SkyDiffuse':('x>=0'),
      'GR':('x>=0'),
      }

  var=pvl_tools.Parse(Vars,Expect)

  Eb = var.DNI*np.cos(np.radians(var.AOI)) 
  E = Eb + var.In_Plane_SkyDiffuse + var.GR
  Ediff = var.In_Plane_SkyDiffuse + var.GR


  return pd.DataFrame({'E':E,'Eb':Eb,'Ediff':Ediff})



def grounddiffuse(SurfTilt,GHI,Albedo):
    '''
    Estimate diffuse irradiance from ground reflections given irradiance, albedo, and surface tilt 

    Function to determine the portion of irradiance on a tilted surface due
    to ground reflections. Any of the inputs may be DataFrames or scalars.

    Parameters
    ----------

    SurfTilt : float or DataFrame 
             Surface tilt angles in decimal degrees. 
             SurfTilt must be >=0 and <=180. The tilt angle is defined as
             degrees from horizontal (e.g. surface facing up = 0, surface facing
             horizon = 90).

    GHI : float or DataFrame 
            Global horizontal irradiance in W/m^2.  
            GHI must be >=0.

    Albedo : float or DataFrame 
            Ground reflectance, typically 0.1-0.4 for
            surfaces on Earth (land), may increase over snow, ice, etc. May also 
            be known as the reflection coefficient. Must be >=0 and <=1.

    Returns
    -------

    GR : float or DataFrame  
            Ground reflected irradiances in W/m^2. 


    References
    ----------

    [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
        solar irradiance on inclined surfaces for building energy simulation"
        2007, Solar Energy vol. 81. pp. 254-267

    See Also
    --------

    pvl_disc
    pvl_perez
    pvl_reindl1990
    pvl_klucher1979
    pvl_haydavies1980
    pvl_isotropicsky
    pvl_kingdiffuse

    '''

    Vars=locals()
    Expect={'SurfTilt':('num'),
            'GHI':('x>=0'),
            'Albedo':('num','array','x>=0','x<=1'),
            }

    var=pvl_tools.Parse(Vars,Expect)

    GR=var.GHI*(var.Albedo)*((1 - np.cos(np.radians(var.SurfTilt)))*(0.5))


    return pd.DataFrame({'GR':GR})

def haydavies1980(SurfTilt,SurfAz,DHI,DNI,HExtra,SunZen,SunAz):

    '''
    Determine diffuse irradiance from the sky on a tilted surface using Hay & Davies' 1980 model

    
    Hay and Davies' 1980 model determines the diffuse irradiance from the sky
    (ground reflected irradiance is not included in this algorithm) on a
    tilted surface using the surface tilt angle, surface azimuth angle,
    diffuse horizontal irradiance, direct normal irradiance, 
    extraterrestrial irradiance, sun zenith angle, and sun azimuth angle.


    Parameters
    ----------

    SurfTilt : float or DataFrame
          Surface tilt angles in decimal degrees.
          SurfTilt must be >=0 and <=180. The tilt angle is defined as
          degrees from horizontal (e.g. surface facing up = 0, surface facing
          horizon = 90)

    SurfAz : float or DataFrame
          Surface azimuth angles in decimal degrees.
          SurfAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, South=180 East = 90, West = 270).

    DHI : float or DataFrame
          diffuse horizontal irradiance in W/m^2. 
          DHI must be >=0.

    DNI : float or DataFrame
          direct normal irradiance in W/m^2. 
          DNI must be >=0.

    HExtra : float or DataFrame
          extraterrestrial normal irradiance in W/m^2. 
           HExtra must be >=0.

    SunZen : float or DataFrame
          apparent (refraction-corrected) zenith
          angles in decimal degrees. 
          SunZen must be >=0 and <=180.

    SunAz : float or DataFrame
          Sun azimuth angles in decimal degrees.
          SunAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, East = 90, West = 270).

    Returns
    --------

    SkyDiffuse : float or DataFrame

          the diffuse component of the solar radiation  on an
          arbitrarily tilted surface defined by the Perez model as given in
          reference [3].
          SkyDiffuse is the diffuse component ONLY and does not include the ground
          reflected irradiance or the irradiance due to the beam.

    References
    -----------
    [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
    solar irradiance on inclined surfaces for building energy simulation"
    2007, Solar Energy vol. 81. pp. 254-267
    
    [2] Hay, J.E., Davies, J.A., 1980. Calculations of the solar radiation incident
    on an inclined surface. In: Hay, J.E., Won, T.K. (Eds.), Proc. of First
    Canadian Solar Radiation Data Workshop, 59. Ministry of Supply
    and Services, Canada.

    See Also
    --------
    pvl_ephemeris   
    pvl_extraradiation   
    pvl_isotropicsky
    pvl_reindl1990   
    pvl_perez 
    pvl_klucher1979   
    pvl_kingdiffuse
    pvl_spa

    '''

    Vars=locals()
    Expect={'SurfTilt':('num','x>=0'),
              'SurfAz':('x>=-180'),
              'DHI':('x>=0'),
              'DNI':('x>=0'),
              'HExtra':('x>=0'),
              'SunZen':('x>=0'),
              'SunAz':('x>0'),
              }
    var=pvl_tools.Parse(Vars,Expect)

    COSTT=pvl_tools.cosd(SurfTilt)*pvl_tools.cosd(SunZen) + pvl_tools.sind(SurfTilt)*pvl_tools.sind(SunZen)*pvl_tools.cosd(SunAz - SurfAz)

    RB=np.max(COSTT,0) / np.max(pvl_tools.cosd(SunZen),0.01745)

    AI=DNI / HExtra

    SkyDiffuse=DHI*((AI*(RB) + (1 - AI)*(0.5)*((1 + pvl_tools.cosd(SurfTilt)))))


    return SkyDiffuse


def isotropicsky(SurfTilt,DHI):
  '''
  Determine diffuse irradiance from the sky on a tilted surface using isotropic sky model

  Hottel and Woertz's model treats the sky as a uniform source of diffuse
  irradiance. Thus the diffuse irradiance from the sky (ground reflected
  irradiance is not included in this algorithm) on a tilted surface can
  be found from the diffuse horizontal irradiance and the tilt angle of
  the surface.

  Parameters
  ----------

  SurfTilt : float or DataFrame
      Surface tilt angles in decimal degrees. 
      SurfTilt must be >=0 and <=180. The tilt angle is defined as
      degrees from horizontal (e.g. surface facing up = 0, surface facing
      horizon = 90)
  
  DHI : float or DataFrame
      Diffuse horizontal irradiance in W/m^2.
      DHI must be >=0.


  Returns
  -------   

  SkyDiffuse : float of DataFrame

      The diffuse component of the solar radiation  on an
      arbitrarily tilted surface defined by the isotropic sky model as
      given in Loutzenhiser et. al (2007) equation 3.
      SkyDiffuse is the diffuse component ONLY and does not include the ground
      reflected irradiance or the irradiance due to the beam.
      SkyDiffuse is a column vector vector with a number of elements equal to
      the input vector(s).


  References
  ----------

  [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
  solar irradiance on inclined surfaces for building energy simulation"
  2007, Solar Energy vol. 81. pp. 254-267
  
  [2] Hottel, H.C., Woertz, B.B., 1942. Evaluation of flat-plate solar heat
  collector. Trans. ASME 64, 91.

  See also    
  --------

  pvl_reindl1990  
  pvl_haydavies1980  
  pvl_perez  
  pvl_klucher1979
  pvl_kingdiffuse
  '''

  Vars=locals()
  Expect={'SurfTilt':'x <= 180 & x >= 0 ',
      'DHI':'x>=0'
      }
  var=pvl_tools.Parse(Vars,Expect)

  SkyDiffuse=DHI * (1 + pvl_tools.cosd(SurfTilt)) * 0.5

  return SkyDiffuse


def kingdiffuse(SurfTilt,DHI,GHI,SunZen):
  '''
  Determine diffuse irradiance from the sky on a tilted surface using the King model

  King's model determines the diffuse irradiance from the sky
  (ground reflected irradiance is not included in this algorithm) on a
  tilted surface using the surface tilt angle, diffuse horizontal
  irradiance, global horizontal irradiance, and sun zenith angle. Note
  that this model is not well documented and has not been published in
  any fashion (as of January 2012).

  Parameters
  ----------

  SurfTilt : float or DataFrame
        Surface tilt angles in decimal degrees.
        SurfTilt must be >=0 and <=180. The tilt angle is defined as
        degrees from horizontal (e.g. surface facing up = 0, surface facing
        horizon = 90)
  DHI : float or DataFrame
        diffuse horizontal irradiance in W/m^2. 
        DHI must be >=0.
  GHI : float or DataFrame
        global horizontal irradiance in W/m^2. 
        DHI must be >=0.

  SunZen : float or DataFrame
        apparent (refraction-corrected) zenith
        angles in decimal degrees. 
        SunZen must be >=0 and <=180.

  Returns
  --------

  SkyDiffuse : float or DataFrame

      the diffuse component of the solar radiation  on an
      arbitrarily tilted surface as given by a model developed by David L.
      King at Sandia National Laboratories. 


  See Also
  --------

  pvl_ephemeris   
  pvl_extraradiation   
  pvl_isotropicsky
  pvl_haydavies1980   
  pvl_perez 
  pvl_klucher1979   
  pvl_reindl1990

  '''
  Vars=locals()
  Expect={'SurfTilt':('num','x>=0'),
        'SunZen':('x>=-180'),
        'DHI':('x>=0'),
        'GHI':('x>=0')
        }

  var=pvl_tools.Parse(Vars,Expect)

  SkyDiffuse=DHI*((1 + pvl_tools.cosd(SurfTilt))) / 2 + GHI*((0.012 * SunZen - 0.04))*((1 - pvl_tools.cosd(SurfTilt))) / 2

  return SkyDiffuse

def klucher1979(SurfTilt,SurfAz,DHI,GHI,SunZen,SunAz):
    '''
    Determine diffuse irradiance from the sky on a tilted surface using Klucher's 1979 model


    Klucher's 1979 model determines the diffuse irradiance from the sky
    (ground reflected irradiance is not included in this algorithm) on a
    tilted surface using the surface tilt angle, surface azimuth angle,
    diffuse horizontal irradiance, direct normal irradiance, global
    horizontal irradiance, extraterrestrial irradiance, sun zenith angle,
    and sun azimuth angle.

    Parameters
    ----------

    SurfTilt : float or DataFrame
            Surface tilt angles in decimal degrees.
            SurfTilt must be >=0 and <=180. The tilt angle is defined as
            degrees from horizontal (e.g. surface facing up = 0, surface facing
            horizon = 90)

    SurfAz : float or DataFrame
            Surface azimuth angles in decimal degrees.
            SurfAz must be >=0 and <=360. The Azimuth convention is defined
            as degrees east of north (e.g. North = 0, South=180 East = 90, West = 270).

    DHI : float or DataFrame
            diffuse horizontal irradiance in W/m^2. 
            DHI must be >=0.

    GHI : float or DataFrame
            Global  irradiance in W/m^2. 
            DNI must be >=0.

    SunZen : float or DataFrame
            apparent (refraction-corrected) zenith
            angles in decimal degrees. 
            SunZen must be >=0 and <=180.

    SunAz : float or DataFrame
            Sun azimuth angles in decimal degrees.
            SunAz must be >=0 and <=360. The Azimuth convention is defined
            as degrees east of north (e.g. North = 0, East = 90, West = 270).

    Returns
    -------
    SkyDiffuse : float or DataFrame

                the diffuse component of the solar radiation  on an
                arbitrarily tilted surface defined by the Klucher model as given in
                Loutzenhiser et. al (2007) equation 4.
                SkyDiffuse is the diffuse component ONLY and does not include the ground
                reflected irradiance or the irradiance due to the beam.
                SkyDiffuse is a column vector vector with a number of elements equal to
                the input vector(s).

    References
    ----------
    [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
    solar irradiance on inclined surfaces for building energy simulation"
    2007, Solar Energy vol. 81. pp. 254-267

    [2] Klucher, T.M., 1979. Evaluation of models to predict insolation on tilted
    surfaces. Solar Energy 23 (2), 111-114.

    See also
    --------
    pvl_ephemeris   
    pvl_extraradiation   
    pvl_isotropicsky
    pvl_haydavies1980   
    pvl_perez 
    pvl_reindl1990  
    pvl_kingdiffuse

    '''
    Vars=locals()
    Expect={'SurfTilt':('num','x>=0'),
            'SurfAz':('x>=-180'),
            'DHI':('x>=0'),
            'GHI':('x>=0'),
            'SunZen':('x>=0'),
            'SunAz':('x>=0')
            }

    var=pvl_tools.Parse(Vars,Expect)

    GHI[GHI < DHI]=DHI
    GHI[GHI < 1e-06]=1e-06

    COSTT=pvl_tools.cosd(SurfTilt)*pvl_tools.cosd(SunZen) + pvl_tools.sind(SurfTilt)*pvl_tools.sind(SunZen)*pvl_tools.cosd(SunAz - SurfAz)

    F=1 - ((DHI / GHI) ** 2)

    SkyDiffuse=DHI*((0.5*((1 + pvl_tools.cosd(SurfTilt)))))*((1 + F*(((pvl_tools.sind(SurfTilt / 2)) ** 3))))*((1 + F*(((COSTT) ** 2))*(((pvl_tools.sind(SunZen)) ** 3))))

    return SkyDiffuse


def perez(SurfTilt, SurfAz, DHI, DNI, HExtra, SunZen, SunAz, AM,modelt='allsitescomposite1990'):
  ''' 
  Determine diffuse irradiance from the sky on a tilted surface using one of the Perez models

  Perez models determine the diffuse irradiance from the sky (ground
  reflected irradiance is not included in this algorithm) on a tilted
  surface using the surface tilt angle, surface azimuth angle, diffuse
  horizontal irradiance, direct normal irradiance, extraterrestrial
  irradiance, sun zenith angle, sun azimuth angle, and relative (not
  pressure-corrected) airmass. Optionally a selector may be used to use
  any of Perez's model coefficient sets.


  Parameters
  ----------
  
  SurfTilt : float or DataFrame
          Surface tilt angles in decimal degrees.
          SurfTilt must be >=0 and <=180. The tilt angle is defined as
          degrees from horizontal (e.g. surface facing up = 0, surface facing
          horizon = 90)

  SurfAz : float or DataFrame
          Surface azimuth angles in decimal degrees.
          SurfAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, South=180 East = 90, West = 270).

  DHI : float or DataFrame
          diffuse horizontal irradiance in W/m^2. 
          DHI must be >=0.

  DNI : float or DataFrame
          direct normal irradiance in W/m^2. 
          DNI must be >=0.

  HExtra : float or DataFrame
          extraterrestrial normal irradiance in W/m^2. 
           HExtra must be >=0.
  
  SunZen : float or DataFrame
          apparent (refraction-corrected) zenith
          angles in decimal degrees. 
          SunZen must be >=0 and <=180.

  SunAz : float or DataFrame
          Sun azimuth angles in decimal degrees.
          SunAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, East = 90, West = 270).

  AM : float or DataFrame
          relative (not pressure-corrected) airmass 
          values. If AM is a DataFrame it must be of the same size as all other 
          DataFrame inputs. AM must be >=0 (careful using the 1/sec(z) model of AM
          generation)

  Other Parameters
  ----------------

  model : string (optional, default='allsitescomposite1990')

          a character string which selects the desired set of Perez
          coefficients. If model is not provided as an input, the default,
          '1990' will be used.
          All possible model selections are: 

          * '1990'
          * 'allsitescomposite1990' (same as '1990')
          * 'allsitescomposite1988'
          * 'sandiacomposite1988'
          * 'usacomposite1988'
          * 'france1988'
          * 'phoenix1988'
          * 'elmonte1988'
          * 'osage1988'
          * 'albuquerque1988'
          * 'capecanaveral1988'
          * 'albany1988'

  Returns
  --------

  SkyDiffuse : float or DataFrame

          the diffuse component of the solar radiation  on an
          arbitrarily tilted surface defined by the Perez model as given in
          reference [3].
          SkyDiffuse is the diffuse component ONLY and does not include the ground
          reflected irradiance or the irradiance due to the beam.
      

  References
  ----------

  [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
  solar irradiance on inclined surfaces for building energy simulation"
  2007, Solar Energy vol. 81. pp. 254-267

  [2] Perez, R., Seals, R., Ineichen, P., Stewart, R., Menicucci, D., 1987. A new
  simplified version of the Perez diffuse irradiance model for tilted
  surfaces. Solar Energy 39(3), 221-232.

  [3] Perez, R., Ineichen, P., Seals, R., Michalsky, J., Stewart, R., 1990.
  Modeling daylight availability and irradiance components from direct
  and global irradiance. Solar Energy 44 (5), 271-289. 

  [4] Perez, R. et. al 1988. "The Development and Verification of the
  Perez Diffuse Radiation Model". SAND88-7030

  See also
  --------
  pvl_ephemeris
  pvl_extraradiation
  pvl_isotropicsky
  pvl_haydavies1980
  pvl_reindl1990
  pvl_klucher1979
  pvl_kingdiffuse
  pvl_relativeairmass

  '''
  Vars=locals()
  Expect={'SurfTilt':('num','x>=0'),
      'SurfAz':('x>=-180'),
      'DHI':('x>=0'),
      'DNI':('x>=0'),
      'HExtra':('x>=0'),
      'SunZen':('x>=0'),
      'SunAz':('x>=0'),
      'AM':('x>=0'),
      'modelt': ('default','default=allsitescomposite1990')}

  var=pvl_tools.Parse(Vars,Expect)

  kappa = 1.041 #for SunZen in radians
  z = var.SunZen*np.pi/180# # convert to radians

  Dhfilter = var.DHI > 0
  
  
  e = ((var.DHI[Dhfilter] + var.DNI[Dhfilter])/var.DHI[Dhfilter]+kappa*z[Dhfilter]**3)/(1+kappa*z[Dhfilter]**3).reindex_like(var.SunZen)
 


  ebin = pd.Series(np.zeros(var.DHI.shape[0]),index=e.index)

  # Select which bin e falls into
  ebin[(e<1.065)]= 1
  ebin[(e>=1.065) & (e<1.23)]= 2
  ebin[(e>=1.23) & (e<1.5)]= 3
  ebin[(e>=1.5) & (e<1.95)]= 4
  ebin[(e>=1.95) & (e<2.8)]= 5
  ebin[(e>=2.8) & (e<4.5)]= 6
  ebin[(e>=4.5) & (e<6.2)]= 7
  ebin[e>=6.2] = 8

  ebinfilter=ebin>0
  ebin=ebin-1 #correct for 0 indexing
  ebin[ebinfilter==False]=np.NaN
  ebin=ebin.dropna().astype(int)

  # This is added because in cases where the sun is below the horizon
  # (var.SunZen > 90) but there is still diffuse horizontal light (var.DHI>0), it is
  # possible that the airmass (var.AM) could be NaN, which messes up later
  # calculations. Instead, if the sun is down, and there is still var.DHI, we set
  # the airmass to the airmass value on the horizon (approximately 37-38).
  #var.AM(var.SunZen >=90 & var.DHI >0) = 37;

  var.HExtra[var.HExtra==0]=.00000001 #very hacky, fix this
  delt = var.DHI*var.AM/var.HExtra

  #

  # The various possible sets of Perez coefficients are contained
  # in a subfunction to clean up the code.
  F1c,F2c = GetPerezCoefficients(var.modelt)

  F1= F1c[ebin,0] + F1c[ebin,1]*delt[ebinfilter] + F1c[ebin,2]*z[ebinfilter]
  F1[F1<0]=0;
  F1=F1.astype(float)

  F2= F2c[ebin,0] + F2c[ebin,1]*delt[ebinfilter] + F2c[ebin,2]*z[ebinfilter]
  F2[F2<0]=0
  F2=F2.astype(float)

  A = pvl_tools.cosd(var.SurfTilt)*pvl_tools.cosd(var.SunZen) + pvl_tools.sind(var.SurfTilt)*pvl_tools.sind(var.SunZen)*pvl_tools.cosd(var.SunAz-var.SurfAz); #removed +180 from azimuth modifier: Rob Andrews October 19th 2012
  A[A < 0] = 0

  B = pvl_tools.cosd(var.SunZen);
  B[B < pvl_tools.cosd(85)] = pvl_tools.cosd(85)


  #Calculate Diffuse POA from sky dome

  #SkyDiffuse = pd.Series(np.zeros(var.DHI.shape[0]),index=data.index)

  SkyDiffuse = var.DHI[ebinfilter]*( 0.5* (1-F1[ebinfilter])*(1+pvl_tools.cosd(var.SurfTilt))+F1[ebinfilter] * A[ebinfilter]/ B[ebinfilter] + F2[ebinfilter]* pvl_tools.sind(var.SurfTilt))
  SkyDiffuse[SkyDiffuse <= 0]= 0


  return pd.DataFrame({'In_Plane_SkyDiffuse':SkyDiffuse})

def GetPerezCoefficients(perezmodelt):
  ''' 
  Find coefficients for the Perez model 

  Parameters
  ----------

  perezmodelt : string (optional, default='allsitescomposite1990')

          a character string which selects the desired set of Perez
          coefficients. If model is not provided as an input, the default,
          '1990' will be used.
  
  All possible model selections are: 

          * '1990'
          * 'allsitescomposite1990' (same as '1990')
          * 'allsitescomposite1988'
          * 'sandiacomposite1988'
          * 'usacomposite1988'
          * 'france1988'
          * 'phoenix1988'
          * 'elmonte1988'
          * 'osage1988'
          * 'albuquerque1988'
          * 'capecanaveral1988'
          * 'albany1988'

  Returns
  --------

          F1coeffs : array
          F1 coefficients for the Perez model
          F2coeffs : array
          F2 coefficients for the Perez model        

  References
  ----------

  [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
  solar irradiance on inclined surfaces for building energy simulation"
  2007, Solar Energy vol. 81. pp. 254-267

  [2] Perez, R., Seals, R., Ineichen, P., Stewart, R., Menicucci, D., 1987. A new
  simplified version of the Perez diffuse irradiance model for tilted
  surfaces. Solar Energy 39(3), 221-232.

  [3] Perez, R., Ineichen, P., Seals, R., Michalsky, J., Stewart, R., 1990.
  Modeling daylight availability and irradiance components from direct
  and global irradiance. Solar Energy 44 (5), 271-289. 

  [4] Perez, R. et. al 1988. "The Development and Verification of the
  Perez Diffuse Radiation Model". SAND88-7030

  '''
  coeffdict= {'allsitescomposite1990':
            [[-0.0080,    0.5880,   -0.0620,   -0.0600,    0.0720,   -0.0220],
             [ 0.1300,    0.6830,   -0.1510,   -0.0190,    0.0660,   -0.0290],
             [ 0.3300,    0.4870,   -0.2210,    0.0550,   -0.0640,   -0.0260],
             [ 0.5680,    0.1870,   -0.2950,    0.1090,   -0.1520,   -0.0140],
             [ 0.8730,   -0.3920,   -0.3620,    0.2260,   -0.4620,    0.0010],
             [ 1.1320,   -1.2370,   -0.4120,    0.2880,   -0.8230,    0.0560],
             [ 1.0600,   -1.6000,   -0.3590,    0.2640,   -1.1270,    0.1310],
             [ 0.6780,   -0.3270,   -0.2500,    0.1560,   -1.3770,    0.2510]],
             'allsitescomposite1988':
            [[-0.0180,    0.7050,   -0.071,0,   -0.0580,    0.1020,   -0.0260],
             [ 0.1910,    0.6450,   -0.1710,    0.0120,    0.0090,   -0.0270],
             [ 0.4400,    0.3780,   -0.2560,    0.0870,   -0.1040,   -0.0250],
             [ 0.7560,   -0.1210,   -0.3460,    0.1790,   -0.3210,   -0.0080],
             [ 0.9960,   -0.6450,   -0.4050,    0.2600,   -0.5900,    0.0170],
             [ 1.0980,   -1.2900,   -0.3930,    0.2690,   -0.8320,    0.0750],
             [ 0.9730,   -1.1350,   -0.3780,    0.1240,   -0.2580,    0.1490],
             [ 0.6890,   -0.4120,   -0.2730,    0.1990,   -1.6750,    0.2370]],
          
              'sandiacomposite1988':
             [[-0.1960,    1.0840,   -0.0060,   -0.1140,    0.1800,   -0.0190],
              [0.2360,    0.5190,   -0.1800,   -0.0110,    0.0200,   -0.0380],
              [0.4540,    0.3210,   -0.2550,    0.0720,   -0.0980,   -0.0460],
              [0.8660,   -0.3810,   -0.3750,    0.2030,   -0.4030,   -0.0490],
              [1.0260,   -0.7110,   -0.4260,    0.2730,   -0.6020,   -0.0610],
              [0.9780,   -0.9860,   -0.3500,    0.2800,   -0.9150,   -0.0240],
              [0.7480,   -0.9130,   -0.2360,    0.1730,   -1.0450,    0.0650],
              [0.3180,   -0.7570,    0.1030,    0.0620,   -1.6980,    0.2360]],
              'usacomposite1988':
              [[-0.0340,    0.6710,   -0.0590,   -0.0590,    0.0860,   -0.0280],
             [ 0.2550,    0.4740,   -0.1910,    0.0180,   -0.0140,   -0.0330],
             [ 0.4270,    0.3490,   -0.2450,    0.0930,   -0.1210,   -0.0390],
             [ 0.7560,   -0.2130,   -0.3280,    0.1750,   -0.3040,   -0.0270],
             [ 1.0200,   -0.8570,   -0.3850,    0.2800,   -0.6380,   -0.0190],
             [ 1.0500,   -1.3440,   -0.3480,    0.2800,   -0.8930,    0.0370],
             [ 0.9740,   -1.5070,   -0.3700,    0.1540,   -0.5680,    0.1090],
             [ 0.7440,   -1.8170,   -0.2560,    0.2460,   -2.6180,    0.2300]],
              'france1988':
          
             [[0.0130,    0.7640,   -0.1000,   -0.0580,    0.1270,   -0.0230],
              [0.0950,    0.9200,   -0.1520,         0,    0.0510,   -0.0200],
              [0.4640,    0.4210,   -0.2800,    0.0640,   -0.0510,   -0.0020],
              [0.7590,   -0.0090,   -0.3730,    0.2010,   -0.3820,    0.0100],
              [0.9760,   -0.4000,   -0.4360,    0.2710,   -0.6380,    0.0510],
              [1.1760,   -1.2540,   -0.4620,    0.2950,   -0.9750,    0.1290],
              [1.1060,   -1.5630,   -0.3980,    0.3010,   -1.4420,    0.2120],
              [0.9340,   -1.5010,   -0.2710,    0.4200,   -2.9170,    0.2490]],
              'phoenix1988':
            [[-0.0030,    0.7280,   -0.0970,   -0.0750,    0.1420,   -0.0430],
              [0.2790,    0.3540,   -0.1760,    0.0300,   -0.0550,   -0.0540],
              [0.4690,    0.1680,   -0.2460,    0.0480,   -0.0420,   -0.0570],
              [0.8560,   -0.5190,   -0.3400,    0.1760,   -0.3800,   -0.0310],
              [0.9410,   -0.6250,   -0.3910,    0.1880,   -0.3600,   -0.0490],
              [1.0560,   -1.1340,   -0.4100,    0.2810,   -0.7940,   -0.0650],
              [0.9010,   -2.1390,   -0.2690,    0.1180,   -0.6650,    0.0460],
              [0.1070,    0.4810,    0.1430,   -0.1110,   -0.1370,    0.2340]],
              'elmonte1988':
              [[0.0270,    0.7010,   -0.1190,   -0.0580,    0.1070 ,  -0.0600],
              [0.1810,    0.6710,   -0.1780,   -0.0790,    0.1940 ,  -0.0350],
              [0.4760,    0.4070,   -0.2880,    0.0540,   -0.0320 ,  -0.0550],
              [0.8750,   -0.2180,   -0.4030,    0.1870,   -0.3090 ,  -0.0610],
              [1.1660,   -1.0140,   -0.4540,    0.2110,   -0.4100 ,  -0.0440],
              [1.1430,   -2.0640,   -0.2910,    0.0970,   -0.3190 ,   0.0530],
              [1.0940,   -2.6320,   -0.2590,    0.0290,   -0.4220 ,   0.1470],
              [0.1550,    1.7230,    0.1630,   -0.1310,   -0.0190 ,   0.2770]],
              'osage1988':
             [[-0.3530,    1.4740 ,   0.0570,   -0.1750,    0.3120 ,   0.0090],
             [ 0.3630,    0.2180 ,  -0.2120,    0.0190,   -0.0340 ,  -0.0590],
             [-0.0310,    1.2620 ,  -0.0840,   -0.0820,    0.2310 ,  -0.0170],
             [ 0.6910,    0.0390 ,  -0.2950,    0.0910,   -0.1310 ,  -0.0350],
             [1.1820,   -1.3500 ,  -0.3210,    0.4080,   -0.9850 ,  -0.0880],
             [0.7640,    0.0190 ,  -0.2030,    0.2170,   -0.2940 ,  -0.1030],
             [0.2190,    1.4120 ,   0.2440,    0.4710,   -2.9880 ,   0.0340],
             [3.5780,   22.2310 , -10.7450,    2.4260,    4.8920 ,  -5.6870]],
              'albuquerque1988':
             [[0.0340,    0.5010,  -0.0940,   -0.0630,    0.1060 ,  -0.0440],
              [0.2290,    0.4670,  -0.1560,   -0.0050,   -0.0190 ,  -0.0230],
              [0.4860,    0.2410,  -0.2530,    0.0530,   -0.0640 ,  -0.0220],
              [0.8740,   -0.3930,  -0.3970,    0.1810,   -0.3270 ,  -0.0370],
              [1.1930,   -1.2960,  -0.5010,    0.2810,   -0.6560 ,  -0.0450],
              [1.0560,   -1.7580,  -0.3740,    0.2260,   -0.7590 ,   0.0340],
              [0.9010,   -4.7830,  -0.1090,    0.0630,   -0.9700 ,   0.1960],
              [0.8510,   -7.0550,  -0.0530,    0.0600,   -2.8330 ,   0.3300]],
              'capecanaveral1988':
             [[0.0750,    0.5330,   -0.1240 ,  -0.0670 ,   0.0420 ,  -0.0200],
             [ 0.2950,    0.4970,   -0.2180 ,  -0.0080 ,   0.0030 ,  -0.0290],
             [ 0.5140,    0.0810,   -0.2610 ,   0.0750 ,  -0.1600 ,  -0.0290],
             [ 0.7470,   -0.3290,   -0.3250 ,   0.1810 ,  -0.4160 ,  -0.0300],
             [ 0.9010,   -0.8830,   -0.2970 ,   0.1780 ,  -0.4890 ,   0.0080],
             [ 0.5910,   -0.0440,   -0.1160 ,   0.2350 ,  -0.9990 ,   0.0980],
             [ 0.5370,   -2.4020,    0.3200 ,   0.1690 ,  -1.9710 ,   0.3100],
             [-0.8050,    4.5460,    1.0720 ,  -0.2580 ,  -0.9500,    0.7530]],
              'albany1988':
             [[0.0120,    0.5540,   -0.0760 , -0.0520,   0.0840 ,  -0.0290],
              [0.2670,    0.4370,   -0.1940 ,  0.0160,   0.0220 ,  -0.0360],
              [0.4200,    0.3360,   -0.2370 ,  0.0740,  -0.0520 ,  -0.0320],
              [0.6380,   -0.0010,   -0.2810 ,  0.1380,  -0.1890 ,  -0.0120],
              [1.0190,   -1.0270,   -0.3420 ,  0.2710,  -0.6280 ,   0.0140],
              [1.1490,   -1.9400,   -0.3310 ,  0.3220,  -1.0970 ,   0.0800],
              [1.4340,   -3.9940,   -0.4920 ,  0.4530,  -2.3760 ,   0.1170],
              [1.0070,   -2.2920,   -0.4820 ,  0.3900,  -3.3680 ,   0.2290]],
              }
          
     
  array=np.array(coeffdict[perezmodelt])

  F1coeffs = array.T[0:3].T
  F2coeffs = array.T[3:7].T

  return F1coeffs ,F2coeffs


def reindl1990(SurfTilt,SurfAz,DHI,DNI,GHI,HExtra,SunZen,SunAz):
  '''
  Determine diffuse irradiance from the sky on a tilted surface using Reindl's 1990 model


  Reindl's 1990 model determines the diffuse irradiance from the sky
  (ground reflected irradiance is not included in this algorithm) on a
  tilted surface using the surface tilt angle, surface azimuth angle,
  diffuse horizontal irradiance, direct normal irradiance, global
  horizontal irradiance, extraterrestrial irradiance, sun zenith angle,
  and sun azimuth angle.

  Parameters
  ----------
    
  SurfTilt : DataFrame
          Surface tilt angles in decimal degrees.
          SurfTilt must be >=0 and <=180. The tilt angle is defined as
          degrees from horizontal (e.g. surface facing up = 0, surface facing
          horizon = 90)

  SurfAz : DataFrame
          Surface azimuth angles in decimal degrees.
          SurfAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, South=180 East = 90, West = 270).

  DHI : DataFrame
          diffuse horizontal irradiance in W/m^2. 
          DHI must be >=0.

  DNI : DataFrame
          direct normal irradiance in W/m^2. 
          DNI must be >=0.

  GHI: DataFrame
          Global irradiance in W/m^2. 
          GHI must be >=0.

  HExtra : DataFrame
          extraterrestrial normal irradiance in W/m^2. 
           HExtra must be >=0.

  SunZen : DataFrame
          apparent (refraction-corrected) zenith
          angles in decimal degrees. 
          SunZen must be >=0 and <=180.

  SunAz : DataFrame
          Sun azimuth angles in decimal degrees.
          SunAz must be >=0 and <=360. The Azimuth convention is defined
          as degrees east of north (e.g. North = 0, East = 90, West = 270).

  Returns
  -------

  SkyDiffuse : DataFrame

           the diffuse component of the solar radiation  on an
           arbitrarily tilted surface defined by the Reindl model as given in
           Loutzenhiser et. al (2007) equation 8.
           SkyDiffuse is the diffuse component ONLY and does not include the ground
           reflected irradiance or the irradiance due to the beam.
           SkyDiffuse is a column vector vector with a number of elements equal to
           the input vector(s).


  Notes
  -----
  
     The POAskydiffuse calculation is generated from the Loutzenhiser et al.
     (2007) paper, equation 8. Note that I have removed the beam and ground
     reflectance portion of the equation and this generates ONLY the diffuse
     radiation from the sky and circumsolar, so the form of the equation
     varies slightly from equation 8.
  
  References
  ----------

  [1] Loutzenhiser P.G. et. al. "Empirical validation of models to compute
  solar irradiance on inclined surfaces for building energy simulation"
  2007, Solar Energy vol. 81. pp. 254-267

  [2] Reindl, D.T., Beckmann, W.A., Duffie, J.A., 1990a. Diffuse fraction
  correlations. Solar Energy 45(1), 1-7.

  [3] Reindl, D.T., Beckmann, W.A., Duffie, J.A., 1990b. Evaluation of hourly
  tilted surface radiation models. Solar Energy 45(1), 9-17.

  See Also 
  ---------
  pvl_ephemeris   
  pvl_extraradiation   
  pvl_isotropicsky
  pvl_haydavies1980   
  pvl_perez 
  pvl_klucher1979   
  pvl_kingdiffuse

  '''          
  Vars=locals()
  Expect={'SurfTilt':('num','x>=0'),
      'SurfAz':('num','x>=-180'),
      'DHI':('num','x>=0'),
      'DNI':('num','x>=0'),
      'GHI':('num','x>=0'),
      'HExtra':('num','x>=0'),
      'SunZen':('num','x>=0'),
      'SunAz':('num','x>=0'),
        }

  var=pvl_tools.Parse(Vars,Expect)


  small=1e-06

  COSTT=pvl_tools.cosd(SurfTilt)*pvl_tools.cosd(SunZen) + pvl_tools.sind(SurfTilt)*pvl_tools.sind(SunZen)*pvl_tools.cosd(SunAz - SurfAz)
  RB=np.max(COSTT,0) / np.max(pvl_tools.cosd(SunZen),0.01745)
  AI=DNI / HExtra
  GHI[GHI < small]=small
  HB=DNI*(pvl_tools.cosd(SunZen))
  HB[HB < 0]=0
  GHI[GHI < 0]=0
  F=np.sqrt(HB / GHI)
  SCUBE=(pvl_tools.sind(SurfTilt*(0.5))) ** 3


  SkyDiffuse=DHI*((AI*(RB) + (1 - AI)*(0.5)*((1 + pvl_tools.cosd(SurfTilt)))*((1 + F*(SCUBE)))))

  return SkyDiffuse


