import math
import numpy


def poly_reg(x, y, m):
    # Performs polynomial regression of degree m by least squares estimation for two variable lists x and y.
    # Returns a list of polynomial coefficients p where: y = sum_i( p[i] * x ** i )

    X = list()

    for xi in x:
        X.append(list())

        for j in range(m + 1):
            X[-1].append(xi ** j)

    XT = numpy.transpose(numpy.array(X))
    XTXi = numpy.linalg.inv(numpy.dot(XT, numpy.array(X)))
    XTXiXT = numpy.dot(XTXi, XT)
    return numpy.dot(XTXiXT, numpy.array(y)).tolist()


def lin_reg(x, y):
    # Performs linear regression by least squares estimation for two variable lists x and y.
    # Returns a pair of coefficients p where: y = p[0] + p[1] * x

    return poly_reg(x, y, 1)


def lin_pol(x1, x2, y1, y2, x):
    # Calculates y for a given variable x given two points (x1, y1) and (x2, y2) by linear inter/extrapolation.
    # Returns the value y.

    poly = lin_reg(list((x1, x2)), list((y1, y2)))
    return poly[0] + poly[1] * x


def coef_det(y, f):
    # Calculates the coefficient of determination R² for a list of variables y and its predictor f.
    # Returns the coefficient R².

    Sr = sum(list((yi - fi) ** 2 for yi, fi in zip(y, f)))
    St = sum(list((yi - sum(y) / len(y)) ** 2 for yi in y))
    return 1 - Sr / St


def poly_fit(x, y, R2min, mmin=0, mmax=math.inf):
    # Determines the polynomial with the best fit for two variable lists x and y by polynomial regression.
    # The polynomial with the highest coefficient of determination R² will be returned, where: R² > R2min
    # The polynomial degree m will fall in the range: mmin <= m <= mmax
    # The polynomial degree will also be lower than the length of the input variable lists x and y.
    # Returns a tuple with first element: a list of polynomial coefficients p where: f(x) = sum_i( p[i] * x ** i )
    #   and second element: the coefficient of determination R² for f

    m = mmin
    polys = list()
    R2s = list()

    while m < min(len(y), mmax + 1):
        poly = poly_reg(x, y, m)
        f = list(sum(list(poly[i] * xi ** i for i in range(len(poly)))) for xi in x)
        R2 = coef_det(y, f)
        polys.append(poly)
        R2s.append(R2)

        if (R2 < 0 and m > 0) or R2 > R2min:
            break

        m += 1

    poly = polys[R2s.index(max(R2s))]
    R2 = max(R2s)
    return poly, R2


def poly_point(poly, x):
    # Calculates f for a polynomial f(x) given a value x and a list of polynomial coefficients p where: f(x) = sum_i( p[i] * x ** i )
    # Returns the value f.

    return sum(list(poly[i] * x ** i for i in range(len(poly))))


def poly_roots(poly):
    # Calculates the real roots of a polynomial f given a list of polynomial coefficients p where: f(x) = sum_i( p[i] * x ** i )
    # Returns the list of real roots of f.

    roots = numpy.polynomial.polynomial.polyroots(numpy.array(poly)).tolist()
    return list(i.real for i in roots if i.imag == 0)


def poly_dif(poly):
    # Calculates the derivative g of a polynomial f given a list of polynomial coefficients p where: f(x) = sum_i( p[i] * x ** i )
    # Returns a list of derivative coefficients q where: g(x) = sum_i( q[i] * x ** i )

    if len(poly) == 1:
        return list((0,))

    return list(poly[i] * i for i in range(1, len(poly)))


def poly_int(poly, intercept):
    # Calculates the integral g of a polynomial f given a list of polynomial coefficients p where: f(x) = sum_i( p[i] * x ** i )
    # The integral g will have the intercept supplied.
    # Returns a list of integral coefficients q where: g(x) = sum_i( q[i] * x ** i )

    output = list(poly[i] / (i + 1) for i in range(len(poly)))
    output.insert(0, intercept)
    return output
