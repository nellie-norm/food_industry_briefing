"""Section definitions, prompts, and constants for the Food Industry Briefing Tool."""

import os

PERPLEXITY_MODEL = "sonar-pro"
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SUBMISSIONS_DIR = os.path.join(os.path.dirname(__file__), "submissions")

SECTIONS = [
    {
        "id": "deals_capital",
        "title": "Deals & Capital",
        "emoji": "\U0001F4B0",
        "domains": ["agfunder.com", "fooddive.com", "ft.com", "crunchbase.com"],
        "prompt_focus": (
            "Find the most significant food and agriculture investment deals, "
            "funding rounds, M&A activity, IPOs, and capital raises from this week. "
            "Include deal sizes, investors, and strategic rationale where available."
        ),
    },
    {
        "id": "grocery_retail",
        "title": "Grocery & Retail",
        "emoji": "\U0001F6D2",
        "domains": ["thegrocer.co.uk", "grocerydive.com", "ft.com"],
        "prompt_focus": (
            "Find the most important grocery and retail developments this week, "
            "including store openings/closings, format changes, pricing moves, "
            "private label trends, e-commerce developments, and retailer earnings."
        ),
    },
    {
        "id": "innovation_product",
        "title": "Innovation & Product",
        "emoji": "\U0001F52C",
        "domains": ["digitalfoodlab.com", "foodnavigator.com", "newfoodmagazine.com"],
        "prompt_focus": (
            "Find notable new food product launches, ingredient innovations, "
            "food technology breakthroughs, alternative protein developments, "
            "and novel food-tech startup activity from this week."
        ),
    },
    {
        "id": "glp1_health",
        "title": "GLP-1 & Health",
        "emoji": "\U0001F489",
        "domains": ["foodnavigator.com", "ft.com", "statnews.com"],
        "prompt_focus": (
            "Find developments at the intersection of GLP-1 receptor agonists "
            "(Ozempic, Wegovy, Mounjaro, etc.) and the food industry this week. "
            "Include reformulation trends, 'GLP-1 friendly' product launches, "
            "impact on food company earnings, and consumer behavior shifts."
        ),
    },
    {
        "id": "research_science",
        "title": "Research & Science",
        "emoji": "\U0001F9EA",
        "domains": [
            "foodnavigator.com",
            "newfoodmagazine.com",
            "nutraingredients.com",
            "sciencedaily.com",
            "nature.com",
            "newscientist.com",
        ],
        "prompt_focus": (
            "Find important food science and nutrition research published or covered "
            "this week. Include new peer-reviewed studies on diet and health, food "
            "safety findings, sustainable agriculture breakthroughs, microbiome "
            "research, novel food processing techniques, and any major scientific "
            "publications with implications for the food industry. Trade press "
            "coverage of new research is valuable."
        ),
    },
    {
        "id": "policy_regulation",
        "title": "Policy & Regulation",
        "emoji": "\U0001F3DB\uFE0F",
        "domains": ["fda.gov", "foodnavigator.com", "fooddive.com"],
        "prompt_focus": (
            "Find significant food policy and regulatory developments this week, "
            "including FDA actions, labeling changes, trade policy, food safety "
            "recalls, sustainability mandates, and international regulatory updates."
        ),
    },
    {
        "id": "macro_consumer",
        "title": "Macro & Consumer",
        "emoji": "\U0001F4CA",
        "domains": ["ft.com", "nytimes.com", "economist.com"],
        "prompt_focus": (
            "Find macroeconomic and consumer trends affecting the food industry "
            "this week, including food price inflation, consumer spending data, "
            "supply chain developments, commodity markets, and shifting dietary patterns."
        ),
    },
]

SYSTEM_PROMPT = (
    "You are a senior food industry analyst preparing a weekly briefing for "
    "investors and executives. Your output should be:\n\n"
    "- 4 to 6 concise markdown bullet points per section\n"
    "- Each bullet starts with a **bold lead-in phrase** summarizing the development\n"
    "- Include specific numbers, company names, and deal sizes where available\n"
    "- Cite source URLs inline as markdown links where possible\n"
    "- Professional, analytical tone — no hype, no filler\n"
    "- Focus on developments from the current week only\n"
    "- Prioritize stories by significance to food industry investors"
)
