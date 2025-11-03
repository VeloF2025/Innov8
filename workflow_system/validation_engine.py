#!/usr/bin/env python3
"""
AI-Powered Validation Engine

This module implements intelligent validation and quality checking for business documents
and answers, including consistency checking, benchmarking, and improvement recommendations.

Author: Innov8 Workflow Team
Version: 1.0
Date: November 2025
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from question_engine import UserContext, Answer, Question

class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    REALISM = "realism"
    CLARITY = "clarity"
    INDUSTRY_FIT = "industry_fit"
    QUALITY = "quality"

@dataclass
class ValidationResult:
    category: ValidationCategory
    severity: ValidationSeverity
    title: str
    description: str
    suggestions: List[str]
    confidence: float
    affected_section: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class DocumentAnalysis:
    document_type: str
    overall_score: float
    grade: str
    validations: List[ValidationResult]
    insights: Dict[str, Any]
    recommendations: List[str]
    benchmark_comparison: Dict[str, Any]

class ValidationEngine:
    """AI-powered validation engine for business documents and answers."""

    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.benchmarks = self._load_benchmarks()
        self.patterns = self._load_patterns()
        self.scoring_weights = self._load_scoring_weights()

    def _load_validation_rules(self) -> Dict[str, Dict]:
        """Load validation rules."""
        return {
            "financial_projections": {
                "must_have_sections": ["revenue_forecast", "expense_forecast", "cash_flow", "profit_loss"],
                "timeframes": ["monthly", "quarterly", "annual"],
                "minimum_years": 3,
                "required_metrics": ["growth_rate", "margin", "break_even"]
            },
            "market_analysis": {
                "must_have_sections": ["tam_sam_som", "target_market", "competitors", "market_trends"],
                "data_sources_required": True,
                "competitive_analysis_depth": "detailed",
                "market_sizing_methodology": "bottom_up"
            },
            "team_section": {
                "must_have_sections": ["founders", "key_hires", "advisors"],
                "experience_requirements": True,
                "role_clarity": True,
                "gaps_identified": True
            }
        }

    def _load_benchmarks(self) -> Dict[str, Dict]:
        """Load industry benchmarks."""
        return {
            "saas": {
                "industry": "SaaS",
                "benchmarks": {
                    "lvr_cac_ratio": {"min": 3.0, "ideal": 4.0, "excellent": 5.0},
                    "churn_rate": {"max": 0.05, "good": 0.03, "excellent": 0.02},
                    "gross_margin": {"min": 0.70, "good": 0.80, "excellent": 0.85},
                    "net_revenue_retention": {"min": 1.0, "good": 1.20, "excellent": 1.30},
                    "cac_payback": {"max": 12, "good": 9, "excellent": 6}
                }
            },
            "infrastructure": {
                "industry": "Infrastructure/Telco",
                "benchmarks": {
                    "deployment_cost_per_customer": {"max": 50000, "good": 30000, "excellent": 20000},
                    "network_utilization": {"min": 0.60, "good": 0.75, "excellent": 0.85},
                    "arpu": {"min": 500, "good": 1000, "excellent": 2000},
                    "churn_rate": {"max": 0.02, "good": 0.015, "excellent": 0.01}
                }
            },
            "agritech": {
                "industry": "AgriTech",
                "benchmarks": {
                    "farmer_acquisition_cost": {"max": 200, "good": 100, "excellent": 50},
                    "yield_improvement": {"min": 0.20, "good": 0.30, "excellent": 0.40},
                    "adoption_rate": {"min": 0.50, "good": 0.70, "excellent": 0.85},
                    "retention_rate": {"min": 0.80, "good": 0.90, "excellent": 0.95}
                }
            }
        }

    def _load_patterns(self) -> Dict[str, Dict]:
        """Load validation patterns."""
        return {
            "email": {
                "pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                "description": "Valid email address format"
            },
            "url": {
                "pattern": r'^https?://[^\s/$.?#].[^\s]*$',
                "description": "Valid URL starting with http:// or https://"
            },
            "phone": {
                "pattern": r'^\+?[\d\s\-\(\)]{10,}$',
                "description": "Valid phone number format"
            },
            "currency": {
                "pattern": r'^\$\d{1,3}(,\d{3})*(\.\d{2})?$',
                "description": "Valid currency format (e.g., $1,000.00)"
            },
            "percentage": {
                "pattern": r'^\d{1,3}(\.\d+)?%',
                "description": "Valid percentage format (e.g., 25.5%)"
            }
        }

    def _load_scoring_weights(self) -> Dict[str, Dict]:
        """Load scoring weights for different validation categories."""
        return {
            "completeness": {"weight": 0.25, "max_score": 100},
            "consistency": {"weight": 0.20, "max_score": 100},
            "realism": {"weight": 0.20, "max_score": 100},
            "clarity": {"weight": 0.15, "max_score": 100},
            "industry_fit": {"weight": 0.20, "max_score": 100}
        }

    def validate_answers(self, context: UserContext, answers: List[Answer]) -> DocumentAnalysis:
        """Validate user answers and provide comprehensive analysis."""
        validations = []

        # Validate each category
        validations.extend(self._validate_completeness(context, answers))
        validations.extend(self._validate_consistency(context, answers))
        validations.extend(self._validate_realism(context, answers))
        validations.extend(self._validate_clarity(answers))
        validations.extend(self._validate_industry_fit(context, answers))

        # Calculate overall score
        overall_score = self._calculate_overall_score(validations)
        grade = self._calculate_grade(overall_score)

        # Generate insights and recommendations
        insights = self._generate_insights(validations)
        recommendations = self._generate_recommendations(validations, context)

        # Benchmark comparison
        benchmark_comparison = self._benchmark_comparison(context, answers)

        return DocumentAnalysis(
            document_type="business_plan",
            overall_score=overall_score,
            grade=grade,
            validations=validations,
            insights=insights,
            recommendations=recommendations,
            benchmark_comparison=benchmark_comparison
        )

    def _validate_completeness(self, context: UserContext, answers: List[Answer]) -> List[ValidationResult]:
        """Validate completeness of answers."""
        validations = []

        # Check critical questions
        critical_questions = self._get_critical_questions(context)
        answered_ids = {answer.question_id for answer in answers}
        critical_answered = [q for q in critical_questions if q.id in answered_ids]

        if len(critical_answered) < len(critical_questions):
            missing_critical = len(critical_questions) - len(critical_answered)
            validations.append(ValidationResult(
                category=ValidationCategory.COMPLETENESS,
                severity=ValidationSeverity.ERROR,
                title="Missing Critical Information",
                description=f"{missing_critical} critical questions remain unanswered. These are essential for investor evaluation.",
                suggestions=[
                    "Complete all critical questions marked as required",
                    "Focus on questions related to your unique value proposition",
                    "Ensure financial projections are comprehensive"
                ],
                confidence=0.95,
                affected_section="critical_questions"
            ))

        # Check answer depth
        shallow_answers = self._find_shallow_answers(answers)
        if shallow_answers:
            validations.append(ValidationResult(
                category=ValidationCategory.COMPLETENESS,
                severity=ValidationSeverity.WARNING,
                title="Superficial Answers Detected",
                description=f"{len(shallow_answers)} answers appear too brief or lack sufficient detail.",
                suggestions=[
                    "Provide specific examples and evidence",
                    "Include measurable metrics and targets",
                    "Add context and reasoning for your statements"
                ],
                confidence=0.80,
                affected_section="answer_depth"
            ))

        return validations

    def _validate_consistency(self, context: UserContext, answers: List[Answer]) -> List[ValidationResult]:
        """Validate consistency across answers."""
        validations = []

        # Check financial consistency
        financial_inconsistencies = self._find_financial_inconsistencies(answers)
        if financial_inconsistencies:
            validations.append(ValidationResult(
                category=ValidationCategory.CONSISTENCY,
                severity=ValidationSeverity.ERROR,
                title="Financial Inconsistencies",
                description="Found inconsistencies in financial projections and assumptions.",
                suggestions=[
                    "Ensure revenue projections match across all sections",
                    "Validate that growth rates are realistic",
                    "Check that costs align with business model"
                ],
                confidence=0.90,
                affected_section="financials"
            ))

        # Check timeline consistency
        timeline_inconsistencies = self._find_timeline_inconsistencies(answers)
        if timeline_inconsistencies:
            validations.append(ValidationResult(
                category=ValidationCategory.CONSISTENCY,
                severity=ValidationSeverity.WARNING,
                title="Timeline Inconsistencies",
                description="Timeline projections appear inconsistent across different sections.",
                suggestions=[
                    "Ensure milestone dates are consistent across documents",
                    "Validate that funding requirements match timeline needs",
                    "Check that hiring plans align with growth projections"
                ],
                confidence=0.75,
                affected_section="timeline"
            ))

        # Check team consistency
        team_inconsistencies = self._find_team_inconsistencies(answers)
        if team_inconsistencies:
            validations.append(ValidationResult(
                category=ValidationCategory.CONSISTENCY,
                severity=ValidationSeverity.INFO,
                title="Team Information Gaps",
                description="Team information appears incomplete or inconsistent.",
                suggestions=[
                    "Ensure all key roles are accounted for",
                    "Add missing team member backgrounds",
                    "Validate team size matches business needs"
                ],
                confidence=0.70,
                affected_section="team"
            ))

        return validations

    def _validate_realism(self, context: UserContext, answers: List[Answer]) -> List[ValidationResult]:
        """Validate realism of answers and assumptions."""
        validations = []

        # Check for unrealistic financial projections
        unrealistic_projections = self._find_unrealistic_projections(context, answers)
        if unrealistic_projections:
            validations.append(ValidationResult(
                category=ValidationCategory.REALISM,
                severity=ValidationSeverity.ERROR,
                title="Unrealistic Financial Projections",
                description="Financial projections appear overly optimistic or lack realistic assumptions.",
                suggestions=[
                    "Provide detailed assumptions for growth rates",
                    "Include conservative scenarios in projections",
                    "Benchmark against industry standards"
                ],
                confidence=0.85,
                affected_section="financial_projections"
            ))

        # Check for unrealistic market claims
        unrealistic_market = self._find_unrealistic_market_claims(context, answers)
        if unrealistic_market:
            validations.append(ValidationResult(
                category=ValidationCategory.REALISM,
                severity=ValidationSeverity.WARNING,
                title="Market Claims Need Validation",
                description="Market sizing or claims need stronger evidence or more realistic assumptions.",
                suggestions=[
                    "Include sources for market research",
                    "Add validation from customer interviews",
                    "Break down total addressable market realistically"
                ],
                confidence=0.75,
                affected_section="market_analysis"
            ))

        # Check for competitive advantages
        weak_competitive_advantage = self._find_weak_competitive_advantage(answers)
        if weak_competitive_advantage:
            validations.append(ValidationResult(
                category=ValidationCategory.REALISM,
                severity=ValidationSeverity.WARNING,
                title="Competitive Advantage Not Clearly Defined",
                description="Your competitive advantage needs to be more clearly articulated.",
                suggestions=[
                    "Be specific about what makes you different",
                    "Include evidence of sustainable competitive moat",
                    "Focus on unique capabilities or assets"
                ],
                confidence=0.70,
                affected_section="competitive_analysis"
            ))

        return validations

    def _validate_clarity(self, answers: List[Answer]) -> List[ValidationResult]:
        """Validate clarity and professionalism of answers."""
        validations = []

        # Check for vague language
        vague_language = self._find_vague_language(answers)
        if vague_language:
            validations.append(ValidationResult(
                category=ValidationCategory.CLARITY,
                severity=ValidationSeverity.WARNING,
                title="Vague Language Detected",
                description="Some answers use vague language that could be more specific and measurable.",
                suggestions=[
                    "Replace vague terms with specific, measurable statements",
                    "Use data and evidence to support claims",
                    "Be precise about metrics and timelines"
                ],
                confidence=0.75,
                affected_section="clarity"
            ))

        # Check for jargon and clarity
        jargon_issues = self._find_jargon_issues(answers)
        if jargon_issues:
            validations.append(ValidationResult(
                category=ValidationCategory.CLARITY,
                severity=ValidationSeverity.INFO,
                title="Clarity Improvements Available",
                description="Some sections could benefit from clearer language or better explanations.",
                suggestions=[
                    "Explain technical terms for broader audience",
                    "Simplify complex concepts where possible",
                    "Ensure all stakeholders can understand your business"
                ],
                confidence=0.65,
                affected_section="readability"
            ))

        # Check for formatting issues
        formatting_issues = self._find_formatting_issues(answers)
        if formatting_issues:
            validations.append(ValidationResult(
                category=ValidationCategory.CLARITY,
                severity=ValidationSeverity.INFO,
                title="Formatting Improvements",
                description="Some answers could benefit from better formatting or organization.",
                suggestions=[
                    "Use bullet points for lists and examples",
                    "Include headings and subheadings for structure",
                    "Ensure consistent formatting throughout"
                ],
                confidence=0.60,
                affected_section="formatting"
            ))

        return validations

    def _validate_industry_fit(self, context: UserContext, answers: List[Answer]) -> List[ValidationResult]:
        """Validate industry-specific requirements."""
        validations = []

        # Check industry-specific metrics
        industry_metrics_gap = self._find_industry_metrics_gap(context, answers)
        if industry_metrics_gap:
            validations.append(ValidationResult(
                category=ValidationCategory.INDUSTRY_FIT,
                severity=ValidationSeverity.ERROR,
                title="Industry-Specific Metrics Missing",
                description=f"Critical {context.industry.value} industry metrics are missing from your plan.",
                suggestions=industry_metrics_gap.get("suggestions", []),
                confidence=0.90,
                affected_section="industry_metrics"
            ))

        # Check regulatory compliance
        regulatory_issues = self._find_regulatory_issues(context, answers)
        if regulatory_issues:
            validations.append(ValidationResult(
                category=ValidationCategory.INDUSTRY_FIT,
                severity=ValidationSeverity.ERROR,
                title="Regulatory Compliance Issues",
                description="Important regulatory considerations for your industry need to be addressed.",
                suggestions=regulatory_issues.get("suggestions", []),
                confidence=0.85,
                affected_section="regulatory"
            ))

        return validations

    def _get_critical_questions(self, context: UserContext) -> List[Question]:
        """Get critical questions based on context."""
        critical_questions = [
            # Business fundamentals
            {"id": "company_name", "weight": 2.0},
            {"id": "primary_problem", "weight": 2.5},
            {"id": "tam_size", "weight": 2.0},
            {"id": "revenue_model", "weight": 2.0},
            {"id": "funding_needed", "weight": 2.0},
            {"id": "team_size", "weight": 1.5}
        ]

        # Add industry-specific critical questions
        if context.industry.value == "saas":
            critical_questions.extend([
                {"id": "current_mrr", "weight": 2.0},
                {"id": "churn_rate", "weight": 2.0},
                {"id": "ltv_cac_ratio", "weight": 1.8}
            ])
        elif context.industry.value == "infrastructure":
            critical_questions.extend([
                {"id": "regulatory_approvals", "weight": 2.5},
                {"id": "network_investment", "weight": 2.0}
            ])
        elif context.industry.value == "agritech":
            critical_questions.extend([
                {"id": "crop_types", "weight": 1.8},
                {"id": "farm_size", "weight": 1.5}
            ])

        # Add stage-specific critical questions
        if context.stage.value in ["series-a", "series-b", "growth"]:
            critical_questions.extend([
                {"id": "current_revenue", "weight": 2.0},
                {"id": "key_hires_needed", "weight": 1.5}
            ])

        return critical_questions

    def _find_shallow_answers(self, answers: List[Answer]) -> List[str]:
        """Find answers that are too brief or lack depth."""
        shallow_answers = []

        for answer in answers:
            if isinstance(answer.value, str):
                # Check for very short answers
                if len(answer.value.strip()) < 20:
                    shallow_answers.append(answer.question_id)
                # Check for answers that are just single words or short phrases
                elif len(answer.value.strip().split()) < 5:
                    shallow_answers.append(answer.question_id)

        return shallow_answers

    def _find_financial_inconsistencies(self, answers: List[Answer]) -> List[str]:
        """Find financial inconsistencies across answers."""
        inconsistencies = []

        # Extract financial data
        revenue = self._extract_financial_value(answers, "current_revenue")
        funding = self._extract_financial_value(answers, "funding_needed")
        team_size = self._extract_numeric_value(answers, "team_size")

        # Check for unrealistic ratios
        if revenue and funding:
            funding_revenue_ratio = funding / revenue
            if funding_revenue_ratio > 20:  # Seeking 20x current revenue
                inconsistencies.append("funding_revenue_ratio")
            elif revenue > 0 and funding_revenue_ratio > 0.5 and funding > 5000000:  # High revenue but still seeking significant funding
                inconsistencies.append("high_revenue_high_funding")

        # Check team size vs revenue
        if revenue and team_size:
            revenue_per_employee = revenue / team_size
            if revenue_per_employee > 1000000:  # $1M+ revenue per employee
                inconsistencies.append("high_revenue_per_employee")
            elif revenue_per_employee < 50000 and revenue > 1000000:  # Low productivity at scale
                inconsistencies.append("low_revenue_per_employee")

        return inconsistencies

    def _find_timeline_inconsistencies(self, answers: List[Answer]) -> List[str]:
        """Find timeline inconsistencies across answers."""
        inconsistencies = []

        # This would look for timeline inconsistencies in a real implementation
        # For now, return empty list as this is complex to implement without full document analysis
        return inconsistencies

    def _find_team_inconsistencies(self, answers: List[Answer]) -> List[str]:
        """Find team inconsistencies."""
        inconsistencies = []

        # Extract team data
        founder_count = self._extract_numeric_value(answers, "founder_count")
        team_size = self._extract_numeric_value(answers, "team_size")
        key_hires = self._extract_list_value(answers, "key_hires_needed")

        # Check team size vs founder count
        if founder_count and team_size:
            if team_size < founder_count:
                inconsistencies.append("team_size_less_than_founders")
            elif team_size > founder_count * 10 and team_size > 50:  # Very large team for small company
                inconsistencies.append("large_team_small_company")

        return inconsistencies

    def _find_unrealistic_projections(self, context: UserContext, answers: List[Answer]) -> List[str]:
        """Find unrealistic financial projections."""
        unrealistic = []

        # Extract SaaS-specific metrics
        if context.industry.value == "saas":
            mrr = self._extract_financial_value(answers, "current_mrr")
            churn = self._extract_percentage_value(answers, "churn_rate")
            growth = self._extract_percentage_value(answers, "mrr_growth_rate")

            # Check for unrealistic growth rates
            if growth and growth > 50:  # 50%+ month-over-month growth
                unrealistic.append("high_growth_rate")

            # Check for unrealistic churn rates
            if churn and churn < 0.01:  # Less than 1% monthly churn
                unrealistic.append("unrealistically_low_churn")

        return unrealistic

    def _find_unrealistic_market_claims(self, context: UserContext, answers: List[Answer]) -> List[str]:
        """Find unrealistic market claims."""
        unrealistic = []

        # This would analyze market sizing claims in a real implementation
        # For now, return empty list
        return unrealistic

    def _find_weak_competitive_advantage(self, answers: List[Answer]) -> List[str]:
        """Find weak competitive advantage statements."""
        weak = []

        # This would analyze competitive advantage statements in a real implementation
        # For now, return empty list
        return weak

    def _find_vague_language(self, answers: List[Answer]) -> List[str]:
        """Find answers with vague language."""
        vague_patterns = [
            r'\b(very|really|quite|rather|somewhat|fairly)\b',
            r'\b(good|great|excellent|amazing|wonderful)\b',
            r'\b(some|many|various|different)\b',
            r'\b(soon|quickly|rapidly)\b',
            r'\b(significant|substantial|considerable)\b'
        ]

        for answer in answers:
            if isinstance(answer.value, str):
                for pattern in vague_patterns:
                    if re.search(pattern, answer.value, re.IGNORECASE):
                        if answer.question_id not in weak:
                            weak.append(answer.question_id)
                        break

        return weak

    def _find_jargon_issues(self, answers: List[Answer]) -> List[str]:
        """Find jargon or clarity issues."""
        issues = []

        # This would analyze for excessive jargon or technical terms
        # For now, return empty list
        return issues

    def _find_formatting_issues(self, answers: List[Answer]) -> List[str]:
        """Find formatting issues."""
        issues = []

        # This would analyze formatting issues
        # For now, return empty list
        return issues

    def _find_industry_metrics_gap(self, context: UserContext, answers: List[Answer]) -> Dict[str, Any]:
        """Find gaps in industry-specific metrics."""
        gaps = {"suggestions": []}

        # Check for SaaS-specific metrics
        if context.industry.value == "saas":
            required_metrics = ["current_mrr", "churn_rate", "ltv_cac_ratio"]
            missing_metrics = []

            for metric in required_metrics:
                if not any(a.question_id == metric for a in answers):
                    missing_metrics.append(metric)

            if missing_metrics:
                gaps["suggestions"] = [
                    "Add Monthly Recurring Revenue (MRR) metrics",
                    "Include customer churn rate calculations",
                    "Calculate and include LTV:CAC ratio"
                ]
                gaps["missing_metrics"] = missing_metrics

        # Check for Infrastructure-specific metrics
        elif context.industry.value == "infrastructure":
            required_metrics = ["regulatory_approvals", "network_investment", "coverage_area"]
            missing_metrics = []

            for metric in required_metrics:
                if not any(a.question_id == metric for a in answers):
                    missing_metrics.append(metric)

            if missing_metrics:
                gaps["suggestions"] = [
                    "Detail regulatory approvals and licensing requirements",
                    "Include comprehensive network investment projections",
                    "Specify geographic coverage area and rollout plan"
                ]
                gaps["missing_metrics"] = missing_metrics

        # Check for AgriTech-specific metrics
        elif context.industry.value == "agritech":
            required_metrics = ["crop_types", "farm_size", "climate_considerations"]
            missing_metrics = []

            for metric in required_metrics:
                if not any(a.question_id == metric for a in answers):
                    missing_metrics.append(metric)

            if missing_metrics:
                gaps["suggestions"] = [
                    "Specify target crop types and agricultural focus",
                    "Define target farm size range",
                    "Address climate change adaptation considerations"
                ]
                gaps["missing_metrics"] = missing_metrics

        return gaps

    def _find_regulatory_issues(self, context: UserContext, answers: List[Answer]) -> Dict[str, Any]:
        """Find regulatory compliance issues."""
        issues = {"suggestions": []}

        # Check for regulatory approvals
        if context.industry.value == "infrastructure":
            approvals_answer = next((a for a in answers if a.question_id == "regulatory_approvals"), None)
            if approvals_answer and "None required" not in approvals_answer.value:
                issues["suggestions"] = [
                    "Detail regulatory approval timeline and process",
                    "Include costs and timeline for regulatory compliance",
                    "Identify potential regulatory risks and mitigation"
                ]

        return issues

    def _extract_financial_value(self, answers: List[Answer], question_id: str) -> Optional[float]:
        """Extract financial value from answer."""
        answer = next((a for a in answers if a.question_id == question_id), None)
        if not answer:
            return None

        if isinstance(answer.value, str):
            # Extract numbers from string
            numbers = re.findall(r'\$?[\d,]+\.?\d*|[kKmMbB]\d+', answer.value)
            if numbers:
                number_str = numbers[0].replace('$', '').replace(',', '').replace('k', '000').replace('m', '000000').replace('b', '000000000')
                try:
                    return float(number_str)
                except ValueError:
                    pass

        elif isinstance(answer.value, (int, float)):
            return float(answer.value)

        return None

    def _extract_numeric_value(self, answers: List[Answer], question_id: str) -> Optional[int]:
        """Extract numeric value from answer."""
        answer = next((a for a in answers if a.question_id == question_id), None)
        if not answer:
            return None

        if isinstance(answer.value, str):
            # Extract numbers from string
            numbers = re.findall(r'\d+', answer.value)
            if numbers:
                try:
                    return int(numbers[0])
                except ValueError:
                    pass

        elif isinstance(answer.value, (int, float)):
            return int(answer.value)

        return None

    def _extract_percentage_value(self, answers: List[Answer], question_id: str) -> Optional[float]:
        """Extract percentage value from answer."""
        answer = next((a for a in answers if a.question_id == question_id), None)
        if not answer:
            return None

        if isinstance(answer.value, str):
            # Extract percentages from string
            percentages = re.findall(r'(\d+\.?\d+)%', answer.value)
            if percentages:
                try:
                    return float(percentages[0])
                except ValueError:
                    pass

        elif isinstance(answer.value, (int, float)):
            return float(answer.value)

        return None

    def _extract_list_value(self, answers: List[Answer], question_id: str) -> List[str]:
        """Extract list value from answer."""
        answer = next((a for a in answers if a.question_id == question_id), None)
        if not answer:
            return []

        if isinstance(answer.value, list):
            return answer.value

        return [str(answer.value)]

    def _calculate_overall_score(self, validations: List[ValidationResult]) -> float:
        """Calculate overall validation score."""
        if not validations:
            return 100.0

        # Calculate weighted scores
        category_scores = {}

        for validation in validations:
            if validation.category not in category_scores:
                category_scores[validation.category] = {"total": 0, "count": 0}

            # Apply severity penalty
            severity_penalty = {
                ValidationSeverity.INFO: 0,
                ValidationSeverity.WARNING: 0.2,
                ValidationSeverity.ERROR: 0.5,
                ValidationSeverity.CRITICAL: 1.0
            }

            score = 100 - (severity_penalty[validation.severity] * 100)
            category_scores[validation.category]["total"] += score
            category_scores[validation.category]["count"] += 1

        # Calculate weighted average
        total_score = 0
        total_weight = 0

        for category, scores in category_scores.items():
            if category in self.scoring_weights:
                average_score = scores["total"] / scores["count"]
                weight = self.scoring_weights[category]["weight"]
                total_score += average_score * weight
                total_weight += weight

        return (total_score / total_weight) if total_weight > 0 else 0

    def _calculate_grade(self, score: float) -> str:
        """Calculate grade based on score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        else:
            return "F"

    def _generate_insights(self, validations: List[ValidationResult]) -> Dict[str, Any]:
        """Generate insights from validation results."""
        insights = {
            "critical_issues": len([v for v in validations if v.severity == ValidationSeverity.CRITICAL]),
            "errors": len([v for v in validations if v.severity == ValidationSeverity.ERROR]),
            "warnings": len([v for v in validations if v.severity == ValidationSeverity.WARNING]),
            "total_validations": len(validations),
            "auto_fixable": len([v for v in validations if v.auto_fixable]),
            "category_breakdown": {},
            "severity_breakdown": {}
        }

        # Category breakdown
        for validation in validations:
            category = validation.category.value
            if category not in insights["category_breakdown"]:
                insights["category_breakdown"][category] = {"count": 0, "severity": {}}

            insights["category_breakdown"][category]["count"] += 1
            severity = validation.severity.value
            if severity not in insights["category_breakdown"][category]["severity"]:
                insights["category_breakdown"][category]["severity"][severity] = 0
            insights["category_breakdown"][category]["severity"][severity] += 1

        # Severity breakdown
        for validation in validations:
            severity = validation.severity.value
            if severity not in insights["severity_breakdown"]:
                insights["severity_breakdown"][severity] = {"count": 0, "categories": {}}

            insights["severity_breakdown"][severity]["count"] += 1
            category = validation.category.value
            if category not in insights["severity_breakdown"][severity]["categories"]:
                insights["severity_breakdown"][severity]["categories"][category] = 0
            insights["severity_breakdown"][severity]["categories"][category] += 1

        return insights

    def _generate_recommendations(self, validations: List[ValidationResult], context: UserContext) -> List[str]:
        """Generate recommendations from validation results."""
        recommendations = []

        # Prioritize critical and error-level validations
        priority_validations = [v for v in validations if v.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]

        for validation in priority_validations:
            recommendations.extend(validation.suggestions)

        # Add general recommendations based on patterns
        if not priority_validations:
            recommendations.append("Your business plan is looking good! Consider having a colleague review it for additional perspectives.")
        else:
            recommendations.append("Address the critical issues above before finalizing your business plan.")

        # Add industry-specific recommendations
        if context.industry.value == "saas":
            recommendations.append("Consider creating a detailed unit economics dashboard to track your SaaS metrics.")
        elif context.industry.value == "infrastructure":
            recommendations.append("Develop a detailed regulatory roadmap and compliance timeline.")
        elif context.industry.value == "agritech":
            recommendations.append("Create a pilot program with a small group of farmers to validate your solution.")

        return list(set(recommendations))  # Remove duplicates

    def _benchmark_comparison(self, context: UserContext, answers: List[Answer]) -> Dict[str, Any]:
        """Compare against industry benchmarks."""
        comparison = {"industry": context.industry.value}

        if context.industry.value in self.benchmarks:
            benchmarks = self.benchmarks[context.industry.value]["benchmarks"]
            comparison["benchmarks"] = {}

            # Compare SaaS metrics
            if context.industry.value == "saas":
                ltv_cac = self._extract_numeric_value(answers, "ltv_cac_ratio")
                if ltv_cac:
                    if ltv_cac >= benchmarks["ltv_cac_ratio"]["excellent"]:
                        comparison["benchmarks"]["ltv_cac_ratio"] = "excellent"
                    elif ltv_cac >= benchmarks["ltv_cac_ratio"]["good"]:
                        comparison["benchmarks"]["ltv_cac_ratio"] = "good"
                    elif ltv_cac >= benchmarks["ltv_cac_ratio"]["min"]:
                        comparison["benchmarks"]["ltv_cac_ratio"] = "minimum"
                    else:
                        comparison["benchmarks"]["ltv_cac_ratio"] = "below_minimum"

                churn = self._extract_percentage_value(answers, "churn_rate")
                if churn:
                    if churn <= benchmarks["churn_rate"]["excellent"]:
                        comparison["benchmarks"]["churn_rate"] = "excellent"
                    elif churn <= benchmarks["churn_rate"]["good"]:
                        comparison["benchmarks"]["churn_rate"] = "good"
                    elif churn <= benchmarks["churn_rate"]["max"]:
                        comparison["benchmarks"]["churn_rate"] = "acceptable"
                    else:
                        comparison["benchmarks"]["churn_rate"] = "too_high"

        return comparison

def main():
    """Test the validation engine."""
    validator = ValidationEngine()

    # Create test context and answers
    context = UserContext(
        industry=Industry.SAAS,
        stage=BusinessStage.SEED,
        geography="US",
        funding_amount=1000000
    )

    # Create sample answers
    answers = [
        Answer("company_name", "TechStart AI", 1.0),
        Answer("primary_problem", "Companies struggle with AI implementation", 1.0),
        Answer("current_mrr", "50000", 1.0),
        Answer("churn_rate", "2.5", 1.0),
        Answer("ltv_cac_ratio", "4.5", 1.0),
        Answer("tam_size", "$10 billion", 1.0),
        Answer("revenue_model", "Subscription", 1.0),
        Answer("funding_needed", "2500000", 1.0),
        Answer("team_size", "12", 1.0)
    ]

    # Run validation
    analysis = validator.validate_answers(context, answers)

    print(f"Document Analysis Results:")
    print(f"Overall Score: {analysis.overall_score}")
    print(f"Grade: {analysis.grade}")
    print(f"Total Validations: {len(analysis.validations)}")
    print(f"Insights: {analysis.insights}")

    print(f"\nRecommendations:")
    for i, recommendation in enumerate(analysis.recommendations[:5], 1):
        print(f"{i}. {recommendation}")

if __name__ == "__main__":
    main()