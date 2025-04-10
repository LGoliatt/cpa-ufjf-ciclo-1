#!/usr/bin/python
# -*- coding: utf-8 -*-  
import pandas as pd
import csv
import os

def extract_questions_and_subquestions(file_path):
    """
Extracts questions and their subquestions from a tab-separated file.

    Args:
        file_path: The path to the file containing question data.  The file is expected 
            to have rows starting with 'Q' for questions and 'SQ' for subquestions.

    Returns:
        dict: A dictionary where keys are question IDs and values are dictionaries 
            containing the question text and a list of its subquestions. Each subquestion
            is represented as a dictionary with 'id' and 'text' keys.  Returns an empty
            dictionary if the file is empty or does not contain valid question data.
    """
    questions = {}
    current_question = None

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        
        for row in reader:
            if row[0] == 'Q':
                # Extract question details
                question_id = row[2]
                question_text = row[4]
                questions[question_id] = {
                    'text': question_text,
                    'subquestions': []
                }
                current_question = question_id
            elif row[0] == 'SQ' and current_question:
                # Extract subquestion details
                subquestion_id = row[2]
                subquestion_text = row[4]
                questions[current_question]['subquestions'].append({
                    'id': subquestion_id,
                    'text': subquestion_text
                })

    return questions

def transform_questions_to_dataframe(questions):
    
    """
Transforms a dictionary of questions into a Pandas DataFrame.

    Args:
        questions (dict): A dictionary where keys are question IDs and values 
                          are dictionaries containing question data, including text
                          and potentially subquestions.

    Returns:
        pd.DataFrame: A DataFrame representing the questions and their 
                      subquestions, with columns for 'question_id', 
                      'question_data', 'subquestions', and 'text'.
    """
    
    Q=[]
    # Print the extracted questions and subquestions
    for question_id, question_data in questions.items():
        if len(question_data['subquestions'])==0:
            q={}
            q['question_id']=question_id
            q['question_data']=question_data['text']
            q['subquestions'] = question_id#f"{question_id}"
            q['text'] = question_data['text']
            Q.append(q)
        else:
            for subquestion in question_data['subquestions']:
                q={}
                q['question_id']=question_id
                q['question_data']=question_data['text']
                q['subquestions'] = subquestion['id']
                q['subquestions'] = f"{question_id}[{subquestion['id']}]"
                q['text'] = subquestion['text']
                Q.append(q)
               
           
        
    Q = pd.DataFrame(Q)
    return Q


def remove_single_occurrences(df,n=1):
    """
Removes values that appear a specified number of times or less in each column of a DataFrame.

    Args:
        df: The input DataFrame.
        n: The maximum number of occurrences allowed for a value to be kept. Defaults to 1.

    Returns:
        DataFrame: The modified DataFrame with single (or fewer) occurrences replaced by None.
    """
    for column in df.columns:
        value_counts = df[column].value_counts()
        to_remove = value_counts[value_counts <= n].index
        df[column] = df[column].apply(lambda x: x if x not in to_remove else None)
    return df

def include_subquestion(A,Q, uploaded_file):
    """
Includes subquestions from Q that are columns in A and saves to a CSV.

    Iterates through the subquestions in Q, checks if they exist as columns in A.
    If a subquestion is found in A, its values are added to a list.  Subquestions 
    not present in A are removed from Q. Finally, the resulting data and updated 
    Q dataframe are saved to a CSV file specified by uploaded_file.

    Args:
        A: The primary DataFrame containing columns to check against.
        Q: The DataFrame with 'subquestions' column to filter.
        uploaded_file: The path for saving the output CSV file.

    Returns:
        DataFrame: The updated Q DataFrame after filtering and adding data.
    """
    l=[]
    for c in Q['subquestions'].values:        
         if c in A.columns:
            l.append(list(A[c].values))
         else:
            Q=Q[Q['subquestions']!=c]
        
        
    Q['data']=l 
    
    output_csv_path = uploaded_file
    Q.to_csv(output_csv_path, index=False, encoding='utf-8')
    return Q


#%%
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# Function to create horizontal stacked bar charts for each subquestion
def create_stacked_bar_charts(df, question_id):
    """
Creates stacked bar charts for each subquestion within a given question.

    Args:
        df: The input DataFrame containing the data.
        question_id: The ID of the question to analyze.

    Returns:
        None
    """
    st.write(f"### Question ID: {question_id}")
    subquestions = df[df['question_id'] == question_id]['subquestions'].unique()
    
    for subq in subquestions:
        st.write(f"#### Subquestion: {subq}")
        subq_data = df[(df['question_id'] == question_id) & (df['subquestions'] == subq)]['data']
        
        # Convert the string representation of the list to an actual list
        subq_data = subq_data.apply(eval)
        
        # Flatten the list of lists
        flat_data = [item for sublist in subq_data for item in sublist]
        
        # Create a DataFrame for plotting
        plot_df = pd.DataFrame(flat_data, columns=['Response'])
        
        # Count the frequency of each response
        response_counts = plot_df['Response'].value_counts().reset_index()
        response_counts.columns = ['Response', 'Count']
        
        # Create a horizontal stacked bar chart
        fig, ax = plt.subplots()
        sns.barplot(data=response_counts, y='Response', x='Count', ax=ax, orient='h')
        ax.set_title(f"Response Distribution for {subq}")
        ax.set_xlabel("Count")
        ax.set_ylabel("Response")
        
        # Display the plot in Streamlit
        st.pyplot(fig)
        
# Function to create bar plots for each subquestion
def create_barplots(df, question_id):
    """
Creates bar plots for each subquestion within a given question.

    Args:
        df: The input DataFrame containing the data.
        question_id: The ID of the question to filter by.

    Returns:
        None
    """
    st.write(f"### Question ID: {question_id}")
    subquestions = df[df['question_id'] == question_id]['subquestions'].unique()
    
    for subq in subquestions:
        st.write(f"#### Subquestion: {subq}")
        subq_data = df[(df['question_id'] == question_id) & (df['subquestions'] == subq)]['data']
        
        # Convert the string representation of the list to an actual list
        subq_data = subq_data.apply(eval)
        
        # Flatten the list of lists
        flat_data = [item for sublist in subq_data for item in sublist]
        
        # Create a DataFrame for plotting
        plot_df = pd.DataFrame(flat_data, columns=['Response'])
        
        # Plot the bar plot
        fig, ax = plt.subplots()
        sns.countplot(data=plot_df, x='Response', ax=ax, order=plot_df['Response'].value_counts().index)
        ax.set_title(f"Response Distribution for {subq}")
        ax.set_xlabel("Response")
        ax.set_ylabel("Count")
        st.pyplot(fig)

def create_stacked_bar_plots(df, question_id):
    """
Creates a stacked bar plot visualizing response distribution for a given question.

    Args:
        df: The input DataFrame containing the data.
        question_id: The ID of the question to visualize.

    Returns:
        None
    """
    st.write(f"### Question ID: {question_id}")
    
    # Filter data for the current question_id
    question_data = df[df['question_id'] == question_id]
    
    # Flatten the 'data' column (convert string lists to actual lists and flatten)
    question_data['data'] = question_data['data'].apply(eval)
    flattened_data = question_data.explode('data')
    
    # Create a DataFrame for plotting
    plot_df = flattened_data.groupby(['subquestions', 'data']).size().reset_index(name='count')
    
    # Create a stacked Altair bar chart
    chart = alt.Chart(plot_df).mark_bar().encode(
        x=alt.X('subquestions:N', title='Subquestions'),
        y=alt.Y('count:Q', title='Count'),
        color=alt.Color('data:N', title='Resposta'),
        tooltip=['subquestions', 'data', 'count']
    ).properties(
        title=f"Response Distribution for Question ID: {question_id}"
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)


def create_horizontal_stacked_bar_plots(df, question_id):
    """
Creates a horizontal stacked bar plot for a given question ID.

    Args:
        df: The input DataFrame containing the data.
        question_id: The ID of the question to visualize.

    Returns:
        None
    """
    st.write(f"### Question ID: {question_id}")
    
    # Filter data for the current question_id
    question_data = df[df['question_id'] == question_id]
    
    # Flatten the 'data' column (convert string lists to actual lists and flatten)
    question_data['data'] = question_data['data'].apply(eval)
    flattened_data = question_data.explode('data')
    
    # Create a DataFrame for plotting
    plot_df = flattened_data.groupby(['subquestions', 'data']).size().reset_index(name='count')
    
    # Create a horizontal stacked Altair bar chart
    chart = alt.Chart(plot_df).mark_bar().encode(
        y=alt.Y('subquestions:N', title='Subquestions'),  # Subquestions on the y-axis
        x=alt.X('count:Q', title='Count'),  # Count on the x-axis
        color=alt.Color('data:N', title='Resposta'),  # Stack by response type
        tooltip=['subquestions', 'data', 'count']  # Add tooltips for interactivity
    ).properties(
        title=f"Response Distribution for Question ID: {question_id}"
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

def create_horizontal_stacked_bar_plots_percentage(df, question_id):
    """
Creates a horizontal stacked bar chart showing the percentage distribution of responses for a given question.

    Args:
        df: The input DataFrame containing question data.
        question_id: The ID of the question to visualize.

    Returns:
        None
    """
    st.write(f"### Question ID: {question_id}")
    
    # Filter data for the current question_id
    question_data = df[df['question_id'] == question_id]
    
    # Flatten the 'data' column (convert string lists to actual lists and flatten)
    question_data['data'] = question_data['data'].apply(eval)
    flattened_data = question_data.explode('data')
    
    # Create a DataFrame for plotting
    plot_df = flattened_data.groupby(['subquestions', 'data']).size().reset_index(name='count')
    
    # Calculate the total count for each subquestion
    total_counts = plot_df.groupby('subquestions')['count'].transform('sum')
    
    # Calculate the percentage of each response
    plot_df['percentage'] = (plot_df['count'] / total_counts) * 100
    
    # Create a horizontal stacked Altair bar chart with percentages
    chart = alt.Chart(plot_df).mark_bar().encode(
        y=alt.Y('subquestions:N', title='Subquestions'),  # Subquestions on the y-axis
        x=alt.X('percentage:Q', title='Porcentagem (%)'),  # Percentage on the x-axis
        color=alt.Color('data:N', title='Resposta'),  # Stack by response type
        tooltip=['subquestions', 'data', 'percentage:Q']  # Add tooltips for interactivity
    ).properties(
        title=f"Response Distribution for Question ID: {question_id} (Percentage)"
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

def create_percentage_table(df, question_data):
    """
Creates and displays a percentage table for a given question.

    Args:
        df: The input DataFrame containing the data.
        question_data: The specific question to analyze.

    Returns:
        None
    """
    st.write(f"### - {question_data}")
    
    # Filter data for the current question_data
    question_data_df = df[df['question_data'] == question_data]
    
    # Flatten the 'data' column (convert string lists to actual lists and flatten)
    question_data_df['data'] = question_data_df['data'].apply(eval)
    flattened_data = question_data_df.explode('data')
    
    # Create a DataFrame for the table
    plot_df = flattened_data.groupby(['text', 'data']).size().reset_index(name='count')
    
    # Calculate the total count for each "text" entry
    total_counts = plot_df.groupby('text')['count'].transform('sum')
    
    # Calculate the percentage of each response
    plot_df['percentage'] = (plot_df['count'] / total_counts) * 100
    
    # Pivot the table for better readability
    pivot_table = plot_df.pivot(index='text', columns='data', values='percentage').fillna(0)
    
    # Round the percentages to 2 decimal places
    pivot_table = pivot_table.round(2)
    
    # Display the table in Streamlit
    st.write(f"#### Percentage Distribution for: {question_data}")
    st.dataframe(pivot_table.style.format("{:.2f}%"), use_container_width=True)


# Function to create horizontal stacked Altair bar plots with percentages for the "text" column
def create_horizontal_stacked_bar_plots_percentage_data(df, question_data):
    """
Creates a horizontal stacked bar chart showing the percentage distribution of responses for a given question.

    Args:
        df: The input DataFrame containing question data and responses.
        question_data: The specific question to visualize.

    Returns:
        None
    """
    st.write(f"### - {question_data}")
    
    # Filter data for the current question_data
    question_data_df = df[df['question_data'] == question_data]
    
    # Flatten the 'data' column (convert string lists to actual lists and flatten)
    question_data_df['data'] = question_data_df['data'].apply(eval)
    flattened_data = question_data_df.explode('data')
    
    # Create a DataFrame for plotting
    plot_df = flattened_data.groupby(['text', 'data']).size().reset_index(name='count')
    
    # Calculate the total count for each "text" entry
    total_counts = plot_df.groupby('text')['count'].transform('sum')
    
    # Calculate the percentage of each response
    plot_df['percentage'] = (plot_df['count'] / total_counts) * 100
    
    # Create a horizontal stacked Altair bar chart with percentages
    chart = alt.Chart(plot_df).mark_bar().encode(
        y=alt.Y('text:N', title='Text', axis=alt.Axis(labelLimit=200)),  # Text on the y-axis with increased label limit
        x=alt.X('percentage:Q', title='Porcentagem (%)', scale=alt.Scale(domain=[0, 100])),  # Percentage on the x-axis
        color=alt.Color('data:N', title='Resposta', legend=alt.Legend(orient='bottom')),  # Stack by response type
        tooltip=['text', 'data', alt.Tooltip('percentage:Q', format='.2f')]  # Add tooltips for interactivity
    )#.properties(
    #    title=f"Response Distribution for - {question_data} (Percentage)",
    #    width='container'  # Make the chart responsive to container width
    #)#.configure_axis(
    #    labelFontSize=12,  # Increase font size for better readability
    #    titleFontSize=14
    #).configure_legend(
    #    titleFontSize=12,
    #    labelFontSize=12
    #)
    
    # Display the chart in Streamlit with full width
    st.altair_chart(chart, use_container_width=True)


def fun_exc_estudantes(A):
    
    """
Renames columns in a DataFrame based on a predefined dictionary.

    This function renames the columns of an input DataFrame (A) according to 
    a mapping defined in the `dic_exc` dictionary. If a column name is not 
    found in the dictionary, it remains unchanged.  It also ensures that all
    keys from the dic_exc values are present as columns in the output DataFrame,
    filling missing ones with None.

    Args:
        A (pd.DataFrame): The input DataFrame whose columns need to be renamed.

    Returns:
        pd.DataFrame: A new DataFrame with potentially renamed columns and 
                      guaranteed presence of all keys from dic_exc values.
    """
    
    dic_exc={}
    dic_exc[ 'Area'						]=	'Unidade'
    dic_exc[ 'Campus'					]=	'Campus'
    dic_exc[ 'Nivel'					]=	'Perfil'
    dic_exc[ 'Nivelcurso'	    		]=	'Perfil'
    dic_exc[ 'Avaliasetores[PROAE]'		]=	'AvaliaSetores[PROAE]'
    dic_exc[ 'Avaliasetores[PROCULT]'	]=	'AvaliaSetores[PRCUL]'
    dic_exc[ 'Avaliasetores[PROEX]'		]=	'AvaliaSetores[PROEX]'
    dic_exc[ 'Avaliasetores[PROGRAD]'	]=	'AvaliaSetores[PRGRA]'
    dic_exc[ 'Avaliasetores[PROPP]'		]=	'AvaliaSetores[PROPP]'
    dic_exc[ 'Avaliasetores[DIAAF]'		]=	'AvaliaSetores[DIAAF]'
    dic_exc[ 'Avaliasetores[DRI]'		]=	'AvaliaSetores[DRI]'
    dic_exc[ 'Avaliasetores[COORD]'		]=	'AvaliaSetores[COORD]'
    dic_exc[ 'Avaliasetores[OUVG]'		]=	'AvaliaSetores[OUVID]'
    dic_exc[ 'Avaliasetores[CAT]'		]=	'AvaliaSetores[CATEND]'
    dic_exc[ 'EstReg'					]=	'EstReg'
    dic_exc[ 'Regimento'				]=	'RAGRI'
    dic_exc[ 'OrgCol[DivDec]'			]=	'OrgCo[DivDec]'
    dic_exc[ 'OrgCol[ImplDec]'			]=	'OrgCo[ImplDec]'
    dic_exc[ 'OrgCol[RepDec]'			]=	'OrgCo[RepOrgCol]'
    dic_exc[ 'CPA'						]=	'CPA'
    dic_exc[ 'ApRecFin[DesAtEns]'		]=	'AplRF[DAtEn]'
    dic_exc[ 'ApRecFin[DesAtPesq]'		]=	'AplRF[DAtPe]'
    dic_exc[ 'ApRecFin[DesAtEx]'		]=	'AplRF[DAtEx]'
    dic_exc[ 'ApRecFin[DesAtInov]'		]=	'AplRF[DAtInov]'
    dic_exc[ 'ApRecFin[AqEqIns]'		]=	'AplRF[AqEqi]'
    dic_exc[ 'ApRecFin[ManAmpRef]'		]=	'AplRF[MAREF]'
    dic_exc[ 'ApRecFin[BProjPesqEx]'	]=	'AplRF[BProj]'
    dic_exc[ 'ApRecFin[BMonitTP]'		]=	'AplRF[BMoTP]'
    dic_exc[ 'ApRecFin[ConcAux]'		]=	'AplRF[CAVS]'
    dic_exc[ 'TranspInv'				]=	'TrInv'
    dic_exc[ 'AvaliaSetores[PROINOV]'	]=	'AvaliaSetores[PROINOV]'
    dic_exc[ 'Qaberta'               	]=	'Qaberta'
    
    #exc_dic=dict(zip(dic_exc.values(), dic_exc.keys()))
    
    B=pd.DataFrame()
    for c in A.columns:
        if c  in dic_exc.keys():
            B[dic_exc[c]]=A[c]
        else:
            B[c]=A[c]

    for c in dic_exc.values():
        if c  not in B.columns:
            B[c]=None
            
    
    return B


def fun_exc_servidores(A):
    
    """
Creates a new DataFrame with standardized column names.

    This function takes a Pandas DataFrame as input and returns a new DataFrame 
    with potentially renamed columns based on a predefined dictionary `dic_exc`. 
    If a column name in the input DataFrame exists as a key in `dic_exc`, it's 
    renamed to the corresponding value. Columns not found in `dic_exc` are kept 
    as is, and any values from dic_exc that aren't present in the original dataframe
    are added as new columns with None values.

    Args:
        A: The input Pandas DataFrame.

    Returns:
        pd.DataFrame: A new Pandas DataFrame with standardized column names.
    """
    
    dic_exc={}
    dic_exc['Perfil'        	    ]=	'Perfil'
    dic_exc['Campus'	            ]=	'Campus'
    dic_exc['Area'	                ]=	'LOTACAO'
    dic_exc['Capacitacao'	        ]=	'CAP'
    dic_exc['Qualificacao'	        ]=	'Proquali'
    dic_exc['Acoesdesenv'	        ]=	'Acoesdesenv'
    dic_exc['apoiofin'	            ]=	'Apoio'
    dic_exc['DistCHDoc'	            ]=	'CHdocente'
    dic_exc['DistCHTae'	            ]=	'CHTAE'
    dic_exc['Qualivida'	            ]=	'Qualivida'
    dic_exc['Saudeocupa'	        ]=	'Saudeocupacional'
    dic_exc['Divulgacarr'	        ]=	'DivulCarreira'
    dic_exc['ClimaOrg'	            ]=	'Ambiente'
    dic_exc['Motivacao'	            ]=	'Motivacao'
    dic_exc['OrgCol[DivDec]'	    ]=	'ORGCOL[DIVDEC]'
    dic_exc['OrgCol[ImplDec]'	    ]=	'ORGCOL[IMPLDEC]'
    dic_exc['OrgCol[RepOrgCol]'	    ]=	'ORGCOL[REPORGCOL]'
    dic_exc['AvaliaSetores[REIT]'	]=	'AVALIASETORES[REIT]'
    dic_exc['AvaliaSetores[PROAE]'	]=	'AVALIASETORES[PROAE]'
    dic_exc['AvaliaSetores[PROPP]'	]=	'AVALIASETORES[PROPP]'
    dic_exc['AvaliaSetores[PRGRA]'	]=	'AVALIASETORES[PRGRA]'
    dic_exc['AvaliaSetores[PROEX]'	]=	'AVALIASETORES[PROEX]'
    dic_exc['AvaliaSetores[PRCUL]'	]=	'AVALIASETORES[PRCUL]'
    dic_exc['AvaliaSetores[PRINF]'	]=	'AVALIASETORES[PRINF]'
    dic_exc['AvaliaSetores[PRGPE]'	]=	'AVALIASETORES[PRGPE]'
    dic_exc['AvaliaSetores[DUX]'	]=	'AVALIASETORES[DUX]'
    dic_exc['AVALIASETORES[PRGEF]'	]=	'AVALIASETORES[PRGEF]'
    dic_exc['AvaliaSetores[PRPLA]'	]=	'AVALIASETORES[PROPLAN]'
    dic_exc['AvaliaSetores[DI]'	    ]=	'AVALIASETORES[PRINOV]'
    dic_exc['AVALIASETORES[PRODAV]'	]=	'AVALIASETORES[PRODAV]'
    dic_exc['AvaliaSetores[DRI]'	]=	'AVALIASETORES[DRI]'
    dic_exc['AvaliaSetores[DII]'	]=	'AVALIASETORES[DII]'
    dic_exc['AvaliaSetores[CDX]'	]=	'AVALIASETORES[CDX]'
    dic_exc['AvaliaSetores[DIRGGV]'	]=	'AVALIASETORES[DIRGGV]'
    dic_exc['AvaliaSetores[DIAFF]'	]=	'AVALIASETORES[DIAAF]'
    dic_exc['AVALIASETORES[DSP]'	]=	'AVALIASETORES[DSP]'
    dic_exc['AVALIASETORES[DCI]'	]=	'AVALIASETORES[DCI]'
    dic_exc['EstReg'            	]=	'ESTREG'
    dic_exc['RegUni'            	]=	'REGUNI'
    dic_exc['CPA'               	]=	'CPA'
    dic_exc['AplRF[DAtEn]'	        ]=	'APLRF[DAtEn]'
    dic_exc['AplRF[DAtPe]'	        ]=	'APLRF[DAtPe]'
    dic_exc['AplRF[DAtEx]'	        ]=	'APLRF[DAtEx]'
    dic_exc['AplRF[DAtInov]'	    ]=	'APLRF[DAtInov]'
    dic_exc['AplRF[AqEqi]'	        ]=	'APLRF[AqEqi]'
    dic_exc['AplRF[MAREF]'	        ]=	'APLRF[MAREF]'
    dic_exc['AplRF[InCapS]'	        ]=	'APLRF[InCapS]'
    dic_exc['AplRF[BProj]'	        ]=	'APLRF[BProj]'
    dic_exc['AplRF[BMoTP]'	        ]=	'APLRF[BMoTP]'
    dic_exc['TrInv'	                ]=	'TrInv'
    dic_exc['ABERTA'	            ]=	'ABERTA'
    dic_exc['AtivAdm'	            ]=	'AtivAdm'
    dic_exc['SitTrab'	            ]=	'SitTrab'
    dic_exc['Qualicursos'	        ]=	'Qualicursos'
    dic_exc['AvaliaSetores[DIAVI]'	]=	'AvaliaSetores[DIAVI]'
    
    B=pd.DataFrame()
    for c in A.columns:
        if c  in dic_exc.keys():
            B[dic_exc[c]]=A[c]
        else:
            B[c]=A[c]

    for c in dic_exc.values():
        if c  not in B.columns:
            B[c]=None
            
    
    return B


# Função para listar as pastas (anos) dentro da pasta 'data'
def listar_anos(diretorio):
    """
Lists the years (subdirectories) within a given directory.

    Args:
        diretorio: The path to the directory to list years from.

    Returns:
        list[str]: A sorted list of year directories found in the specified directory.
    """
    # Obtém a lista de pastas dentro da pasta 'data'
    anos = [pasta for pasta in os.listdir(diretorio) if os.path.isdir(os.path.join(diretorio, pasta))]
    return sorted(anos)  # Ordena os anos de forma crescente


styles = [dict(selector="th", props=[('width', '40px')]),
                  dict(selector="th.col_heading",
                       props=[("writing-mode", "vertical-lr"),
                              ('transform', 'rotateZ(180deg)'), 
                              #('height', '290px'),
                              ('horizontal-align', 'bottom'),
                              ('vertical-align', 'bottom')])]

def color_coding_change_flag_2(val):
        """
Returns a string representing the background color based on the input value.

    Args:
        val: The input value to determine the color.

    Returns:
        str: A string formatted as 'background-color: {color}', where color is 
             'red', 'orange', 'yellow', 'green', or None depending on the value of val.
    """
        if val==None or val=='':
            color = None
        else:
            if val>=0 and val <25:
                color = "red"
            elif val>=25 and val <50:
                color = "orange"     
            elif val>=50 and val <75:
                color = "yellow"     
            elif val>=75:
                color = "green"     
            else:
                color = None
    
        return f'background-color: {color}'
    

repl={
 'Concordo'                   : '2-Concordo'                   ,
 'Concordo totalmente'        : '1-Concordo totalmente'        ,
 'Discordo'                   : '4-Discordo'                   ,
 'Discordo totalmente'        : '5-Discordo totalmente'        ,
 'Não concordo nem discordo'  : '3-Não concordo nem discordo'  ,
 'Não sei / Não se aplica'    : '6-Não sei / Não se aplica'    ,
 '':'6-Não sei / Não se aplica' ,
}

repl0={
 'Concordo'                   : 0.66,
 'Concordo totalmente'        : 1,
 'Discordo'                   : 0.33,
 'Discordo totalmente'        : 0,
 'Não concordo nem discordo'  : None,
 'Não sei / Não se aplica'    : None,
 '':None,
}

#%%
    
css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:3rem;
    }
</style>
'''

#st.set_page_config(layout="wide")  # this needs to be the first Streamlit command
st.markdown(css, unsafe_allow_html=True)

# Streamlit app
def main():

    """
Main function for the Avalia UFJF 2024 application.

    This function sets up a Streamlit web application to display and analyze
    evaluation data from students and servers of Universidade Federal de Juiz de Fora.
    It includes tabs for results, comparison, and raw data exploration, allowing users
    to filter and visualize satisfaction indices based on selected criteria.

    Args:
        None

    Returns:
        None
    """

    st.header("Universidade Federal de Juiz de Fora")
    st.markdown("[**Comissão Própria de Avaliação**](https://www2.ufjf.br/cpa/)")
    st.image('avalia-ufjf-2024.png', caption='')
    st.title('Avalia UFJF 2024 - Ciclo 1')
    ## Create tabs


    perfil_selecionado = st.radio("Escolha o Perfil para análise", ['Estudantes', 'Servidores'])
    pasta_dados = "data"

    fun_exc={
        'Estudantes': fun_exc_estudantes,
        'Servidores': fun_exc_servidores,
        } 
    

    tab1, tab2, tab3 = st.tabs(["Resultados", "Comparação", 'Dados'])
    with tab2:
    
        anos = listar_anos(pasta_dados)[::-1]
        # Cria um seletor de ano a partir das pastas listadas
        C=pd.DataFrame()
        for ano_selecionado in anos:
            cod_path = f'./data/2024/Códigos_{perfil_selecionado}.csv'
            file_path = f'./data/{ano_selecionado}/{perfil_selecionado}_dados_{ano_selecionado}.csv'
            uploaded_file = f'questions_and_subquestions_{perfil_selecionado}.csv'
            questions = extract_questions_and_subquestions(cod_path)
            A = pd.read_csv(file_path, sep=';', keep_default_na=False)
            questions = extract_questions_and_subquestions(cod_path)
            A = pd.read_csv(file_path, sep=';', keep_default_na=False)
            A=fun_exc[perfil_selecionado](A)    
            A = remove_single_occurrences(A)
            A.fillna('', inplace=True)
            A['Ano']=ano_selecionado
            C = pd.concat([C,A])
            Q = transform_questions_to_dataframe(questions)
            Q = include_subquestion(A,Q, uploaded_file)
            dic_q = dict(zip(Q['subquestions'].values,Q['text'].values))
           
        D=[]
        question_data_values = Q['question_data'].unique()
        for ano, A in C.groupby('Ano'):
            print('----\n'*12)
            for question_data in question_data_values:
                #print(f"### - {question_data}")
                # Filter data for the current question_data
                question_data_df = Q[Q['question_data'] == question_data]
                cols=list(question_data_df['subquestions'].unique())
                print('\n', cols)
                
                B=A[cols].replace(repl0).select_dtypes(include=['number'])
                satisfaction_index = (B.sum(skipna=True)/B.count()*100).round(2)
                neg=((1-B.count()/len(B))*100).round(2)
                satisfaction_index.index = [dic_q[i] for i in satisfaction_index.index]
                satisfaction_index = pd.DataFrame(satisfaction_index, columns = ['Indice de Satisfação (%)'])
                print(ano, satisfaction_index)
                D.append({'Ano':ano, 'Item':question_data, 'df':satisfaction_index})
    
        D = pd.DataFrame(D)            
        for i, df in D.groupby('Item'):
            print(i)
            c=pd.DataFrame()
            for a, da in df.groupby('Ano'):
                aux=da['df'].iloc[0]
                aux.columns=[a]
                c[a]=aux[a]
            
            print(c)
            if len(c)>0:
                st.write(f"### - {i}")
                st.table(
                    c.style.applymap(
                        color_coding_change_flag_2, #subset=NPS.columns.drop('Ambiente'),
                    ).set_table_styles(styles).format("{:.1f}"),
                    #height=1200,
                    #hide_index=False,
                    #use_container_width=True,
                )
    

    with tab1:
        #perfil_selecionado = st.radio("Escolha o Perfil", ['Estudantes', 'Servidores'])
        ano_selecionado = st.radio("Escolha um ano", anos)
        # Exibe os arquivos dentro da pasta selecionada
        caminho_pasta_ano = os.path.join(pasta_dados, ano_selecionado)
       
        
        cod_path = f'./data/2024/Códigos_{perfil_selecionado}.csv'
        file_path = f'./data/{ano_selecionado}/{perfil_selecionado}_dados_{ano_selecionado}.csv'
        uploaded_file = f'questions_and_subquestions_{perfil_selecionado}.csv'
    
        questions = extract_questions_and_subquestions(cod_path)
        A = pd.read_csv(file_path, sep=';', keep_default_na=False)
        A=fun_exc[perfil_selecionado](A)    
        A = remove_single_occurrences(A)
        A.fillna('', inplace=True)     
        A.drop(['Unidade','LOTACAO'], axis=1, errors='ignore', inplace=True)
        #A.replace(repl, inplace=True)
        
        keys_dict = {}
        length={}
        nn=2
        cols=sorted(A.columns[:nn])
        for s in cols:
            #s = A.columns[i]
            #op = list(A[A.columns[i]].unique())
            op = list(A[s].unique())
            options = st.multiselect(
                label=f"{s}",
                options = op,
                default=None,
                key=f'res-{s}',
            )
            keys_dict[s]=options
            length[s]=len(options)
    
        keys=keys_dict.copy()
        for nam,opt in keys_dict.items():
            print(nam,opt)
            if len(opt)==0:
                keys.pop(nam)
            for k in opt:
                if 'Tod' in k:
                    keys.pop(nam)
               
           #df_selected=X.copy()    
        st.markdown('Parâmetros selecionados:')    
        if len(keys)>0:    
            q=''
            for nam,opt in keys.items():
                #print(nam)
                s='('
                for i,k in enumerate(opt):
                    #print('\t\t--',k)
                    s+=f'{nam}=="{k}"'
                    if i<len(opt)-1:
                        s+=' | '
                
                s+=')'
                #print(s)
                q+=s+'&'
                #aux=X.query(f'{nam}=="{k}"', inplace=True)
                #st.metric(label=nam+':\t', value=k, delta="")
            df_selected = A.query(q[:-1])
        else:
            df_selected = A.copy()                            
    
    
        if len(df_selected)==1:
                df_selected.drop(labels=df_selected.index[0],axis=0, inplace=True)
                
        col = st.columns(1)
        #for i in range(nn):
        #    s, v = list(length.keys())[i], list(length.values())[i]
        #    col[i].metric(label=s, value=v, delta="")
    
        col[0].metric(label='Respondentes', value=len(df_selected), delta="")
    
                
        Q = transform_questions_to_dataframe(questions)
        Q = include_subquestion(df_selected,Q, uploaded_file)
        dic_q = dict(zip(Q['subquestions'].values,Q['text'].values))
    
      
        question_data_values = Q['question_data'].unique()
        for question_data in question_data_values:
            #print(f"### - {question_data}")
            # Filter data for the current question_data
            question_data_df = Q[Q['question_data'] == question_data]
            cols=list(question_data_df['subquestions'].unique())
            print('\n', cols)
           
            B=df_selected[cols].replace(repl0).select_dtypes(include=['number'])
            satisfaction_index = (B.sum(skipna=True)/B.count()*100).round(2)
            neg=((1-B.count()/len(B))*100).round(2)
            satisfaction_index.index = [dic_q[i] for i in satisfaction_index.index]
            satisfaction_index = pd.DataFrame(satisfaction_index, columns = ['Indice de Satisfação (%)'])
            #satisfaction_index['Não sei/Não se aplica (%)'] = neg.values
            if len(satisfaction_index)>0:
                st.write(f"### - {question_data}")
                st.table(
                    satisfaction_index.style.applymap(
                        color_coding_change_flag_2, #subset=NPS.columns.drop('Ambiente'),
                    ).set_table_styles(styles).format("{:.1f}"),
                    #height=1200,
                    #hide_index=False,
                    #use_container_width=True,
                )
    
    
        B=df_selected[list(dic_q.keys())].replace(repl0).select_dtypes(include=['number'])
        satisfaction_index = (B.sum(skipna=True)/B.count()*100).round(2)
        neg=((1-B.count()/len(B))*100).round(2)
        satisfaction_index.index = [dic_q[i] for i in satisfaction_index.index]
        satisfaction_index = pd.DataFrame(satisfaction_index, columns = ['Indice de Satisfação (\%)'])
        #satisfaction_index['Item avaliado'] = [dic_q[i] for i in satisfaction_index.index]
        #satisfaction_index = satisfaction_index[['Item avaliado','Indice de Satisfação (\%)']]
        satisfaction_index['Não sei/Não se aplica (%)'] = neg.values
    
        #st.dataframe(satisfaction_index,use_container_width=True,hide_index=False)
        #st.bar_chart(satisfaction_index)
        st.title("Resumo dos indicadores")    
        st.download_button(
            label="📁 Baixar o resumo como arquivo CSV",
            data=satisfaction_index.to_csv(index=True, sep=',').encode('utf-8'),
            file_name=f'indice_satisfacao_resumo_selecao_{perfil_selecionado}_{ano_selecionado}.csv'.lower(),
            mime='text/csv'
        )
        
        
        
        #print(satisfaction_index)
        st.table(
            #satisfaction_index.style.applymap(
            #    color_coding_change_flag_2, #subset=NPS.columns.drop('Ambiente'),
            #).set_table_styles(styles).format("{:.1f}"),
    
            satisfaction_index.style.set_table_styles(styles).format("{:.1f}"),
    
            #height=1200,
            #hide_index=False,
            #use_container_width=True,
        )    
    
    with tab3:
         st.header("Dados")
         #perfil_selecionado = st.radio("Escolha o Perfil", ['Estudantes', 'Servidores'])
         ano_selecionado = st.radio("Escolha o ano de referência", anos)
         # Exibe os arquivos dentro da pasta selecionada
         caminho_pasta_ano = os.path.join(pasta_dados, ano_selecionado)
        
         
         cod_path = f'./data/2024/Códigos_{perfil_selecionado}.csv'
         file_path = f'./data/{ano_selecionado}/{perfil_selecionado}_dados_{ano_selecionado}.csv'
         uploaded_file = f'questions_and_subquestions_{perfil_selecionado}.csv'
     
         questions = extract_questions_and_subquestions(cod_path)
         A = pd.read_csv(file_path, sep=';', keep_default_na=False)
         A=fun_exc[perfil_selecionado](A)    
         A = remove_single_occurrences(A)
         A.fillna('', inplace=True)       
         A.replace(repl, inplace=True)
         A.drop(['Unidade','LOTACAO'], axis=1, errors='ignore', inplace=True)

         
         keys_dict = {}
         length={}
         nn=2
         cols=sorted(A.columns[:nn])
         for s in cols:
             #s = A.columns[i]
             #op = list(A[A.columns[i]].unique())
             op = list(A[s].unique())
             options = st.multiselect(
                 label=f"{s}",
                 options = op,
                 default=None,
                 key=f'dados-{s}',
             )
             keys_dict[s]=options
             length[s]=len(options)
     
         keys=keys_dict.copy()
         for nam,opt in keys_dict.items():
             print(nam,opt)
             if len(opt)==0:
                 keys.pop(nam)
             for k in opt:
                 if 'Tod' in k:
                     keys.pop(nam)
                
            #df_selected=X.copy()    
         st.markdown('Parâmetros selecionados:')    
         if len(keys)>0:    
             q=''
             for nam,opt in keys.items():
                 #print(nam)
                 s='('
                 for i,k in enumerate(opt):
                     #print('\t\t--',k)
                     s+=f'{nam}=="{k}"'
                     if i<len(opt)-1:
                         s+=' | '
                 
                 s+=')'
                 #print(s)
                 q+=s+'&'
                     #aux=X.query(f'{nam}=="{k}"', inplace=True)
                     #st.metric(label=nam+':\t', value=k, delta="")
             df_selected = A.query(q[:-1])
         else:
             df_selected = A.copy()                            
     
     
         if len(df_selected)==1:
                 df_selected.drop(labels=df_selected.index[0],axis=0, inplace=True)
                 
         col = st.columns(1)
         #for i in range(nn):
         #    s, v = list(length.keys())[i], list(length.values())[i]
         #    col[i].metric(label=s, value=v, delta="")
     
         col[0].metric(label='Respondentes', value=len(df_selected), delta="")
     
         Q = transform_questions_to_dataframe(questions)
         Q = include_subquestion(df_selected,Q, uploaded_file)

         #st.title("Question and Subquestion Analysis")
        
         if uploaded_file is not None:
             df = pd.read_csv(uploaded_file)

             question_data_values = df['question_data'].unique()
            
             for q_data in question_data_values:
                 create_horizontal_stacked_bar_plots_percentage_data(df, q_data)
    
    
    st.markdown('''
              ----------------------------------------------------\n
              Modelo computacional e análise de dados por [Leonardo Goliatt](http://lattes.cnpq.br/9030707448549156)\n
              Departamento de Mecânica Aplicada e Computacional\n
              Pós-graduação em Modelagem Computacional\n
              Faculdade de Engenharia - UFJF\n
              leonardo.goliatt@ufjf.br
              ''')

if __name__ == "__main__":
    main()        
        

#%%
