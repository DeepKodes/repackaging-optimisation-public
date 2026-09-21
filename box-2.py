class Box:
    
    def __init__(self, l, w, h, box_id=None):
        
        self.l = l
        self.w = w
        self.h = h
        self.box_id = box_id
    
    def volume(self):
       
        return self.l * self.w * self.h
    
    def fits_inside(self, other: "Box"):
        
        sorted_dim1 = sorted([self.l, self.w, self.h])
        sorted_dim2 = sorted([other.l, other.w, other.h])
        return all(x <= y for x, y in zip(sorted_dim1, sorted_dim2))
    
    def repack_box(self, boxes):
        
        list_boxes = sorted(boxes, key = lambda x: x.volume())
        for box in list_boxes:
            if self.fits_inside(box):
                return box
        return None
    def __repr__(self):
        
        return f'Box({self.l}, {self.w}, {self.h})'
