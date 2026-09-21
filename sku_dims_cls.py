import pandas as pd

class SkuDims:
    
    def __init__(self, dataset):

        self.dataset = dataset.copy()

    def sort_dims(self):
       
        def sort_row_dims(row):
            
            dims_sorted = sorted([row['l'], row['w'], row['h']], reverse=True)
            return pd.Series(dims_sorted, index=['dim_1', 'dim_2', 'dim_3'])
        
        sorted_dims_df = self.dataset.apply(sort_row_dims, axis=1)
        
        self.dataset[['dim_1', 'dim_2', 'dim_3']] = sorted_dims_df
        return self.dataset
    
    def largest_sku_dims(self):
       
        dims = self.dataset[['l', 'w', 'h']].values
        # find SKU with maximum dimensions (horizontal axis)
        largest_sku = dims.max(axis=0)
        largest_sku_sorted = sorted(largest_sku, reverse=True)
        return largest_sku_sorted
