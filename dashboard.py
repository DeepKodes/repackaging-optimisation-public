import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from current_box_fit import PackingOptimiser
from optimise_kmeans import BoxDimensionsOptimiser
from sku_dims_cls import SkuDims
from matplotlib.patches import Rectangle
from kmeans_original import BoxDimensionsOptimiserK


#Void-fill-rate distribution(Current vs Optimised)- Histogram 
def plot_void_fill_before_after(before_list, after_list):
    plt.figure(figsize=(12, 6))
    plt.hist(before_list, bins=40, alpha=0.5, label='Current')
    plt.hist(after_list, bins=40, alpha=0.5, label='Optimised')
    plt.xlabel("Void-Fill Rate")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    return plt.gcf()


#Void-Fill Rate Distribution(Optimised)- boxplot
def plot_void_fill_boxplot(box_void_fill_dict):
    filtered = {k: v for k, v in box_void_fill_dict.items() if len(v) > 0}
    plt.figure(figsize=(12, 6))
    plt.boxplot(filtered.values(), labels=filtered.keys(), showfliers=False)
    plt.xlabel("Box ID")
    plt.ylabel("Void-Fill Rate")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    return plt.gcf()

#Current/Optimised percentage of items assigned to each boxes- pie charts
def pie_chart_same_size(box_dict):
    labels = []
    counts = []
    # extract inputs
    for box_id, v in box_dict.items():
        if len(v) > 0:
            labels.append(box_id)
            counts.append(len(v))    
    if sum(counts) == 0:
        fig, ax = plt.subplots(figsize=(5,5))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return fig, pd.DataFrame(columns=["Box", "percentage-usage", "color"])
    total = sum(counts)
    # FIXED SIZE PIE
    fig, ax = plt.subplots(figsize=(5,5))
    wedges = ax.pie(counts,radius=1.0,labels=None,autopct=None,startangle=140,normalize=True)[0]
    rows = []
    label_dist = 1.30
    for wedge, label, count in zip(wedges, labels, counts):
        pct = (count / total) * 100
        rgba = wedge.get_facecolor()
        rows.append([label, round(pct, 2), rgba])      
        angle = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
        x = np.cos(np.deg2rad(angle)) * label_dist
        y = np.sin(np.deg2rad(angle)) * label_dist
        ax.text(x, y,f"{label}",ha="center", va="center",fontsize=10, color=rgba)  
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    df = pd.DataFrame(rows, columns=["Box", "percentage-usage", "color"])
    return fig, df

#pie chart data table
def color_table(df):
    if df.empty:
        fig, ax = plt.subplots()
        ax.axis("off")
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        return fig

    fig, ax = plt.subplots(figsize=(7, len(df) * 0.55))
    ax.axis("off") 
    table = ax.table(
        cellText=[[r["Box"], r["percentage-usage"], ""] for _, r in df.iterrows()],
        colLabels=["Box", "Percentage-usage(%)", "Color"],
        cellLoc="center",
        loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.4)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer() 
    for i, rgba in enumerate(df["color"]):
        cell = table[(i + 1, 2)]  
        bbox = cell.get_window_extent(renderer)
        inv = ax.transAxes.inverted()
        x0, y0 = inv.transform((bbox.x0, bbox.y0))
        x1, y1 = inv.transform((bbox.x1, bbox.y1))
        width, height = x1 - x0, y1 - y0
        size = min(width, height) * 0.7
        sx = x0 + (width - size) / 2
        sy = y0 + (height - size) / 2
        square = Rectangle((sx, sy), size, size,
                           transform=ax.transAxes,
                           facecolor=rgba,
                           edgecolor="black")
        ax.add_patch(square)
    plt.tight_layout()
    return fig


# Bar Chart: Before vs After Box Usage
def plot_items_distribution_before_after(before_dict, after_dict):
    all_boxes = sorted(set(before_dict.keys()) | set(after_dict.keys()))
    before_counts = [len(before_dict.get(b, [])) for b in all_boxes]
    after_counts = [len(after_dict.get(b, [])) for b in all_boxes]
    x = np.arange(len(all_boxes))
    width = 0.30
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(x - width/2, before_counts, width, label="Current")
    ax.bar(x + width/2, after_counts, width, label="Optimised")

    ax.set_xlabel("Box Type", fontsize=12)
    ax.set_ylabel("Number of Items Assigned", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(all_boxes, rotation=45, ha='center')
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    ax.xaxis.set_label_coords(0.5, -0.16) 
    return fig


st.set_page_config(page_title="Box Optimisation Dashboard", layout="wide")
st.title("Packaging Box Size Optimisation Dashboard")


st.sidebar.header("Upload Input Files")
returns_file = st.sidebar.file_uploader("Returns Data", type=["csv"])
boxes_file = st.sidebar.file_uploader("Boxes Data", type=["csv"])

if returns_file and boxes_file:

    returns_df = pd.read_csv(returns_file)
    boxes_df = pd.read_csv(boxes_file)

    st.sidebar.success("Data Loaded.")

    if st.sidebar.button("Click to optimise"):
        
        sorter = SkuDims(returns_df)
        sorted_returns = sorter.sort_dims()

        # Initial (Current Boxes)
        base_opt = PackingOptimiser(sorted_returns, boxes_df)
        initial_metrics = base_opt.assign_boxes()
        
        
        # 2. Intermediate optimisation (centroid-based)
        kmeans_optK = BoxDimensionsOptimiserK(sorted_returns, boxes_df)
        inter_stats = kmeans_optK.optimise_box_sizes()


        # Optimise_kmeans.py
        kmeans_opt = BoxDimensionsOptimiser(sorted_returns, boxes_df)
        box_results = kmeans_opt.optimise_box_sizes()

        st.success("Optimisation Completed Successfully.")

        # void fill rate and outlier before and after optimisation
        st.header("Key Performance Indicators")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Initial Avg Void Fill", f"{initial_metrics['avg_void_fill_rate']:.4f}")
            st.metric("Initial Outlier Rate", f"{initial_metrics['outlier_rate']:.4f}")

        with col2:
            st.metric("Intermediate Avg Void Fill",f"{inter_stats['avg_void_fill_rate']:.4f}")
            st.metric("Intermediate Outlier Rate", f"{inter_stats['outlier_rate']:.4f}")
        
        with col3:
            st.metric("Optimised Avg Void Fill",
                      f"{box_results['avg_void_fill_rate']:.4f}")
            st.metric("Optimised Outlier Rate",
                      f"{box_results['outlier_rate']:.4f}")


        # Extracting dicts
        before_dict = initial_metrics["box_void_fill"]
        after_dict  = box_results["void_fill_per_box"]

        before_list = initial_metrics["void_fill_list"]
        after_list  = box_results["void_fill_list"]
        st.header("Visualisations")
        tab1, tab2, tab3,tab4= st.tabs(['Void-Fill Rate','Current/Optimised void fill rate distribution','Void fill rate distribution','Current/Optimised percentage of items assigned to each boxes'])
        
        with tab1:
            st.subheader("Void-Fill distribution(Current vs Optimised)")
            st.pyplot(plot_void_fill_before_after(before_list, after_list))
        
        with tab2:
            st.subheader("Current vs Optimised: Items Assigned per Box")
            st.pyplot(plot_items_distribution_before_after(before_dict, after_dict))
        
        with tab3:
                st.subheader("Void-Fill Rate Distribution (Optimised)")
                st.pyplot(plot_void_fill_boxplot(after_dict))            
        
        with tab4:
            col1, col2 = st.columns(2)

            with col1:
                fig_before, df_before = pie_chart_same_size(before_dict)
                st.subheader("Current – Box Usage")
                st.pyplot(fig_before)

                st.write("Current")
                st.pyplot(color_table(df_before))

            with col2:
                fig_after, df_after = pie_chart_same_size(after_dict)
                st.subheader("Optimised – Box Usage")
                st.pyplot(fig_after)

                st.write("Optimised")
                st.pyplot(color_table(df_after))
else:
    st.info("Please upload both Returns Data and Boxes CSV files to optimise.")
