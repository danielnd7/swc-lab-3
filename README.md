## 1. What to Do

The goal is to create a Python application that you will run  times simultaneously. The requirements are:

* 
**Unique Identification:** Each instance must have a unique ID passed via the command line.


* 
**Measurement Simulation:** Each instance generates a random measurement every 5 seconds.


* 
**Data Storage:** These measurements must be stored in Zookeeper using **ephemeral znodes** at the path `/mediciones/{id}`.


* 
**Leader Election:** One of the  instances must be elected as the "Leader" using Kazoo’s `Election` recipe.


* 
**Leader Responsibility:** The leader must retrieve all measurements from Zookeeper, calculate their average, and send it to an external REST API.


* 
**Fault Tolerance:** The system must keep working if any node (including the leader) fails.



---

## 2. Implementation Steps

### A. Environment Setup

First, ensure you have Zookeeper running and the necessary Python library installed.

1. **Start Zookeeper via Docker:**
```bash
docker run --name some-zookeeper --restart always -d -p 2181:2181 zookeeper
[cite_start]``` [cite: 17]

```


2. **Install Kazoo and Requests:**
```bash
pip install kazoo requests
[cite_start]``` [cite: 26, 47]


```



### B. Coding the Application

Your Python script (e.g., `app.py`) should follow this logical structure:

1. 
**Initialize Connection:** Connect to Zookeeper using `KazooClient(hosts='127.0.0.1:2181')`.


2. **Define the Leader Task:** Create a function that:
* Lists all children of `/mediciones`.


* Reads the data from each child znode.
* Calculates the average.
* Sends a POST/GET request to your API using `requests.get(url, params=params)`.




3. **Leader Election:** Use the `Election` recipe. Only the winner will execute the leader task loop.


```python
election = client.Election("/election_path", "identifier")
election.run(leader_task_function)

```


4. **Worker Task (Measurement):** All nodes (including the leader) must:
* Create an **ephemeral znode** at `/mediciones/{id}`.


* Update this znode every 5 seconds with a new random value.





---

## 3. How to Test Your Implementation

The document suggests several ways to verify your work:

### Testing the Leader Election and Data

1. **Run multiple instances:** Open three terminals and run the script with different IDs:
* Terminal 1: `python app.py 1`
* Terminal 2: `python app.py 2`
* Terminal 3: `python app.py 3` 




2. **Check Zookeeper CLI:** Enter the Zookeeper container to see if the znodes are being created correctly:
```bash
docker exec -it some-zookeeper zkCli.sh
ls /mediciones
get /mediciones/1
[cite_start]``` [cite: 18, 19, 21]


```



### Testing the REST API Sending

If you don't have the API from your previous practice running, use a simple Python local server to verify that the Leader is actually sending data:

* 
**Run a dummy listener:** `python -m http.server 8000`.


* Check the terminal of this listener to see incoming GET/POST requests from your Leader node.

### Testing Fault Tolerance

1. **Kill a follower:** Stop one of the non-leader scripts. Verify that its znode in `/mediciones` disappears (because it's ephemeral).


2. **Kill the Leader:** Stop the leader script. Observe one of the other terminals; Kazoo should automatically elect a new leader to take over the averaging and reporting tasks.
