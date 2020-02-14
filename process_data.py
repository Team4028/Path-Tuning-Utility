import scipy as sp
import numpy as np
import math as m
from sklearn.linear_model import LinearRegression
import pwlf
from timeit import default_timer as tictoc

measurement_points = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

class data_point:
    def __init__(self, m_time, m_vbus, m_velo):
        self.time = m_time
        self.vbus = m_vbus
        self.velo = m_velo
        
    def from_raw_list(rawlist, vbus):
        return data_point(rawlist[0]/1000, vbus/100, rawlist[2])

def read(percent_out):
    filename = 'Calibration/' + str(percent_out) + '_PERCENT.tsv'
    raw = list(sp.genfromtxt(filename, delimiter = '\t'))
    res = []
    for ind in range(1, len(raw)):
        res.append(data_point.from_raw_list(raw[ind], percent_out))
    return res

def average(l):
    return sum(l)/len(l)

def get_max_speed(percent_out):
    unprocessed_data = read(percent_out)
    x_vals = []
    y_vals = []
    for datum in unprocessed_data:
        x_vals.append(datum.time)
        y_vals.append(datum.velo)
    num_trials = 200
    trials = []
    for ind in range(num_trials):
        bestfit = pwlf.PiecewiseLinFit(np.array(x_vals), np.array(y_vals), degree = 0)
        bestfit.fitfast(5)
        trials.append(bestfit.predict(x_vals[-1])[0])
    return average(trials)

def run():
    steady_vbus_vals = []
    steady_velo_vals = []
    for mp in measurement_points:
        steady_vbus_vals.append(mp/100)
        steady_velo_vals.append(get_max_speed(mp))
    x = np.array(steady_velo_vals).reshape((-1, 1))
    y = np.array(steady_vbus_vals)
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)
    kFFV = model.coef_[0]
    kFFS =  model.intercept_
    return kFFV, kFFS, r_sq

start_time = tictoc()

num_trials = 100
velo_feed_forward = 0
static_feed_forward = 0
r_squared = 0

for trial in range(num_trials):
    if trial % 10 == 0 and trial > 0:
        print(str(trial) + ' trials completed')
    velo_feed_forward_add, static_feed_forward_add, r_squared_add = run()
    velo_feed_forward += velo_feed_forward_add
    static_feed_forward += static_feed_forward_add
    r_squared += r_squared_add

velo_feed_forward /= num_trials
static_feed_forward /= num_trials
r_squared /= num_trials

end_time = tictoc()

print("Velocity Feed Forward: " + str(velo_feed_forward))
print("Static Feed Forward: " + str(max(0, static_feed_forward)))
print("R-Squared: " + str(1E-5 * m.floor(r_squared * 1E5)))
print("Computation Time: " + str(end_time - start_time))

###############################################################
####################  PROGRAM OUTPUT  #########################
###############################################################
##                                                           ##
##   10 trials completed                                     ##
##   20 trials completed                                     ##
##   30 trials completed                                     ##
##   40 trials completed                                     ##
##   50 trials completed                                     ##
##   60 trials completed                                     ##
##   70 trials completed                                     ##
##   80 trials completed                                     ##
##   90 trials completed                                     ##
##   Velocity Feed Forward: 0.005811813001730558             ##
##   Static Feed Forward: 0.0016373042839475038              ##
##   R-Squared: 0.9998100000000001                           ##
##   Computation Time: 1135.0278686000001                    ##
##                                                           ##
###############################################################
###############################################################
###############################################################