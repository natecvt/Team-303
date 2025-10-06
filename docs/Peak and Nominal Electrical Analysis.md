Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
There are 3 applicable voltage levels used in this project. One is the wall outlet voltage (120V), and will possess the amperage reflective of the whole system. The other is the gantry driver voltage, which we can say this will have to be above 36V, since the stepper motors will run on it. The third is the logic level (5V) which the sensors and Raspberry Pi will run on. Sensors will take up a negligible amount of power, so they will be treated as peripherals of the Raspberry Pi, making it take up the max of 5 Amps.

[Application Note on Buck Converter Efficiency](https://fscdn.rohm.com/en/products/databook/applinote/ic/power/switching_regulator/buck_converter_efficiency_app-e.pdf)

The following analysis will go up the chain of voltages from smallest to biggest. From the mid-level voltage to the lowest, a buck converter will be used, which has the characteristic equation:

$$ V_LI_L=\eta_{L/M} V_MI_M $$

where $\eta_{L/M}$ is the efficiency of the buck converter, from mid-level voltage to low. $I_L$ is the low-level current, which will be taken as the peak of all devices at that level, including the Raspberry Pi, manipulator servo and stepper motor. I’ll start by taking that. The current of all parts is:

$$ I_L=I_{RP}+ I_{ST}+I_{SV}=5+2+0.5=7.5\text{A} $$

The current reflected on the mid-level voltage is, with a (conservative) efficiency of 0.8:

$$ I_M=\frac{V_LI_L}{\eta_{L/M}V_M}=1.3A $$

The current from the door opener (if outside the manipulator), will be considered mutually exclusive from the gantry operation, and will be necessarily less. The voltage from the gantry motors reflected on the mid-level voltage will represent less current, so a calculation at that level will be enough. The max current from these will be 8A each, so 16A. The total current at the mid-level will be 17.3A, then. I will estimate another efficiency for switch-mode power supplies converting 120VAC to 36VDC, $\eta_{M/H}=0.8$ (good values of this will be above 0.9). The current reflected on the mains power lines will then be:

$$ I_{PEAK,H}=\sqrt{2}I_{RMS,H}=\sqrt{2}\frac{V_MI_M}{\eta_{M/H}V_{RMS,H}}=2\frac{V_MI_M}{\eta_{M/H}V_{PEAK,H}}=13.0A $$

This is below the common fused amount of 16A, so safe for this system. The RMS value of this is lower, at 9.2A.
# References
