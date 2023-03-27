import boto3
import streamlit as st
import datetime

# define a function to fetch CPUUtilization metric data from CloudWatch
def get_cpu_utilization(region,instance_id,minutes):
    # create a Boto3 session with the specified AWS credentials and region
    session = boto3.Session(
        aws_access_key_id='AKIATCH7KFDEZY2WCB7J',#Paste Your access key
        aws_secret_access_key='IhPrHDZHaJDR8VSEUUAwqQT/G/xpqkZq9km5DLQm',#paste your secret access key
        region_name=region#paste your region  
    )

    # create a CloudWatch client
    cloudwatch = session.client('cloudwatch')

    # specify the time range for which to fetch the metric data
    end_time = datetime.datetime.utcnow()  # current time in UTC
    start_time = end_time - datetime.timedelta(minutes=minutes)


    # use the CloudWatch client to fetch the CPUUtilization metric for the specified instance
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',  # the namespace for EC2 metrics
        MetricName='CPUUtilization',  # the name of the metric to fetch
        Dimensions=[  # the dimensions of the metric
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,  # the granularity of the metric data (in seconds)
        Statistics=['Average']  # the type of statistic to fetch (e.g. average, maximum, minimum)
    )
    datapoints = response['Datapoints']
    if datapoints:
        average_cpu_utilization = sum(point['Average'] for point in datapoints) / len(datapoints)
        return average_cpu_utilization
    else:
        return 0


# define a function to provide a suggestion based on the CPU utilization value
def get_suggestion(cpu_utilization):
    if cpu_utilization == 0:
        return "No CPU utilization data available for the specified time range."
    elif cpu_utilization < 25:
        return "CPU utilization is below 25%, so you may be able to save costs by scaling down the instance."
    elif cpu_utilization < 80:
        return "CPU utilization is between 25% and 80%, so the instance is being used normally."
    else:
        return "CPU utilization is above 80%, so you may need to consider scaling up the instance."


# create a Streamlit app
st.title("AWS EC2 CPU Utilization Analyzer")
#access_key = st.text_input("AWS access key ID:")
#secret_key = st.text_input("AWS secret access key:", type="password")
region = st.text_input("AWS region:")
# instance_id = st.text_input("EC2 instance ID:")
minutes = st.number_input("Number of minutes to analyze:", value=20, min_value=1)

print(ec2Instances.instances.all())
if st.button("Analyze CPU utilization"):
    with st.spinner("Fetching CPU utilization data..."):
        for instance in ec2InstancesList:
            cpu_utilization = get_cpu_utilization(region,instance.id,minutes)
            print(cpu_utilization)
            suggestion = get_suggestion(cpu_utilization)
            st.write(f"{instance.id} -- Average CPU utilization over the past {minutes} minutes: {cpu_utilization:.2f}%")
            st.warning(suggestion)

