"""
Simple proposal-writing experiment: For a given signal-to-noise in a line, what
signal-to-noise do you get in a derived parameter (e.g., temperature)?
"""
import pyradex
import pylab as pl
import numpy as np
import matplotlib
import astropy.units as u
import os

# for pretty on-screen plots
if os.path.exists('/Users/adam/.matplotlib/ggplotrc'):
    matplotlib.rc_file('/Users/adam/.matplotlib/ggplotrc')

# Download the data file if it's not here already
if not os.path.exists('ph2co-h2.dat'):
    import urllib
    urllib.urlretrieve('http://home.strw.leidenuniv.nl/~moldata/datafiles/ph2co-h2.dat')

# Formatting tool
def latex_float(f):
    float_str = "{0:.1g}".format(f)
    if "e" in float_str:
        base, exponent = float_str.split("e")
        return r"{0} \times 10^{{{1}}}".format(base, int(exponent))
    else:
        return float_str

# Define the grid parameters
ntemp = 25
temperatures = np.linspace(10,100,ntemp)

# initial density; will be modified later
density = 1e4

deltav = 1.0 # km/s

for abundance in (10**-8.5,10**-9):
    for nh2 in (1e22,1e23):

        R = pyradex.Radex(species='ph2co-h2',
                          abundance=abundance,
                          collider_densities={'H2':density},
                          deltav=1.0,
                          column=None,
                          temperature=temperatures[0],
                          h2column=nh2)

        pl.figure(1)
        pl.clf()

        for temperature in [10,50,100]:
            R.temperature = temperature
            R.run_radex()
            S = pyradex.synthspec.SyntheticSpectrum(218.2*u.GHz,218.8*u.GHz,R.get_table(),linewidth=10*u.km/u.s)
            S.plot(label='%i K' % temperature)

        pl.legend(loc='best')

        # create a small grid...
        densities = [10**x for x in xrange(4,7)]
        ratio = {d:[] for d in densities}
        f1 = {d:[] for d in densities}
        f2 = {d:[] for d in densities}

        for density in densities:
            R.density = {'H2': density}
            for temperature in temperatures:
                R.temperature = temperature
                print R.run_radex(),

                F1 = R.T_B[2]
                F2 = R.T_B[12]

                ratio[density].append(F2/F1)
                f2[density].append(F2)
                f1[density].append(F1)
            print

        f1 = {d:np.array([x.value for x in f1[d]]) for d in densities}
        f2 = {d:np.array([x.value for x in f2[d]]) for d in densities}
        ratio = {d:np.array(ratio[d]) for d in densities}

        pl.figure(2)
        pl.clf()

        for d in densities:
            pl.plot(ratio[d],temperatures,label='$n=10^{%i}$' % (np.log10(d)))

            m = 1/((ratio[d][15]-ratio[d][5])/(temperatures[15]-temperatures[5]))
            b = temperatures[5]-ratio[d][5]*m
            line=(m,b)
            print d,m,b
            pl.plot(ratio[d],ratio[d]*line[0]+line[1],'--')

        pl.ylabel("Temperature")
        pl.xlabel("$S(3_{2,1}-2_{2,0})/S(3_{0,3}-2_{0,2})$")
        pl.legend(loc='best',fontsize=14)
        pl.title("$N(H_2) = %s$ cm$^{-2}$, X(p-H$_2$CO)$=10^{%0.1f}$" % (latex_float(nh2),np.log10(abundance)))

        pl.axis([0,0.5,10,200,])

        pl.savefig("pH2CO_ratio_vs_temperature_N=%1.0e_X=%0.1e.pdf" % (nh2,abundance),bbox_inches='tight')

        pl.figure(3)
        pl.clf()

        for d in densities:
            L, = pl.plot(temperatures,f2[d],label='$n=10^{%i}$' % (np.log10(d)))
            pl.plot(temperatures,f1[d],'--',color=L.get_color())
        pl.xlabel("Temperature")
        pl.ylabel("$T_B(3_{2,1}-2_{2,0})$ (solid), $T_B(3_{0,3}-2_{0,2})$ (dashed)")
        ax = pl.gca()
        #pl.plot(ax.get_xlim(),[1.5,1.5],'k--',label='S/N$=5$, $\sigma=0.3$ K')
        #pl.plot(ax.get_xlim(),[2.5,2.5],'k:',label='S/N$=5$, $\sigma=0.5$ K')
        #pl.plot(ax.get_xlim(),[0.25,0.25],'k-.',label='S/N$=5$, $\sigma=0.05$ K')
        ax.axis([10,100,0,3.2])
        pl.legend(loc='best',fontsize=14)
        pl.title("$N(H_2) = %s$ cm$^{-2}$, X(p-H$_2$CO)$=10^{%0.1f}$" % (latex_float(nh2),np.log10(abundance)))

        pl.savefig("pH2CO_321-220_vs_temperature_N=%1.0e_X=%0.1e.pdf" % (nh2,abundance),bbox_inches='tight')


        pl.figure(4,figsize=(10,10))
        pl.clf()
        ax1= pl.subplot(2,1,1)

        for d in densities:
            pl.plot(temperatures,ratio[d],label='$n=10^{%i}$' % (np.log10(d)))
        #pl.xlabel("Temperature")
        pl.ylabel("$S(3_{2,1}-2_{2,0})/S(3_{0,3}-2_{0,2})$")
        pl.legend(loc='best',fontsize=18)
        pl.title("$N(H_2) = %s$ cm$^{-2}$, X(p-H$_2$CO)$=10^{%0.1f}$" % (latex_float(nh2),np.log10(abundance)))
        ax1.set_xticks([])
        pl.subplots_adjust(hspace=0.0)


        ax2 = pl.subplot(2,1,2)


        for d in densities:
            L, = pl.plot(temperatures,f2[d],dashes=[2,2],label='$n=10^{%i}$' % (np.log10(d)))
            pl.plot(temperatures,f1[d],'--',color=L.get_color())
        pl.xlabel("Temperature")
        pl.ylabel("$T_B$")
        ax2.axis([10,100,0,3.2])

        pl.legend((pl.Line2D([0],[0],dashes=[2,2],color='k'),pl.Line2D([0],[0],linestyle='--',color='k')),
                  ("$3_{2,1}-2_{2,0}$","$3_{0,3}-2_{0,2}$"),
                  fontsize=16,
                  loc='center right',
                  bbox_to_anchor=[1,1.2])

        #pl.savefig("pH2CO_321-220_vs_temperature_N=%1.0e_X=%0.1e.pdf" % (nh2,abundance),bbox_inches='tight')
        pl.savefig("pH2CO_flux_and_ratio_vs_temperature_N=%1.0e_X=%0.1e.pdf" % (nh2,abundance),bbox_inches='tight')
