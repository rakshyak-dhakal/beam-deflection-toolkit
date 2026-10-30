
import numpy as np


def ss_center(x,beam):
    x=np.asarray(x)
    L=beam["L"]
    P=beam["P"]
    E=beam["E"]
    I=beam["I"]

    v1=P*x*(3*L**2-4*x**2)/(48*E*I)
    v2=P*(L-x)*(3*L**2-4*(L-x)**2)/(48*E*I)

    return np.where(x<=L/2,v1,v2)


def ss_point(x,beam):
    x=np.asarray(x)
    L=beam["L"]
    P=beam["P"]
    a=beam["a"]
    E=beam["E"]
    I=beam["I"]
    b=L-a

    v1=P*b*x*(L**2-b**2-x**2)/(6*L*E*I)
    v2=P*a*(L-x)*(L**2-a**2-(L-x)**2)/(6*L*E*I)

    return np.where(x<=a,v1,v2)


def ss_udl(x,beam):
    x=np.asarray(x)
    L=beam["L"]
    w=beam["w"]
    E=beam["E"]
    I=beam["I"]

    v=w*x*(L**3-2*L*x**2+x**3)/(24*E*I)

    return v


def cantilever_point(x,beam):
    x=np.asarray(x)
    L=beam["L"]
    P=beam["P"]
    E=beam["E"]
    I=beam["I"]

    v=P*x**2*(3*L-x)/(6*E*I)

    return v


def cantilever_udl(x,beam):
    x=np.asarray(x)
    L=beam["L"]
    w=beam["w"]
    E=beam["E"]
    I=beam["I"]

    v=w*x**2*(6*L**2-4*L*x+x**2)/(24*E*I)

    return v
