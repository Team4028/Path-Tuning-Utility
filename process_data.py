import scipy as sp
import numpy as np
import math as m
from sklearn.linear_model import LinearRegression
import pwlf
from timeit import default_timer as tictoc

running_case = 'with_accel'
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
        bestfit.fitfast(5) #Tunable by application
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

def unify_data():
    in_data = []
    out_data = []
    for po in measurement_points:
        cur = read(po)
        # There's a little latency, so start a few cycles in
        for ind in range(4, len(cur)):
            v = cur[ind].velo
            a = (cur[ind].velo - cur[ind - 1].velo) / (cur[ind].time - cur[ind - 1].time)
            in_data.append([v, a])
            out_data.append(po / 100)
    return in_data, out_data

def get_reg(in_d, out_d):
    i = np.array(in_d)
    o = np.array(out_d)
    reg = LinearRegression().fit(i, o)
    kFFV = reg.coef_[0]
    kFFA = reg.coef_[1]
    kFFS = reg.intercept_
    r_sq = reg.score(i, o)
    return kFFV, kFFA, kFFS, r_sq

start_time = tictoc()

accel_feed_forward = 0
velo_feed_forward = 0
static_feed_forward = 0
r_squared = 0

if running_case == 'without_accel':
    num_trials = 100
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
elif running_case == 'with_accel':
    ins, outs = unify_data()
    velo_feed_forward, accel_feed_forward, static_feed_forward, r_squared = get_reg(ins, outs)
else:
    print("INVALID CASE")
    

end_time = tictoc()

print("Velocity Feed Forward: " + str(velo_feed_forward))
print("Acceleration Feed Forward: " + str(accel_feed_forward))
print("Static Feed Forward: " + str(max(0, static_feed_forward)))
print("R-Squared: " + str(1E-5 * m.floor(r_squared * 1E5)))
print("Computation Time: " + str(end_time - start_time))


###############################################################
####################  PROGRAM OUTPUT  #########################
###############################################################
##                                                           ##
##                                                           ##
#######   WITHOUT ACCEL   #####################################
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
##                                                           ##
##                                                           ##
#######    WITH ACCEL    ######################################
##                                                           ##
##  Velocity Feed Forward: 0.005667726992668362              ##
##  Acceleration Feed Forward: 0.0014214995411802947         ##
##  Static Feed Forward: 0.01572899998212729                 ##
##  R-Squared: 0.9486600000000001                            ##
##  Computation Time: 0.05500300000005609                    ##
##                                                           ##
###############################################################
##                                                           ##
##                                                           ##
###############################################################
###############################################################
###############################################################