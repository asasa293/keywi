import streamlit as st
import pandas as pd
import plotly.express as px
import math

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
# if the string "La Corsaria" is part of the class, replace with "La Corsaria"
# (Fixed in notebook)
# df_cogs.Class = df_cogs.Class.apply(lambda x: 'La Corsaria SAS' if 'La Corsaria' in x else x)

# load expenses
df_expenses = pd.read_csv("EXPENSES_CLASS_HERBS.csv")

df = pd.read_csv("sales.csv")
# if the string "La Corsaria" is part of the class, replace with "La Corsaria"
df.Class = df.Class.apply(lambda x: 'La Corsaria SAS' if 'La Corsaria' in x else x)

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
df_cogs['SKU'] = df_cogs['SKU'].str.replace('CM-', '')

# apply the mapping to the "Month" column of the dataframe
df_expenses['Month'] = df_expenses['Month'].map(month_map)
df_expenses['Month Number'] = df_expenses['Month'].map(month_num)

ventana = st.selectbox("", ["Farms", "Clients"])
if ventana == "Farms":

    # Sidebar
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

    cogs_selection = df_cogs.query("Class in @Class & Month in @Month & SKU in @SKU")
    df_selection = df.query("Class in @Class & Month in @Month & SKU in @SKU")
    expenses_selection = df_expenses.query("Class in @Class & Month in @Month & SKU in @SKU")

    # --- MAIN PAGE ---
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

    total_expenses = int(expenses_selection["Sum of Amount"].sum())  # Sum of all expenses
    expenses_per_month = expenses_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month Number")
    expenses_per_month['% Change'] = expenses_per_month['Sum of Amount'].pct_change()

    # % change of gross profit
    sales_df_g = df_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month")[
        ['Total NET Sales ($)',
         'Month Number']]
    cogs_df_g = cogs_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(
        by="Month Number")[['Sum of Amount', 'Month Number']].sort_values(by="Month Number")
    df_gross_profit = sales_df_g['Total NET Sales ($)'] - cogs_df_g['Sum of Amount']
    df_gross_profit = df_gross_profit.to_frame()
    df_gross_profit = df_gross_profit.reset_index()
    df_gross_profit['Month Number'] = df_gross_profit['Month'].map(month_num)
    df_gross_profit.sort_values(by="Month Number", inplace=True)
    df_gross_profit['% Change'] = df_gross_profit[0].pct_change()
    df_gross_profit = df_gross_profit.rename(columns={0: 'Gross Profit'})

    # st.dataframe(df_gross_profit)

    # % change in operating profit
    expenses_per_month = expenses_per_month.reset_index().sort_values(by="Month Number")
    df_operating_profit = pd.DataFrame()
    df_operating_profit['Month_Number'] = expenses_per_month['Month Number']
    df_operating_profit.sort_values(by="Month_Number", inplace=True)
    df_operating_profit['Operating Profit'] = df_gross_profit['Gross Profit'] - expenses_per_month['Sum of Amount']
    df_operating_profit['% Change'] = df_operating_profit['Operating Profit'].pct_change()

    # st.dataframe(expenses_per_month)
    df_gross_profit.reset_index(inplace=True)
    df_gross_profit['Expenses'] = expenses_per_month['Sum of Amount']
    df_gross_profit['Operating Profit'] = df_gross_profit['Gross Profit'] - df_gross_profit['Expenses']
    df_gross_profit['% Change op'] = df_gross_profit['Operating Profit'].pct_change()

    # Metrics for the top KPIs
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

    with left_column:
        delta_value = f"{net_rejections_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Rejections:",
                      value=f"${total_rejections:,} ({total_rejections / total_gross_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Rejections:",
                      value=f"${total_rejections:,} ({total_rejections / total_gross_sales * 100:.1f}%)")

    with middle_column:
        delta_value = f"{net_sales_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Net Sales:",
                      value=f"${total_sales:,} ({total_sales / total_gross_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Net Sales:",
                      value=f"${total_sales:,} ({total_sales / total_gross_sales * 100:.1f}%)")

    with middle_column:
        delta_value = f"{cogs_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total COGS:",
                      value=f"${int(total_cogs):,} ({total_cogs / total_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total COGS (Per Farm):",
                      value=f"${int(total_cogs):,} ({total_cogs / total_sales * 100:.1f}%)")

    # Gross Profit Metrics with delta in %
    gross_profit = total_sales - total_cogs
    with right_column:
        delta_value = f"{df_gross_profit['% Change'].mean() * 100:.1f}%"  # Gross Profit % Change
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Gross Profit:",
                      value=f"${gross_profit:,} ({gross_profit / total_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Gross Profit:",
                      value=f"${gross_profit:,} ({gross_profit / total_sales * 100:.1f}%)")

    # Expenses Metrics with delta in %
    with right_column:
        delta_value = f"{expenses_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Expenses:",
                      value=f"${total_expenses:,} ({total_expenses / gross_profit * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Expenses:",
                      value=f"${total_expenses:,} ({total_expenses / total_sales * 100:.1f}%)")

    # Operating Profit Metrics with delta in %
    total_operating_profit = df_gross_profit['Operating Profit'].sum()
    with right_column_2:
        delta_value = f"{df_operating_profit['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Operating Profit:",
                      value=f"${total_operating_profit:,.0f} ({total_operating_profit / total_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Operating Profit:",
                      value=f"${total_operating_profit:,.0f} ({total_operating_profit / total_sales * 100:.1f}%)")

    # --- CHARTS ---
    st.markdown("---")

    sales_by_farm = (
        df_selection.groupby(by=["Class"]).sum(numeric_only=True)[["Total NET Sales ($)"]]
        .sort_values(by="Total NET Sales ($)")
    )

    total_sales = sales_by_farm["Total NET Sales ($)"].sum()

    sales_by_farm["% of Total Sales"] = sales_by_farm["Total NET Sales ($)"] / total_sales * 100

    # Create a new column with the total value
    sales_by_farm["Total Sales"] = sales_by_farm["Total NET Sales ($)"]

    sales_by_farm = sales_by_farm[sales_by_farm["% of Total Sales"] > 1]

    # Create plot for the sales by farm
    fig_sales_by_farm = px.bar(
        sales_by_farm,
        x="% of Total Sales",
        y=sales_by_farm.index,
        orientation="h",
        title="<b>Sales by Farm: (Only displaying >1%)</b>",
        color_discrete_sequence=["#2E86C1"] * len(sales_by_farm),
        template="plotly_white",
        text=sales_by_farm["% of Total Sales"].apply(lambda x: f"{x:.1f}%"),
        # Add the Total Sales and % of Total Sales columns to the hover tooltip
        hover_data={
            "Total Sales": ":,.2f",
            "% of Total Sales": ":.1f%"
        }
    )
    fig_sales_by_farm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=False),
        height=570
    )
    fig_sales_by_farm.update_traces(textposition="inside")

    # Create a plot for % rejections by farm
    rejections_by_farm = (
        df_selection.groupby(by=["Class"]).sum(numeric_only=True)[["Total Rejections $$", "Total Gross Sales $$"]]
        .sort_values(by="Total Rejections $$")
    )
    rejections_by_farm["% rejections"] = (rejections_by_farm["Total Rejections $$"] / rejections_by_farm[
        "Total Gross Sales $$"]) * 100

    filtered_rejections_by_farm = rejections_by_farm[rejections_by_farm["% rejections"] > 0].sort_values(
        by="% rejections", ascending=False)

    fig_rejections_by_farm = px.bar(
        filtered_rejections_by_farm,
        x=filtered_rejections_by_farm.index,
        y="% rejections",
        title="<b>% Rejections by Farm:</b>",
        color_discrete_sequence=["#2E86C1"] * len(filtered_rejections_by_farm),
        template="plotly_white",
        text=filtered_rejections_by_farm["% rejections"].apply(lambda x: f"{x:.1f}%"),
        # Add the Total Sales and % of Total Sales columns to the hover tooltip
        hover_data={
            "Total Rejections $$": ":,.2f",
            "Total Gross Sales $$": ":,.2f",
            "% rejections": ":.1f%"
        }
    )
    fig_rejections_by_farm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        height=550
    )
    fig_rejections_by_farm.update_traces(textposition="outside")

    # Create pie chart for sku sales
    sku_sales = (
        df_selection.groupby(by=["SKU"]).sum(numeric_only=True)[["Total NET Sales ($)"]].sort_values(
            by="Total NET Sales "
               "($)")
    )
    try:
        sku_sales = sku_sales.drop('Handling', axis=0)
    except KeyError:
        pass
    try:
        sku_sales = sku_sales.drop('Cross-docking', axis=0)
    except KeyError:
        pass
    try:
        sku_sales = sku_sales.drop('Logistics', axis=0)
    except KeyError:
        pass

    # create pie chart for sku sales
    fig_sku_sales = px.pie(
        sku_sales,
        values="Total NET Sales ($)",
        names=sku_sales.index,
        title="<b>Sales by SKU:</b>",
        color_discrete_sequence=px.colors.sequential.RdBu,
        template="plotly_white",
        # Add the Total Sales and % of Total Sales columns to the hover tooltip
        hover_data={
            "Total NET Sales ($)": ":,.2f",
        }
    )
    fig_sku_sales.update_layout(xaxis=dict(showgrid=False), width=700, height=700)

    # Display charts in columns
    left_column, right_column = st.columns(2)
    with left_column:
        st.plotly_chart(fig_sales_by_farm)
    with right_column:
        st.plotly_chart(fig_rejections_by_farm)
    with left_column:
        st.plotly_chart(fig_sku_sales)

    # rejections by SKU: Removed by Carlos's request
    # with right_column:
    #     st.plotly_chart(fig_rejections_by_sku)

    # webfx.com/tools/emoji-cheat-sheet/
    # This is a good site to find emojis
    st.markdown("---")

else:
    # Sidebar
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

    Customer = st.sidebar.multiselect("Select the Customer:",
                                      options=df["Customer"].unique(),
                                      default=[])
    if not Customer:
        Customer = df["Customer"].unique()

    cogs_selection = df_cogs.query("Month in @Month & SKU in @SKU")
    df_selection = df.query("Customer in @Customer & Month in @Month & SKU in @SKU")
    expenses_selection = df_expenses.query("Month in @Month & SKU in @SKU")

    # --- MAIN PAGE ---
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

    total_expenses = int(expenses_selection["Sum of Amount"].sum())  # Sum of all expenses
    expenses_per_month = expenses_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month Number")
    expenses_per_month['% Change'] = expenses_per_month['Sum of Amount'].pct_change()

    # % change of gross profit
    sales_df_g = df_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(by="Month")[
        ['Total NET Sales ($)',
         'Month Number']]
    cogs_df_g = cogs_selection.groupby(by=["Month"]).sum(numeric_only=True).sort_values(
        by="Month Number")[['Sum of Amount', 'Month Number']].sort_values(by="Month Number")
    df_gross_profit = sales_df_g['Total NET Sales ($)'] - cogs_df_g['Sum of Amount']
    df_gross_profit = df_gross_profit.to_frame()
    df_gross_profit = df_gross_profit.reset_index()
    df_gross_profit['Month Number'] = df_gross_profit['Month'].map(month_num)
    df_gross_profit.sort_values(by="Month Number", inplace=True)
    df_gross_profit['% Change'] = df_gross_profit[0].pct_change()
    df_gross_profit = df_gross_profit.rename(columns={0: 'Gross Profit'})

    # st.dataframe(df_gross_profit)

    # % change in operating profit
    expenses_per_month = expenses_per_month.reset_index().sort_values(by="Month Number")
    df_operating_profit = pd.DataFrame()
    df_operating_profit['Month_Number'] = expenses_per_month['Month Number']
    df_operating_profit.sort_values(by="Month_Number", inplace=True)
    df_operating_profit['Operating Profit'] = df_gross_profit['Gross Profit'] - expenses_per_month['Sum of Amount']
    df_operating_profit['% Change'] = df_operating_profit['Operating Profit'].pct_change()

    # st.dataframe(expenses_per_month)
    df_gross_profit.reset_index(inplace=True)
    df_gross_profit['Expenses'] = expenses_per_month['Sum of Amount']
    df_gross_profit['Operating Profit'] = df_gross_profit['Gross Profit'] - df_gross_profit['Expenses']
    df_gross_profit['% Change op'] = df_gross_profit['Operating Profit'].pct_change()

    # Metrics for the top KPIs
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

    with left_column:
        delta_value = f"{net_rejections_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Rejections:",
                      value=f"${total_rejections:,} ({total_rejections / total_gross_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Rejections:",
                      value=f"${total_rejections:,} ({total_rejections / total_gross_sales * 100:.1f}%)")

    with middle_column:
        delta_value = f"{net_sales_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Net Sales:",
                      value=f"${total_sales:,} ({total_sales / total_gross_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Net Sales:",
                      value=f"${total_sales:,} ({total_sales / total_gross_sales * 100:.1f}%)")

    with middle_column:
        delta_value = f"{cogs_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total COGS:",
                      value=f"${int(total_cogs):,} ({total_cogs / total_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total COGS (Per Farm):",
                      value=f"${int(total_cogs):,} ({total_cogs / total_sales * 100:.1f}%)")

    # Gross Profit Metrics with delta in %
    gross_profit = total_sales - total_cogs
    with right_column:
        delta_value = f"{df_gross_profit['% Change'].mean() * 100:.1f}%"  # Gross Profit % Change
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Gross Profit:",
                      value=f"${gross_profit:,} ({gross_profit / total_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Gross Profit:",
                      value=f"${gross_profit:,} ({gross_profit / total_sales * 100:.1f}%)")

    # Expenses Metrics with delta in %
    with right_column:
        delta_value = f"{expenses_per_month['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Expenses:",
                      value=f"${total_expenses:,} ({total_expenses / gross_profit * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Expenses:",
                      value=f"${total_expenses:,} ({total_expenses / total_sales * 100:.1f}%)")

    # Operating Profit Metrics with delta in %
    total_operating_profit = df_gross_profit['Operating Profit'].sum()
    with right_column_2:
        delta_value = f"{df_operating_profit['% Change'].mean() * 100:.1f}%"
        if not math.isnan(float(delta_value[:-1])):
            st.metric(label="Total Operating Profit:",
                      value=f"${total_operating_profit:,.0f} ({total_operating_profit / total_sales * 100:.1f}%)",
                      delta=delta_value)
        else:
            st.metric(label="Total Operating Profit:",
                      value=f"${total_operating_profit:,.0f} ({total_operating_profit / total_sales * 100:.1f}%)")
