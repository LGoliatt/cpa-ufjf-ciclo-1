#!/usr/bin/python
# -*- coding: utf-8 -*-  
import pandas as pd
import csv

def extract_questions_and_subquestions(file_path):
    """
Extracts questions and their subquestions from a tab-separated file.

    Args:
        file_path: The path to the file containing question data.  The file is expected 
            to have rows starting with 'Q' for questions and 'SQ' for subquestions. 
            Each row should be tab separated.

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
               
           
        #if len(question_data['subquestions'])==0:
        #    print(f"{question_id} -- {question_data['text']}")
        #else:
        #    for subquestion in question_data['subquestions']:
        #        print(f"{question_id}[{subquestion['id']}] -- {subquestion['text']}")
                
        
        
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
Includes subquestion data from A into Q and saves to a CSV file.

    Args:
        A: Dictionary containing answer data.
        Q: Dictionary containing question data with 'subquestions' key.
        uploaded_file: Path to the output CSV file.

    Returns:
        Q: The updated question dictionary, which is also saved as a CSV.
    """
    l=[]
    for c in Q['subquestions'].values:
        l.append(list(A[c].values))
        
        
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
        color=alt.Color('data:N', title='Response'),
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
        color=alt.Color('data:N', title='Response'),  # Stack by response type
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
        x=alt.X('percentage:Q', title='Percentage (%)'),  # Percentage on the x-axis
        color=alt.Color('data:N', title='Response'),  # Stack by response type
        tooltip=['subquestions', 'data', 'percentage:Q']  # Add tooltips for interactivity
    ).properties(
        title=f"Response Distribution for Question ID: {question_id} (Percentage)"
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

def create_percentage_table(df, question_data):
    """
Creates and displays a percentage table for a given question's responses.

    Args:
        df: The input DataFrame containing the data.
        question_data: The specific question to analyze.

    Returns:
        None
    """
    st.write(f"### Question Data: {question_data}")
    
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
        question_data: The specific question to analyze.

    Returns:
        None
    """
    st.write(f"### Question Data: {question_data}")
    
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
        x=alt.X('percentage:Q', title='Percentage (%)', scale=alt.Scale(domain=[0, 100])),  # Percentage on the x-axis
        color=alt.Color('data:N', title='Response', legend=alt.Legend(orient='bottom')),  # Stack by response type
        tooltip=['text', 'data', alt.Tooltip('percentage:Q', format='.2f')]  # Add tooltips for interactivity
    ).properties(
        title=f"Response Distribution for Question Data: {question_data} (Percentage)",
        width='container'  # Make the chart responsive to container width
    ).configure_axis(
        labelFontSize=12,  # Increase font size for better readability
        titleFontSize=14
    ).configure_legend(
        titleFontSize=12,
        labelFontSize=12
    )
    
    # Display the chart in Streamlit with full width
    st.altair_chart(chart, use_container_width=True)


    
# Streamlit app
def main():
    
    """
Creates a Streamlit app with two tabs for student and server data analysis.

    This application displays content related to students in one tab and 
    server information in another. It performs question and subquestion 
    analysis using data from CSV files, generating horizontal stacked bar plots 
    to visualize the results.

    Args:
        None

    Returns:
        None
    """
    
    import streamlit as st
    
    # Create a Streamlit app with two tabs
    st.title('Basic Streamlit App with Two Tabs')
    
    # Create tabs
    tab1, tab2 = st.tabs(["Estudantes", "Servidores"])
    
    # Content for the "Estudantes" tab
    with tab1:
        st.header("Estudantes")
        st.write("Content for Estudantes tab goes here.")
    
        cod_path = './data/Códigos_estudantes.csv'
        file_path = './data/Parcial_estudantes_09_02.csv'
        uploaded_file = 'questions_and_subquestions_estudantes.csv'


        questions = extract_questions_and_subquestions(cod_path)
        A = pd.read_csv(file_path, sep=';')
        A = remove_single_occurrences(A)
        Q = transform_questions_to_dataframe(questions)
        Q = include_subquestion(A,Q, uploaded_file)
        
        st.title("Question and Subquestion Analysis")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
    
            question_data_values = df['question_data'].unique()
            
            for q_data in question_data_values:
                create_horizontal_stacked_bar_plots_percentage_data(df, q_data)

    # Content for the "Servidores" tab
    with tab2:
        st.header("Servidores")
        st.write("Content for Servidores tab goes here.")
    
        cod_path = './data/Códigos_servidores.csv'
        file_path = './data/Parcial_servidores_09_02.csv'
        uploaded_file = 'questions_and_subquestions_servidores.csv'


        questions = extract_questions_and_subquestions(cod_path)
        A = pd.read_csv(file_path, sep=';')
        A = remove_single_occurrences(A)
        Q = transform_questions_to_dataframe(questions)
        Q = include_subquestion(A,Q, uploaded_file)
        
        st.title("Question and Subquestion Analysis")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            question_data_values = df['question_data'].unique()
            
            for q_data in question_data_values:
                create_horizontal_stacked_bar_plots_percentage_data(df, q_data)
    
    


if __name__ == "__main__":
    main()        
        
