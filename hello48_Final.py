import boto3
import streamlit as st
import datetime
import base64
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('blue.jpg')
st.markdown("""
    <style>
    .st-b5 {
        padding: 0.5rem;
        background-color: #ffd700;
        border-color: #ffd700;
        color: #000000;
        border-radius: 0.25rem;
    }
    </style>
    """, 
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    div.st-cc {
        background-color: #f8f9fa !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
def create_bar_chart(data, labels):
    # Create bar chart
    fig, ax = plt.subplots()
    x = np.arange(len(data))
    ax.bar(x, data)

    # Set title and labels
    ax.set_title('Comparison of values')
    ax.set_xlabel('Labels')
    ax.set_ylabel('Values (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    return fig
# define a function to fetch CPUUtilization metric data from CloudWatch for all instances in the specified region
def get_cpu_utilization_all_instances(region, minutes):
    # create a Boto3 session with the specified AWS credentials and region
    session = boto3.Session(
        aws_access_key_id='AKIASDR4F7U3VOLC4LUG',
        aws_secret_access_key='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',
        region_name=region
    )

    # create EC2 and CloudWatch clients
    ec2 = session.client('ec2')
    cloudwatch = session.client('cloudwatch')

    # get information about all instances in the region
    response = ec2.describe_instances()
    instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]

    # loop through the instances and fetch the CPUUtilization metric data for each instance
    cpu_utilizations = []
    instance_data = []
    for instance in instances:
        instance_id = instance['InstanceId']
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',  # the namespace for EC2 metrics
            MetricName='CPUUtilization',  # the name of the metric to fetch
            Dimensions=[  # the dimensions of the metric
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes),
            EndTime=datetime.datetime.utcnow(),
            Period=60,  # the granularity of the metric data (in seconds)
            Statistics=['Average']  # the type of statistic to fetch (e.g. average, maximum, minimum)
        )
        datapoints = response['Datapoints']
        if datapoints:
            average_cpu_utilization = sum(point['Average'] for point in datapoints) / len(datapoints)
            cpu_utilizations.append(average_cpu_utilization)
            instance_data.append({'InstanceId': instance_id, 'AvgCPUUtilization': average_cpu_utilization})
    df = pd.DataFrame(instance_data)
    st.header("Reports")
    st.write(df)
    values_list = df.values.tolist()
    data=[row[1] for row in values_list]
    labels=[row[0] for row in values_list]
    st.header("Bar Chart")
    fig = create_bar_chart(data, labels)
    st.pyplot(fig)

    if cpu_utilizations:
        average_cpu_utilization_all_instances = sum(cpu_utilizations) / len(cpu_utilizations)
        return average_cpu_utilization_all_instances
    else:
        return None
    
    

# define a function to provide a suggestion based on the CPU utilization value
def get_suggestion(cpu_utilization):
    if cpu_utilization is None:
        return "No CPU utilization data available for the specified time range."
    elif cpu_utilization < 25:
        return "CPU utilization is below 25%, so you may be able to save costs by scaling down the instance."
    elif cpu_utilization < 80:
        return "CPU utilization is between 25% and 80%, so the instance is being used normally."
    else:
        return "CPU utilization is above 80%, so you may need to consider scaling up the instance."


# create a Streamlit app
st.title("AWS EC2 CPU Utilization Analyzer")
#st.markdown("<div style='border:1px solid #ccc; padding:10px'>", unsafe_allow_html=True)
#access_key = st.text_input("AWS access key ID:")
#secret_key = st.text_input("AWS secret access key:", type="password")
region = st.text_input("AWS region:")
#instance_id = st.text_input("EC2 instance ID:")
minutes = st.number_input("Number of minutes to analyze (UTC):", value=20, min_value=10,max_value=1440)
f1=str(minutes)
if st.button("Analyze CPU utilization"):
    with st.spinner("Fetching CPU utilization data..."):
        cpu_utilization = get_cpu_utilization_all_instances(region, minutes)
    suggestion = get_suggestion(cpu_utilization)
    st.header("Suggetion")
    st.warning(f"Average CPU utilization over the past {minutes} minutes: {cpu_utilization:.2f}%")
    st.warning(suggestion)
