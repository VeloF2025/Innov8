"""
Test Suite for Innov8 Workflow System
=====================================

Comprehensive test suite covering all components of the workflow system.
Tests are organized by component and include both unit and integration tests.
"""

import asyncio
import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from main import Innov8WorkflowSystem
from question_engine import QuestionEngine, UserContext, BusinessStage, Industry, Question
from user_experience import UserExperience, UserType, WorkflowStage
from validation_engine import ValidationEngine, ValidationResult
from integration_framework import IntegrationFramework, IntegrationType

class TestQuestionEngine:
    """Test suite for the Question Engine component."""

    @pytest.fixture
    def question_engine(self):
        """Create a question engine instance for testing."""
        return QuestionEngine()

    @pytest.fixture
    def sample_user_context(self):
        """Create a sample user context for testing."""
        return UserContext(
            user_id="test_user_001",
            user_type="entrepreneur",
            business_stage=BusinessStage.IDEA,
            industry=Industry.TECHNOLOGY,
            experience_level="beginner"
        )

    def test_question_engine_initialization(self, question_engine):
        """Test that question engine initializes correctly."""
        assert question_engine is not None
        assert len(question_engine.questions) > 0
        assert hasattr(question_engine, 'question_weights')

    def test_get_next_question_idea_stage(self, question_engine, sample_user_context):
        """Test getting next question for idea stage."""
        question = question_engine.get_next_question(sample_user_context)

        assert question is not None
        assert isinstance(question, Question)
        assert question.id is not None
        assert question.text is not None
        assert question.category in ['business_model', 'market_analysis', 'team']

    def test_get_next_question_seed_stage(self, question_engine):
        """Test getting next question for seed stage."""
        user_context = UserContext(
            user_id="test_user_002",
            user_type="entrepreneur",
            business_stage=BusinessStage.SEED,
            industry=Industry.TECHNOLOGY,
            experience_level="intermediate"
        )

        question = question_engine.get_next_question(user_context)

        assert question is not None
        # Seed stage should include more financial questions
        financial_questions = [q for q in question_engine.questions
                              if q.category == 'financial_projections']
        assert len(financial_questions) > 0

    def test_process_answer(self, question_engine, sample_user_context):
        """Test answer processing."""
        initial_answer_count = len(sample_user_context.answers)

        question_engine.process_answer(sample_user_context, "Test answer")

        assert len(sample_user_context.answers) == initial_answer_count + 1
        assert sample_user_context.answers[-1].answer == "Test answer"

    def test_industry_specific_questions(self, question_engine):
        """Test industry-specific question filtering."""
        # Technology industry context
        tech_context = UserContext(
            user_id="tech_user",
            user_type="entrepreneur",
            business_stage=BusinessStage.IDEA,
            industry=Industry.TECHNOLOGY,
            experience_level="beginner"
        )

        # Healthcare industry context
        health_context = UserContext(
            user_id="health_user",
            user_type="entrepreneur",
            business_stage=BusinessStage.IDEA,
            industry=Industry.HEALTHCARE,
            experience_level="beginner"
        )

        tech_question = question_engine.get_next_question(tech_context)
        health_question = question_engine.get_next_question(health_context)

        # Questions should be different based on industry
        assert tech_question is not None
        assert health_question is not None

    def test_generate_document_checklist(self, question_engine, sample_user_context):
        """Test document checklist generation."""
        # Add some answers to user context
        sample_user_context.answers.extend([
            Mock(answer="SaaS business model"),
            Mock(answer="Targeting SMB market"),
            Mock(answer="2 founders with tech background")
        ])

        checklist = question_engine.generate_document_checklist(sample_user_context)

        assert isinstance(checklist, list)
        assert len(checklist) > 0
        assert any('business plan' in item.lower() for item in checklist)

class TestUserExperience:
    """Test suite for the User Experience component."""

    @pytest.fixture
    def user_experience(self):
        """Create a user experience instance for testing."""
        return UserExperience()

    def test_create_entrepreneur_session(self, user_experience):
        """Test creating an entrepreneur session."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = user_experience.create_session(UserType.ENTREPRENEUR, user_info)

        assert session_id is not None
        assert session_id in user_experience.sessions
        assert user_experience.sessions[session_id].user_type == UserType.ENTREPRENEUR

    def test_create_investor_session(self, user_experience):
        """Test creating an investor session."""
        user_info = {
            'business_stage': BusinessStage.SERIES_A,
            'experience_level': 'expert'
        }

        session_id = user_experience.create_session(UserType.INVESTOR, user_info)

        assert session_id is not None
        assert user_experience.sessions[session_id].user_type == UserType.INVESTOR

    def test_get_dashboard_entrepreneur(self, user_experience):
        """Test getting entrepreneur dashboard."""
        user_info = {'business_stage': BusinessStage.IDEA}
        session_id = user_experience.create_session(UserType.ENTREPRENEUR, user_info)

        dashboard = user_experience.get_dashboard(session_id)

        assert isinstance(dashboard, dict)
        assert 'user_type' in dashboard
        assert dashboard['user_type'] == UserType.ENTREPRENEUR.value
        assert 'widgets' in dashboard
        assert len(dashboard['widgets']) > 0

    def test_get_dashboard_investor(self, user_experience):
        """Test getting investor dashboard."""
        user_info = {'experience_level': 'expert'}
        session_id = user_experience.create_session(UserType.INVESTOR, user_info)

        dashboard = user_experience.get_dashboard(session_id)

        assert isinstance(dashboard, dict)
        assert dashboard['user_type'] == UserType.INVESTOR.value
        assert 'widgets' in dashboard
        assert len(dashboard['widgets']) > 0

    def test_update_progress(self, user_experience):
        """Test progress tracking."""
        user_info = {'business_stage': BusinessStage.IDEA}
        session_id = user_experience.create_session(UserType.ENTREPRENEUR, user_info)

        initial_progress = user_experience.get_progress(session_id)
        user_experience.update_progress(session_id, 25)
        updated_progress = user_experience.get_progress(session_id)

        assert updated_progress > initial_progress
        assert updated_progress == 25

    def test_workflow_stage_transitions(self, user_experience):
        """Test workflow stage transitions."""
        user_info = {'business_stage': BusinessStage.IDEA}
        session_id = user_experience.create_session(UserType.ENTREPRENEUR, user_info)

        # Should start at initial stage
        current_stage = user_experience.get_current_stage(session_id)
        assert current_stage == WorkflowStage.INITIAL

        # Transition to questionnaire
        user_experience.transition_stage(session_id, WorkflowStage.QUESTIONNAIRE)
        current_stage = user_experience.get_current_stage(session_id)
        assert current_stage == WorkflowStage.QUESTIONNAIRE

class TestValidationEngine:
    """Test suite for the Validation Engine component."""

    @pytest.fixture
    def validation_engine(self):
        """Create a validation engine instance for testing."""
        return ValidationEngine()

    @pytest.fixture
    def sample_document(self):
        """Create a sample document for testing."""
        content = """
        TechStart Inc. - Business Plan

        Executive Summary:
        We are a technology startup focused on SaaS solutions for SMBs.

        Business Model:
        Subscription-based SaaS with tiered pricing starting at $29/month.

        Market Analysis:
        Target market of 50,000+ SMBs in North America.
        Growing demand for specialized tech solutions.

        Financial Projections:
        Year 1: $500K revenue
        Year 2: $1.2M revenue
        Year 3: $2M revenue

        Team:
        Two founders with technical and business backgrounds.
        """

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(content)
        temp_file.close()

        yield temp_file.name

        # Cleanup
        Path(temp_file.name).unlink()

    @pytest.fixture
    def sample_user_context(self):
        """Create sample user context for validation."""
        return UserContext(
            user_id="test_user",
            user_type="entrepreneur",
            business_stage=BusinessStage.IDEA,
            industry=Industry.TECHNOLOGY,
            experience_level="beginner"
        )

    @pytest.mark.asyncio
    async def test_validate_business_plan(self, validation_engine, sample_document, sample_user_context):
        """Test business plan validation."""
        result = await validation_engine.validate_document(
            document_path=sample_document,
            document_type="business_plan",
            user_context=sample_user_context
        )

        assert isinstance(result, ValidationResult)
        assert 0 <= result.overall_score <= 1
        assert 0 <= result.completeness_score <= 1
        assert 0 <= result.consistency_score <= 1
        assert 0 <= result.realism_score <= 1
        assert 0 <= result.clarity_score <= 1
        assert 0 <= result.industry_fit_score <= 1
        assert isinstance(result.recommendations, list)

    @pytest.mark.asyncio
    async def test_validate_financial_projections(self, validation_engine, sample_user_context):
        """Test financial projections validation."""
        # Create financial projections document
        financial_content = """
        Financial Projections - TechStart Inc.

        Revenue:
        Year 1: $500,000
        Year 2: $1,200,000
        Year 3: $2,000,000

        Expenses:
        Year 1: $400,000
        Year 2: $800,000
        Year 3: $1,200,000

        Profit:
        Year 1: $100,000
        Year 2: $400,000
        Year 3: $800,000
        """

        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(financial_content)
        temp_file.close()

        try:
            result = await validation_engine.validate_document(
                document_path=temp_file.name,
                document_type="financial_projections",
                user_context=sample_user_context
            )

            assert isinstance(result, ValidationResult)
            assert result.overall_score > 0
            assert len(result.recommendations) > 0
        finally:
            Path(temp_file.name).unlink()

    def test_industry_benchmarks(self, validation_engine):
        """Test industry benchmark loading."""
        tech_benchmarks = validation_engine.get_industry_benchmarks(Industry.TECHNOLOGY)
        assert isinstance(tech_benchmarks, dict)
        assert 'expected_sections' in tech_benchmarks
        assert 'financial_metrics' in tech_benchmarks

        healthcare_benchmarks = validation_engine.get_industry_benchmarks(Industry.HEALTHCARE)
        assert isinstance(healthcare_benchmarks, dict)
        # Benchmarks should be different for different industries
        assert tech_benchmarks != healthcare_benchmarks

class TestIntegrationFramework:
    """Test suite for the Integration Framework component."""

    @pytest.fixture
    def integration_framework(self):
        """Create an integration framework instance for testing."""
        return IntegrationFramework()

    @pytest.mark.asyncio
    async def test_create_salesforce_integration(self, integration_framework):
        """Test creating Salesforce integration."""
        config = {
            'domain': 'test.salesforce.com',
            'api_key': 'test_api_key',
            'auto_sync': True
        }

        integration_id = await integration_framework.create_integration(
            integration_type='salesforce',
            user_id='test_user_001',
            config=config
        )

        assert integration_id is not None
        assert isinstance(integration_id, str)

    @pytest.mark.asyncio
    async def test_create_google_sheets_integration(self, integration_framework):
        """Test creating Google Sheets integration."""
        config = {
            'spreadsheet_id': 'test_spreadsheet_id',
            'api_key': 'test_api_key',
            'auto_sync': True
        }

        integration_id = await integration_framework.create_integration(
            integration_type='google_sheets',
            user_id='test_user_002',
            config=config
        )

        assert integration_id is not None
        assert isinstance(integration_id, str)

    @pytest.mark.asyncio
    async def test_get_user_integrations(self, integration_framework):
        """Test retrieving user integrations."""
        # Create a few integrations first
        await integration_framework.create_integration(
            integration_type='salesforce',
            user_id='test_user_003',
            config={'api_key': 'test_key'}
        )
        await integration_framework.create_integration(
            integration_type='google_sheets',
            user_id='test_user_003',
            config={'spreadsheet_id': 'test_id'}
        )

        integrations = await integration_framework.get_user_integrations('test_user_003')

        assert len(integrations) >= 2
        integration_types = [integration.type for integration in integrations]
        assert 'salesforce' in integration_types
        assert 'google_sheets' in integration_types

    @pytest.mark.asyncio
    async def test_health_check(self, integration_framework):
        """Test integration framework health check."""
        health_status = await integration_framework.health_check()

        assert 'status' in health_status
        assert 'active_integrations' in health_status
        assert 'total_integrations' in health_status
        assert isinstance(health_status['active_integrations'], int)
        assert isinstance(health_status['total_integrations'], int)

class TestMainWorkflowSystem:
    """Test suite for the main workflow system orchestrator."""

    @pytest.fixture
    def workflow_system(self):
        """Create a workflow system instance for testing."""
        return Innov8WorkflowSystem()

    @pytest.mark.asyncio
    async def test_start_entrepreneur_session(self, workflow_system):
        """Test starting an entrepreneur session."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = await workflow_system.start_session(UserType.ENTREPRENEUR, user_info)

        assert session_id is not None
        assert session_id in workflow_system.active_sessions
        assert workflow_system.active_sessions[session_id]['user_context'].user_type == 'entrepreneur'

    @pytest.mark.asyncio
    async def test_start_investor_session(self, workflow_system):
        """Test starting an investor session."""
        user_info = {
            'business_stage': BusinessStage.SERIES_A,
            'experience_level': 'expert'
        }

        session_id = await workflow_system.start_session(UserType.INVESTOR, user_info)

        assert session_id is not None
        assert session_id in workflow_system.active_sessions
        assert workflow_system.active_sessions[session_id]['user_context'].user_type == 'investor'

    @pytest.mark.asyncio
    async def test_question_flow(self, workflow_system):
        """Test complete question flow."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = await workflow_system.start_session(UserType.ENTREPRENEUR, user_info)

        # Get first question
        question_data = await workflow_system.get_next_question(session_id)
        assert question_data['status'] == 'question'
        assert 'question_text' in question_data

        # Submit answer and get next question
        next_question = await workflow_system.get_next_question(session_id, "Test answer")

        if next_question['status'] == 'question':
            assert 'question_text' in next_question
        elif next_question['status'] == 'questionnaire_complete':
            assert 'next_stage' in next_question

    @pytest.mark.asyncio
    async def test_document_validation_workflow(self, workflow_system):
        """Test document validation in workflow context."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = await workflow_system.start_session(UserType.ENTREPRENEUR, user_info)

        # Create sample document
        content = "Sample business plan content for testing..."
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(content)
        temp_file.close()

        try:
            # Upload and validate document
            result = await workflow_system.upload_document(
                session_id,
                temp_file.name,
                "business_plan"
            )

            assert result['status'] == 'document_validated'
            assert 'validation_score' in result
            assert 'recommendations' in result
            assert 'next_steps' in result
        finally:
            Path(temp_file.name).unlink()

    @pytest.mark.asyncio
    async def test_dashboard_data_retrieval(self, workflow_system):
        """Test dashboard data retrieval."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = await workflow_system.start_session(UserType.ENTREPRENEUR, user_info)

        dashboard = await workflow_system.get_dashboard_data(session_id)

        assert isinstance(dashboard, dict)
        assert 'user_type' in dashboard
        assert 'progress' in dashboard
        assert 'validation_score' in dashboard
        assert dashboard['user_type'] == UserType.ENTREPRENEUR.value

    @pytest.mark.asyncio
    async def test_integration_setup(self, workflow_system):
        """Test integration setup in workflow context."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = await workflow_system.start_session(UserType.ENTREPRENEUR, user_info)

        # Setup Google Sheets integration
        with patch('workflow_system.integration_framework.IntegrationFramework.test_integration') as mock_test:
            mock_test.return_value = {'status': 'success'}

            result = await workflow_system.setup_integration(
                session_id,
                'google_sheets',
                {
                    'spreadsheet_id': 'test_id',
                    'api_key': 'test_key'
                }
            )

            assert result['status'] == 'integration_setup_success'
            assert 'integration_id' in result

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, workflow_system):
        """Test AI-powered recommendations generation."""
        user_info = {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner'
        }

        session_id = await workflow_system.start_session(UserType.ENTREPRENEUR, user_info)

        recommendations = await workflow_system.get_recommendations(session_id)

        assert recommendations['status'] == 'success'
        assert 'recommendations' in recommendations
        assert 'priority' in recommendations
        assert 'actionable_items' in recommendations
        assert len(recommendations['recommendations']) > 0

    def test_system_metrics(self, workflow_system):
        """Test system metrics retrieval."""
        metrics = workflow_system.get_system_metrics()

        assert isinstance(metrics, dict)
        assert 'total_sessions' in metrics
        assert 'active_sessions' in metrics
        assert 'documents_validated' in metrics
        assert 'questions_answered' in metrics
        assert 'active_integrations' in metrics
        assert isinstance(metrics['total_sessions'], int)

class TestIntegrationTests:
    """Integration tests for the complete workflow system."""

    @pytest.mark.asyncio
    async def test_complete_entrepreneur_workflow(self):
        """Test complete entrepreneur workflow from start to finish."""
        workflow = Innov8WorkflowSystem()

        # 1. Start session
        session_id = await workflow.start_session(
            UserType.ENTREPRENEUR,
            {
                'business_stage': BusinessStage.IDEA,
                'industry': Industry.TECHNOLOGY,
                'experience_level': 'beginner'
            }
        )

        # 2. Answer some questions
        questions_answered = 0
        while questions_answered < 3:
            question_data = await workflow.get_next_question(session_id)

            if question_data['status'] == 'questionnaire_complete':
                break

            await workflow.get_next_question(session_id, f"Answer {questions_answered + 1}")
            questions_answered += 1

        # 3. Get dashboard
        dashboard = await workflow.get_dashboard_data(session_id)
        assert dashboard['questions_answered'] >= 3

        # 4. Get recommendations
        recommendations = await workflow.get_recommendations(session_id)
        assert len(recommendations['recommendations']) > 0

        # 5. Verify session data
        assert session_id in workflow.active_sessions
        session_data = workflow.active_sessions[session_id]
        assert session_data['questions_answered'] >= 3

    @pytest.mark.asyncio
    async def test_complete_investor_workflow(self):
        """Test complete investor workflow from start to finish."""
        workflow = Innov8WorkflowSystem()

        # 1. Start session
        session_id = await workflow.start_session(
            UserType.INVESTOR,
            {
                'business_stage': BusinessStage.SERIES_A,
                'experience_level': 'expert'
            }
        )

        # 2. Get investor dashboard
        dashboard = await workflow.get_dashboard_data(session_id)
        assert dashboard['user_type'] == UserType.INVESTOR.value

        # 3. Get investor recommendations
        recommendations = await workflow.get_recommendations(session_id)
        assert len(recommendations['recommendations']) > 0

        # 4. Verify investor-specific features
        assert 'investment_opportunities' in dashboard or 'portfolio_performance' in dashboard

    @pytest.mark.asyncio
    async def test_system_component_interaction(self):
        """Test interaction between different system components."""
        workflow = Innov8WorkflowSystem()

        # Start entrepreneur session
        session_id = await workflow.start_session(
            UserType.ENTREPRENEUR,
            {
                'business_stage': BusinessStage.IDEA,
                'industry': Industry.TECHNOLOGY,
                'experience_level': 'beginner'
            }
        )

        # 1. Question engine interacts with user experience
        question_data = await workflow.get_next_question(session_id)
        assert 'progress' in question_data  # From user experience

        # 2. Validation engine provides insights for recommendations
        # (Mock document upload for testing)
        with patch('workflow_system.validation_engine.ValidationEngine.validate_document') as mock_validate:
            mock_validate.return_value = ValidationResult(
                overall_score=0.8,
                completeness_score=0.9,
                consistency_score=0.7,
                realism_score=0.8,
                clarity_score=0.85,
                industry_fit_score=0.75,
                recommendations=["Improve financial projections"],
                analysis={"word_count": 1000, "readability_score": 0.8}
            )

            content = "Test document content"
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            temp_file.write(content)
            temp_file.close()

            try:
                result = await workflow.upload_document(session_id, temp_file.name, "business_plan")
                assert result['validation_score'] == 0.8

                # 3. Validation results influence recommendations
                recommendations = await workflow.get_recommendations(session_id)
                assert len(recommendations['recommendations']) > 0
            finally:
                Path(temp_file.name).unlink()

        # 4. System metrics track all interactions
        metrics = workflow.get_system_metrics()
        assert metrics['total_sessions'] > 0
        assert metrics['questions_answered'] > 0

# Performance and load tests
class TestPerformance:
    """Performance tests for the workflow system."""

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test system performance with multiple concurrent sessions."""
        workflow = Innov8WorkflowSystem()
        sessions = []

        # Create multiple concurrent sessions
        tasks = []
        for i in range(10):
            task = workflow.start_session(
                UserType.ENTREPRENEUR,
                {
                    'business_stage': BusinessStage.IDEA,
                    'industry': Industry.TECHNOLOGY,
                    'experience_level': 'beginner'
                }
            )
            tasks.append(task)

        # Wait for all sessions to be created
        sessions = await asyncio.gather(*tasks)

        # Verify all sessions were created successfully
        assert len(sessions) == 10
        assert all(session_id is not None for session_id in sessions)
        assert len(workflow.active_sessions) == 10

        # Test concurrent question answering
        question_tasks = []
        for session_id in sessions:
            task = workflow.get_next_question(session_id)
            question_tasks.append(task)

        question_results = await asyncio.gather(*question_tasks)
        assert len(question_results) == 10
        assert all(result['status'] == 'question' for result in question_results)

    @pytest.mark.asyncio
    async def test_large_document_validation(self):
        """Test performance with large documents."""
        workflow = Innov8WorkflowSystem()

        # Create large document
        large_content = "This is a test. " * 10000  # ~200KB document
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(large_content)
        temp_file.close()

        try:
            session_id = await workflow.start_session(
                UserType.ENTREPRENEUR,
                {'business_stage': BusinessStage.IDEA}
            )

            # Measure validation time
            start_time = datetime.now()

            with patch('workflow_system.validation_engine.ValidationEngine.validate_document') as mock_validate:
                mock_validate.return_value = ValidationResult(
                    overall_score=0.7,
                    completeness_score=0.8,
                    consistency_score=0.6,
                    realism_score=0.7,
                    clarity_score=0.75,
                    industry_fit_score=0.65,
                    recommendations=["Improve clarity"],
                    analysis={"word_count": 20000, "readability_score": 0.7}
                )

                result = await workflow.upload_document(session_id, temp_file.name, "business_plan")

            end_time = datetime.now()
            validation_time = (end_time - start_time).total_seconds()

            # Should complete within reasonable time (less than 5 seconds)
            assert validation_time < 5.0
            assert result['status'] == 'document_validated'

        finally:
            Path(temp_file.name).unlink()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])