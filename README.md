Introduction
============

This is an event delivery implementation in Python using Redis
for supporting the desired system's requirements.

- **Durability:** Received events through HTTP are stored inside a Redis queue
  and each destination handler only commit offset after the
  successful processing of an event. after a restart/crash,
  worker shall resume from the last delivered offset. 

- **At-least-once delivery:** Redis queues provides at-least-once guarantees
  as long as you make sure that you don't commit offsets for
  unprocessed events.

- **Retry backoff and limit:** Since we care about ordering guarantees,
  there is no simple way to implement a retry mechanism using Redis's
  native constructs. This implementation uses an in-memory retry
  mechanism during event processing.

  1. Retries will be done in some time delays. Time delay will be double the 
     previous delay and process will backoff after delay is more than a limit.    
  2. Delays or failures with a single event delivery, affect the delivery
     of all other events behind the problematic event in the same queue.

- **Maintaining order:** Redis queue can guarantee the order of events in the
  same queue. 

- **Delivery isolation:** Parallel threads in python handles the delivery to
  different destinations which does not hinder with each other i.e. no delays 
  are created because of any delays or failures in any one destination.

# Compromises

1. A single slow or failing message will block all messages behind the
   problematic message, ie. the entire partition. The process may recover,
   but the latency of all the messages behind the problematic one will be
   negatively impacted severely.

Running docker containers
=================

1. Run docker compose which will start the following containers:
- Redis server
- MongoDB server
- Flask App which will expose APIs to receive events.
- Python script which will handle delivery of events to different destination.
- Python script to verify unit test cases.
