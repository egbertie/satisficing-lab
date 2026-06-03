def run(params):
    company = params.get("company_name")
    depth = params.get("depth")
    focus = params.get("focus")

    # Step 1: 信息采集
    raw_data = research(company, depth)

    # Step 2: 数据结构化
    structured_data = structure_data(raw_data)

    # Step 3: 分模块分析
    analysis = {
        "business_model": analyze_business(structured_data),
        "products": analyze_products(structured_data),
        "financial": analyze_financial(structured_data),
        "supply_chain": analyze_supply_chain(structured_data),
        "competitors": analyze_competitors(structured_data),
        "risks": analyze_risks(structured_data),
    }

    # Step 4: 战略输出
    strategy = generate_strategy(analysis)

    # Step 5: 报告生成
    report = generate_report(company, analysis, strategy)

    return report


def research(company, depth):
    return f"Collected data about {company} with depth {depth}"


def structure_data(data):
    return {"structured": data}


def analyze_business(data):
    return "Business Model Analysis"


def analyze_products(data):
    return "Product Analysis"


def analyze_financial(data):
    return "Financial Analysis"


def analyze_supply_chain(data):
    return "Supply Chain Analysis"


def analyze_competitors(data):
    return "Competitor Analysis"


def analyze_risks(data):
    return "Risk Analysis"


def generate_strategy(analysis):
    return "Strategic Recommendations"


def generate_report(company, analysis, strategy):
    return f"# {company} 深度调研报告\n\n{analysis}\n\n{strategy}"