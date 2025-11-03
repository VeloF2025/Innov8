#!/usr/bin/env python3
"""
Intelligent Adaptive Question Engine

This module implements the core question engine that adapts based on user responses,
industry type, business stage, and other contextual factors.

Author: Innov8 Workflow Team
Version: 1.0
Date: November 2025
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class BusinessStage(Enum):
    PRE_SEED = "pre-seed"
    SEED = "seed"
    SERIES_A = "series-a"
    SERIES_B = "series-b"
    GROWTH = "growth"
    LATE_STAGE = "late-stage"

class Industry(Enum):
    SAAS = "saas"
    INFRASTRUCTURE = "infrastructure"
    AGRITECH = "agritech"
    FINTECH = "fintech"
    ECOMMERCE = "ecommerce"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    GENERAL = "general"

class QuestionType(Enum):
    TEXT = "text"
    NUMBER = "number"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"
    BOOLEAN = "boolean"
    DATE = "date"
    URL = "url"
    EMAIL = "email"

@dataclass
class Question:
    id: str
    text: str
    type: QuestionType
    options: Optional[List[str]] = None
    required: bool = True
    conditional_on: Optional[str] = None
    conditional_values: Optional[List[Any]] = None
    skip_if: Optional[str] = None
    skip_values: Optional[List[Any]] = None
    help_text: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None
    weight: float = 1.0
    industry_specific: List[Industry] = None
    stage_specific: List[BusinessStage] = None

@dataclass
class Answer:
    question_id: str
    value: Any
    confidence: float = 1.0
    source: str = "user_input"
    timestamp: str = ""

@dataclass
class UserContext:
    industry: Industry
    stage: BusinessStage
    geography: str
    funding_amount: Optional[float] = None
    company_size: Optional[str] = None
    business_model: Optional[str] = None
    target_market: Optional[str] = None

class QuestionEngine:
    """Intelligent adaptive question engine for business planning workflows."""

    def __init__(self):
        self.questions_db = self._load_question_database()
        self.question_paths = self._load_question_paths()
        self.industry_weights = self._load_industry_weights()
        self.stage_depth_config = self._load_stage_depth_config()

    def _load_question_database(self) -> Dict[str, Question]:
        """Load the comprehensive question database."""
        return {
            # Business Overview Questions
            "company_name": Question(
                id="company_name",
                text="What is your company name?",
                type=QuestionType.TEXT,
                required=True,
                help_text="This will be used throughout all your documents and materials."
            ),
            "tagline": Question(
                id="tagline",
                text="What is your company tagline (one compelling sentence)?",
                type=QuestionType.TEXT,
                required=True,
                help_text="This should capture your unique value proposition in one sentence.",
                validation_rules={"max_length": 100}
            ),
            "mission": Question(
                id="mission",
                text="What is your company's mission statement?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Your mission should describe why your company exists and what you aim to achieve."
            ),
            "vision": Question(
                id="vision",
                text="What is your long-term vision for the company?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Describe what the world will look like when your company succeeds."
            ),

            # Problem & Solution Questions
            "primary_problem": Question(
                id="primary_problem",
                text="What primary problem does your business solve?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Clearly articulate the main pain point your customers experience."
            ),
            "problem_severity": Question(
                id="problem_severity",
                text="How severe is this problem for your target customers? (Scale 1-10)",
                type=QuestionType.NUMBER,
                required=True,
                validation_rules={"min": 1, "max": 10},
                help_text="10 = Extremely painful, 1 = Minor inconvenience"
            ),
            "problem_frequency": Question(
                id="problem_frequency",
                text="How frequently do customers experience this problem?",
                type=QuestionType.CHOICE,
                options=["Daily", "Weekly", "Monthly", "Quarterly", "Rarely"],
                required=True
            ),

            # SaaS-Specific Questions
            "current_mrr": Question(
                id="current_mrr",
                text="What is your current Monthly Recurring Revenue (MRR)?",
                type=QuestionType.NUMBER,
                required=True,
                industry_specific=[Industry.SAAS],
                validation_rules={"min": 0}
            ),
            "current_customers": Question(
                id="current_customers",
                text="How many paying customers do you currently have?",
                type=QuestionType.NUMBER,
                required=True,
                industry_specific=[Industry.SAAS]
            ),
            "mrr_growth_rate": Question(
                id="mrr_growth_rate",
                text="What is your month-over-month MRR growth rate?",
                type=QuestionType.NUMBER,
                required=True,
                industry_specific=[Industry.SAAS],
                validation_rules={"min": -100, "max": 1000}
            ),
            "churn_rate": Question(
                id="churn_rate",
                text="What is your monthly customer churn rate?",
                type=QuestionType.NUMBER,
                required=True,
                industry_specific=[Industry.SAAS],
                validation_rules={"min": 0, "max": 100}
            ),
            "ltv_cac_ratio": Question(
                id="ltv_cac_ratio",
                text="What is your current LTV:CAC ratio?",
                type=QuestionType.NUMBER,
                required=True,
                industry_specific=[Industry.SAAS],
                validation_rules={"min": 0}
            ),

            # Infrastructure-Specific Questions
            "regulatory_approvals": Question(
                id="regulatory_approvals",
                text="What regulatory approvals or licenses do you need?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["None required", "FCC License", "ICASA License", "Local permits", "Environmental permits", "Other"],
                required=True,
                industry_specific=[Industry.INFRASTRUCTURE]
            ),
            "network_investment": Question(
                id="network_investment",
                text="What is your total capital expenditure for network infrastructure?",
                type=QuestionType.NUMBER,
                required=True,
                industry_specific=[Industry.INFRASTRUCTURE],
                validation_rules={"min": 0}
            ),
            "coverage_area": Question(
                id="coverage_area",
                text="What geographic area will your network cover initially?",
                type=QuestionType.TEXT,
                required=True,
                industry_specific=[Industry.INFRASTRUCTURE]
            ),

            # AgriTech-Specific Questions
            "crop_types": Question(
                id="crop_types",
                text="What crop types do you primarily serve?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["Grains", "Vegetables", "Fruits", "Legumes", "Specialty crops", "Mixed farming", "Other"],
                required=True,
                industry_specific=[Industry.AGRITECH]
            ),
            "farm_size": Question(
                id="farm_size",
                text="What is the average size of your target farms?",
                type=QuestionType.CHOICE,
                options=["Small (1-5 hectares)", "Medium (5-50 hectares)", "Large (50-500 hectares)", "Very large (500+ hectares)"],
                required=True,
                industry_specific=[Industry.AGRITECH]
            ),
            "climate_considerations": Question(
                id="climate_considerations",
                text="How does your solution address climate change challenges?",
                type=QuestionType.TEXT,
                required=True,
                industry_specific=[Industry.AGRITECH],
                help_text="Consider drought resistance, water efficiency, climate adaptation, etc."
            ),

            # Market Questions
            "tam_size": Question(
                id="tam_size",
                text="What is your Total Addressable Market (TAM) size?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Provide in both monetary value and number of potential customers."
            ),
            "sam_size": Question(
                id="sam_size",
                text="What is your Serviceable Addressable Market (SAM) size?",
                type=QuestionType.TEXT,
                required=True,
                help_text="The portion of TAM you can realistically target with your solution."
            ),
            "som_size": Question(
                id="som_size",
                text="What is your Serviceable Obtainable Market (SOM) size?",
                type=QuestionType.TEXT,
                required=True,
                help_text="The realistic share of SAM you can capture in the near term."
            ),

            # Team Questions
            "founder_count": Question(
                id="founder_count",
                text="How many founders does your company have?",
                type=QuestionType.NUMBER,
                required=True,
                validation_rules={"min": 1}
            ),
            "team_size": Question(
                id="team_size",
                text="How many total employees does your company have?",
                type=QuestionType.NUMBER,
                required=True,
                validation_rules={"min": 0}
            ),
            "key_hires_needed": Question(
                id="key_hires_needed",
                text="What key positions do you need to hire in the next 6 months?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["Engineering", "Sales", "Marketing", "Operations", "Finance", "Customer Success", "Other"],
                required=True
            ),

            # Financial Questions
            "current_revenue": Question(
                id="current_revenue",
                text="What is your current annual revenue?",
                type=QuestionType.NUMBER,
                required=True,
                validation_rules={"min": 0}
            ),
            "funding_needed": Question(
                id="funding_needed",
                text="How much funding are you seeking?",
                type=QuestionType.NUMBER,
                required=True,
                validation_rules={"min": 0}
            ),
            "runway_months": Question(
                id="runway_months",
                text="How many months of runway do you have with current cash?",
                type=QuestionType.NUMBER,
                required=True,
                validation_rules={"min": 0}
            ),

            # Technology Questions
            "technology_stack": Question(
                id="technology_stack",
                text="What are your key technologies and programming languages?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["Python", "JavaScript/Node.js", "Java", "C#", "Ruby", "PHP", "Go", "Rust", "Other"],
                required=True
            ),
            "infrastructure": Question(
                id="infrastructure",
                text="Where do you host your applications?",
                type=QuestionType.MULTIPLE_CHOICE,
                options=["AWS", "Google Cloud", "Microsoft Azure", "On-premise", "Vercel", "Netlify", "Other"],
                required=True
            ),

            # Business Model Questions
            "revenue_model": Question(
                id="revenue_model",
                text="What is your primary revenue model?",
                type=QuestionType.CHOICE,
                options=["Subscription", "Transaction-based", "Advertising", "Marketplace", "Licensing", "Freemium", "Other"],
                required=True
            ),
            "pricing_model": Question(
                id="pricing_model",
                text="How do you structure your pricing?",
                type=QuestionType.TEXT,
                required=True,
                help_text="Describe your pricing tiers, rates, or structure."
            ),
        }

    def _load_question_paths(self) -> Dict[str, List[str]]:
        """Load question paths for different scenarios."""
        return {
            "pre_seed_general": [
                "company_name", "tagline", "mission", "vision",
                "primary_problem", "problem_severity", "problem_frequency",
                "tam_size", "sam_size", "som_size",
                "founder_count", "team_size", "key_hires_needed",
                "current_revenue", "funding_needed", "runway_months",
                "technology_stack", "infrastructure",
                "revenue_model", "pricing_model"
            ],
            "seed_saas": [
                "company_name", "tagline", "mission", "vision",
                "primary_problem", "problem_severity", "problem_frequency",
                "current_mrr", "current_customers", "mrr_growth_rate", "churn_rate", "ltv_cac_ratio",
                "tam_size", "sam_size", "som_size",
                "founder_count", "team_size", "key_hires_needed",
                "funding_needed", "runway_months",
                "technology_stack", "infrastructure",
                "revenue_model", "pricing_model"
            ],
            "seed_infrastructure": [
                "company_name", "tagline", "mission", "vision",
                "primary_problem", "problem_severity", "problem_frequency",
                "regulatory_approvals", "network_investment", "coverage_area",
                "tam_size", "sam_size", "som_size",
                "founder_count", "team_size", "key_hires_needed",
                "current_revenue", "funding_needed", "runway_months",
                "technology_stack", "infrastructure",
                "revenue_model", "pricing_model"
            ],
            "seed_agritech": [
                "company_name", "tagline", "mission", "vision",
                "primary_problem", "problem_severity", "problem_frequency",
                "crop_types", "farm_size", "climate_considerations",
                "tam_size", "sam_size", "som_size",
                "founder_count", "team_size", "key_hires_needed",
                "funding_needed", "runway_months",
                "technology_stack", "infrastructure",
                "revenue_model", "pricing_model"
            ],
            "series_a_saas": [
                "company_name", "tagline", "mission", "vision",
                "primary_problem", "problem_severity", "problem_frequency",
                "current_mrr", "current_customers", "mrr_growth_rate", "churn_rate", "ltv_cac_ratio",
                "tam_size", "sam_size", "som_size",
                "team_size", "key_hires_needed",
                "funding_needed", "runway_months",
                "technology_stack", "infrastructure",
                "revenue_model", "pricing_model"
            ]
        }

    def _load_industry_weights(self) -> Dict[Industry, Dict[str, float]]:
        """Load industry-specific question weights."""
        return {
            Industry.SAAS: {
                "current_mrr": 2.0,
                "current_customers": 1.5,
                "mrr_growth_rate": 2.0,
                "churn_rate": 1.5,
                "ltv_cac_ratio": 1.8
            },
            Industry.INFRASTRUCTURE: {
                "regulatory_approvals": 2.5,
                "network_investment": 2.0,
                "coverage_area": 1.5
            },
            Industry.AGRITECH: {
                "crop_types": 1.8,
                "farm_size": 1.5,
                "climate_considerations": 2.0
            }
        }

    def _load_stage_depth_config(self) -> Dict[BusinessStage, Dict[str, Any]]:
        """Load stage-specific depth configuration."""
        return {
            BusinessStage.PRE_SEED: {
                "required_only": True,
                "detail_level": "basic",
                "skip_advanced": True
            },
            BusinessStage.SEED: {
                "required_only": False,
                "detail_level": "standard",
                "skip_advanced": False
            },
            BusinessStage.SERIES_A: {
                "required_only": False,
                "detail_level": "comprehensive",
                "skip_advanced": False
            },
            BusinessStage.GROWTH: {
                "required_only": False,
                "detail_level": "comprehensive",
                "skip_advanced": False,
                "include_advanced": True
            }
        }

    def generate_question_path(self, context: UserContext) -> List[Question]:
        """Generate an adaptive question path based on user context."""
        # Base question path
        if context.stage == BusinessStage.PRE_SEED:
            base_path = self.question_paths["pre_seed_general"]
        elif context.stage == BusinessStage.SEED:
            if context.industry == Industry.SAAS:
                base_path = self.question_paths["seed_saas"]
            elif context.industry == Industry.INFRASTRUCTURE:
                base_path = self.question_paths["seed_infrastructure"]
            elif context.industry == Industry.AGRITECH:
                base_path = self.question_paths["seed_agritech"]
            else:
                base_path = self.question_paths["pre_seed_general"]
        else:
            base_path = self.question_paths["pre_seed_general"]

        # Generate questions
        questions = []
        for question_id in base_path:
            if question_id in self.questions_db:
                question = self.questions_db[question_id]

                # Apply industry-specific logic
                if question.industry_specific and context.industry not in question.industry_specific:
                    continue

                # Apply stage-specific logic
                if question.stage_specific and context.stage not in question.stage_specific:
                    continue

                # Apply industry-specific weights
                if context.industry in self.industry_weights:
                    industry_weights = self.industry_weights[context.industry]
                    if question.id in industry_weights:
                        question.weight = industry_weights[question.id]

                questions.append(question)

        # Sort by weight (highest first)
        questions.sort(key=lambda q: q.weight, reverse=True)

        return questions

    def validate_answer(self, question: Question, answer: Any) -> Tuple[bool, str]:
        """Validate an answer against question rules."""
        if not answer and question.required:
            return False, f"Answer is required for {question.text}"

        if answer is None:
            return True, ""

        # Type-specific validation
        if question.type == QuestionType.NUMBER:
            try:
                num_value = float(answer)
                if question.validation_rules:
                    if "min" in question.validation_rules and num_value < question.validation_rules["min"]:
                        return False, f"Value must be at least {question.validation_rules['min']}"
                    if "max" in question.validation_rules and num_value > question.validation_rules["max"]:
                        return False, f"Value must be no more than {question.validation_rules['max']}"
            except ValueError:
                return False, "Please enter a valid number"

        elif question.type == QuestionType.TEXT:
            if question.validation_rules and "max_length" in question.validation_rules:
                if len(str(answer)) > question.validation_rules["max_length"]:
                    return False, f"Text must be no more than {question.validation_rules['max_length']} characters"

        elif question.type == QuestionType.CHOICE:
            if answer not in question.options:
                return False, f"Please select one of: {', '.join(question.options)}"

        elif question.type == QuestionType.EMAIL:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(answer)):
                return False, "Please enter a valid email address"

        elif question.type == QuestionType.URL:
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, str(answer)):
                return False, "Please enter a valid URL starting with http:// or https://"

        return True, ""

    def get_next_question(self, context: UserContext, answers: List[Answer]) -> Optional[Question]:
        """Get the next question based on context and previous answers."""
        question_path = self.generate_question_path(context)

        # Find questions that haven't been answered
        answered_ids = {answer.question_id for answer in answers}

        for question in question_path:
            if question.id not in answered_ids:
                # Check conditional logic
                if question.conditional_on:
                    conditional_answer = next((a for a in answers if a.question_id == question.conditional_on), None)
                    if not conditional_answer or conditional_answer.value not in question.conditional_values:
                        continue

                # Check skip logic
                if question.skip_if:
                    skip_answer = next((a for a in answers if a.question_id == question.skip_if), None)
                    if skip_answer and skip_answer.value in question.skip_values:
                        continue

                return question

        return None

    def should_skip_question(self, question: Question, answers: List[Answer]) -> bool:
        """Determine if a question should be skipped based on previous answers."""
        if question.skip_if:
            skip_answer = next((a for a in answers if a.question_id == question.skip_if), None)
            if skip_answer and skip_answer.value in question.skip_values:
                return True

        return False

    def calculate_completion_score(self, context: UserContext, answers: List[Answer]) -> float:
        """Calculate completion score based on answered questions."""
        question_path = self.generate_question_path(context)
        total_weight = sum(q.weight for q in question_path)

        if total_weight == 0:
            return 0.0

        answered_weight = 0.0
        for answer in answers:
            question = next((q for q in question_path if q.id == answer.question_id), None)
            if question:
                answered_weight += question.weight

        return (answered_weight / total_weight) * 100

    def generate_insights(self, context: UserContext, answers: List[Answer]) -> Dict[str, Any]:
        """Generate insights and recommendations based on answers."""
        insights = {
            "completion_score": self.calculate_completion_score(context, answers),
            "missing_critical": [],
            "recommendations": [],
            "strengths": [],
            "concerns": []
        }

        # Analyze critical missing information
        critical_questions = [q for q in self.generate_question_path(context) if q.required and q.weight >= 2.0]
        answered_ids = {answer.question_id for answer in answers}

        for question in critical_questions:
            if question.id not in answered_ids:
                insights["missing_critical"].append(question.id)

        # Generate industry-specific insights
        if context.industry == Industry.SAAS:
            saas_insights = self._generate_saas_insights(answers)
            insights.update(saas_insights)
        elif context.industry == Industry.INFRASTRUCTURE:
            infra_insights = self._generate_infrastructure_insights(answers)
            insights.update(infra_insights)
        elif context.industry == Industry.AGRITECH:
            agritech_insights = self._generate_agritech_insights(answers)
            insights.update(agritech_insights)

        return insights

    def _generate_saas_insights(self, answers: List[Answer]) -> Dict[str, Any]:
        """Generate SaaS-specific insights."""
        insights = {"recommendations": [], "strengths": [], "concerns": []}

        # Check SaaS metrics
        mrr_answer = next((a for a in answers if a.question_id == "current_mrr"), None)
        churn_answer = next((a for a in answers if a.question_id == "churn_rate"), None)
        ltv_cac_answer = next((a for a in answers if a.question_id == "ltv_cac_ratio"), None)

        if mrr_answer and float(mrr_answer.value) > 10000:
            insights["strengths"].append("Strong initial revenue base")
        elif mrr_answer and float(mrr_answer.value) < 1000:
            insights["concerns"].append("Low revenue base - may need more traction")

        if churn_answer and float(churn_answer.value) > 5:
            insights["concerns"].append("High churn rate - focus on retention")
        elif churn_answer and float(churn_answer.value) < 2:
            insights["strengths"].append("Excellent customer retention")

        if ltv_cac_answer and float(ltv_cac_answer.value) < 3:
            insights["concerns"].append("LTV:CAC ratio below 3:1 - improve unit economics")
        elif ltv_cac_answer and float(ltv_cac_answer.value) > 5:
            insights["strengths"].append("Excellent unit economics")

        return insights

    def _generate_infrastructure_insights(self, answers: List[Answer]) -> Dict[str, Any]:
        """Generate infrastructure-specific insights."""
        insights = {"recommendations": [], "strengths": [], "concerns": []}

        # Check infrastructure metrics
        investment_answer = next((a for a in answers if a.question_id == "network_investment"), None)
        approvals_answer = next((a for a in answers if a.question_id == "regulatory_approvals"), None)

        if investment_answer and float(investment_answer.value) > 5000000:
            insights["strengths"].append("Significant infrastructure investment commitment")

        if approvals_answer and "None required" in approvals_answer.value:
            insights["strengths"].append("No regulatory barriers identified")
        elif approvals_answer and len(approvals_answer.value) > 3:
            insights["concerns"].append("Multiple regulatory approvals required - may delay launch")

        return insights

    def _generate_agritech_insights(self, answers: List[Answer]) -> Dict[str, Any]:
        """Generate AgriTech-specific insights."""
        insights = {"recommendations": [], "strengths": [], "concerns": []}

        # Check AgriTech metrics
        crops_answer = next((a for a in answers if a.question_id == "crop_types"), None)
        climate_answer = next((a for a in answers if a.question_id == "climate_considerations"), None)

        if crops_answer and len(crops_answer.value) > 3:
            insights["strengths"].append("Diverse crop portfolio - reduces market risk")

        if climate_answer and "climate" in climate_answer.value.lower():
            insights["strengths"].append("Climate change adaptation focus")

        return insights

    def export_session_data(self, context: UserContext, answers: List[Answer]) -> Dict[str, Any]:
        """Export session data for template generation."""
        return {
            "context": asdict(context),
            "answers": [asdict(answer) for answer in answers],
            "insights": self.generate_insights(context, answers),
            "completion_score": self.calculate_completion_score(context, answers),
            "question_path": [q.id for q in self.generate_question_path(context)]
        }

def main():
    """Test the question engine."""
    engine = QuestionEngine()

    # Test with different scenarios
    scenarios = [
        UserContext(Industry.SAAS, BusinessStage.SEED, "US", 1000000),
        UserContext(Industry.INFRASTRUCTURE, BusinessStage.SERIES_A, "South Africa", 10000000),
        UserContext(Industry.AGRITECH, BusinessStage.SEED, "Kenya", 2500000)
    ]

    for i, context in enumerate(scenarios):
        print(f"\n=== Scenario {i+1}: {context.industry.value} @ {context.stage.value} ===")

        questions = engine.generate_question_path(context)
        print(f"Generated {len(questions)} questions")

        # Show first few questions
        for j, question in enumerate(questions[:3]):
            print(f"  {j+1}. {question.text} (Weight: {question.weight})")

        # Calculate total weight
        total_weight = sum(q.weight for q in questions)
        print(f"Total question weight: {total_weight}")

if __name__ == "__main__":
    main()