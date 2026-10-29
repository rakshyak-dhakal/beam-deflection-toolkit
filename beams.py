
def ss_center(x,beam):
    L=beam["L"]
    P=beam["P"]
    E=beam["E"]
    I=beam["I"]

    if x<=L/2:
        v=P*x*(3*L**2-4*x**2)/(48*E*I)
    else:
        v=P*(L-x)*(3*L**2-4*(L-x)**2)/(48*E*I)

    return v


def ss_point(x,beam):
    L=beam["L"]
    P=beam["P"]
    a=beam["a"]
    E=beam["E"]
    I=beam["I"]
    b=L-a

    if x<=a:
        v=P*b*x*(L**2-b**2-x**2)/(6*L*E*I)
    else:
        v=P*a*(L-x)*(L**2-a**2-(L-x)**2)/(6*L*E*I)

    return v


def ss_udl(x,beam):
    L=beam["L"]
    w=beam["w"]
    E=beam["E"]
    I=beam["I"]

    v=w*x*(L**3-2*L*x**2+x**3)/(24*E*I)

    return v


def cantilever_point(x,beam):
    L=beam["L"]
    P=beam["P"]
    E=beam["E"]
    I=beam["I"]

    v=P*x**2*(3*L-x)/(6*E*I)

    return v


def cantilever_udl(x,beam):
    L=beam["L"]
    w=beam["w"]
    E=beam["E"]
    I=beam["I"]

    v=w*x**2*(6*L**2-4*L*x+x**2)/(24*E*I)

    return v
