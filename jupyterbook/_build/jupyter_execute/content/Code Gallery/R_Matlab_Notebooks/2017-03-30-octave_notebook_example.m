x = [1, 2, 3]
y = [1; 2; 3]

z = x*y

x = linspace(0, 2*pi, 100);
y = sin(x);

plot(x, y)

addpath(genpath('t_tide_v1.3beta'))

pkg load signal;

t_demo
