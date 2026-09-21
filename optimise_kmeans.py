from current_box_fit import PackingOptimiser
from box import Box
from sklearn.cluster import KMeans
import numpy as np
from sku_dims_cls import SkuDims

class BoxDimensionsOptimiser(PackingOptimiser):
    def optimise_box_sizes(self, quantile=90, k=4, alpha=0.7):
       
        sku_dims = self.units_df[['l','w','h']].values
        best_config = None     # variable to store optimised box configuration
        best_score = float('inf')   # variable to store best score of algorithm
        best_void = None       # variable to store void fill rate of optimised boxes
        best_outlier = None    # variable to store outlier rate of optimised boxes
        
        sku_units_dims = SkuDims(self.units_df)
        largest_dims = sku_units_dims.largest_sku_dims()
        catchall_box = Box(largest_dims[0], largest_dims[1], largest_dims[2], box_id="fit_outliers_box")    # box to capture all outliers
        kmeans = KMeans(n_clusters=k, random_state=42).fit(sku_dims)    # fit KMeans clustering onto the SKU dimensions
        labels = kmeans.labels_
        box_sizes = []
        for i in range(k):
            cluster_data = sku_dims[labels==i]
            # Extract each dimension using the best quantile fit
            box_l = np.percentile(cluster_data[:, 0], quantile)
            box_w = np.percentile(cluster_data[:, 1], quantile)
            box_h = np.percentile(cluster_data[:, 2], quantile)
            box_sizes.append((box_l, box_w, box_h))
            boxes_dims = np.array(box_sizes)
            # Compare new box dimensions with minimum dimensional constraints
        boxes_dims = np.maximum(boxes_dims, np.array([self.min_dim['l'], self.min_dim['w'], self.min_dim['h']]))
        # boxes_dims = np.round(boxes_dims / 10) * 10
        boxes_dims = np.round(boxes_dims)
        possible_boxes = [Box(l,w,h,box_id=f'opt_box_{i}') for i, (l,w,h) in enumerate(boxes_dims)] # list of optimised boxes 
        
        all_boxes = possible_boxes + [catchall_box] # add outlier fit box to solution
        metrics = self.assign_boxes(all_boxes)  # calculate metrics for new solution
        avg_void_fill_rate = metrics['avg_void_fill_rate']
        box_void_fill_dict = metrics['box_void_fill']
        outlier_rate = metrics['outlier_rate']
        box_avg_void_fill = metrics['void_fill_rate_per_box']
        
        score = alpha * avg_void_fill_rate + outlier_rate  # calculate measure of performance of the algorithm
        
        if score < best_score:  # new better score found, reassign score
            best_score = score
            best_config = all_boxes
            best_void = float(avg_void_fill_rate)
            best_outlier = outlier_rate
                
        if best_config:     # new box configuration found, reassign boxes 
            self.boxes = best_config
        
        return {
            'optimised_boxes': [(b.box_id, int(b.l), int(b.w), int(b.h)) for b in self.boxes],
            'void_fill_per_box': box_void_fill_dict,
            'void_fill_rate_per_box': box_avg_void_fill,
            'avg_void_fill_rate': best_void,
            'outlier_rate': best_outlier,
            'void_fill_list': metrics['void_fill_list']
            }
