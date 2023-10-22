import time


class PID:
    def __init__(self, Kp=0.2, Ki=0.0, Kd=0.0):
        self.Kp = Kp  # Proportional Gain
        self.Ki = Ki  # Integral Gain
        self.Kd = Kd  # Derivative Gain
        self.sample_time = 0.00  # sample time for PID update (unit: second)
        self.current_time = time.time()
        self.last_time = self.current_time

        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""
        self.SetPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 20.0

        self.output = 0.0

    def update(self, feedback_value, enable_windup=False, define_delta_time=None):
        """Calculates PID value for given reference feedback"""
        # Calculate Error
        error = self.SetPoint - feedback_value

        # Calculate Delta Error over time
        self.current_time = time.time()
        delta_error = error - self.last_error
        
        # Calculate Delta Time while `define_delta_time` is None
        if define_delta_time is None:
            delta_time = self.current_time - self.last_time
        else:
            # Apply user's defined delta time in PID calculation
            delta_time = define_delta_time

        if (delta_time >= self.sample_time) or (define_delta_time is not None):
            # Calculate P Term
            self.PTerm = self.Kp * error
            
            # Calculate I Term
            self.ITerm += error * delta_time
            # Apply windup guard for I Term
            if enable_windup:
                if (self.ITerm < -self.windup_guard):
                    self.ITerm = -self.windup_guard
                elif (self.ITerm > self.windup_guard):
                    self.ITerm = self.windup_guard

            # Calculate D Term
            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            # update lastest time and error for next iteration
            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
            
        return self.output

    def set_kp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain

    def set_ki(self, integral_gain):
        """Determines how aggressively the PID reacts over time with setting Integral Gain"""
        self.Ki = integral_gain

    def set_kd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the change in error with setting Derivative Gain"""
        self.Kd = derivative_gain

    def set_target(self, target):
        """Sets PID target value"""
        self.SetPoint = target

    def set_windup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral term accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting."""
        self.windup_guard = windup

    def set_sample_time(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sample time, the PID decides if it should compute or return immediately."""
        self.sample_time = sample_time
