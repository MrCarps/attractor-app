# attractor-app
Project developed for Python course.

This app is to explore some strange attractors as e.g. the Lorenz Attractor which are chaotic systems of differential equations.
Although they are chaotic, some stationary solutions can be found, which are plottet within the app. Sliders can be used to 
tweak the parameters ever so slightly and watch the big differences that happen from small adjustments of the input (chaotic
system).
Since attractors are differential equations, they must be solved in order to plot them. There are however numerous methods of 
solving such equations some of which are featured in this app. Those can be compared (some of them are faster but less accurate)
and the timestep for the solvers can be adjusted with a slider to get a feeling of how important the right timestep is when 
solving differential equations. The solvers can also be compared in terms of average calculation speed (for one timestep) and
estimated local error occured during this calculation.
