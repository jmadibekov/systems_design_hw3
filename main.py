from neo4j import GraphDatabase


class HelloWorldExample:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_all_nodes(self):
        query = """
CREATE
(AppClient:Component {name: "App client"}),
(Redis:Component {name: "Redis"}),
(Mongo:Component {name: "Mongo DB"}),
(FullAPI:Component {name: "Full info API"}),
(BatchAPI:Component {name: "Batch info API"}),
(FullAPIJob:Component {name: "Full info retrieval job"}),
(BatchAPIJob:Component {name: "Batch info retrieval job"})
CREATE 
(AppClient)-[:USES {description: "Checks whether info is in cache and gets it"}]->(Redis),
(AppClient)-[:USES {description: "Gets batch info from storage"}]->(Mongo),
(AppClient)-[:USES {description: "Creates request for info retrieval"}]->(FullAPIJob),
(AppClient)-[:USES {description: "Creates request for info retrieval"}]->(BatchAPIJob)
"""
        summary = self.driver.execute_query(
            query,
            database_="neo4j",
        ).summary
        print(
            "Created {nodes_created} nodes in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after,
            )
        )

    def print_greeting(self, message):
        with self.driver.session() as session:
            greeting = session.execute_write(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run(
            "CREATE (a:Greeting) "
            "SET a.message = $message "
            "RETURN a.message + ', from node ' + id(a)",
            message=message,
        )
        return result.single()[0]


if __name__ == "__main__":
    greeter = HelloWorldExample("bolt://localhost:7687", "neo4j", "helloworld")
    greeter.create_all_nodes()
    greeter.close()
