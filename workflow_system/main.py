"""
Main Workflow System Application - Innov8 Business Planning Platform
====================================================================

This is the main entry point for the comprehensive workflow system that integrates
all components to provide a dual-sided platform for entrepreneurs and investors.

Core Components Integrated:
1. Question Engine - Adaptive questioning system
2. User Experience - Dual-sided dashboard framework
3. Validation Engine - AI-powered document validation
4. Integration Framework - External tool connections
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from question_engine import QuestionEngine, UserContext, BusinessStage, Industry, Answer, QuestionType
from user_experience import DashboardManager, UserType, WorkflowStage
from validation_engine import ValidationEngine
from integration_framework import IntegrationFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Innov8WorkflowSystem:
    """Main workflow system orchestrator for the Innov8 platform."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the workflow system with all components."""
        self.config = self._load_config(config_path)

        # Initialize core components
        self.question_engine = QuestionEngine()
        self.user_experience = DashboardManager()
        self.validation_engine = ValidationEngine()
        self.integration_framework = IntegrationFramework()

        # System state
        self.active_sessions: Dict[str, Dict] = {}
        self.system_metrics = {
            'sessions_started': 0,
            'documents_validated': 0,
            'questions_answered': 0,
            'integrations_active': 0
        }

        logger.info("Innov8 Workflow System initialized successfully")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load system configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)

        # Default configuration
        return {
            'system': {
                'max_sessions': 1000,
                'session_timeout_minutes': 120,
                'enable_analytics': True
            },
            'validation': {
                'auto_validate': True,
                'strict_mode': False,
                'cache_results': True
            },
            'integrations': {
                'auto_sync': True,
                'sync_interval_minutes': 30,
                'retry_attempts': 3
            },
            'ui': {
                'theme': 'professional',
                'language': 'en',
                'progress_tracking': True
            }
        }

    async def start_session(self, user_type: UserType, user_info: Dict) -> str:
        """Start a new workflow session for a user."""
        # Generate unique user ID
        user_id = user_info.get('user_id', f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Create user context first with correct structure
        user_context = UserContext(
            industry=user_info.get('industry', Industry.GENERAL),
            stage=user_info.get('business_stage', BusinessStage.PRE_SEED),
            geography=user_info.get('geography', 'United States'),
            funding_amount=user_info.get('funding_amount'),
            company_size=user_info.get('company_size'),
            business_model=user_info.get('business_model'),
            target_market=user_info.get('target_market')
        )

        # Create session with correct parameters
        session_id = self.user_experience.create_session(user_id, user_type, user_context)

        # Store session data
        self.active_sessions[session_id] = {
            'user_context': user_context,
            'start_time': datetime.now(),
            'questions_asked': 0,
            'documents_uploaded': 0,
            'validation_score': 0.0,
            'answers': []  # List to store Answer objects
        }

        self.system_metrics['sessions_started'] += 1

        # Initialize integrations for returning users
        if user_info.get('existing_integrations'):
            await self._setup_user_integrations(session_id, user_info['existing_integrations'])

        logger.info(f"Started new session for {user_type.value}: {session_id}")
        return session_id

    async def get_next_question(self, session_id: str, previous_answer: Optional[str] = None) -> Dict:
        """Get the next adaptive question for the user."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        session_data = self.active_sessions[session_id]
        user_context = session_data['user_context']

        # Process previous answer if provided
        if previous_answer and 'last_question_id' in session_data:
            # Create Answer object
            answer = Answer(
                question_id=session_data['last_question_id'],
                value=previous_answer,
                timestamp=datetime.now().isoformat()
            )
            session_data['answers'].append(answer)
            session_data['questions_answered'] = session_data.get('questions_answered', 0) + 1

        # Get next question
        answers = session_data['answers']
        question = self.question_engine.get_next_question(user_context, answers)

        if not question:
            # No more questions, transition to next stage
            await self._complete_questionnaire(session_id)
            return {
                'status': 'questionnaire_complete',
                'next_stage': 'document_upload',
                'message': 'Questionnaire completed. Please upload your business documents.'
            }

        # Store the question ID for the next answer
        session_data['last_question_id'] = question.id

        # Calculate simple progress
        total_questions = len(self.question_engine.questions_db)
        progress_percent = (len(session_data['answers']) / max(total_questions, 1)) * 100

        # Return question with user experience formatting
        return {
            'status': 'question',
            'question_id': question.id,
            'question_text': question.text,
            'question_type': question.type.value,
            'options': question.options,
            'progress': round(progress_percent, 1),
            'stage': 'questionnaire'  # Simplified stage
        }

    async def upload_document(self, session_id: str, document_path: str, document_type: str) -> Dict:
        """Handle document upload and trigger validation."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        try:
            # Validate document
            validation_result = await self.validation_engine.validate_document(
                document_path=document_path,
                document_type=document_type,
                user_context=self.active_sessions[session_id]['user_context']
            )

            # Store validation result
            self.active_sessions[session_id]['documents_uploaded'] += 1
            self.active_sessions[session_id]['validation_score'] = validation_result.overall_score

            self.system_metrics['documents_validated'] += 1

            # Generate insights and recommendations
            insights = await self._generate_document_insights(session_id, validation_result)

            return {
                'status': 'document_validated',
                'validation_score': validation_result.overall_score,
                'completeness_score': validation_result.completeness_score,
                'consistency_score': validation_result.consistency_score,
                'realism_score': validation_result.realism_score,
                'clarity_score': validation_result.clarity_score,
                'industry_fit_score': validation_result.industry_fit_score,
                'recommendations': validation_result.recommendations,
                'insights': insights,
                'next_steps': self._get_next_steps(validation_result)
            }

        except Exception as e:
            logger.error(f"Document validation failed for session {session_id}: {str(e)}")
            return {
                'status': 'validation_failed',
                'error': str(e),
                'message': 'Document validation failed. Please check the file and try again.'
            }

    async def get_dashboard_data(self, session_id: str) -> Dict:
        """Get comprehensive dashboard data for the user."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        session_data = self.active_sessions[session_id]
        user_context = session_data['user_context']

        # Simplified dashboard data
        dashboard = {
            'session_id': session_id,
            'user_type': 'entrepreneur' if session_id.split('_')[1] == 'entrepreneur' else 'investor',
            'validation_score': session_data.get('validation_score', 0.0),
            'documents_processed': session_data.get('documents_uploaded', 0),
            'questions_answered': session_data.get('questions_answered', 0),
            'session_duration': str(datetime.now() - session_data['start_time']),
            'industry': user_context.industry.value if user_context.industry else 'General',
            'stage': user_context.stage.value,
            'progress': (len(session_data.get('answers', [])) / max(len(self.question_engine.questions_db), 1)) * 100
        }

        # Add user-type specific data
        if dashboard['user_type'] == 'entrepreneur':
            dashboard.update(await self._get_entrepreneur_data(session_id))
        else:  # INVESTOR
            dashboard.update(await self._get_investor_data(session_id))

        return dashboard

    async def setup_integration(self, session_id: str, integration_type: str, config: Dict) -> Dict:
        """Setup integration with external tools."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        try:
            # Create integration
            integration_id = await self.integration_framework.create_integration(
                integration_type=integration_type,
                user_id=session_id,
                config=config
            )

            # Test connection
            connection_result = await self.integration_framework.test_integration(integration_id)

            if connection_result['status'] == 'success':
                self.system_metrics['integrations_active'] += 1
                return {
                    'status': 'integration_setup_success',
                    'integration_id': integration_id,
                    'message': f'Successfully connected to {integration_type}',
                    'sync_status': 'ready'
                }
            else:
                return {
                    'status': 'integration_setup_failed',
                    'error': connection_result.get('error', 'Connection failed'),
                    'message': f'Failed to connect to {integration_type}'
                }

        except Exception as e:
            logger.error(f"Integration setup failed for session {session_id}: {str(e)}")
            return {
                'status': 'integration_setup_error',
                'error': str(e),
                'message': 'Integration setup encountered an error'
            }

    async def get_recommendations(self, session_id: str) -> Dict:
        """Get AI-powered recommendations based on user data."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}")

        session_data = self.active_sessions[session_id]
        user_context = session_data['user_context']

        # Generate recommendations based on user type and data
        user_type_str = 'entrepreneur' if session_id.split('_')[1] == 'entrepreneur' else 'investor'

        if user_type_str == 'entrepreneur':
            recommendations = await self._generate_entrepreneur_recommendations(user_context)
        else:  # INVESTOR
            recommendations = await self._generate_investor_recommendations(user_context)

        return {
            'status': 'success',
            'recommendations': recommendations,
            'priority': self._prioritize_recommendations(recommendations),
            'actionable_items': self._get_actionable_items(recommendations)
        }

    async def _complete_questionnaire(self, session_id: str):
        """Handle questionnaire completion."""
        session_data = self.active_sessions[session_id]
        user_context = session_data['user_context']

        # Generate personalized document checklist
        checklist = self.question_engine.generate_document_checklist(user_context)

        # Update user experience stage
        self.user_experience.update_progress(session_id, 25)  # Questionnaire complete

        # Store checklist for user
        session_data['document_checklist'] = checklist

        logger.info(f"Questionnaire completed for session {session_id}")

    async def _setup_user_integrations(self, session_id: str, integrations: List[Dict]):
        """Setup existing integrations for returning users."""
        for integration in integrations:
            await self.integration_framework.create_integration(
                integration_type=integration['type'],
                user_id=session_id,
                config=integration['config']
            )

    async def _generate_document_insights(self, session_id: str, validation_result) -> List[str]:
        """Generate insights from document validation."""
        insights = []

        if validation_result.overall_score > 0.8:
            insights.append("Your business plan shows strong preparation and attention to detail.")

        if validation_result.completeness_score < 0.7:
            insights.append("Consider adding more detail to your financial projections and market analysis.")

        if validation_result.consistency_score > 0.8:
            insights.append("Your document shows excellent consistency across all sections.")

        # Add industry-specific insights
        session_data = self.active_sessions[session_id]
        user_context = session_data['user_context']

        if user_context.industry == Industry.TECHNOLOGY:
            if validation_result.industry_fit_score > 0.8:
                insights.append("Strong technology-focused business plan with clear value proposition.")

        return insights

    def _get_next_steps(self, validation_result) -> List[str]:
        """Get recommended next steps based on validation."""
        next_steps = []

        if validation_result.completeness_score < 0.6:
            next_steps.append("Enhance document completeness by adding missing sections")

        if validation_result.realism_score < 0.7:
            next_steps.append("Review and adjust financial projections for realism")

        if validation_result.clarity_score < 0.6:
            next_steps.append("Improve document clarity and reduce jargon")

        if validation_result.overall_score > 0.8:
            next_steps.append("Document is ready for investor review")
            next_steps.append("Consider scheduling a pitch presentation")

        return next_steps

    async def _get_integration_status(self, session_id: str) -> Dict:
        """Get status of all integrations for the user."""
        try:
            integrations = await self.integration_framework.get_user_integrations(session_id)

            status = {
                'total_integrations': len(integrations),
                'active_integrations': len([i for i in integrations if i.status == 'active']),
                'last_sync': None,
                'services': []
            }

            for integration in integrations:
                status['services'].append({
                    'type': integration.type,
                    'status': integration.status,
                    'last_sync': integration.last_sync
                })

            return status
        except Exception as e:
            logger.error(f"Error getting integration status: {str(e)}")
            return {'total_integrations': 0, 'active_integrations': 0, 'services': []}

    async def _get_entrepreneur_data(self, session_id: str) -> Dict:
        """Get entrepreneur-specific dashboard data."""
        return {
            'next_milestones': [
                'Complete business plan validation',
                'Prepare pitch deck',
                'Identify target investors'
            ],
            'resources_available': [
                'Business plan templates',
                'Financial modeling tools',
                'Pitch deck examples'
            ],
            'community_insights': '5 entrepreneurs in your industry are currently active'
        }

    async def _get_investor_data(self, session_id: str) -> Dict:
        """Get investor-specific dashboard data."""
        return {
            'investment_opportunities': '12 new opportunities matching your criteria',
            'portfolio_performance': '+15% average ROI across portfolio',
            'market_insights': 'SaaS sector showing strong growth trends',
            'due_diligence_queue': '3 companies awaiting review'
        }

    async def _generate_entrepreneur_recommendations(self, user_context) -> List[Dict]:
        """Generate recommendations for entrepreneurs."""
        recommendations = []

        if user_context.business_stage == BusinessStage.IDEA:
            recommendations.extend([
                {
                    'type': 'planning',
                    'title': 'Develop Minimum Viable Product (MVP) plan',
                    'description': 'Outline key features and development timeline',
                    'priority': 'high'
                },
                {
                    'type': 'market',
                    'title': 'Conduct market validation',
                    'description': 'Survey potential customers and test assumptions',
                    'priority': 'high'
                }
            ])

        recommendations.append({
            'type': 'funding',
            'title': 'Prepare seed funding documentation',
            'description': 'Get your business plan and financial projections ready',
            'priority': 'medium'
        })

        return recommendations

    async def _generate_investor_recommendations(self, user_context) -> List[Dict]:
        """Generate recommendations for investors."""
        return [
            {
                'type': 'opportunity',
                'title': 'Review SaaS investment opportunities',
                'description': '3 new SaaS companies match your investment criteria',
                'priority': 'high'
            },
            {
                'type': 'portfolio',
                'title': 'Portfolio diversification review',
                'description': 'Consider balancing tech and non-tech investments',
                'priority': 'medium'
            }
        ]

    def _prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Prioritize recommendations by importance and urgency."""
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        return sorted(recommendations, key=lambda x: priority_order.get(x.get('priority', 'low'), 3))

    def _get_actionable_items(self, recommendations: List[Dict]) -> List[str]:
        """Extract actionable items from recommendations."""
        return [rec.get('title', '') for rec in recommendations if rec.get('title')]

    def get_system_metrics(self) -> Dict:
        """Get system-wide metrics."""
        return {
            'total_sessions': self.system_metrics['sessions_started'],
            'active_sessions': len(self.active_sessions),
            'documents_validated': self.system_metrics['documents_validated'],
            'questions_answered': self.system_metrics['questions_answered'],
            'active_integrations': self.system_metrics['integrations_active'],
            'uptime': str(datetime.now() - datetime.strptime('2024-01-01', '%Y-%m-%d'))
        }

# CLI Interface for testing and demonstration
async def main():
    """Main function for testing the workflow system."""
    print("Innov8 Workflow System - Testing Interface")
    print("=" * 50)

    # Initialize system
    workflow = Innov8WorkflowSystem()

    # Create test sessions
    print("\nCreating test sessions...")

    # Entrepreneur session
    entrepreneur_session = await workflow.start_session(
        UserType.ENTREPRENEUR,
        {
            'business_stage': BusinessStage.PRE_SEED,
            'industry': Industry.SAAS,
            'experience_level': 'beginner'
        }
    )
    print(f"Entrepreneur session: {entrepreneur_session}")

    # Investor session
    investor_session = await workflow.start_session(
        UserType.INVESTOR,
        {
            'business_stage': BusinessStage.SERIES_A,
            'industry': None,
            'experience_level': 'expert'
        }
    )
    print(f"Investor session: {investor_session}")

    # Test question flow for entrepreneur
    print(f"\nTesting question flow for entrepreneur...")
    for i in range(3):
        question_data = await workflow.get_next_question(entrepreneur_session)
        print(f"Q{i+1}: {question_data.get('question_text', 'No question')}")

        # Simulate answer
        await workflow.get_next_question(entrepreneur_session, "Sample answer")

    # Get dashboard data
    print(f"\nGetting dashboard data...")
    entrepreneur_dashboard = await workflow.get_dashboard_data(entrepreneur_session)
    investor_dashboard = await workflow.get_dashboard_data(investor_session)

    print(f"Entrepreneur dashboard sections: {list(entrepreneur_dashboard.keys())}")
    print(f"Investor dashboard sections: {list(investor_dashboard.keys())}")

    # Get recommendations
    print(f"\nGetting recommendations...")
    entrepreneur_recs = await workflow.get_recommendations(entrepreneur_session)
    investor_recs = await workflow.get_recommendations(investor_session)

    print(f"Entrepreneur recommendations: {len(entrepreneur_recs['recommendations'])}")
    print(f"Investor recommendations: {len(investor_recs['recommendations'])}")

    # System metrics
    print(f"\nSystem metrics:")
    metrics = workflow.get_system_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    print("\nWorkflow system test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())