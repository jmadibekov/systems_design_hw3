# Instructions to run

1. Run Neo4j with Docker: 
```shell
$ docker run --restart always --publish=7474:7474 --publish=7687:7687 --env NEO4J_AUTH=neo4j/helloworld neo4j:5.12.0
```
2. Create virtual environment for Python and install dependencies:
```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

3. Run the Python script:
```shell
$ python main.py
```

## Notes

To display the graph with Cypher, run:
```sql
MATCH (n) RETURN n LIMIT 25
```

To delete the whole graph, run:
```sql
MATCH (n) DETACH DELETE n
```