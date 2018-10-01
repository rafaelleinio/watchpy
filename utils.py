def xy_calc(xy):
	return (xy[0], 600 - xy[1] ) #invert y ax

def convert_xy_tuple(xy):
	return tuple(map(xy_calc, xy))