Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
This is mostly a trade study on the different aspects of Bare Metal Programming as opposed to **Typical Programming (TP)**. **Bare Metal Programming (BMP)** is the process of writing code that runs directly on hardware, as opposed to running on an Operating System that hosts a **Hardware Abstraction Layer (HAL)** and **Drivers** that can simplify programming in certain situations.

The following matrix rates the ease with which certain requirements can be met by programming on 3 different microcomputers:

![[Pasted image 20251005052013.png]]

Cost is self explanatory, since the price of each is easily found.

Wifi interactions can be difficult with the Arduino, since an external wifi chip is needed to connect. ESP is simpler and there are a lot of libraries for exchanging data on a connection. Raspberry pi is a bit simpler, data can be exchanged using SCP or FTP across a secure connection.

API implementation is simplest on the Raspberry pi, since there are many libraries for interacting with `.json` files. It is a lot harder on the ESP and Arduino, since they do not have a file system.

Sensor reading is easy with ESP and Arduino is easy, as there are libraries for communication protocols like **SPI**, **I²C**, **UART**, and analog voltage reading. The Pi has the same capabilities, but is managed through the HAL and Drivers, which introduce some complexity into programming at the low level. Actuator control is much the same.

Accurate timing is easier on the Pi, since it keeps time at the OS/Kernel level, many programs can reference the same clock to keep time. Arduino and ESP keep time using a counter, but 1 program would have to use it, otherwise it would be much harder to make work.

UI implementation is a nonstarter on ESP and Arduino, unless an LCD screen UI is acceptable, since they both do not have graphics processing capabilities. If this is accepted, it would still be harder.

The Raspberry Pi seems like the overall winner, so we should go with this.
# References
