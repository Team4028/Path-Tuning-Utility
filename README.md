# Path-Tuning-Utility

This is a repository used by FRC Team 4028 The Beak Squad to process path-following data in order to compute certain key Path-Following Constants. 

## The Problem

In general, a basic and robust basic path-following algorithm for a 1-dimensional robot attempting to follow some time-dependent motion profile computes the manipulated (output) variable at each moment in time as a position PID loop plus a three-fold feed-forward term consisting of 

1. A static feed-forward, profile independent
2. A velocity feed-forward, proportional to the intended velocity of the profile
3. An acceleration feed-forward, proportional to the intended acceleration of the profile.

This algotihm is adaptable to both swerve and tank drive in a couple of ways, but the simplest are running it on both wheels independently for tank and on the forward and strafe directions for swerve. In many cases, especially when the tuning doesn't need to be remarkably aggressive, the acceleration term may be readily ignored. Indeed, simply a velocity feed-forward equal to the reciprocal of max speed is often enough. The goal of this repository is to compute these path-following feed-forward constants from physical data on the robot. 

## The Algorithm

Depending on the desired agressiveness of the path-following, for various applications in various games it may be desired to either have a zero or a nonzero acceleration term. Therefore, both applications have been developed. 

### No acceleration

The key to the no acceleration algorithm is that the steady state velocity is linear in vbus. Consequently, the vbus to get a steady state velocity should also be linear. After doing the approprate parsing, ignoring latency and so forth, the algorithm to compute the max speed of a run given data from that run is to model the velocity of the run as a best fit sequence of 5 constant functions, spaced freely as part of the model, of time. Since the end of the run should be more or less a long constant function, this will result in at least the final segment modeling the appopriate constant max-speed quite well. To actually get the max speed then, simply apply the model to the last-time datapoint. From this, if one has 10 trials, say, one has 10 steady state velo and vbus combinations. Then we run a simple linear regression on the vbus values as a function of max-speed. The slope of this line gives the velocty feed-forward and the intercept the static feed-forward. 

The actual algorithm has one slight caveat to this, however. See, the piecewise constant fit is actually a random algorithm. So we repeat the process of getting the max speed a few hundred times and take the average of that sample for each trial, and we run a hundred or so trials of getting a full set of datapoints and path-following constants from them and average over all those trials as well. This random sampling drives up runtime substantially, but also significantly increases the accuracy of the computation, so that it is unlikely any one run will produce a value far off from the true value. Currently, the trials are set up to run in roughly the time of a half-hour television show without commercials, say *Jeopary!*, or *The Big Bang Theory* due to the recreational interests of the programmers, but the runtimes are fairly linear, so with some simple math this could easily be adapted to other time-predictable leisure activities as new people come along with new favorite methods of recreation. 

### With Acceleration

The algorithm to model with acceleration is actually quite simple. The whole equation for the feed forward considers vbus as linear combination of velocity and acceleration plus a constant static vbus. We use every data point we have as a point with a velocity, acceleration, and vbus. Hopefully you can see then that we just need to find the best fit plane of vbus as a function of acceleration and vbus. This is a special case of finding best-fit hyperplanes in more dimensions--a process called multi-linear regression. We compute a simple 3-dimensional multilinear (planar) regression on all of our data points, and the coeffcients on velocity, acceleration, and the interecept of this fit are simply the velocity, acceleration, and static feed-forwards respectively. Note that because our acceleration data comes from velocity, there is more measurement-noise to this approach, and consequently. 

## Setup Instructions
The simplest setup instructions are as follows (note this assumes the current logging practices of team 4028). 

1. Install Anaconda for your os (or otherwise get set up with python and all of the dependencies other than pwlf).
2. Open Anaconda prompt and type in `pip install pwlf`
3. Put the `process_data.py` file in the folder in which you will be working
4. Create a folder within the folder `process_data.py` exists call "Calibration". 
  5. In `AutonomousPeriodic` of the robot project to be tuned, run the robot forward (either with a forward arcade-drive or holonomic-drive command) at constant vbus that you manipulate across several trials. For each trial, move and rename the tsv output to be "Calibration/X_PERCENT.tsv" where X is vbus as a percentage. You can do this quite quickly if you're connected to the radio by WinSCP. Be sure that in  your robot project you only log the velocity and the time which will log automatically. Note that choice of measurement points needn't be a huge deal, and consequently we currently reccomend the simple set of X values {10, 20, 30, 40, 50, 60, 70, 80, 90, 100}.
6. In `process_data.py` modify the variable `running_case` to be either `'with_accel'` or `'without_accel'` as desired. In the same file, modify the `measurement_points` list to match the measured percent outputs in step 5. Dependendingly, a few other modifications can be made as specified in the comments of `process_data.py`.
7. Run `process_data.py`. Your IPython console or otherwise your python will print the computed constants. 


## The Future of This Repository
In the long run, it is likely this repository will be replaced with the FRC robot characterization tool. We eschew this approach now only because it is slightly simpler with the resources we already have to use this as a quite easy solution. That is, we maintain this repository for the present, and may continue to do so for some period of time. 


## Dependencies
* scipy
* numpy
* sklearn 
* timeit
* pwlf -- a piecewise linear (and polynomial) fit repository for python
