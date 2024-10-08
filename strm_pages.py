import streamlit as st
import pandas as pd
import plotly.express as px
import math
from streamlit_option_menu import option_menu

# """
# PARA PREPARAR ESTE DASHBOARD, SE DEBEN ACTUALIZAR LAS VENTAS Y LOS COGS EN EL ARCHIVO 'MS SALES'
# PARA EL ARCHIVO DE COGS, SE USA EL NOTEBOOK 'ANALISIS COGS'. EL CUAL NOS AYUDA A PONDERAR LOS COGS POR FARM
# Y POR MES. ESTO ES IMPORTANTE PARA PODER HACER UNA COMPARACION DE LOS COGS CON LAS VENTAS.
# ADEMAS, SE USA UNA MACRO EN VBA PARA PREPARAR LOS DATOS DE VENTAS Y LUEGO SI SE PUEDE ACTUALIZAR
# DICHO ARCHIVO... UNA VEZ ACTUALIZADO, SE OBTIENE LA TABLA GENERAL, Y SE PEGA EN EL ARCHIVO VENTAS.CSV
# Y DE LA HOJA DE COGS, SE OBTIENE EL RESUMEN POR FARM Y MES, Y SE PEGA EN EL ARCHIVO COGS.CSV.
# """

# TODO: crecimiento en ventas por producto, cliente.
# Product mix. Cliente mas rentable
# % de reclamaciones por producto, cliente, vendor
# ms.it@misterspecialties.com
# Basil2021

df_cogs = pd.read_csv("COGS.csv")
df = pd.read_csv("sales.csv")
st.set_page_config(page_title="Sales Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide",
                   initial_sidebar_state="collapsed")

month_num = {'January': 1, 'February': 4, 'March': 16, 'April': 64, 'May': 256, 'June': 1042,
             'July': 4096, 'August': 16384, 'September': 65536, 'October': 262144, 'November': 1048576,
             'December': 4194304}

month_map = {
    'Jan': 'January',
    'Feb': 'February',
    'Mar': 'March',
    'Apr': 'April',
    'May': 'May',
    'Jun': 'June',
    'Jul': 'July',
    'Aug': 'August',
    'Sep': 'September',
    'Oct': 'October',
    'Nov': 'November',
    'Dec': 'December'
}

# apply the mapping to the "Month" column of the dataframe to get month number
df['Month Number'] = df['Month'].map(month_num)
# apply the mapping to the "Month" column of the dataframe
df_cogs['Month'] = df_cogs['Month'].map(month_map)
df_cogs['Month Number'] = df_cogs['Month'].map(month_num)

# Side bar
st.sidebar.header("Filters:")
st.sidebar.markdown("###### Select the filters you want to apply to the data.")
st.sidebar.markdown("###### You can select multiple filters at the same time.")
# Write description under Month selector
st.sidebar.markdown("###### If you don't select any filter, the data will be shown with no filters.")

Month = st.sidebar.multiselect("Select the Month:",
                               options=df["Month"].unique(),
                               default=[])
if not Month:
    Month = df["Month"].unique()

SKU = st.sidebar.multiselect("Select the SKU:",
                             options=df["SKU"].unique(),
                             default=[])
if not SKU:
    SKU = df["SKU"].unique()

Class = st.sidebar.multiselect("Select the Class:",
                               options=df["Class"].unique(),
                               default=[])
if not Class:
    Class = df["Class"].unique()

cogs_selection = df_cogs.query("Class in @Class & Month in @Month")
df_selection = df.query("Class in @Class & Month in @Month & SKU in @SKU")

# st.dataframe(df_selection)

# Icons for the menu:
# https://icons.getbootstrap.com/
selected = option_menu(
    menu_title="Main Menu",
    options=["Home", "Indicators"],
    icons=["house", "bar-chart-line"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# --- MAIN PAGE ---
if selected == "Home":

    st.title(":bar_chart: Sales Dashboard")
    st.markdown("##")

    # TOP KPIs
    total_gross_sales = int(df_selection["Total Gross Sales $$"].sum())  # Sum of all sales
    gross_sales_per_month = df_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month Number")
    gross_sales_per_month['% Change'] = gross_sales_per_month['Total Gross Sales $$'].pct_change()

    total_sales = int(df_selection["Total NET Sales ($)"].sum())  # Sum of all sales
    net_sales_per_month = df_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month Number")
    net_sales_per_month['% Change'] = net_sales_per_month['Total NET Sales ($)'].pct_change()

    total_rejections = int(df_selection["Total Rejections $$"].sum())  # Sum of all rejections
    net_rejections_per_month = df_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month Number")
    net_rejections_per_month['% Change'] = net_rejections_per_month['Total Rejections $$'].pct_change()

    total_cogs = int(cogs_selection["Sum of Amount"].sum())  # Sum of all COGS
    cogs_per_month = cogs_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month Number")
    cogs_per_month['% Change'] = cogs_per_month['Sum of Amount'].pct_change()

    left_column, middle_column, right_column, right_column_2 = st.columns(4)
    with left_column:
        delta_value = f"{gross_sales_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Gross Sales:",
                      value=f"${total_gross_sales:,}",
                      delta=delta_value)
        else:
            st.metric(label="Total Gross Sales:",
                      value=f"${total_gross_sales:,}")

    with middle_column:
        delta_value = f"{net_rejections_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Rejections:",
                      value=f"${total_rejections:,}",
                      delta=delta_value)
        else:
            st.metric(label="Total Rejections:",
                      value=f"${total_rejections:,}")

    with right_column:
        delta_value = f"{net_sales_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Net Sales:",
                      value=f"${total_sales:,}",
                      delta=delta_value)
        else:
            st.metric(label="Total Net Sales:",
                      value=f"${total_sales:,}")

    with right_column_2:
        delta_value = f"{cogs_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total COGS (Per Farm):",
                      value=f"${int(total_cogs):,}",
                      delta=delta_value)
        else:
            st.metric(label="Total COGS (Per Farm):",
                      value=f"${int(total_cogs):,}")

    # --- CHARTS ---
    st.markdown("---")

    sales_by_farm = (
        df_selection.groupby(by=["Class"]).sum(numeric_only=True)[["Total NET Sales ($)"]].sort_values(by="Total NET "
                                                                                                          "Sales ($)")
    )

    sales_by_farm["% of Total Sales"] = sales_by_farm["Total NET Sales ($)"] / total_sales * 100
    sales_by_farm = sales_by_farm[sales_by_farm["% of Total Sales"] > 1]

    # Create plot
    fig_sales_by_farm = px.bar(
        sales_by_farm,
        x="% of Total Sales",
        y=sales_by_farm.index,
        orientation="h",
        title="<b>Sales by Farm: (Only displaying >1%)</b>",
        color_discrete_sequence=["#2E86C1"] * len(sales_by_farm),
        template="plotly_white",
        text=sales_by_farm["% of Total Sales"].apply(lambda x: f"{x:.1f}%")
    )
    fig_sales_by_farm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False)
    )
    fig_sales_by_farm.update_traces(textposition="inside")  # Move text outside of bars

    # Create a plot for % reclamations by sku
    reclamations_by_sku = (
        df_selection.groupby(by=["SKU"]).sum(numeric_only=True)[["Total Rejections $$", "Total Gross Sales $$"]]
        .sort_values(by="Total Rejections $$")
    )
    reclamations_by_sku["% Reclamations"] = (reclamations_by_sku["Total Rejections $$"] /
                                             reclamations_by_sku["Total Gross Sales $$"]) * 100
    filtered_reclamations_by_sku = reclamations_by_sku[reclamations_by_sku["% Reclamations"] > 0].sort_values(
        by="% Reclamations", ascending=False)

    fig_reclamations_by_sku = px.bar(
        filtered_reclamations_by_sku,
        x=filtered_reclamations_by_sku.index,
        y="% Reclamations",
        orientation="v",
        title="<b>% Reclamations by SKU:</b>",
        color_discrete_sequence=["#2E86C1"] * len(filtered_reclamations_by_sku),
        template="plotly_white",
        text=filtered_reclamations_by_sku["% Reclamations"].apply(lambda x: f"{x:.1f}%")
    )
    fig_reclamations_by_sku.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=False)
    )
    fig_reclamations_by_sku.update_traces(textposition="outside")  # Move text outside of bars

    # Display charts in columns
    left_column, right_column = st.columns(2)
    with left_column:
        st.plotly_chart(fig_sales_by_farm)
    with right_column:
        st.plotly_chart(fig_reclamations_by_sku)


# # Styling
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)  # Hide menu bar

# This is a good site to find emojis
# webfx.com/tools/emoji-cheat-sheet/
