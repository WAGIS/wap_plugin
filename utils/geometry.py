class Line2D():   
    """
        Class used to create a line 2D with comparative properties.

        ...

        Attributes
        ----------


        Methods
        -------

    """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.x1 = p1[0]
        self.y1 = p1[1]
        self.x2 = p2[0]
        self.y2 = p2[1]

    def getP1(self):
        """
            Return the point 1.
        """
        return self.p1

    def getP2(self):
        """
            Return the point 2.
        """
        return self.p2

    def getX1(self):
        """
            Return the coordinate x of the point 1.
        """
        return self.x1

    def getY1(self):
        """
            Return the coordinate y of the point 1.
        """
        return self.y1

    def getX2(self):
        """
            Return the coordinate x of the point 2.
        """
        return self.x2

    def getY2(self):
        """
            Return the coordinate y of the point 2.
        """
        return self.y2
    
    def __str__(self):
        return 'Line from {} to {}'.format(self.p1, self.p2)

    def __repr__(self):
        return str(self)
    
    def __eq__(self, compLine):
        if isinstance(compLine, Line2D):
            return self.p1 == compLine.getP1() and self.p2 == compLine.getP2()
        return False
    
    def intersectsLine(self, compLine):
        # print(self)
        # print(compLine)

        o1 = getOrientation(self.p1, self.p2, compLine.getP1())
        o2 = getOrientation(self.p1, self.p2, compLine.getP2())
        o3 = getOrientation(compLine.getP1(), compLine.getP2(), self.p1)
        o4 = getOrientation(compLine.getP1(), compLine.getP2(), self.p2)

        if o1 != o2 and o3 != o4:
            return True
        if o1 == 0 and isOnSegment(self.p1, self.p2, compLine.getP1()):
            return True
        if o2 == 0 and isOnSegment(self.p1, self.p2, compLine.getP2()):
            return True
        if o3 == 0 and isOnSegment(compLine.getP1(), compLine.getP2(), self.p1):
            return True
        if o4 == 0 and isOnSegment(compLine.getP1(), compLine.getP2(), self.p2):
            return True
        return False
    
    def connectsLine(self, compLine):
        # print(self)
        # print(compLine)

        if self.p2 == compLine.getP1():
            return True
        if compLine.getP2() == self.p1:
            return True
        return False

def isOnSegment(A, B, C):
    # check if C lies on (A, B)
    if C[0] <= max(A[0], B[0]) and C[0] >= min(A[0], B[0]) and C[1] <= max(A[1], B[1]) and C[1] >= min(A[1], B[1]):
        return True
    return False

def getOrientation(A, B, C):
    # return 0/1/-1 for colinear/clockwise/counterclockwise
    val = ((B[1] - A[1]) * (C[0] - B[0])) - ((B[0] - A[0]) * (C[1] - B[1]))
    if val == 0 : 
        return 0
    return 1 if val > 0 else -1

def isValid(polygon):
    lines2D_arr = [Line2D(polygon[idx], polygon[idx+1]) for idx in range(len(polygon)-1)]
    lines2D_arr.append(Line2D(polygon[-1], polygon[0]))

    # print(lines2D_arr)

    isValid_res = True 
    for line in lines2D_arr:
        for compLine in lines2D_arr:
            # print('Comparing {} with {}'.format(line, compLine))
            # print('They are same line: ', line is compLine)
            # print('They intersect: ', line.intersectsLine(compLine))
            # print('They connect: ', line.connectsLine(compLine))
            # print('')
            # if line.intersectsLine(compLine) and not line is compLine:
            if line.intersectsLine(compLine) and not line is compLine and \
                not line.connectsLine(compLine):
                isValid_res = False
    return isValid_res