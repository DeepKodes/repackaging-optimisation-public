from box import Box
import numpy as np

class PackingOptimiser:
    def __init__(self, returns_data, current_boxes, min_box_dims=(200,100,50)):
    
        self.min_dim = {'l': min_box_dims[0], 'w': min_box_dims[1], 'h': min_box_dims[2]}
        # Expand units individually from returns_data by splitting on quantity column
        self.units_df = returns_data.loc[returns_data.index.repeat(returns_data['quantity'])].reset_index(drop=True)
        # Create Box instances of each box present in the current boxes dataset
        self.boxes = [Box(max(row.l, min_box_dims[0]), max(row.w, min_box_dims[1]), max(row.h, min_box_dims[2]), box_id=row.box_id) for _, row in current_boxes.iterrows()]
        
    def assign_boxes(self, boxes=None):
        
        if boxes is None:   
            boxes = self.boxes   
        void_fill_rates = []
        outliers = 0
        box_void_fill = {}
            
        for _, item in self.units_df.iterrows():    # iterate for each SKU unit
            item_box = Box(item.l, item.w, item.h)  # create Box instance for the item
            best_box = item_box.repack_box(boxes)   # check repack condition for item against all boxes in list
            if best_box:    # if a box has been found
                void_fill_rate = 1 - (item_box.volume() / best_box.volume())
                void_fill_rates.append(void_fill_rate)
                box_id = best_box.box_id
                if box_id not in box_void_fill:     # if box type has not been created yet
                    box_void_fill[box_id] = []
                box_void_fill[box_id].append(void_fill_rate)    # add each unit void fill rate to list of void fill rates for each box
            else:   # no box found, assign as outlier
                outliers += 1
        avg_void_fill_rate = np.mean(void_fill_rates) if void_fill_rates else 0
        outlier_rate = outliers / len(self.units_df)
        box_avg_void_fill = {box_id: (np.mean(rates) if rates else 0) for box_id, rates in box_void_fill.items()}   # populate mean void fill rate for each box type
        return {
            'avg_void_fill_rate': float(avg_void_fill_rate),
            'box_void_fill': box_void_fill,
            'outlier_rate': outlier_rate,
            'void_fill_rate_per_box': box_avg_void_fill,
            'void_fill_list': void_fill_rates
            }

        
