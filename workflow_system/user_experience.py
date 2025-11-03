#!/usr/bin/env python3
"""
Dual-Sided User Experience Framework

This module implements the dual-sided user experience with separate dashboards
and workflows for entrepreneurs and investors.

Author: Innov8 Workflow Team
Version: 1.0
Date: November 2025
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from question_engine import UserContext, Question, Answer, QuestionEngine, Industry

class UserType(Enum):
    ENTREPRENEUR = "entrepreneur"
    INVESTOR = "investor"

class WorkflowStage(Enum):
    ONBOARDING = "onboarding"
    PLANNING = "planning"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    PRESENTATION = "presentation"

@dataclass
class UserSession:
    session_id: str
    user_id: str
    user_type: UserType
    current_stage: WorkflowStage
    context: UserContext
    answers: List[Answer]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

class DashboardManager:
    """Manages dual-sided dashboards for entrepreneurs and investors."""

    def __init__(self):
        self.question_engine = QuestionEngine()
        self.sessions = {}  # session_id -> UserSession
        self.dashboard_config = self._load_dashboard_config()

    def _load_dashboard_config(self) -> Dict[str, Any]:
        """Load dashboard configuration."""
        return {
            "entrepreneur": {
                "welcome_message": "Welcome to your business planning workspace! Let's create a comprehensive business plan together.",
                "sections": {
                    "overview": {
                        "title": "Project Overview",
                        "widgets": ["progress_tracker", "quick_actions", "milestone_timeline"]
                    },
                    "questionnaire": {
                        "title": "Business Planning Questions",
                        "widgets": ["adaptive_questions", "help_resources", "saved_progress"]
                    },
                    "documents": {
                        "title": "Your Documents",
                        "widgets": ["template_library", "generated_docs", "collaboration_tools"]
                    },
                    "analytics": {
                        "title": "Insights & Analytics",
                        "widgets": ["completion_score", "quality_metrics", "recommendations"]
                    }
                },
                "navigation": ["overview", "questionnaire", "documents", "analytics"]
            },
            "investor": {
                "welcome_message": "Welcome to your investment evaluation dashboard. Track and analyze investment opportunities efficiently.",
                "sections": {
                    "pipeline": {
                        "title": "Investment Pipeline",
                        "widgets": ["deal_flow", "stage_filter", "quick_stats"]
                    },
                    "evaluation": {
                        "title": "Deal Evaluation",
                        "widgets": ["deal_scoring", "due_diligence_tracker", "risk_assessment"]
                    },
                    "portfolio": {
                        "title": "Portfolio Management",
                        "widgets": ["portfolio_overview", "performance_metrics", "sector_analysis"]
                    },
                    "analytics": {
                        "title": "Analytics & Insights",
                        "widgets": ["market_trends", "investment_thesis_fit", "benchmarking"]
                    }
                },
                "navigation": ["pipeline", "evaluation", "portfolio", "analytics"]
            }
        }

    def create_session(self, user_id: str, user_type: UserType, context: UserContext) -> str:
        """Create a new user session."""
        session_id = f"{user_id}_{user_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            user_type=user_type,
            current_stage=WorkflowStage.ONBOARDING,
            context=context,
            answers=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={}
        )

        self.sessions[session_id] = session
        return session_id

    def get_dashboard_data(self, session_id: str) -> Dict[str, Any]:
        """Get dashboard data for a specific session."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        config = self.dashboard_config[session.user_type.value]

        if session.user_type == UserType.ENTREPRENEUR:
            return self._get_entrepreneur_dashboard(session, config)
        else:
            return self._get_investor_dashboard(session, config)

    def _get_entrepreneur_dashboard(self, session: UserSession, config: Dict) -> Dict[str, Any]:
        """Get entrepreneur dashboard data."""
        # Calculate progress metrics
        questions = self.question_engine.generate_question_path(session.context)
        answered_count = len(session.answers)
        total_questions = len(questions)
        completion_score = self.question_engine.calculate_completion_score(session.context, session.answers)

        # Get insights
        insights = self.question_engine.generate_insights(session.context, session.answers)

        # Generate next question
        next_question = self.question_engine.get_next_question(session.context, session.answers)

        # Determine stage based on completion
        if completion_score == 0:
            current_stage = WorkflowStage.ONBOARDING
        elif completion_score < 50:
            current_stage = WorkflowStage.PLANNING
        elif completion_score < 90:
            current_stage = WorkflowStage.DOCUMENTATION
        else:
            current_stage = WorkflowStage.VALIDATION

        return {
            "session_info": {
                "session_id": session.session_id,
                "user_type": session.user_type.value,
                "context": session.context.__dict__,
                "current_stage": current_stage.value
            },
            "welcome_message": config["welcome_message"],
            "progress": {
                "total_questions": total_questions,
                "answered_questions": answered_count,
                "completion_score": round(completion_score, 1),
                "next_question": {
                    "id": next_question.id if next_question else None,
                    "text": next_question.text if next_question else "All questions completed!",
                    "type": next_question.type.value if next_question else None,
                    "options": next_question.options if next_question else None,
                    "help_text": next_question.help_text if next_question else None
                }
            },
            "insights": insights,
            "navigation": config["navigation"],
            "sections": self._get_entrepreneur_sections(session, config)
        }

    def _get_entrepreneur_sections(self, session: UserSession, config: Dict) -> Dict[str, Any]:
        """Get entrepreneur-specific sections."""
        sections = {}

        for section_key, section_config in config["sections"].items():
            sections[section_key] = {
                "title": section_config["title"],
                "widgets": self._get_entrepreneur_widgets(section_key, session)
            }

        return sections

    def _get_entrepreneur_widgets(self, section: str, session: UserSession) -> Dict[str, Any]:
        """Get entrepreneur-specific widgets."""
        widgets = {}

        if section == "overview":
            questions = self.question_engine.generate_question_path(session.context)
            answered_count = len(session.answers)
            total_questions = len(questions)

            widgets["progress_tracker"] = {
                "type": "progress",
                "data": {
                    "completed": answered_count,
                    "total": total_questions,
                    "percentage": round((answered_count / total_questions) * 100, 1) if total_questions > 0 else 0
                }
            }

            widgets["quick_actions"] = {
                "type": "actions",
                "data": {
                    "actions": [
                        {"id": "continue_questions", "text": "Continue Questions", "primary": True},
                        {"id": "save_progress", "text": "Save Progress", "primary": False},
                        {"id": "invite_team", "text": "Invite Team", "primary": False}
                    ]
                }
            }

            widgets["milestone_timeline"] = {
                "type": "timeline",
                "data": {
                    "milestones": [
                        {"title": "Started Planning", "date": session.created_at.strftime("%Y-%m-%d"), "status": "completed"},
                        {"title": "Complete Questions", "date": None, "status": "pending"},
                        {"title": "Generate Documents", "date": None, "status": "pending"},
                        {"title": "Review & Finalize", "date": None, "status": "pending"}
                    ]
                }
            }

        elif section == "questionnaire":
            next_question = self.question_engine.get_next_question(session.context, session.answers)

            widgets["adaptive_questions"] = {
                "type": "questions",
                "data": {
                    "current_question": {
                        "id": next_question.id if next_question else None,
                        "text": next_question.text if next_question else "All questions completed!",
                        "type": next_question.type.value if next_question else None,
                        "options": next_question.options if next_question else None,
                        "required": next_question.required if next_question else False,
                        "help_text": next_question.help_text if next_question else None
                    } if next_question else None
                }
            }

            widgets["help_resources"] = {
                "type": "resources",
                "data": {
                    "resources": [
                        {"title": "Business Plan Guide", "url": "/guides/business-plan"},
                        {"title": "Market Research Tips", "url": "/guides/market-research"},
                        {"title": "Financial Modeling", "url": "/guides/financial-modeling"},
                        {"title": "FAQ", "url": "/faq"}
                    ]
                }
            }

            widgets["saved_progress"] = {
                "type": "progress_summary",
                "data": {
                    "completion_score": round(self.question_engine.calculate_completion_score(session.context, session.answers), 1),
                    "critical_answers": self._get_critical_answers(session),
                    "missing_critical": self._get_missing_critical_answers(session)
                }
            }

        elif section == "documents":
            widgets["template_library"] = {
                "type": "templates",
                "data": {
                    "available_templates": self._get_recommended_templates(session),
                    "generated_docs": self._get_generated_documents(session)
                }
            }

            widgets["generated_docs"] = {
                "type": "documents",
                "data": {
                    "documents": self._get_generated_documents(session)
                }
            }

            widgets["collaboration_tools"] = {
                "type": "collaboration",
                "data": {
                    "team_members": self._get_team_members(session),
                    "shared_documents": self._get_shared_documents(session),
                    "comments": self._get_document_comments(session)
                }
            }

        elif section == "analytics":
            insights = self.question_engine.generate_insights(session.context, session.answers)

            widgets["completion_score"] = {
                "type": "score",
                "data": {
                    "score": insights["completion_score"],
                    "grade": self._get_completion_grade(insights["completion_score"]),
                    "recommendations": insights.get("recommendations", [])
                }
            }

            widgets["quality_metrics"] = {
                "type": "metrics",
                "data": {
                    "metrics": {
                        "completeness": insights["completion_score"],
                        "detail_level": self._calculate_detail_level(session),
                        "consistency": self._calculate_consistency_score(session),
                        "industry_fit": self._calculate_industry_fit_score(session)
                    }
                }
            }

            widgets["recommendations"] = {
                "type": "recommendations",
                "data": {
                    "recommendations": insights.get("recommendations", []),
                    "strengths": insights.get("strengths", []),
                    "concerns": insights.get("concerns", []),
                    "next_steps": self._get_recommended_next_steps(session)
                }
            }

        return widgets

    def _get_investor_dashboard(self, session: UserSession, config: Dict) -> Dict[str, Any]:
        """Get investor dashboard data."""
        # Mock data for now - in a real implementation, this would come from investor database
        mock_deals = [
            {
                "id": "deal_001",
                "company_name": "TechStart AI",
                "industry": "SAAS",
                "stage": "Series A",
                "asking_price": 10000000,
                "status": "under_review",
                "last_updated": "2025-11-01",
                "completion_score": 85.5
            },
            {
                "id": "deal_002",
                "company_name": "FiberConnect",
                "industry": "Infrastructure",
                "stage": "Seed",
                "asking_price": 2000000,
                "status": "pending_review",
                "last_updated": "2025-10-30",
                "completion_score": 72.3
            }
        ]

        return {
            "session_info": {
                "session_id": session.session_id,
                "user_type": session.user_type.value,
                "current_stage": session.current_stage.value
            },
            "welcome_message": config["welcome_message"],
            "pipeline_data": {
                "total_deals": len(mock_deals),
                "deals_by_stage": {"Seed": 1, "Series A": 1},
                "total_value": sum(deal["asking_price"] for deal in mock_deals),
                "recent_updates": [deal for deal in mock_deals if deal["status"] == "under_review"]
            },
            "navigation": config["navigation"],
            "sections": self._get_investor_sections(mock_deals, config)
        }

    def _get_investor_sections(self, deals: List[Dict], config: Dict) -> Dict[str, Any]:
        """Get investor-specific sections."""
        sections = {}

        for section_key, section_config in config["sections"].items():
            sections[section_key] = {
                "title": section_config["title"],
                "widgets": self._get_investor_widgets(section_key, deals)
            }

        return sections

    def _get_investor_widgets(self, section: str, deals: List[Dict]) -> Dict[str, Any]:
        """Get investor-specific widgets."""
        widgets = {}

        if section == "pipeline":
            widgets["deal_flow"] = {
                "type": "pipeline",
                "data": {
                    "stages": ["Screening", "Due Diligence", "Investment Committee", "Closed"],
                    "deals": deals
                }
            }

            widgets["stage_filter"] = {
                "type": "filter",
                "data": {
                    "filters": [
                        {"id": "industry", "label": "Industry", "options": ["SAAS", "Infrastructure", "AgriTech", "All"]},
                        {"id": "stage", "label": "Stage", "options": ["Seed", "Series A", "Series B", "All"]},
                        {"id": "status", "label": "Status", "options": ["Under Review", "Pending", "Rejected", "All"]}
                    ]
                }
            }

            widgets["quick_stats"] = {
                "type": "stats",
                "data": {
                    "total_deals": len(deals),
                    "avg_completion": round(sum(deal["completion_score"] for deal in deals) / len(deals), 1),
                    "total_value": sum(deal["asking_price"] for deal in deals),
                    "hot_deals": len([d for d in deals if d["completion_score"] > 80])
                }
            }

        elif section == "evaluation":
            # Mock evaluation data
            widgets["deal_scoring"] = {
                "type": "scoring",
                "data": {
                    "scoring_criteria": [
                        {"criterion": "Team", "weight": 30, "score": 85},
                        {"criterion": "Market", "weight": 25, "score": 90},
                        {"criterion": "Product", "weight": 25, "score": 80},
                        {"criterion": "Financials", "weight": 20, "score": 75}
                    ]
                }
            }

            widgets["due_diligence_tracker"] = {
                "type": "tracker",
                "data": {
                    "checklist_items": [
                        {"item": "Business Plan Review", "status": "completed", "assigned_to": "John Doe"},
                        {"item": "Financial Model Validation", "status": "in_progress", "assigned_to": "Jane Smith"},
                        {"item": "Team Background Check", "status": "pending", "assigned_to": "Mike Johnson"},
                        {"item": "Market Research", "status": "completed", "assigned_to": "Sarah Wilson"}
                    ]
                }
            }

            widgets["risk_assessment"] = {
                "type": "risk_analysis",
                "data": {
                    "risks": [
                        {"category": "Market Risk", "level": "Medium", "description": "Competition in SaaS space"},
                        {"category": "Team Risk", "level": "Low", "description": "Strong founding team"},
                        {"category": "Technology Risk", "level": "Low", "description": "Proprietary technology"},
                        {"category": "Financial Risk", "level": "High", "description": "High burn rate"}
                    ]
                }
            }

        return widgets

    def submit_answer(self, session_id: str, question_id: str, answer: Any) -> Dict[str, Any]:
        """Submit an answer to a question."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        # Get the question
        questions = self.question_engine.generate_question_path(session.context)
        question = next((q for q in questions if q.id == question_id), None)

        if not question:
            return {"error": "Question not found"}

        # Validate the answer
        is_valid, error_message = self.question_engine.validate_answer(question, answer)
        if not is_valid:
            return {"error": error_message}

        # Update or add answer
        existing_answer = next((a for a in session.answers if a.question_id == question_id), None)
        if existing_answer:
            existing_answer.value = answer
            existing_answer.confidence = 1.0
            existing_answer.timestamp = datetime.now().isoformat()
        else:
            new_answer = Answer(
                question_id=question_id,
                value=answer,
                confidence=1.0,
                source="user_input",
                timestamp=datetime.now().isoformat()
            )
            session.answers.append(new_answer)

        # Update session
        session.updated_at = datetime.now()

        # Get next question
        next_question = self.question_engine.get_next_question(session.context, session.answers)

        # Calculate completion
        completion_score = self.question_engine.calculate_completion_score(session.context, session.answers)

        return {
            "success": True,
            "next_question": {
                "id": next_question.id if next_question else None,
                "text": next_question.text if next_question else "All questions completed!",
                "type": next_question.type.value if next_question else None,
                "options": next_question.options if next_question else None,
                "help_text": next_question.help_text if next_question else None
            },
            "completion_score": round(completion_score, 1),
            "insights": self.question_engine.generate_insights(session.context, session.answers)
        }

    def save_session(self, session_id: str) -> Dict[str, Any]:
        """Save session data."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        # Export session data
        session_data = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "user_type": session.user_type.value,
            "context": session.context.__dict__,
            "answers": [answer.__dict__ for answer in session.answers],
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "metadata": session.metadata,
            "export_data": self.question_engine.export_session_data(session.context, session.answers)
        }

        # In a real implementation, this would save to a database
        # For now, return the data for testing
        return {"success": True, "session_data": session_data}

    def _get_recommended_templates(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get recommended templates for the user."""
        templates = []

        # Base templates
        templates.extend([
            {"id": "business_plan", "name": "Business Plan", "type": "comprehensive"},
            {"id": "financial_model", "name": "Financial Model", "type": "financial"},
            {"id": "pitch_deck", "name": "Pitch Deck", "type": "presentation"}
        ])

        # Industry-specific templates
        if session.context.industry.value == "saas":
            templates.append({"id": "saas_metrics", "name": "SaaS Metrics Dashboard", "type": "analytics"})
        elif session.context.industry.value == "infrastructure":
            templates.append({"id": "infrastructure_plan", "name": "Infrastructure Plan", "type": "technical"})
        elif session.context.industry.value == "agritech":
            templates.append({"id": "agricultural_plan", "name": "Agricultural Business Plan", "type": "industry"})

        return templates

    def _get_generated_documents(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get generated documents."""
        documents = []

        # Check if user has enough answers to generate documents
        completion_score = self.question_engine.calculate_completion_score(session.context, session.answers)

        if completion_score > 50:
            documents.append({
                "id": "business_plan_draft",
                "name": "Business Plan Draft",
                "type": "draft",
                "generated_at": session.updated_at.isoformat(),
                "download_url": f"/download/{session.session_id}/business_plan_draft"
            })

        if completion_score > 80:
            documents.append({
                "id": "business_plan_final",
                "name": "Final Business Plan",
                "type": "final",
                "generated_at": session.updated_at.isoformat(),
                "download_url": f"/download/{session.session_id}/business_plan_final"
            })

        return documents

    def _get_team_members(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get team members (mock data)."""
        return [
            {"id": "user_001", "name": "John Doe", "email": "john@example.com", "role": "Founder", "status": "active"},
            {"id": "user_002", "name": "Jane Smith", "email": "jane@example.com", "role": "CTO", "status": "active"}
        ]

    def _get_shared_documents(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get shared documents (mock data)."""
        return [
            {"id": "doc_001", "name": "Business Plan Draft", "shared_by": "John Doe", "shared_at": "2025-11-01", "status": "shared"},
            {"id": "doc_002", "name": "Financial Model", "shared_by": "Jane Smith", "shared_at": "2025-10-30", "status": "under_review"}
        ]

    def _get_document_comments(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get document comments (mock data)."""
        return [
            {"id": "comment_001", "document_id": "doc_001", "author": "Jane Smith", "comment": "Great market analysis!", "timestamp": "2025-11-01T10:30:00"},
            {"id": "comment_002", "document_id": "doc_001", "author": "John Doe", "comment": "Need more detail on revenue model.", "timestamp": "2025-11-01T14:15:00"}
        ]

    def _get_critical_answers(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get critical answers that have high weight."""
        questions = self.question_engine.generate_question_path(session.context)
        critical_questions = [q for q in questions if q.weight >= 2.0]

        critical_answers = []
        for question in critical_questions:
            answer = next((a for a in session.answers if a.question_id == question.id), None)
            if answer:
                critical_answers.append({
                    "question": question.text,
                    "answer": answer.value,
                    "weight": question.weight
                })

        return critical_answers

    def _get_missing_critical_answers(self, session: UserSession) -> List[Dict[str, Any]]:
        """Get missing critical answers."""
        questions = self.question_engine.generate_question_path(session.context)
        critical_questions = [q for q in questions if q.weight >= 2.0]
        answered_ids = {answer.question_id for answer in session.answers}

        missing_critical = []
        for question in critical_questions:
            if question.id not in answered_ids:
                missing_critical.append({
                    "question": question.text,
                    "weight": question.weight,
                    "required": question.required
                })

        return missing_critical

    def _get_completion_grade(self, score: float) -> str:
        """Get completion grade based on score."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        else:
            return "C"

    def _calculate_detail_level(self, session: UserSession) -> float:
        """Calculate detail level score."""
        # Analyze answer depth and completeness
        total_score = 0
        max_score = 0

        for answer in session.answers:
            if isinstance(answer.value, str):
                length_score = min(len(answer.value) / 100, 1.0)  # Normalize to 0-1
                total_score += length_score
            max_score += 1.0

        return (total_score / max_score * 100) if max_score > 0 else 0

    def _calculate_consistency_score(self, session: UserSession) -> float:
        """Calculate consistency score across answers."""
        # This is a simplified version - in practice, would use more sophisticated logic
        base_score = 85.0  # Base score for having answered questions

        # Penalize for obvious inconsistencies
        consistency_deductions = 0

        # Check for common inconsistencies
        revenue_answer = next((a for a in session.answers if a.question_id == "current_revenue"), None)
        funding_answer = next((a for a in session.answers if a.question_id == "funding_needed"), None)

        if revenue_answer and funding_answer:
            try:
                revenue = float(revenue_answer.value)
                funding = float(funding_answer.value)
                if funding > revenue * 5:  # Funding more than 5x revenue
                    consistency_deductions += 10
            except:
                pass

        return max(0, base_score - consistency_deductions)

    def _calculate_industry_fit_score(self, session: UserSession) -> float:
        """Calculate industry fit score."""
        # This is a simplified version - would use industry-specific validation
        base_score = 90.0

        # Check if industry-specific questions are answered
        industry_specific_questions = self.question_engine.get_industry_specific_questions(session.context.industry)
        answered_industry = 0

        for question in industry_specific_questions:
            if next((a for a in session.answers if a.question_id == question.id), None):
                answered_industry += 1

        if industry_specific_questions:
            industry_fit = (answered_industry / len(industry_specific_questions)) * 100
            return base_score * (industry_fit / 100)

        return base_score

    def _get_recommended_next_steps(self, session: UserSession) -> List[str]:
        """Get recommended next steps for the user."""
        steps = []
        completion_score = self.question_engine.calculate_completion_score(session.context, session.answers)
        insights = self.question_engine.generate_insights(session.context, session.answers)

        if completion_score < 25:
            steps.append("Complete basic business overview questions")
            steps.append("Define your target market and customer segments")
        elif completion_score < 50:
            steps.append("Detail your product or service offerings")
            steps.append("Outline your business model and revenue streams")
        elif completion_score < 75:
            steps.append("Develop comprehensive financial projections")
            steps.append("Create team plan and organizational structure")
        elif completion_score < 90:
            steps.append("Review and refine your business plan")
            steps.append("Prepare for investor presentations")
        else:
            steps.append("Your business plan is complete and ready for investors!")
            steps.append("Consider creating additional supporting documents")

        # Add specific recommendations based on insights
        if insights.get("concerns"):
            steps.append("Address the identified concerns in your plan")

        if insights.get("missing_critical"):
            steps.append("Complete the critical missing sections")

        return steps

    def get_industry_specific_questions(self, industry: Industry) -> List[Question]:
        """Get industry-specific questions."""
        return [q for q in self.questions_db.values() if q.industry_specific and industry in q.industry_specific]

def main():
    """Test the user experience framework."""
    dashboard = DashboardManager()

    # Test entrepreneur session
    entrepreneur_context = UserContext(
        industry=Industry.SAAS,
        stage=BusinessStage.SEED,
        geography="US",
        funding_amount=1000000
    )

    entrepreneur_session_id = dashboard.create_session("user_001", UserType.ENTREPRENEUR, entrepreneur_context)
    print(f"Created entrepreneur session: {entrepreneur_session_id}")

    # Get entrepreneur dashboard
    entrepreneur_dashboard = dashboard.get_dashboard_data(entrepreneur_session_id)
    print(f"Entrepreneur dashboard loaded with {len(entrepreneur_dashboard)} sections")

    # Test investor session
    investor_context = UserContext(
        industry=Industry.SAAS,
        stage=BusinessStage.SERIES_A,
        geography="US",
        funding_amount=10000000
    )

    investor_session_id = dashboard.create_session("investor_001", UserType.INVESTOR, investor_context)
    print(f"Created investor session: {investor_session_id}")

    # Get investor dashboard
    investor_dashboard = dashboard.get_dashboard_data(investor_session_id)
    print(f"Investor dashboard loaded with {len(investor_dashboard)} sections")

    # Test answer submission
    result = dashboard.submit_answer(entrepreneur_session_id, "company_name", "TechStart AI")
    print(f"Answer submission result: {result}")

if __name__ == "__main__":
    main()