from math import sqrt
    
def get_variance(x):
    """
    http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
    """
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    if n-1 == 0:
        std = 0
    else:
        std = sqrt(std / float(n-1))
    return mean, std, min(x), max(x)
