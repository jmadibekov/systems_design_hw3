import pandas as pd
from neo4j import GraphDatabase


class HelloWorldExample:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_all_nodes(self):
        query = """
        CREATE
        (AppClient:Component {name: "App client", fanIn: 0, fanOut: 0}),
        (RedisClient:Component {name: "Redis client", fanIn: 0, fanOut: 0}),
        (Redis:Component {name: "Redis", fanIn: 0, fanOut: 0}),
        (Mongo:Component {name: "Mongo DB", fanIn: 0, fanOut: 0}),
        (FullAPI:Component {name: "Full info API", fanIn: 0, fanOut: 0}),
        (BatchAPI:Component {name: "Batch info API", fanIn: 0, fanOut: 0}),
        (FullAPIJob:Component {name: "Full info retrieval job", fanIn: 0, fanOut: 0}),
        (BatchAPIJob:Component {name: "Batch info retrieval job", fanIn: 0, fanOut: 0})
        CREATE 
        (AppClient)-[:USES {description: "Checks whether info is in cache and gets it"}]->(RedisClient),
        (RedisClient)-[:USES {description: "Gets cache from Redis"}]->(Redis),
        (RedisClient)-[:USES {description: "Gets batch info from storage"}]->(Mongo),
        (AppClient)-[:USES {description: "Creates request for info retrieval"}]->(FullAPIJob),
        (AppClient)-[:USES {description: "Creates request for info retrieval"}]->(BatchAPIJob),
        (BatchAPIJob)-[:USES {description: "Make the API request"}]->(BatchAPI),
        (FullAPIJob)-[:USES {description: "Make the API request"}]->(FullAPI)
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

    def get_and_write_instability(self):
        queries = [
            """
        MATCH (c:Component)<-[:USES]-(other:Component)
        WITH c, COUNT(other) AS fanIn
        SET c.fanIn = fanIn
        """,
            """
        MATCH (c:Component)-[:USES]->(other:Component)
        WITH c, COUNT(other) AS fanOut
        SET c.fanOut = fanOut
        """,
            """
        MATCH (c:Component)
        SET c.instability = CASE
            WHEN c.fanIn + c.fanOut = 0 THEN 0
            ELSE 1.0 * c.fanOut / (c.fanIn + c.fanOut)
        END
        """,
        ]
        instability_values = []
        with self.driver.session() as session:
            for query in queries:
                session.run(query)
            result = session.run(
                "MATCH (c:Component) RETURN c.name AS Component, c.instability AS Instability, c.fanIn AS FanIn, c.fanOut AS FanOut"
            )
            for record in result:
                instability_values.append(
                    (
                        record["Component"],
                        record["Instability"],
                        record["FanIn"],
                        record["FanOut"],
                    )
                )
        df = pd.DataFrame(
            instability_values, columns=["Component", "Instability", "FanIn", "FanOut"]
        )
        excel_file_path = "instability_data.xlsx"
        df.to_excel(excel_file_path, index=True)


if __name__ == "__main__":
    greeter = HelloWorldExample("bolt://localhost:7687", "neo4j", "helloworld")
    greeter.create_all_nodes()
    greeter.get_and_write_instability()
    greeter.close()
