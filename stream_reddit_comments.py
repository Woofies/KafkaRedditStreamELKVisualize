import praw
from kafka import KafkaProducer

# PRAW setup and extracting the comments from the selected subreddit
# Need to have your own reddit account and create an app to get values to fill fields below
reddit = praw.Reddit(
	client_id="your client id",
	client_secret="your client secret",
	password="yourpassword",
	user_agent = "whatever",
	username="yourusername",
)

# Kafka settings for topic1
kafka_bootstrap_servers = "localhost:9092"
topic1 = "topic1"

# Initialize Kafka producer for topic1
producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)

# Fetch comments from the subreddit and publish to Kafka topic1
subreddit = reddit.subreddit('amitheasshole')
comment_stream = subreddit.stream.comments(skip_existing=True)

for comment in comment_stream:
    # Extract the comment body
    comment_body = comment.body
    # Send the comment body to topic1
    producer.send(topic1, value=comment_body.encode('utf-8'))

# Close the Kafka producer when finished
producer.close()
