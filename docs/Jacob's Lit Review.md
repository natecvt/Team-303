Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
ME 4015 Literature Review J. Kennett

A laser curtain is a device that has been used in industry for a very long time. The manufacturing plant I work at currently has one for their laser cutter, so that when it is changing the bed for new material, an operator is not in the way to avoid the potential of being harmed. This seemed like a potential solution for safety in the 3D printer farm automation, so that if the operator needs to adjust the machine in any way it will shut off automatically when the light barrier is tripped. In reviewing an article by “_[Automate.org](http://Automate.org)_” they discuss a comprehensive guide to a light curtain and all the components associated with it. To explain how a light curtain operates, a transmitter produces an infrared light beam which must connect to a receiver. If there is any disconnect between the transmitter and receiver, the light curtain will signal either shutting down the machine or sound an alarm [1]. In the case of the 3D printer farm, we would implement a feature to stop the machine from moving completely but ideally keep its memory of where the print beds are and their completion times. This should not be too hard of a feat due to the nature of this sensor. The beauty of these sensors is that they are fairly customizable and can be extended for a great distance if needed. The current setup that is at my plant uses two transmitters and two receivers, and these transmitters bounce off of two mirrors that have been aligned to hit the receivers.

![[Pasted image 20251005054256.png]]
_Figure 1 Illustration of a light curtain setup for a Bystronic Byfiber Laser Cutter._

Figure 1 shown above shows the setup of the laser cutter at the manufacturing plant I work at, and the figure was created by me. Illustrated are the transmitters (T), the mirrors (M), the receiver (R), and the light beam shown as a right line. Now in reality, the light beam is not able to be seen but is shown in the context of illustrating the setup and concept. Now, in this set up the transmitters, mirrors, and receivers are stacked with two of the respective components on top of each other in one block. If at any point something crosses the beam in any position, the device will not allow the bed to change until the sensor is reset.

Now, how does this apply to an automatic 3D printer farm? Since the machine will be

automatically moving, grabbing printer beds, loading printer beds, and storing them it would be crucial if any interference introduced to the system such as human intervention, pets, children, etc. If for some reason they enter the area, the device should be able to automatically power down in order to not harm anything. While there is ideally going to be a E-Stop in addition to this system, it would be nice that as soon as something crossed this barrier the entire device stops and will not continue to move until the sensor is reset. This prevents any harm to the users and will allow for seamless human-robot interaction of the device without any worry of harm.

ME 4015 Literature Review J. Kennett

The second article to be discussed was about a variety of different position sensors and how they work. The first position sensor discussed was using a potentiometer as a position sensor. To summarize the section, using a potentiometer the distance was measured by the increase or decrease in resistance of the potentiometer. These sensors are inexpensive but are not very reliable since they are not very accurate and they will need to be replaced frequently [2]. A model of how a potentiometer works is shown below in Figure 2.

![[Pasted image 20251005054309.png]]
_Figure 2 Construction and Function of a Potentiometer [2]_

The second position sensor discussed was an inductive position sensor also known as a linear variable differential transformer or LVDT for short. The way this sensor functions is there is a capped hollow tube with three coils of wire connected to it. The first coil is wrapped along the length of the tube (primary coil) and then two others (secondary coils) are wrapped around open end and the capped end of the tube and are connected in series, which are also 180° out of phase with one another. Inside of the hollow tube there is a ferromagnetic core called the “armature” and when it is in its home position the two coils output cancels each other out; however, whenever the core is moved in either direction the phases do not cancel each other out and results in an output value. These sensors have a lot of advantages such as being highly accurate, having great resolution, have high sensitivity, and are frictionless which results in less “wear-and-tear.” Figure 3 shows an image of the sensor for added clarity on its operation [2].

![[Pasted image 20251005054422.png]]
_Figure 3 A LVDT sensor and how it operates [2]._

ME 4015 Literature Review J. Kennett

These were only 2 of the 9 sensors discussed in this article but give a lot to choose from. These sensors can be applied to the 3D printer farm in multiple ways. First, we can use a position sensor to locate where the print bed is in order to successfully grab and remove it from the printer, the second way is using it to align the print bed back into the correct position in the printer, and the third way is using it on the mechanism to move the print beds back and forth from the printer to the shelf. In my opinion, a more accurate sensor such as the LVDT sensor would be needed for the movement of the print bed in and out of the printer, and then a less accurate sensor could be used for the movement between the printer and the shelf. However, this may need more research and testing before moving forward on either.

The third article discusses a Renishaw alignment laser. While the brand of the laser itself is not crucial to what I wanted to explore, the device is what will be discussed. So, the laser alignment system works similarly to the light curtain from the first section. There is a transmitter and a receiver, the transmitter produces a laser beam that connects to the receiver; however, instead of detecting when the beam is broken, this device looks for when it is connected. According to the article, this device is very versatile and flexible. It also appears to be very accurate which would be crucial in our operation of lining up the 3D printer bed because even if the bed is < 1 mm off, it could cause issues in the print [3]. Figure 4 shows this device in use, again while this particular brand would more than likely not be ideal/overkill for what we are trying to complete in our design the basic premise has potential.

![[Pasted image 20251005054432.png]]
_Figure 4 The Renishaw XK10 laser alignment system at work [3]._

This particular brand appears to be more used in aligning components, it could have a application in the 3D printer farm automation. The general concept for how it would be applied is a receiver

ME 4015 Literature Review J. Kennett

will be mounted in some way to the printer bed/printer, and the transmitter will be connected to

the mechanism removing/inserting the print beds.

Sources:

[1] A. for, “A Comprehensive Guide to Light Curtains: Safety Applications and Emerging

Trends,” _Automate_, 2024. [https://www.automate.org/industry-insights/a-comprehensive-guide-to-](https://www.automate.org/industry-insights/a-comprehensive-guide-to-)

light-curtains-safety-applications-and-emerging-trends

[2] “Position Sensor and Linear Positional Sensors,” _Basic Electronics Tutorials_, Feb. 11, 2018.

[3] Renishaw plc, “Renishaw: Alignment lasers for machine build,” Renishaw, 2025.
# References
