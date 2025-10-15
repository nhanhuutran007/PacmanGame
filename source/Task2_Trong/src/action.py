
class Direction:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'
    _directions = {NORTH: (0, -1),
                   SOUTH: (0, 1),
                   EAST:  (1, 0),
                   WEST:  (-1, 0),
                   STOP:  (0, 0)}
   
