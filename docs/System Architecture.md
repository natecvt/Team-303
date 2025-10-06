Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
A diagram of the relevant systems, subsystems, and functions in our system:

```mermaid
---
config:
  layout: dagre
  themeVariables:
    fontSize: '40px'
---
flowchart TD
 subgraph s1["Subsystems"]
        B["SS1: Plate Storage"]
        C["SS2: Locomotion"]
        D["SS3: Door Opener"]
        E["SS4: Plate Effector"]
  end
 subgraph s2["Configuration Items"]
        F[/"CI1.1: Clean<br>Plate Storage"\\]
        G[/"CI1.2: Printed<br>Plate Storage"\\]
        H[/"CI2.1: Actuation<br>and Control"\\]
        I[/"CI2.2: Electrical<br>Power and Driving"\\]
        J[/"CI3.1: Mechanical<br>Power"\\]
        K[/"CI3.2: Opening<br>Mechanism"\\]
        L[/"CI4.1: Removing<br>Mechanism"\\]
        M[/"CI4.2: Mechanical<br>Power"\\]
  end
 subgraph s3["Functions"]
        N["F1.1.1: Hold <br>clean plates"]
        V["F1.1.2: Dispense <br>clean plates"]
        O["F1.2.1: Hold <br>printed plates"]
        P["F2.1.1: Move <br>manipulator between <br>printers and print storage"]
        Q["F2.2.1: Delivers<br>power to all actuators"]
        R["F3.1.1: Drives <br> actuators"]
        S["F3.2.1: Open and <br>close door"]
        T["F4.1.1: <br>Ejects Prints"]
        X["F4.1.2: Holds <br> plates for locomotion"]
        U["F4.2.1: Provide <br>Power to system"]

  end
    A(("System")) --> B & C & D & E
    B --> F & G
    C --> H & I
    D --> J & K
    E --> L & M
    F --> N & V
    G --> O
    H --> P
    I --> Q
    J --> R
    K --> S
    L --> T & X
    M --> U
    B@{ shape: rounded}
    C@{ shape: rounded}
    D@{ shape: rounded}
    E@{ shape: rounded}
    N@{ shape: triangle}
    O@{ shape: triangle}
    P@{ shape: triangle}
    Q@{ shape: triangle}
    R@{ shape: triangle}
    S@{ shape: triangle}
    T@{ shape: triangle}
    U@{ shape: triangle}
    V@{ shape: tri}
    X@{ shape: tri}
    style B fill:#FFF9C4
    style C fill:#FFF9C4
    style D fill:#FFF9C4
    style E fill:#FFF9C4
    style F fill:#C8E6C9
    style G fill:#C8E6C9
    style H fill:#C8E6C9
    style I fill:#C8E6C9
    style J fill:#C8E6C9
    style K fill:#C8E6C9
    style L fill:#C8E6C9
    style M fill:#C8E6C9
    style N fill:#BBDEFB
    style O fill:#BBDEFB
    style P fill:#BBDEFB
    style Q fill:#BBDEFB
    style R fill:#BBDEFB
    style S fill:#BBDEFB
    style T fill:#BBDEFB
    style U fill:#BBDEFB
    style V fill:#BBDEFB
    style X fill:#BBDEFB
    style A fill:#FFE0B2
    style s1 fill:#FFD600
    style s2 fill:#00C853
    style s3 fill:#29A2FF

```

Concepts, see [Meeting 5](https://www.notion.so/Meeting-5-26f179526f308065bbf6c12aca77c5dc?pvs=21) listed per CI:

- 1.1: carousel, Pez-dispenser type, track (for both)
- 1.2: stacked shelf, slanted shelf
- 2.1: gantry system, Roomba, cable-driven, drone
- 2.2: stepper driver, DC power supply, battery
- 3.1: individual motor, motor on effector, linear actuator inside
- 3.2: motor-driven lever, spinning star, custom handle
- 4.1: magnet/electromagnet, lever-type with top gripper, individual eject, suction cup
- 4.2: EM driver, servo, stepper motor, print head itself (modified), nothing

In image form

![[Pasted image 20251005052429.png]]
# References
