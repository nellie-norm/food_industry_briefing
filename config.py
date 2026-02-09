"""Section definitions, prompts, and constants for the Food Industry Briefing Tool."""

import os

PERPLEXITY_MODEL = "sonar-pro"
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SUBMISSIONS_DIR = os.path.join(os.path.dirname(__file__), "submissions")

SECTIONS = [
    {
        "id": "deals_corporate",
        "title": "Corporate M&A & Big Food",
        "emoji": "\U0001F3E2",
        "domains": ["fooddive.com", "ft.com", "thegrocer.co.uk", "foodnavigator.com"],
        "prompt_focus": (
            "Find the most significant large-scale food industry corporate deals "
            "this week: M&A, major acquisitions, divestitures, IPOs, and large "
            "capital raises (Series C+, $50M+). Focus on Big Food companies, "
            "major retailers, and large private equity transactions. "
            "Include deal sizes, acquirers, and strategic rationale."
        ),
    },
    {
        "id": "deals_earlystage",
        "title": "Early-Stage & VC",
        "emoji": "\U0001F331",
        "domains": [
            "agfunder.com",
            "sifted.eu",
            "techcrunch.com",
            "foodnavigator.com",
            "vegconomist.com",
            "greenqueen.com.hk",
            "foodhack.global",
            "ukri.org",
            "eitfood.eu",
            "eif.org",
        ],
        "prompt_focus": (
            "Find early-stage food, foodtech, and agtech venture capital deals "
            "from this week: Seed rounds, Series A, Series B, and accelerator "
            "announcements. Prioritise UK and European deals. Look for investments "
            "by firms such as Astanor Ventures, Five Seasons "
            "Ventures, CPT Capital, Synthesis Capital, Blue Horizon, Nordic "
            "Foodtech VC, S2G Ventures, AgFunder, Acre Venture Partners, Unovis, "
            "and similar early-stage food/ag investors. Also include grants or "
            "innovation funding from EIF, UKRI, Innovate UK, EIT Food, and UK "
            "Agritech Centre. Include the startup name, what they do, round size, "
            "lead investors, and stage."
        ),
    },
    {
        "id": "new_funds",
        "title": "New Funds & Programmes",
        "emoji": "\U0001F4E3",
        "optional": True,
        "domains": [
            "agfunder.com",
            "sifted.eu",
            "eif.org",
            "eitfood.eu",
            "ukri.org",
            "foodnavigator.com",
            "ft.com",
        ],
        "prompt_focus": (
            "Find any NEW venture capital funds, investment vehicles, grant "
            "programmes, or accelerator programmes launched or announced this week "
            "that focus on food, foodtech, agritech, or sustainable agriculture. "
            "Include new fund launches by VCs, new EIF or UKRI funding programmes, "
            "new EIT Food calls, government agritech initiatives, and corporate "
            "venture fund announcements. Include fund size, geographic focus, "
            "thesis, and timeline. If there are no new funds or programmes "
            "announced this week, respond with exactly: NO_CONTENT"
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
            "ukri.org",
            "eitfood.eu",
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
        "domains": [
            "foodnavigator.com",
            "fooddive.com",
            "gov.uk",
            "food.gov.uk",
            "fda.gov",
        ],
        "prompt_focus": (
            "Find significant food policy and regulatory developments this week. "
            "Prioritise UK and EU actions: FSA, DEFRA, UK government food policy, "
            "EU food safety authority (EFSA), and European Commission regulations. "
            "Also include major FDA and international actions with UK implications. "
            "Cover labelling changes, trade policy, food safety recalls, "
            "sustainability mandates, and novel food approvals."
        ),
    },
    {
        "id": "macro_consumer",
        "title": "Macro & Consumer",
        "emoji": "\U0001F4CA",
        "domains": [
            "fooddive.com",
            "grocerydive.com",
            "foodnavigator.com",
            "reuters.com",
            "bls.gov",
            "usda.gov",
        ],
        "prompt_focus": (
            "Find macroeconomic and consumer trends affecting the food industry "
            "this week, including food price inflation data (CPI, PPI), consumer "
            "spending reports, grocery sales figures, commodity price movements, "
            "supply chain disruptions, trade and tariff developments, and shifting "
            "dietary or shopping patterns. Include specific numbers and data points."
        ),
    },
]

SYSTEM_PROMPT = (
    "You are a senior food industry analyst based in London, preparing a weekly "
    "briefing for UK-based investors and executives. Your output should be:\n\n"
    "- 4 to 6 concise markdown bullet points per section\n"
    "- Each bullet starts with a **bold lead-in phrase** summarizing the development\n"
    "- Include specific numbers, company names, and deal sizes where available\n"
    "- Prioritise UK and European developments, but include major global stories "
    "(especially US) where they have clear implications for the UK food industry\n"
    "- CRITICAL: Embed source URLs as inline markdown hyperlinks within the text, "
    "e.g. [Food Dive](https://www.fooddive.com/...). "
    "NEVER use numbered reference citations like [1], [2], [3]. "
    "Every claim should link directly to its source within the sentence.\n"
    "- Professional, analytical tone — no hype, no filler\n"
    "- Focus on developments from the current week only\n"
    "- Prioritise stories by significance to food industry investors"
)
