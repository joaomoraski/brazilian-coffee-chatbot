from langsmith import Client

from app.settings import settings

DATASET_NAME = "coffee-chatbot-eval"
DATASET_DESCRIPTION = "Dataset for evaluating the coffee chatbot"

EXAMPLES = [
    # --- History, economy, geography ---
    {
        "inputs": {"question": "What is the history of coffee in Brazil?"},
        "outputs": {
            "answer": "Explain coffee arrival in Brazil, 19th-century expansion, links to labor/infrastructure, and why Brazil became a leading exporter."
        },
    },
    {
        "inputs": {"question": "How did coffee shape Brazil's economy in the 19th and 20th centuries?"},
        "outputs": {
            "answer": "Cover export-led growth, railway/port development, and coffee's role in regional economic transformation."
        },
    },
    {
        "inputs": {"question": "Why is Minas Gerais so important for Brazilian coffee?"},
        "outputs": {
            "answer": "Mention production scale, key subregions, altitude/climate advantages, and profile diversity."
        },
    },
    {
        "inputs": {"question": "What are the main coffee regions in Brazil?"},
        "outputs": {
            "answer": "Mention Minas Gerais, São Paulo, Espírito Santo, Bahia, Paraná, Rondônia and summarize each region's production characteristics."
        },
    },
    {
        "inputs": {"question": "How do Arabica and Conilon production differ across Brazil?"},
        "outputs": {
            "answer": "Compare geographic concentration, climate suitability, processing, and common flavor outcomes for each species."
        },
    },
    {
        "inputs": {"question": "What is an indication of origin in Brazilian coffee?"},
        "outputs": {
            "answer": "Explain geographical indication concept, why it matters, and examples of value for traceability and quality identity."
        },
    },
    # --- Cultivation and post-harvest ---
    {
        "inputs": {"question": "How is coffee planted and cultivated?"},
        "outputs": {
            "answer": "Cover planting stages, soil and climate requirements, spacing, nutrition, pruning, and crop cycle basics."
        },
    },
    {
        "inputs": {"question": "How is coffee harvested in Brazil?"},
        "outputs": {
            "answer": "Explain manual and mechanical harvesting, selective vs strip picking, and immediate post-harvest handling."
        },
    },
    {
        "inputs": {"question": "What are the differences between natural, pulped natural, and washed processing?"},
        "outputs": {
            "answer": "Define each process step-by-step and compare impact on sweetness, acidity, body, and cup cleanliness."
        },
    },
    {
        "inputs": {"question": "How does drying affect coffee quality?"},
        "outputs": {
            "answer": "Describe patio or mechanical drying principles, moisture targets, and risks like mold or uneven drying."
        },
    },
    {
        "inputs": {"question": "What defects can appear in green coffee beans?"},
        "outputs": {
            "answer": "List common defects and explain how they reduce quality score and sensory performance."
        },
    },
    {
        "inputs": {"question": "How should green coffee be stored before roasting?"},
        "outputs": {
            "answer": "Mention stable humidity/temperature, airflow, packaging, and contamination prevention best practices."
        },
    },
    # --- Classification and standards ---
    {
        "inputs": {"question": "How is coffee classified by quality levels?"},
        "outputs": {
            "answer": "Explain quality terms (e.g., extra strong market labels), sensory scoring logic, and references to Brazilian and specialty standards."
        },
    },
    {
        "inputs": {"question": "What is the difference between specialty and commercial coffee?"},
        "outputs": {
            "answer": "Compare sensory quality, defect tolerance, scoring thresholds, traceability, and pricing/value implications."
        },
    },
    {
        "inputs": {"question": "What does an 84-point SCA coffee mean?"},
        "outputs": {
            "answer": "Explain SCA scoring scale, what 84 implies in quality terms, and limitations of using score alone."
        },
    },
    {
        "inputs": {"question": "How do ABIC and specialty grading approaches differ?"},
        "outputs": {
            "answer": "Provide a clear comparison of objective, methodology focus, and expected consumer interpretation."
        },
    },
    # --- Roasting ---
    {
        "inputs": {"question": "What is the coffee roasting process?"},
        "outputs": {
            "answer": "Describe roast phases, first crack, development time, and how roast level changes flavor and aroma."
        },
    },
    {
        "inputs": {"question": "How do light, medium, and dark roast profiles differ?"},
        "outputs": {
            "answer": "Compare acidity, sweetness, bitterness, body, and origin-character preservation across roast levels."
        },
    },
    {
        "inputs": {"question": "What is first crack and why is it important?"},
        "outputs": {
            "answer": "Explain first crack as a roasting milestone and its role in roast development decisions."
        },
    },
    {
        "inputs": {"question": "How can I reduce bitterness when roasting?"},
        "outputs": {
            "answer": "Suggest process-control adjustments (time/temperature/development) and caution against overdevelopment."
        },
    },
    # --- Brewing and extraction ---
    {
        "inputs": {"question": "What are the best brewing methods?"},
        "outputs": {
            "answer": "Explain popular methods including ARAM, French press, V60, Melitta, AeroPress, moka, and espresso with practical differences."
        },
    },
    {
        "inputs": {"question": "What is the ARAM method?"},
        "outputs": {
            "answer": "Explain ARAM as a Brazilian manual espresso method, including workflow and flavor characteristics."
        },
    },
    {
        "inputs": {"question": "How do I brew coffee in a V60 at home?"},
        "outputs": {
            "answer": "Provide step-by-step recipe guidance with ratio, grind, water temperature, bloom, and total brew time."
        },
    },
    {
        "inputs": {"question": "How does French press extraction differ from pour-over?"},
        "outputs": {
            "answer": "Compare immersion vs percolation, grind size, filtration, body, and clarity outcomes."
        },
    },
    {
        "inputs": {"question": "What is a good coffee-to-water ratio for filter coffee?"},
        "outputs": {
            "answer": "Provide a practical ratio range and explain when to adjust for strength preference."
        },
    },
    {
        "inputs": {"question": "What grind size should I use for AeroPress?"},
        "outputs": {
            "answer": "Offer a practical baseline grind recommendation plus adaptation by recipe and brew time."
        },
    },
    {
        "inputs": {"question": "How does water temperature affect extraction?"},
        "outputs": {
            "answer": "Explain under- vs over-extraction risk and recommended temperature ranges for common methods."
        },
    },
    {
        "inputs": {"question": "How can I make sweeter coffee without adding sugar?"},
        "outputs": {
            "answer": "Recommend recipe and extraction adjustments that increase sweetness and balance."
        },
    },
    {
        "inputs": {"question": "How do I dial in espresso at home?"},
        "outputs": {
            "answer": "Give a compact dial-in framework using dose, yield, time, grind, and tasting feedback loops."
        },
    },
    # --- Sensory and flavor ---
    {
        "inputs": {"question": "What tasting notes are common in Brazilian specialty coffees?"},
        "outputs": {
            "answer": "Describe common sensory descriptors such as chocolate, nuts, caramel, fruit nuances, body, and sweetness."
        },
    },
    {
        "inputs": {"question": "How can beginners learn coffee sensory evaluation?"},
        "outputs": {
            "answer": "Suggest practical cupping basics, note-taking, triangulation, and palate training routines."
        },
    },
    {
        "inputs": {"question": "What causes sour coffee in the cup?"},
        "outputs": {
            "answer": "Explain likely causes related to under-extraction, grind size, brew ratio, and temperature, with fixes."
        },
    },
    {
        "inputs": {"question": "What causes bitter coffee in the cup?"},
        "outputs": {
            "answer": "Explain likely causes related to over-extraction or roast and provide corrective actions."
        },
    },
    # --- Storage and freshness ---
    {
        "inputs": {"question": "How should I store roasted coffee beans at home?"},
        "outputs": {
            "answer": "Recommend airtight, opaque storage away from heat/light/moisture and explain freshness windows."
        },
    },
    {
        "inputs": {"question": "Should I freeze coffee beans?"},
        "outputs": {
            "answer": "Provide balanced guidance on freezing strategy, portioning, condensation risks, and use cases."
        },
    },
    {
        "inputs": {"question": "How long after roast is coffee at its best?"},
        "outputs": {
            "answer": "Explain rest period and freshness curve differences for espresso and filter brewing."
        },
    },
    # --- Health / consumer education ---
    {
        "inputs": {"question": "Does coffee have health benefits?"},
        "outputs": {
            "answer": "Provide a balanced, non-medical summary of potential benefits and caution on individual sensitivity."
        },
    },
    {
        "inputs": {"question": "How much caffeine is usually in a cup of coffee?"},
        "outputs": {
            "answer": "Give typical ranges by brew style and note major variables that change caffeine content."
        },
    },
    {
        "inputs": {"question": "Is decaf coffee naturally caffeine-free?"},
        "outputs": {
            "answer": "Clarify that decaf still contains small caffeine amounts and briefly explain decaffeination methods."
        },
    },
    # --- Tool-call cases: Places ---
    {
        "inputs": {"question": "Where can I find coffee shops in São Paulo?"},
        "outputs": {
            "answer": "Return coffee shop suggestions in São Paulo with names, addresses, and ratings.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "Find specialty coffee shops near Avenida Paulista."},
        "outputs": {
            "answer": "Use location search and return nearby specialty cafés with practical details.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "Any good cafés in Belo Horizonte city center?"},
        "outputs": {
            "answer": "Return cafés in central Belo Horizonte with ratings and addresses.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "Can you suggest coffee shops around Copacabana, Rio de Janeiro?"},
        "outputs": {
            "answer": "Use Places search for Copacabana and list viable coffee shops.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "Find 24-hour coffee places in Curitiba."},
        "outputs": {
            "answer": "Search places in Curitiba and prioritize entries that indicate late-night/24-hour operation.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "Show coffee shops near Porto Alegre airport."},
        "outputs": {
            "answer": "Return cafés near Porto Alegre airport with concise location details.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "What are top-rated coffee shops in Recife?"},
        "outputs": {
            "answer": "Use location data to list highly rated cafés in Recife.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    {
        "inputs": {"question": "Find coffee shops near me in Florianópolis."},
        "outputs": {
            "answer": "Use place lookup for Florianópolis and provide nearby coffee options.",
            "expected_tools": ["find_coffee_shops"],
        },
    },
    # --- Tool-call cases: Web search ---
    {
        "inputs": {"question": "What is the current price of coffee from Semeado Cafe?"},
        "outputs": {
            "answer": "Fetch current web information about Semeado Cafe coffee pricing.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "What is today's arabica coffee futures price?"},
        "outputs": {
            "answer": "Use web search for up-to-date arabica futures pricing information.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "Any recent Brazil coffee export numbers for this month?"},
        "outputs": {
            "answer": "Search the web for the latest monthly export figures and cite the source context.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "Who won the latest Cup of Excellence Brazil?"},
        "outputs": {
            "answer": "Use web search to fetch the latest winner information.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "What are the newest ARAM brewer model updates?"},
        "outputs": {
            "answer": "Search for recent ARAM product updates not guaranteed in static knowledge base.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "Which cafés in São Paulo are open right now?"},
        "outputs": {
            "answer": "Use current web/live data to answer opening status, since this is time-sensitive.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "What is the exchange rate impact on coffee exports this week?"},
        "outputs": {
            "answer": "Use web search for current macroeconomic context relevant to coffee exports.",
            "expected_tools": ["search_web"],
        },
    },
    {
        "inputs": {"question": "Find recent news about coffee rust outbreaks in Brazil."},
        "outputs": {
            "answer": "Use web search to find recent disease-outbreak reporting and summarize cautiously.",
            "expected_tools": ["search_web"],
        },
    },
    # --- Ambiguous / mixed intent checks ---
    {
        "inputs": {"question": "I am starting a coffee shop in Brazil. What should I learn first?"},
        "outputs": {
            "answer": "Provide a structured beginner roadmap covering coffee basics, sourcing, menu design, equipment, and training."
        },
    },
    {
        "inputs": {"question": "Recommend a study plan to become a coffee professional in 3 months."},
        "outputs": {
            "answer": "Return a realistic staged learning plan with sensory, brewing, roasting, and market topics."
        },
    },
    {
        "inputs": {"question": "Can you summarize Brazilian coffee from farm to cup?"},
        "outputs": {
            "answer": "Provide an end-to-end overview from cultivation and harvest to processing, roasting, brewing, and consumption."
        },
    },
    {
        "inputs": {"question": "How can climate change affect coffee production in Brazil?"},
        "outputs": {
            "answer": "Explain likely impacts on productivity/quality and adaptation strategies without overstating certainty."
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
