import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import base64
import io

#--------------------------------------------------------------------------------------------------------
def pagecounter():
     #pagecounter
    if 'page_count' not in st.session_state: st.session_state.page_count = 0
    # Increment the page count
    st.session_state.page_count += 1    
    st.markdown(f"<div style=padding: 1px;'><h6 style='text-align: center; color: blue;'>Total Visits - {st.session_state.page_count}</h6></div>", unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------------------
#KPI colored boxes at the top
def display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc):
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                {wch_colour_box[1]}, 
                                                {wch_colour_box[2]}, 0.75); 
                            color: rgb({wch_colour_font[0]}, 
                                    {wch_colour_font[1]}, 
                                    {wch_colour_font[2]}, 0.75); 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 12px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{iconname} fa-xs'></i><b> {i}</b> ({per}%)</style>
                            <BR><span style='font-size: 16px;margin-top: 0;'><b>{sline}</style></span>
                            <BR><span style='font-size: 14px;margin-top: 0;'> SHC - {shc}, AYUSH - {ayush}, PHC - {phc}, UPHC - {uphc}, UHWCS - {uhwc}</b></p>"""
    st.markdown(lnk + htmlstr, unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------------------
def gototop():
    # Add a button at the end of the page to scroll to the top
    st.markdown(
        """
        <style>
            .scroll-to-top-button {
                position: fixed;
                bottom: 45px;
                right: 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 24px;
                cursor: pointer;
                transition: background-color 0.3s;
            }

            .scroll-to-top-button:hover {
                background-color: #0056b3;
            }
        </style>
        """
        , unsafe_allow_html=True)

    st.markdown(
        """
        <a href="#top">
        <button class="scroll-to-top-button" onclick="scrollToTop()">
            &#8679;
        </button>
        </a>
        """
        , unsafe_allow_html=True)
    
#-------------------------------------------------------------------------------------------------------------
#formatted Table
def formattedtable(table_df):     
        table_df1=table_df
        # Calculate the percentage and store in a new column
        table_df1.iloc[:, 0] = table_df1.iloc[:, 0].replace('Total', 'Jharkhand Total')
        #divided by 0 error aslo handeled
        table_df1['Percentage'] = (table_df1.iloc[:, 2] / (table_df1.iloc[:, 1] + 1e-10)) * 100
        table_df1=table_df1.sort_values(by='Percentage', ascending=False)
        # Handle division by zero and NaN values
        table_df1['Percentage'] = table_df1['Percentage'].fillna(0).replace([float('inf'), -float('inf')], 0)
        # Format the percentage to 2 decimal places
        table_df1['Percentage'] = table_df1['Percentage'].map('{:.2f}'.format)
        # Apply heatmap to the Occurrences column (RdYlGn/summer_r/PiYG)
        styled_df = table_df1.style.background_gradient(subset=['Percentage'], cmap='RdYlGn').set_properties(**{'font-weight': 'bold','color': 'black', 'border-color': 'light gray'})
        # Add custom styling for column headers
        styled_df = styled_df.set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#2196F3'), ('color', 'white')]}]
        )
        # Hide the index column
        styled_df = styled_df.hide(axis='index')        
        # Convert styled dataframe to HTML
        html_table = styled_df.to_html()
        # Display the styled, sorted merged dataframe with heatmap
        st.markdown(html_table, unsafe_allow_html=True)         
        generate_excel_download_link(styled_df)  

#----------------------------------------------------------------------
def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Rename_This_File.xlsx">Download </a>'
    return st.markdown(href, unsafe_allow_html=True)

#--------------------------------------------------------------------------
def get_table_download_link(df, file_name='District wise Target Vs Operational.xlsx'):
    excel_file = download_excel_file(df)
    b64 = base64.b64encode(excel_file.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">Download Excel file</a>'
    return href

#---------------------------------------------------------------------
def download_excel_file(df):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')        
        # Get the xlsxwriter workbook and worksheet objects.
        workbook  = writer.book
        worksheet = writer.sheets['Sheet1']        
        # Apply conditional formatting to the percentage columns
        percentage_columns = [col for col in df.columns if col.endswith('%')]
        for col_num, column in enumerate(df.columns):
                if column in percentage_columns:
                        col_letter = chr(65 + col_num)
                        worksheet.conditional_format(f'{col_letter}2:{col_letter}{len(df) + 1}', 
                                                        {'type': '3_color_scale',
                                                        'min_color': "#ff0000",
                                                        'mid_color': "#ffff00",
                                                        'max_color': "#00ff00"})
        # Format the header
        header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1,
                'align': 'center'
        })
        for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)        
        # Format all data cells
        data_format = workbook.add_format({
                'border': 1,
                'align': 'center'
        })
        for row_num in range(1, len(df) + 1):
                for col_num, value in enumerate(df.iloc[row_num - 1]):
                        worksheet.write(row_num, col_num, value, data_format)
        # Format the last row
        last_row_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'align': 'center'
        })
        for col_num, value in enumerate(df.iloc[-1]):
                worksheet.write(len(df), col_num, value, last_row_format)   
        # Set automatic column width
        for col_num, column in enumerate(df.columns):
                max_length = max(
                        df[column].astype(str).map(len).max(),  # Get the max length of the data in the column
                        len(column)  # Get the length of the column header
                ) + 2  # Add a little extra space
                worksheet.set_column(col_num, col_num, max_length)    
        writer.close()
        output.seek(0)    
        return output

#---------------------------------------------------------------------
#same as bargarph 1 but with more bar width
def bargraph2(df, x, y, top, titlegraph, yaxistitle):
    # Create a melted DataFrame for easier plotting
    melted_df = df.melt(id_vars=[x], value_vars=[y, top], var_name='Category', value_name='Count')
    # Base chart for common encodings
    base = alt.Chart(melted_df).encode(
        x=alt.X(x, title=None, axis=alt.Axis(labelAngle=-90)),
        tooltip=[x, 'Category:N', 'Count']
    )    
    # Bar chart for Main bar with larger bar width
    bar1 = base.transform_filter(
        alt.datum.Category == top
    ).mark_bar(size=65).encode(
        y=alt.Y('Count', title=yaxistitle),
        color=alt.value('blue')
    )    
    # Bar chart for Secondary bar with smaller bar width
    bar2 = base.transform_filter(
        alt.datum.Category == y
    ).mark_bar(size=45).encode(
        y=alt.Y('Count', title=yaxistitle, axis=alt.Axis(titleColor='black', titleFontWeight='bold')),
        color=alt.value('orange')
    )
    # Data labels for Main Bar
    bar1_text = base.transform_filter(
        alt.datum.Category == top
    ).mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Adjust vertical position of labels
        color='black',
        fontWeight='bold',
        fontSize=16
    ).encode(
        y=alt.Y('Count'),
        text=alt.Text('Count:Q')
    )
    # Data labels for Secondary bar
    bar2_text = base.transform_filter(
        alt.datum.Category == y
    ).mark_text(
        align='center',
        baseline='middle',
        dy=10,  # Adjust vertical position of labels
        color='black',
        fontWeight='bold',
        fontSize=14
    ).encode(
        y=alt.Y('Count'),
        text=alt.Text('Count:Q')
    )
    # Combine the charts
    chart = alt.layer(
        bar1,
        bar1_text,
        bar2,
        bar2_text
    ).resolve_scale(
        y='shared'
    ).encode(        
        color=alt.Color('Category:N', legend=alt.Legend(orient='top', title=None), scale=alt.Scale(
            domain=[top, y],
            range=['blue', 'black']
        ))
    ).properties(
        width=600,
        height=450,
        title=titlegraph
    ).configure_axisX(
        labelFontSize=14,
        labelFontWeight='bold',
        labelColor='black'
    ).configure_axisY(
        labelFontSize=12,
        labelColor='white'
    ).configure_title(
        fontSize=24,  # Adjust the font size as needed   
        anchor='middle'     
    ).configure_legend(
        labelColor='black',  # Set legend text color to black
        titleColor='black',   # Set legend title color to black        
        labelFontWeight='bold'
    ).configure_view(
        strokeWidth=0
    )
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

#-----------------------------------------------------------------------------------------------
def bargraph1(df, x, y, top, titlegraph, yaxistitle):
    # Create a melted DataFrame for easier plotting
    melted_df = df.melt(id_vars=[x], value_vars=[y, top], var_name='Category', value_name='Count')
    # Base chart for common encodings
    base = alt.Chart(melted_df).encode(
        x=alt.X(x, title=None, axis=alt.Axis(labelAngle=-90)),
        tooltip=[x, 'Category:N', 'Count']
    )    
    # Bar chart for Main bar with larger bar width
    bar1 = base.transform_filter(
        alt.datum.Category == top
    ).mark_bar(size=45).encode(
        y=alt.Y('Count', title=yaxistitle),
        color=alt.value('blue')
    )    
    # Bar chart for Secondary bar with smaller bar width
    bar2 = base.transform_filter(
        alt.datum.Category == y
    ).mark_bar(size=30).encode(
        y=alt.Y('Count', title=yaxistitle, axis=alt.Axis(titleColor='black', titleFontWeight='bold')),
        color=alt.value('orange')
    )
    # Data labels for Main Bar
    bar1_text = base.transform_filter(
        alt.datum.Category == top
    ).mark_text(
        align='center',
        baseline='middle',
        dy=-10,  # Adjust vertical position of labels
        color='black',
        fontWeight='bold',
        fontSize=16
    ).encode(
        y=alt.Y('Count'),
        text=alt.Text('Count:Q')
    )
    # Data labels for Secondary bar
    bar2_text = base.transform_filter(
        alt.datum.Category == y
    ).mark_text(
        align='center',
        baseline='middle',
        dy=10,  # Adjust vertical position of labels
        color='black',
        fontWeight='bold',
        fontSize=14
    ).encode(
        y=alt.Y('Count'),
        text=alt.Text('Count:Q')
    )
    # Combine the charts
    chart = alt.layer(
        bar1,
        bar1_text,
        bar2,
        bar2_text
    ).resolve_scale(
        y='shared'
    ).encode(
        #color=alt.Color('Category:N', legend=alt.Legend(orient='top'))
        color=alt.Color('Category:N', legend=alt.Legend(orient='top', title=None), scale=alt.Scale(
            domain=[top, y],
            range=['blue', 'black']
        ))
    ).properties(
        width=600,
        height=450,
        title=titlegraph
    ).configure_axisX(
        labelFontSize=14,
        labelFontWeight='bold',
        labelColor='black'
    ).configure_axisY(
        labelFontSize=12,
        labelColor='white'
    ).configure_title(
        fontSize=24,  # Adjust the font size as needed   
        anchor='middle'     
    ).configure_legend(
        labelColor='black',  # Set legend text color to black
        titleColor='black',   # Set legend title color to black        
        labelFontWeight='bold'
    ).configure_view(
        strokeWidth=0
    )
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)