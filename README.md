# KafkaRedditStreamELKVisualize
Below are the steps to execute program to stream subreddit comments and extract named entities and count them along with displaying a bar graph of the frequency of named entities and their counts of occurrences during certain durations
Assumed steps already completed before hand are:
- Kafka installed
- Hadoop and PySpark environment setup
- ELK Pipeline setup already and running

WARNING: If streaming from a popular subreddit you will need a decent amount of RAM availability if on local or local VM and not some cloud-based cluster like AWS

# Steps begin here
For the steps below involving kafka run after cd $KAFKA_HOME or cd to kafka folder location 

1. Start ZOOKEEPER IN ITS OWN TERMINAL:
bin/zookeeper-server-start.sh config/zookeeper.properties

2. Start KAFKA BROKERS IN ITS OWN TERMINAL:
bin/kafka-server-start.sh config/server.properties

3. Create KAFKA TOPICS 1 & 2 IN A NEW TERMINAL:
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic topic1 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic topic2 --partitions 1 --replication-factor 1

4. Begin streaming data using PRAW from certain subreddit defined in .py file:
If in same terminal cd back to home then execute file or if in specific location cd to that...
python stream_reddit_comments.py
or
python3 stream_reddit_comments.py

5. View the contents of the streaming data in topic 1 (for visaulization sake) IN A NEW TERMINAL:
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic topic1 --from-beginning

6. Begin processing streamed data using from kafka topic1 IN A NEW TERMINAL:
python process_reddit_comments.py
or
python3 process_reddit_comments.py

7. View the contents of the streaming data in topic 2 (for visaulization sake) IN A NEW TERMINAL:
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic topic2 --from-beginning

8. IN A NEW TERMINAL
sudo /usr/share/logstash/bin/logstash -f logstash-named-entity-count.conf
file contains config like below:
input {
  kafka {
    bootstrap_servers => "localhost:9092"
    topics => ["topic2"]
    codec => "json"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "named_entities"
  }
}

Should index data to elasticsearch using logstash

9. Create Kibana index pattern: Web Interface => http://localhost:5601
target named_entities as mentioned in above config

10. Create Kibana Visualization same site go to kibana create visualization and then dashboard then save monitor for time intervals 
