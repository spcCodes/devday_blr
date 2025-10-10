from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.models import ResearchState, CompanyInfo, CompanyAnalysis
from src.firecrawl_service import FirecrawlService
from src.prompts import DeveloperToolsPrompts


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("extract_tools", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"🔍 Finding articles about: {state.query}")

        article_query = f"{state.query} best alternatives"
        search_results = self.firecrawl.search_companies(article_query, num_results=2)

        combined_content = ""

        # Loop through the web results (Document objects with markdown content)
        for doc in search_results.web:
            # Safely access markdown content, handling both Document and SearchResultWeb objects
            markdown_content = getattr(doc, 'markdown', None)
            if markdown_content:
                # Increase content limit to capture more tools
                combined_content += markdown_content[:3000] + "\n\n"

        if not combined_content:
            print("⚠️ No content found from search results")
            return {"extracted_tools": []}

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, combined_content))
        ]

        try:
            response = self.llm.invoke(messages)
            print(f"LLM Response: {response.content}")  # Add debug logging
            
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip() and not name.lower().startswith(("no relevant", "no tools"))
            ]
            
            # Filter out the main query term if it's in the results
            query_term = state.query.lower().strip()
            filtered_tools = [
                tool for tool in tool_names 
                if query_term not in tool.lower() and len(tool) > 2
            ]
            
            print(f"Extracted tools: {', '.join(filtered_tools[:5])}")
            return {"extracted_tools": filtered_tools[:5]}  # Limit to top 5
        except Exception as e:
            print(f"Error extracting tools: {e}")
            return {"extracted_tools": []}

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            if hasattr(search_results, 'web') and search_results.web:
                tool_names = [
                    getattr(doc.metadata, 'title', 'Unknown')
                    for doc in search_results.web
                ]
            else:
                tool_names = []
        else:
            tool_names = extracted_tools[:4]

        print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site", num_results=1)

            if tool_search_results and hasattr(tool_search_results, 'web') and tool_search_results.web:
                result = tool_search_results.web[0]
                url = getattr(result.metadata, 'url', '')

                company = CompanyInfo(
                    name=tool_name,
                    description=getattr(result, 'markdown', ''),
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                scraped = self.firecrawl.scrape_company_pages(url)
                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content)

                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("Generating recommendations")

        company_data = ", ".join([
            company.json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        response = self.llm.invoke(messages)
        return {"analysis": response.content}

    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)