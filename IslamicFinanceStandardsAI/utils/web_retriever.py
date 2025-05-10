"""
Web Retriever for Islamic Finance Standards

This module provides functionality to retrieve Shariah standards and resources
from the internet to enhance the validation process.
"""

import os
import logging
import requests
import json
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import openai
import re
from dotenv import load_dotenv
from .gemini_client import GeminiClient

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class WebRetriever:
    """
    Retrieves Islamic finance standards and resources from the internet
    to support the validation process.
    """
    
    def __init__(self):
        """Initialize the web retriever"""
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("SERP_API_KEY")  # For search engine results
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAND61l0rHF-p2UQg28RSMe62DZgQOHsLE")
        self.use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
        self.aaoifi_base_url = "https://aaoifi.com/standards/"
        self.ifsb_base_url = "https://www.ifsb.org/published.php"
        self.trusted_domains = [
            "aaoifi.com",
            "ifsb.org",
            "islamicbanker.com",
            "islamic-finance.com",
            "isdb.org",
            "irti.org",
            "scholar.google.com",
            "researchgate.net",
            "academia.edu"
        ]
        
    def search_standards(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant Islamic finance standards using the query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant standards with metadata
        """
        self.logger.info(f"Searching for standards with query: {query}")
        
        try:
            # Always use direct sources since SerpAPI requires an API key
            return self._search_direct_sources(query, max_results)
        except Exception as e:
            self.logger.error(f"Error searching standards: {str(e)}")
            return []
    
    def _search_with_serp_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using SerpAPI"""
        search_query = f"Islamic finance standards {query}"
        
        params = {
            "api_key": self.api_key,
            "q": search_query,
            "num": max_results,
            "gl": "us",  # Country to search from
            "hl": "en"   # Language
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Extract organic search results
            if "organic_results" in data:
                for result in data["organic_results"][:max_results]:
                    # Check if the domain is trusted
                    domain = self._extract_domain(result.get("link", ""))
                    if domain in self.trusted_domains:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("link", ""),
                            "snippet": result.get("snippet", ""),
                            "source": domain,
                            "trusted": True
                        })
            
            return results
        else:
            self.logger.error(f"SerpAPI error: {response.status_code}")
            return []
    
    def _search_direct_sources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search direct sources like AAOIFI and IFSB websites"""
        results = []
        
        # Define a list of pre-defined standards and their details
        predefined_standards = [
            {
                "title": "FAS 1: General Presentation and Disclosure in the Financial Statements of Islamic Banks and Financial Institutions",
                "url": "https://aaoifi.com/standard/fas-1-general-presentation-and-disclosure-in-the-financial-statements-of-islamic-banks-and-financial-institutions/",
                "source": "AAOIFI",
                "snippet": "This standard defines the financial reports that should be periodically published by Islamic banks to meet the common information needs of users of financial reports."
            },
            {
                "title": "FAS 4: Musharaka Financing",
                "url": "https://aaoifi.com/standard/fas-4-musharaka-financing/",
                "source": "AAOIFI",
                "snippet": "This standard defines Musharaka financing and specifies the accounting rules for recording Musharaka transactions in the books of the Islamic bank, whether the bank is acting as a partner or as a manager."
            },
            {
                "title": "FAS 8: Ijarah and Ijarah Muntahia Bittamleek",
                "url": "https://aaoifi.com/standard/fas-8-ijarah-and-ijarah-muntahia-bittamleek/",
                "source": "AAOIFI",
                "snippet": "This standard prescribes the accounting rules and procedures for both Ijarah and Ijarah Muntahia Bittamleek for Islamic financial institutions."
            },
            {
                "title": "FAS 9: Zakah",
                "url": "https://aaoifi.com/standard/fas-9-zakah/",
                "source": "AAOIFI",
                "snippet": "This standard aims at setting out the accounting rules for the treatment of Zakah in the financial statements of Islamic banks."
            },
            {
                "title": "FAS 10: Salam and Parallel Salam",
                "url": "https://aaoifi.com/standard/fas-10-salam-and-parallel-salam/",
                "source": "AAOIFI",
                "snippet": "This standard prescribes the accounting rules for Salam and Parallel Salam transactions for Islamic financial institutions."
            },
            {
                "title": "FAS 17: Investments",
                "url": "https://aaoifi.com/standard/fas-17-investments/",
                "source": "AAOIFI",
                "snippet": "This standard prescribes the accounting rules for recognition, measurement, and disclosure of investments made by Islamic financial institutions."
            },
            {
                "title": "FAS 28: Murabaha and Other Deferred Payment Sales",
                "url": "https://aaoifi.com/standard/fas-28-murabaha-and-other-deferred-payment-sales/",
                "source": "AAOIFI",
                "snippet": "This standard prescribes the accounting rules for recognition, measurement, and disclosure of Murabaha and other deferred payment sales transactions for Islamic financial institutions."
            },
            {
                "title": "Shariah Standard 5: Guarantees",
                "url": "https://aaoifi.com/standard/shariah-standard-5-guarantees/",
                "source": "AAOIFI",
                "snippet": "This standard defines the Shariah rules for guarantees and their applications in contemporary Islamic banking."
            },
            {
                "title": "Shariah Standard 9: Ijarah and Ijarah Muntahia Bittamleek",
                "url": "https://aaoifi.com/standard/shariah-standard-9-ijarah-and-ijarah-muntahia-bittamleek/",
                "source": "AAOIFI",
                "snippet": "This standard defines the Shariah rules for Ijarah and Ijarah Muntahia Bittamleek contracts and their applications in Islamic financial institutions."
            },
            {
                "title": "Shariah Standard 12: Sharika (Musharaka) and Modern Corporations",
                "url": "https://aaoifi.com/standard/shariah-standard-12-sharika-musharaka-and-modern-corporations/",
                "source": "AAOIFI",
                "snippet": "This standard defines the Shariah rules for different forms of Musharaka (partnership) and their applications in Islamic financial institutions."
            },
            {
                "title": "Shariah Standard 13: Mudaraba",
                "url": "https://aaoifi.com/standard/shariah-standard-13-mudaraba/",
                "source": "AAOIFI",
                "snippet": "This standard defines the Shariah rules for Mudaraba contracts and their applications in Islamic financial institutions."
            },
            {
                "title": "Shariah Standard 17: Investment Sukuk",
                "url": "https://aaoifi.com/standard/shariah-standard-17-investment-sukuk/",
                "source": "AAOIFI",
                "snippet": "This standard defines the Shariah rules for investment Sukuk and their applications in Islamic financial institutions."
            }
        ]
        
        # Simple keyword matching to find relevant standards
        query_keywords = set(query.lower().split())
        
        for standard in predefined_standards:
            title_keywords = set(standard["title"].lower().split())
            snippet_keywords = set(standard["snippet"].lower().split())
            all_keywords = title_keywords.union(snippet_keywords)
            
            # Calculate a simple relevance score based on keyword matches
            matches = len(query_keywords.intersection(all_keywords))
            
            if matches > 0:
                # Add relevance score to the standard
                standard_with_score = standard.copy()
                standard_with_score["relevance_score"] = matches
                results.append(standard_with_score)
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        # Limit to max_results
        return results[:max_results]
        
        # Search AAOIFI standards
        try:
            response = requests.get(self.aaoifi_base_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                standards = soup.find_all("div", class_="standard-item")
                
                for standard in standards[:max_results]:
                    title_elem = standard.find("h3")
                    desc_elem = standard.find("p")
                    link_elem = standard.find("a")
                    
                    if title_elem and link_elem:
                        title = title_elem.text.strip()
                        url = link_elem.get("href", "")
                        description = desc_elem.text.strip() if desc_elem else ""
                        
                        # Simple keyword matching
                        if any(keyword.lower() in title.lower() or 
                               keyword.lower() in description.lower() 
                               for keyword in query.split()):
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": description,
                                "source": "aaoifi.com",
                                "trusted": True
                            })
        except Exception as e:
            self.logger.error(f"Error searching AAOIFI: {str(e)}")
        
        # Limit results to max_results
        return results[:max_results]
    
    def retrieve_standard_content(self, url: str) -> str:
        """
        Retrieve the content of a standard from its URL
        
        Args:
            url: URL of the standard
            
        Returns:
            Content of the standard as text
        """
        self.logger.info(f"Retrieving content from URL: {url}")
        
        try:
            domain = self._extract_domain(url)
            
            # Check if the domain is trusted
            if domain not in self.trusted_domains:
                self.logger.warning(f"Domain {domain} is not in the trusted domains list")
                return ""
            
            # For demonstration purposes, return predefined content based on URL
            # This avoids making actual web requests which might fail
            if "fas-4" in url.lower():
                return """
                FAS 4: Musharaka Financing
                
                1. Scope
                This standard shall apply to Musharaka financing and Diminishing Musharaka transactions carried out by Islamic financial institutions.
                
                2. Definition
                Musharaka is a form of partnership between the Islamic bank and its clients whereby each party contributes to the capital of partnership in equal or varying degrees to establish a new project or share in an existing one, and whereby each of the parties becomes an owner of the capital on a permanent or declining basis and shall have his due share of profits. However, losses are shared in proportion to the contributed capital. It is not permissible to stipulate otherwise.
                
                3. Accounting Treatment
                3.1 Initial Recognition
                3.1.1 The Islamic bank's share in Musharaka capital shall be recognized when it is paid to the partner or made available to him on account of the Musharaka.
                3.1.2 Musharaka capital provided in cash by the Islamic bank shall be measured by the amount paid or the amount made available to the partner on account of the Musharaka.
                
                4. Profit and Loss Recognition
                4.1 Profits shall be recognized based on the profit-sharing ratio agreed upon by the partners.
                4.2 Losses shall be recognized in proportion to the contributed capital.
                
                5. Disclosure Requirements
                5.1 The Islamic bank shall disclose the amount of Musharaka financing and its share in each Musharaka project.
                5.2 The Islamic bank shall disclose the profit-sharing ratio agreed upon with the partners.
                5.3 The Islamic bank shall disclose the method used to recognize profits and losses.
                """
            elif "fas-8" in url.lower():
                return """
                FAS 8: Ijarah and Ijarah Muntahia Bittamleek
                
                1. Scope
                This standard shall apply to Ijarah and Ijarah Muntahia Bittamleek assets acquired by the Islamic bank for the purpose of leasing them out, and to the expenses incurred subsequently on these assets.
                
                2. Definitions
                2.1 Ijarah is the transfer of the usufruct of an asset for an agreed period for an agreed consideration.
                2.2 Ijarah Muntahia Bittamleek is a form of leasing contract which includes a promise by the lessor to transfer the ownership in the leased property to the lessee, either at the end of the term of the Ijarah period or by stages during the term of the contract.
                
                3. Accounting Treatment for the Lessor
                3.1 Ijarah assets shall be recognized at historical cost less accumulated depreciation and impairment losses.
                3.2 Ijarah revenue shall be allocated proportionately to the financial periods in the lease term.
                3.3 Initial direct costs incurred by the lessor shall be allocated to periods in the lease term in proportion to the allocation of Ijarah revenue.
                
                4. Accounting Treatment for the Lessee
                4.1 Ijarah installments shall be recognized as an expense in the period to which they relate.
                4.2 If material, initial direct costs incurred by the lessee shall be allocated to periods in the lease term.
                
                5. Disclosure Requirements
                5.1 The lessor shall disclose the historical cost of Ijarah assets and related accumulated depreciation.
                5.2 The lessor shall disclose the method used to recognize Ijarah revenue.
                5.3 The lessee shall disclose the future Ijarah installments.
                """
            elif "shariah-standard-12" in url.lower():
                return """
                Shariah Standard 12: Sharika (Musharaka) and Modern Corporations
                
                1. Scope
                This standard aims to explain the types of companies that are recognized in Shariah, their essential elements and conditions, modern applications, and Shariah rulings.
                
                2. Definition of Sharika (Partnership)
                Sharika (partnership) in Islamic jurisprudence means the existence of a right belonging to two or more persons in common in a single asset.
                
                3. Types of Partnerships
                3.1 Sharikat al-Milk (Partnership in Ownership)
                3.2 Sharikat al-'Aqd (Contractual Partnership)
                   3.2.1 Sharikat al-Amwal (Partnership in Capital)
                   3.2.2 Sharikat al-A'mal (Partnership in Labor/Services)
                   3.2.3 Sharikat al-Wujuh (Partnership in Reputation/Creditworthiness)
                   3.2.4 Mudaraba (Silent Partnership)
                
                4. Essential Elements of Partnership
                4.1 Partners (at least two)
                4.2 Offer and acceptance (Sighah)
                4.3 Capital contribution
                4.4 Profit-sharing ratio
                
                5. Conditions of Valid Partnership
                5.1 The subject of the partnership must be capable of being an agent and being a principal.
                5.2 The capital contribution must be clearly known.
                5.3 The profit-sharing ratio must be clearly known and agreed upon at the time of the contract.
                5.4 Losses are shared in proportion to the capital contribution.
                
                6. Modern Applications
                6.1 Joint Stock Companies
                6.2 Limited Liability Companies
                6.3 Diminishing Musharaka
                6.4 Musharaka Sukuk
                
                7. Shariah Rulings
                7.1 It is not permissible to stipulate that a partner receives a lump sum amount of profit.
                7.2 It is permissible to agree that if the profit exceeds a certain percentage, one partner receives a higher percentage of the excess.
                7.3 It is not permissible to stipulate that a partner bears all the loss or a percentage of it that exceeds his percentage share in the partnership capital.
                """
            elif "shariah-standard-17" in url.lower():
                return """
                Shariah Standard 17: Investment Sukuk
                
                1. Scope
                This standard aims to explain the Shariah rules for issuing, trading and redeeming investment Sukuk.
                
                2. Definition of Sukuk
                Investment Sukuk are certificates of equal value representing undivided shares in the ownership of tangible assets, usufructs and services or (in the ownership of) the assets of particular projects or special investment activity.
                
                3. Types of Sukuk
                3.1 Ijarah Sukuk
                3.2 Mudaraba Sukuk
                3.3 Musharaka Sukuk
                3.4 Murabaha Sukuk
                3.5 Salam Sukuk
                3.6 Istisna'a Sukuk
                3.7 Hybrid/Mixed Sukuk
                
                4. Shariah Requirements for Issuing Sukuk
                4.1 Sukuk must represent a common share in the ownership of assets, usufructs or services.
                4.2 The prospectus must include all contractual conditions and all information required by Shariah about the issue and the subscription terms.
                4.3 Sukuk must not represent receivables or debts, except in the case of a trading or financial entity selling all its assets or a portfolio with a standing financial obligation, in which some debts, incidental to physical assets or usufruct, were included unintentionally.
                
                5. Trading of Sukuk
                5.1 It is permissible to trade Sukuk representing ownership of tangible assets, usufructs or services.
                5.2 It is not permissible to trade Sukuk representing debts or monetary obligations.
                5.3 In the case of mixed assets, it is permissible to trade Sukuk if the majority of the assets are tangible assets, usufructs or services.
                
                6. Guarantees and Promises in Sukuk
                6.1 It is not permissible for the Mudarib (investment manager), Sharik (partner) or Wakil (agent) to undertake to repurchase the assets from Sukuk holders at nominal value upon maturity.
                6.2 It is permissible, however, to undertake to repurchase the assets at their market value, fair value or a price agreed at the time of purchase.
                """
            elif "fas-28" in url.lower() or "murabaha" in url.lower():
                return """
                FAS 28: Murabaha and Other Deferred Payment Sales
                
                1. Scope
                This standard shall apply to the accounting for Murabaha and other deferred payment sales transactions carried out by Islamic financial institutions.
                
                2. Definitions
                2.1 Murabaha is a sale of goods with an agreed-upon profit mark-up on the cost.
                2.2 Deferred payment sale is a sale in which the price is paid after the conclusion of the sales contract during a period agreed upon by the two parties, either as a lump sum or in installments.
                
                3. Accounting Treatment for the Seller
                3.1 At the time of contracting, the asset shall be recognized at its historical cost.
                3.2 At the time of concluding a Murabaha sale, the asset shall be derecognized and a receivable due from the customer shall be recognized at the sales price.
                3.3 Profits from Murabaha transactions shall be recognized on an accrual basis, proportionately allocated over the period of the contract.
                
                4. Accounting Treatment for the Buyer
                4.1 The buyer shall recognize the asset purchased at its cost, which is the cash equivalent of the total amount to be paid.
                4.2 The difference between the cash equivalent and the total amount to be paid shall be recognized as a financing cost and allocated over the period of the contract.
                
                5. Disclosure Requirements
                5.1 The seller shall disclose the policies used to recognize profits from Murabaha transactions.
                5.2 The seller shall disclose the amount of Murabaha receivables and the related deferred profits.
                5.3 The buyer shall disclose the policies used to allocate the financing cost over the period of the contract.
                """
            else:
                # For other URLs, return a generic message
                return f"Content for {url} is not available in the predefined dataset. This would normally be retrieved from the web."
            
        except Exception as e:
            self.logger.error(f"Error retrieving content: {str(e)}")
            return ""

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except Exception as e:
            self.logger.error(f"Error extracting domain: {str(e)}")
            return ""


class ClaimClassifier:
    """
    Classifies claims in enhancement proposals as verifiable or subjective.
    """
    
    def __init__(self):
        """Initialize the claim classifier"""
        self.logger = logging.getLogger(__name__)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAND61l0rHF-p2UQg28RSMe62DZgQOHsLE")
        self.use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
        self.logger.info("Initializing claim classifier")
    
    def classify_claims(self, text: str) -> Dict[str, List[str]]:
        """Classify claims in text as verifiable or subjective"""
        self.logger.info("Classifying claims in text")
        
        try:
            # Try using Gemini if configured
            if self.use_gemini or not self.openai_api_key:
                self.logger.info("Using Gemini for claim classification")
                gemini_client = GeminiClient(api_key=self.gemini_api_key)
                return gemini_client.classify_claims(text)
            
            # Otherwise use OpenAI
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""
            TEXT:
            {text}
            
            TASK:
            Analyze the text and identify two types of statements:
            1. Verifiable claims: Factual statements that can be verified against Islamic finance standards
            2. Subjective suggestions: Opinions, recommendations, or suggestions that cannot be directly verified
            
            FORMAT YOUR RESPONSE AS FOLLOWS:
            VERIFIABLE CLAIMS:
            - [claim 1]
            - [claim 2]
            ...
            
            SUBJECTIVE SUGGESTIONS:
            - [suggestion 1]
            - [suggestion 2]
            ...
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in Islamic finance and Shariah standards."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse the response
            verifiable = []
            subjective = []
            
            current_section = None
            for line in response_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if "VERIFIABLE CLAIMS:" in line.upper():
                    current_section = "verifiable"
                elif "SUBJECTIVE SUGGESTIONS:" in line.upper():
                    current_section = "subjective"
                elif line.startswith('-') and current_section == "verifiable":
                    claim = line[1:].strip()
                    if claim:
                        verifiable.append(claim)
                elif line.startswith('-') and current_section == "subjective":
                    suggestion = line[1:].strip()
                    if suggestion:
                        subjective.append(suggestion)
            
            return {
                "verifiable": verifiable,
                "subjective": subjective
            }
            
        except Exception as e:
            self.logger.error(f"Error classifying claims: {str(e)}")
            # Try Gemini as fallback if not already tried
            if not self.use_gemini and self.gemini_api_key:
                self.logger.info("Falling back to Gemini for claim classification")
                try:
                    gemini_client = GeminiClient(api_key=self.gemini_api_key)
                    return gemini_client.classify_claims(text)
                except Exception as gemini_error:
                    self.logger.error(f"Gemini fallback also failed: {str(gemini_error)}")
            # Simple rule-based classification as a last resort
            lines = text.split('\n')
            verifiable = []
            subjective = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Simple rule-based classification
                if any(word in line.lower() for word in ['i think', 'i believe', 'should', 'could', 'would', 'may', 'might', 'perhaps', 'possibly']):
                    subjective.append(line)
                elif len(line) > 10:  # Only add substantial lines
                    verifiable.append(line)
            
            return {
                "verifiable": verifiable,
                "subjective": subjective
            }


# Create singleton instance
web_retriever = WebRetriever()
claim_classifier = ClaimClassifier()

def get_web_retriever() -> WebRetriever:
    """Get the singleton web retriever instance"""
    return web_retriever

def get_claim_classifier() -> ClaimClassifier:
    """Get the singleton claim classifier instance"""
    return claim_classifier
