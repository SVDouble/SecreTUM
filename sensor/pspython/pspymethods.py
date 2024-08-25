from enum import Enum

from PalmSens.Techniques import AmperometricDetection
from PalmSens.Techniques import ImpedimetricMethod
from PalmSens.Techniques.Impedance import enumScanType, enumFrequencyType


def chronoamperometry(**kwargs):
    e_deposition = kwargs.get("e_deposition", 0.0)
    t_deposition = kwargs.get("t_deposition", 0.0)
    e_conditioning = kwargs.get("e_conditioning", 0.0)
    t_conditioning = kwargs.get("t_conditioning", 0.0)
    equilibration_time = kwargs.get("equilibration_time", 0.0)
    interval_time = kwargs.get("interval_time", 0.1)
    e = kwargs.get("e", 0.0)
    run_time = kwargs.get("run_time", 1.0)
    ca = AmperometricDetection()
    ca.DepositionPotential = e_deposition
    ca.DepositionTime = t_deposition
    ca.ConditioningPotential = e_conditioning
    ca.ConditioningTime = t_conditioning
    ca.EquilibrationTime = equilibration_time
    ca.IntervalTime = interval_time
    ca.Potential = e
    ca.RunTime = run_time
    return ca


def electrochemical_impedance_spectroscopy(**kwargs):
    scan_type = kwargs.get("scan_type", 2)  # (0 = potential, 1 = time, 2 = fixed)
    freq_type = kwargs.get("freq_type", 1)  # (0 = fixed, 1 = scan)
    equilibration_time = kwargs.get("equilibration_time", 0.0)
    e_dc = kwargs.get("e_dc", 0.0)
    e_ac = kwargs.get("e_ac", 0.01)
    n_frequencies = kwargs.get("n_frequencies", 11)
    max_frequency = kwargs.get("max_frequency", 1e5)
    min_frequency = kwargs.get("min_frequency", 1e4)
    eis = ImpedimetricMethod()
    eis.ScanType = enumScanType(scan_type)
    eis.FreqType = enumFrequencyType(freq_type)
    eis.EquilibrationTime = equilibration_time
    eis.Potential = e_dc
    eis.Eac = e_ac
    eis.nFrequencies = n_frequencies
    eis.MaxFrequency = max_frequency
    eis.MinFrequency = min_frequency
    return eis


# just a test
if __name__ == "__main__":
    ca = chronoamperometry(interval_time=0.01, e=0.2, run_time=5.0)
    test = "test"
