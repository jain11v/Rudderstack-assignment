# Introduction

This is an event delivery implementation in Python using Redis
for supporting the desired system's requirements.

- **Durability:** Received events through HTTP are stored inside a Redis queue
  and each destination handler only commit offset after the
  successful processing of the event. After a restart/crash,
  worker resumes from the last delivered offset. 

- **At-least-once delivery:** Redis queues provides at-least-once guarantee
  as long as you make sure that you don't commit offsets for
  unprocessed events.

- **Retry backoff and limit:** Since we care about ordering,
  there is no simple way to implement a retry mechanism using Redis's
  native constructs. This implementation uses an in-memory retry
  mechanism during event processing.

  1. Retries will be done in some time delays. Time delay will be double the 
     previous delay and process will backoff after delay is more than a limit.    
  2. Delays or failures with a single event delivery, affect the delivery
     of all other events behind the problematic event in the same queue.

- **Maintaining order:** Redis queue can guarantee the order of events in the
  same queue. 

- **Delivery isolation:** Different threads in python handles the delivery to
  different destinations which does not hinder with each other i.e. no delays 
  are created because of any delays or failures in any one destination.

## Pipeline
![alt text](https://github.com/jain11v/Rudderstack-assignment/blob/master/app/Rudderstack-pipeline.svg)
1. Here, the gateway service accepts the incoming HTTP requests which contains **_userId_** and the **_payload_** for the event.
2. Gateway, after receiving the request makes a call to redis server and pushes the _event_ to redis queue. Only after pushing the _event_ to the queue, a success response is returned.
3. Router service handles the job of routing the events in the redis queue and send them to muptiple destinations. Destinations used in this projects are: 
    - Webhooks
    - mongoDB
4. Router service picks up an event from redis queue (FIFO) and further send it across all the destinations. If event is successfully processed then that event is acknowledged in the redis queue. If anything goes wrong during this process, that message is not acknowledged. 
5. Destination handlers works in parallel during handling of any single event, i.e. if there is some delay in sending event to a particular destination, it does not affect time taken by other destination handlers.
6. Each destination handler has a failure retry mechanism under which if there is a failure during this process, a retry is initiated. These retries are done in increasing time delays (in each retry delay is set to double the previous time) and if the delay time crosses a certain limit, error is logged.  

## Installation
Docker to handle environment and dependencies. Run the docker containers.

```sh
sudo docker-compose up
```
This will start the following containers:
- Redis server
- MongoDB server
- Flask App which will expose APIs to receive events.
- Python script which will handle delivery of events to different destination.
- Flask app which act as destination webhooks
#### Run test cases:
- Initiate the docker containers.
```sh
sudo docker compose up
```
- Check process status of the running docker containers and copy the container Id of gateway container
```sh
sudo docker ps
```
- Using the container Id of gateway container enter into its shell.
```sh
sudo docker exec -it <container_id> /bin/sh
```
- Go into tests directory
```sh
cd tests
```
- Run the python script for unit testing
```sh
python3 unittests.py
```
## Compromises

1. A single slow or failing message will block all messages behind the
   problematic message, ie. the entire partition. The process may recover,
   but the latency of all the messages behind the problematic one will be
   negatively impacted severely.
2. If the rounting server crashes when the routing to different destinations 
   was done and acknowledgement to redis was pending, in that case when the server 
   starts again it will again pick up the event and will again process it.

## Further Work
1. In this assignment, we currently operate under the assumption that every event will be disseminated to all available destinations. However, in practical scenarios, this may not always hold true. Each HTTP request may specify a specific set of destinations to which it should be directed. There are two potential approaches to address this issue:
- Incorporate destination information as part of the HTTP request itself, allowing a dedicated controller to manage event delivery based on this information.
- Develop a separate controller service responsible for routing events to their respective destinations by analyzing the event's source.
