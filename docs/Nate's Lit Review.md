Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
**303 - Print Farm Automation: Methods of Locomotion**

For this review, I focused on finding ways for a robot to move in the plane of the shelf and 3D printers. This will be a challenge given the limited budget of this project, so exploring the options in this space is a needed endeavor.

**Approach 1 - 2-DOF Cable-Driven Planar Robot (CDPR)**

![[Pasted image 20251005054019.png]]
Fig 1. Kinematics of CDPR [3]

The above video shows the system setup for a robot that guides a ring using 4 cables on a programmable path within a 2D area [1]. This could be used to guide the actuating element of our system to specific points, then pick up a print bed and go somewhere else. This design uses 3 motors, 2 for control, and 1 to maintain tension on the ropes. It uses 2 pulley blocks with the tensioner rope pulling them up. There are 16 pulleys in this design, used as guides for all the ropes, though a few are nonessential [1]. An advantage of this design is that most of the actuating elements are set off to the side, making less danger for human contact while moving.

The guidance seems to be fairly accurate, I am assuming that better kinematic modelling and control algorithms will improve this (see the next video and the next paper) [2, 3].

The paper demonstrates the creation of a set of different controller types for the same type of CDPR that I propose. Following the procedures laid out in this paper, we could create a well-tuned PID controller that optimizes the motor torques and positions required to follow a path or go to a certain position. Event the Model Free (MF) PID controller developed by them produced extremely accurate results (See Figs. 5, 7, 11, 13) [3]. Another advantage of this approach is the fact that the yaw angle (denoted $\phi$ in [3]) of the robot stays within -2° to 2° throughout operation, if needed [3]. Since the strings are not perfectly damping, the system is bound to oscillate somewhat along a path or under certain tensions. This highlights the need to choose cable and chassis materials with care. Analysis can be done using the motor torques and accelerations to try and prevent resonant behavior.

**A1 Cost Analysis**

I am assuming that the end piece will be the same in all scenarios.

Since most parts can be 3D printed, the only parts that would cost much would be the motors and controllers. These may need to be upsized for a large torque requirement, but an appropriate gearbox could also be used. Stepper motors should be used for precise positioning, and a ratchet-type locking mechanism could be used to freeze the motors in place when not under motion.

Bare bones cost:

- Stepper motors (sized for 2x max torque registered in the paper, ~1.4Nm): $25-100 x 3 or 4, depending on design. Many designs include gearboxes with high ratios that step up torque further.
- Motor drivers, sized for current (2-5A): ~$20-40 x1 or 3 or 4, depending on multi-channel or switched-control designs.

This totals between $95 and $560.

**Approach 2: 2 DOF 5R Parallel Manipulators**

The video shows a 2 degree-of-freedom parallel manipulator, which is just a 5-bar linkage [4]. This simplifies the design a bit and adds a “home” position that would be fully out of the way of all printers. A downside is that the yaw of the piece at the end would not remain the same, or it couldn’t be referenced to the bar [4]. This could be solved by having a part at the end that could arbitrarily rotate the work part to any angle, then program this to compensate for the bar angle, since this angle will be known for any position.

![[Pasted image 20251005054043.png]]
Figure 2. Image and diagram of a parallel manipulator [5]

This may have the consequence of requiring more motor torque to actuate the motion of the heavy bars and the robotic apparatus at the end. To make the workspace large enough to accommodate the whole space, the bars will have to be fairly large and made of a strong material [5]. Efforts would have to be taken to optimize the workspace of this robot for the available space. The kinematic modelling of this type of system will be easier than the first approach, but designing for the workspace will present a challenge [5, 6]. Care will have to be taken to not produce undesirable effects, like where the end part goes after the 2 end linkages become colinear. This creates a scenario where further actuation by the motor can make the end move in 2 equally-likely directions: up or down.

This type of design would only need 3 motors, and would need 4 similar bars. The motors for this design could be servos instead of steppers, since the work area will need less than 180° of actuation. Servos do generally cost more than steppers, but usually do provide more force.

**A2 Cost Analysis**

Including 2 motors for positioning and 1 more for active levelling, this system would include 3 motors, 3 motor controllers, 4 bars, and 2 mounting mechanisms (could be 3D printed, need strength analysis). No sizing could be done because torque required depends heavily on accelerations and masses of the components. Assuming the same motor size as the last approach:

- Stepper motors, $25-100 x 3
- Bars, probably aluminum, around 5-6 feet each, $60-84 x 4
- Mounting mechanisms, machined out of aluminum or steel stock $110 x 2, plus a small amount for bearings and attachment ~$10.

This totals to between $545-866.

**Conclusions**

Approach 1 seems to be the clear winner in terms of cost, but there are many other factors to consider including repeatability, ease of control, and vibrational concerns. With approach 1, the cables could wear over time, stretching and creating the need for periodic calibration. Approach 2 would create the need to compensate for the change in bar angle in order to level the work piece. This would add cost to the system and complicate the work piece design somewhat. Currently, approach 1 seems to be the overall winner, but a trade study would have to be done to know for sure.

**References**

[1] “A Three-Actuator Cable-Driven Parallel Robot with a Rectangular Workspace,” YouTube, [https://www.youtube.com/watch?v=qmGK_-rO6Ds](https://www.youtube.com/watch?v=qmGK_-rO6Ds) (accessed Sep. 11, 2025).

[2] M. Arslan and L. Birglen, “Open-Source Planar Cable-Driven Parallel Robot: Interpolated Trajectory,” YouTube, [https://www.youtube.com/watch?v=gsjz_0bn3mc](https://www.youtube.com/watch?v=gsjz_0bn3mc) (accessed Sep. 11, 2025).

[3] C. Sancak, M. Itik, and T. T. Nguyen, “Position control of a fully constrained planar cable-driven parallel robot with unknown or partially known dynamics,” _IEEE/ASME Transactions on Mechatronics_, vol. 28, no. 3, pp. 1605–1615, Jun. 2023. doi:10.1109/tmech.2022.3228444

[4] T. D. Le, YouTube, [https://www.youtube.com/watch?v=vVCAzG0RxTs](https://www.youtube.com/watch?v=vVCAzG0RxTs) (accessed Sep. 11, 2025).

[5] X.-J. Liu, J. Wang, and G. Pritschow, “Kinematics, singularity and workspace of planar 5R symmetrical parallel mechanisms,” _Mechanism and Machine Theory_, vol. 41, no. 2, pp. 145–169, Feb. 2006. doi:10.1016/j.mechmachtheory.2005.05.004

[6] J. Jesús Cervantes-Sánchez, J. César Hernández-Rodríguez, and J. Angeles, “On the kinematic design of the 5R planar, symmetric manipulator,” _Mechanism and Machine Theory_, vol. 36, no. 11–12, pp. 1301–1313, Nov. 2001. doi:10.1016/s0094-114x(01)00053-2
# References
