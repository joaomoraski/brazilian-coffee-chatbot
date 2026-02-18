from langsmith import Client

from app.settings import settings

DATASET_NAME = "coffee-chatbot-eval"
DATASET_DESCRIPTION = "Dataset for evaluating the coffee chatbot"

EXAMPLES = [
    {
        "inputs": {"question": "What is the history of coffee in Brazil?"},
        "outputs": {
            "answer": "Needs to have a explanation of the arrival of coffee in Brazil, how the expasion for the rest of the country are made and why Brazil became the biggest exporter"
        },
    },
    {
        "inputs": {"question": "How is coffee classified by quality levels?"},
        "outputs": {
            "answer": "Need's to specify the quality like 'Extra forte' and etc, explain about the points to be considered a Special or Gourmet coffee and needs to explain about the COB Classification, ABIC Classification and SCA Methodology"
        },
    },
    {
        "inputs": {"question": "What are the best brewing methods?"},
        "outputs": {
            "answer": "Need to contain the explanation of the brazilian method ARAM or other methods like French Press, V60, Melitta, Aeropress, Moka and Espresso"
        },
    },
    {
        "inputs": {"question": "What are the main coffee regions in Brazil?"},
        "outputs": {
            "answer": "Must mention regions like Minas Gerais, São Paulo, Espírito Santo, Bahia, Paraná, Rondônia; explain geographic distribution and production characteristics"
        },
    },
    {
        "inputs": {"question": "What is the ARAM method?"},
        "outputs": {
            "answer": "Must explain the Brazilian ARAM brewing method, its steps and characteristics, and its relation to specialty coffee culture"
        },
    },
    {
        "inputs": {"question": "How is coffee planted and cultivated?"},
        "outputs": {
            "answer": "Must cover planting process, soil/climate requirements, cultivation practices, and growth cycle of coffee plants"
        },
    },
    {
        "inputs": {"question": "How is coffee harvested in Brazil?"},
        "outputs": {
            "answer": "Must explain harvesting methods (manual vs mechanical), selective picking, strip picking, and processing after harvest"
        },
    },
    {
        "inputs": {"question": "What is the coffee roasting process?"},
        "outputs": {
            "answer": "Must explain roasting stages, roast levels (light, medium, dark), and how roasting affects flavor"
        },
    },
    {
        "inputs": {"question": "Where can I find coffee shops in São Paulo?"},
        "outputs": {
            "answer": "Must return a list of coffee shops with names, addresses and ratings in São Paulo (uses Places tool)",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "What is the current price of coffee from Semeado Cafe?"},
        "outputs": {
            "answer": "Must return current/updated price information for Semeado Cafe coffee (uses web search - not in knowledge base)",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "What is the difference between specialty and commercial coffee?"},
        "outputs": {
            "answer": "Must explain quality criteria, scoring (e.g. SCA points), defects, and what distinguishes specialty from commercial grades"
        },
    },
]


def main():
    client = Client(
        api_key=settings.LANGSMITH_API_KEY,
        api_url=settings.LANGSMITH_ENDPOINT,
    )

    # Find dataset by name (unique)
    dataset = None
    for ds in client.list_datasets():
        if ds.name == DATASET_NAME:
            dataset = ds
            break

    if dataset is None:
        dataset = client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESCRIPTION,
        )
        print(f"Created dataset: {dataset.name} (id={dataset.id})")
    else:
        # Delete existing examples before adding new ones
        for example in client.list_examples(dataset_id=dataset.id):
            client.delete_example(example_id=example.id)
        print(f"Updated dataset: {dataset.name} (id={dataset.id})")

    # Add examples
    inputs = [ex["inputs"] for ex in EXAMPLES]
    outputs = [ex["outputs"] for ex in EXAMPLES]
    client.create_examples(dataset_id=dataset.id, inputs=inputs, outputs=outputs)
    print(f"Added {len(EXAMPLES)} examples")


if __name__ == "__main__":
    main()
