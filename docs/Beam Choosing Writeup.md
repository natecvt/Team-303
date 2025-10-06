Status: #literature 
Tags: `=this.file.tags`
Links: `=this.file.outlinks`

---
## Definitions and Assumptions

The maximum yielding of the bottom beam will occur when the middle bar is directly over the middle, placing a point-load half of its weight at the exact middle. A distributed load of the weight of the bar per unit length will be placed along the length. This is shown below:

![[Pasted image 20251005051837.png]]

where $q=m_bg/L$, $P=m_mg/2$, and

$$ R=\left(\frac{m_m}{4}+\frac{m_b}{2}\right)g $$

where $m_b$ is the mass of the bottom bar, $L$ is the length, and $m_m$ is the mass of the middle bar.

[https://haluminium.com/Product/20-series-t-slot-aluminium-extrusion-profile/](https://haluminium.com/Product/20-series-t-slot-aluminium-extrusion-profile/)

The materials will be the same in either case - aluminum 6063-T6, having a modulus of elasticity of 68.9 GPa. The difference will be in geometry, chosen between 2020 T-slot and 2040 T-slot bars.

The moment of inertia for bending will be $I_{zx}$, which is $7.2\times10^{-9}m^4$ for 2020 and $4.64\times10^{-8}m^4$ for 2040.

For the 2020 size, $q=4.905$N/m, for 2040, $q=8.829$N/m.

$L=2.584m$.

For the 2020 size, $m_b=1.292kg$, for 2040, $m_b=2.326kg$.

For the 2020 size, $R=17.13N$, for 2040, $R=22.20N$

## Deriving the Displacement

The loading function for this setup is:

$$ w(x)=R\left<x\right>^{-1}-q\left<x\right>^0-P\left<x-L/2\right>^{-1}+R\left<x-L\right>^{-1} $$

This can be converted to the shear force function $V(x)$ with

$$ V(x)=-\int{}{}{w(x)dx} $$

giving:

$$ V(x)=-R\left<x\right>^0+q\left<x\right>^1+P\left<x-L/2\right>^0-R\left<x-L\right>^0 $$

This can be converted to the bending moment function $M(x)$ with

$$ M(x)=-\int{}{}{V(x)dx} $$

giving:

$$ M(x)=R\left<x\right>^1-\frac{q}{2}\left<x\right>^2-P\left<x-L/2\right>^1+R\left<x-L\right>^1 $$

This can be converted to the curvature of displacement $\delta'(x)$ with

$$ EI_{zx}\delta'(x)=\int{}{}{M(x)dx}+c_1 $$

giving:

$$ EI_{zx}\delta'(x)=\frac{R}{2}\left<x\right>^2-\frac{q}{6}\left<x\right>^3-\frac{P}{2}\left<x-L/2\right>^2+\frac{R}{2}\left<x-L\right>^2+c_1 $$

Where $c_1$ is a constant of integration. We know by symmetry that $\delta'(x=L/2)=0$, so we can find that:

$$ c_1=-\frac{R}{2}\left(\frac{L}{2}\right)^2+\frac{q}{6}\left(\frac{L}{2}\right)^3+0-0 $$

$$ c_1=\frac{qL^3}{48}-\frac{RL^2}{8} $$

With a final integration, this can be converted to the displacement $\delta(x)$ with

$$ EI_{zx}\delta(x)=EI_{zx}\int{}{}{\delta'(x)dx}+c_2 $$

since $\delta(x=0)=0$, $c_2=0$, giving:

$$ EI_{zx}\delta(x)=\frac{R}{6}\left<x\right>^3-\frac{q}{24}\left<x\right>^4-\frac{P}{6}\left<x-L/2\right>^3+\frac{R}{6}\left<x-L\right>^3+\left(\frac{qL^3}{48}-\frac{RL^2}{8}\right)x $$

The displacement is maximized at the middle of the bar, so:

$$ \delta_\text{max}=\delta(x=L/2)=\frac{1}{EI_{zx}}\left(\frac{qL^4}{128}+\frac{RL^3}{24}\right)=\frac{L^3g}{EI_{zx}}\left(\frac{m_m}{96}+\frac{5m_b}{384}\right) $$

This gives the max displacement for the 2020 bar as $0.0214m$, and $0.0040m$ for the 2040 bar.
# References
