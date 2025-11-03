"""
Example Usage of Innov8 Workflow System
=======================================

This file demonstrates how to use the complete workflow system for different
user scenarios. It shows practical examples for entrepreneurs, investors,
and system administrators.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from main import Innov8WorkflowSystem
from user_experience import UserType
from question_engine import BusinessStage, Industry

async def entrepreneur_workflow_example():
    """Complete example of entrepreneur using the workflow system."""
    print("🚀 ENTREPRENEUR WORKFLOW EXAMPLE")
    print("=" * 50)

    # Initialize system
    workflow = Innov8WorkflowSystem()

    # 1. Start entrepreneur session
    print("\n📝 Step 1: Starting entrepreneur session...")
    session_id = await workflow.start_session(
        UserType.ENTREPRENEUR,
        {
            'business_stage': BusinessStage.IDEA,
            'industry': Industry.TECHNOLOGY,
            'experience_level': 'beginner',
            'company_name': 'TechStart Inc.',
            'founder_name': 'Jane Doe'
        }
    )
    print(f"✅ Session started: {session_id}")

    # 2. Go through adaptive questioning
    print("\n❓ Step 2: Answering adaptive questions...")
    question_count = 0
    max_questions = 5  # For demo purposes

    while question_count < max_questions:
        question_data = await workflow.get_next_question(session_id)

        if question_data['status'] == 'questionnaire_complete':
            print("✅ Questionnaire completed!")
            break

        print(f"\nQ{question_count + 1}: {question_data['question_text']}")

        # Simulate different types of answers based on question
        if 'business model' in question_data['question_text'].lower():
            answer = "We plan to use a SaaS subscription model with tiered pricing"
        elif 'target market' in question_data['question_text'].lower():
            answer = "Small to medium businesses in the tech industry"
        elif 'revenue' in question_data['question_text'].lower():
            answer = "Projecting $500K in year 1, growing to $2M by year 3"
        elif 'team' in question_data['question_text'].lower():
            answer = "Currently 2 founders with technical backgrounds"
        else:
            answer = "This is an example answer for demonstration purposes"

        # Submit answer
        await workflow.get_next_question(session_id, answer)
        print(f"✅ Answer submitted: {answer[:50]}...")

        question_count += 1

    # 3. Get dashboard data
    print("\n📊 Step 3: Getting entrepreneur dashboard...")
    dashboard = await workflow.get_dashboard_data(session_id)

    print(f"Dashboard sections: {list(dashboard.keys())}")
    print(f"Progress: {dashboard.get('progress', 'N/A')}%")
    print(f"Questions answered: {dashboard.get('questions_answered', 0)}")

    if 'next_milestones' in dashboard:
        print(f"Next milestones: {dashboard['next_milestones']}")

    # 4. Simulate document upload and validation
    print("\n📄 Step 4: Document validation...")

    # Create a sample document for demonstration
    sample_doc_path = "sample_business_plan.txt"
    with open(sample_doc_path, 'w') as f:
        f.write("""
        TechStart Inc. - Business Plan

        Executive Summary:
        TechStart Inc. is a technology startup focused on providing innovative SaaS solutions
        for small to medium businesses in the technology sector.

        Business Model:
        We operate on a subscription-based SaaS model with three pricing tiers:
        - Basic: $29/month
        - Professional: $99/month
        - Enterprise: Custom pricing

        Market Analysis:
        Our target market includes 50,000+ SMBs in the tech industry across North America.
        Market research indicates a growing demand for our specialized solutions.

        Financial Projections:
        Year 1: $500K revenue
        Year 2: $1.2M revenue
        Year 3: $2M revenue

        Team:
        - Jane Doe, CEO (Technical background)
        - John Smith, CTO (Software engineering expert)
        """)

    validation_result = await workflow.upload_document(
        session_id,
        sample_doc_path,
        "business_plan"
    )

    print(f"✅ Document validation complete!")
    print(f"Overall Score: {validation_result['validation_score']:.2f}")
    print(f"Completeness: {validation_result['completeness_score']:.2f}")
    print(f"Consistency: {validation_result['consistency_score']:.2f}")
    print(f"Realism: {validation_result['realism_score']:.2f}")

    if validation_result['recommendations']:
        print(f"Recommendations: {len(validation_result['recommendations'])}")
        for i, rec in enumerate(validation_result['recommendations'][:3], 1):
            print(f"  {i}. {rec}")

    # 5. Get personalized recommendations
    print("\n💡 Step 5: Getting personalized recommendations...")
    recommendations = await workflow.get_recommendations(session_id)

    print(f"Generated {len(recommendations['recommendations'])} recommendations:")
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"  {i}. {rec['title']}")
        print(f"     Priority: {rec['priority']}")
        print(f"     {rec['description'][:80]}...")

    # 6. Setup integrations (optional)
    print("\n🔗 Step 6: Setting up integrations...")

    # Setup Google Sheets integration
    sheets_result = await workflow.setup_integration(
        session_id,
        'google_sheets',
        {
            'spreadsheet_id': 'demo_sheet_id',
            'api_key': 'demo_api_key',
            'auto_sync': True
        }
    )

    print(f"Google Sheets integration: {sheets_result['status']}")

    # Cleanup
    if Path(sample_doc_path).exists():
        Path(sample_doc_path).unlink()

    print("\n✅ Entrepreneur workflow example completed!")
    return session_id

async def investor_workflow_example():
    """Example of investor using the workflow system."""
    print("\n\n💼 INVESTOR WORKFLOW EXAMPLE")
    print("=" * 50)

    # Initialize system
    workflow = Innov8WorkflowSystem()

    # 1. Start investor session
    print("\n📝 Step 1: Starting investor session...")
    session_id = await workflow.start_session(
        UserType.INVESTOR,
        {
            'business_stage': BusinessStage.SERIES_A,
            'industry': None,  # No industry restriction
            'experience_level': 'expert',
            'firm_name': 'Venture Partners LP',
            'investor_name': 'Michael Chen',
            'investment_focus': ['Technology', 'Healthcare', 'SaaS']
        }
    )
    print(f"✅ Session started: {session_id}")

    # 2. Get investor dashboard
    print("\n📊 Step 2: Getting investor dashboard...")
    dashboard = await workflow.get_dashboard_data(session_id)

    print(f"Dashboard sections: {list(dashboard.keys())}")
    print(f"Investment opportunities: {dashboard.get('investment_opportunities', 'N/A')}")
    print(f"Portfolio performance: {dashboard.get('portfolio_performance', 'N/A')}")
    print(f"Due diligence queue: {dashboard.get('due_diligence_queue', 'N/A')}")

    # 3. Simulate reviewing company documents
    print("\n📄 Step 3: Reviewing company documents...")

    # Create sample company documents
    companies = [
        {
            'name': 'CloudSync Solutions',
            'document': 'cloudsync_business_plan.txt',
            'type': 'business_plan'
        },
        {
            'name': 'HealthTech AI',
            'document': 'healthtech_business_plan.txt',
            'type': 'business_plan'
        }
    ]

    for company in companies:
        print(f"\nReviewing {company['name']}...")

        # Create sample document
        with open(company['document'], 'w') as f:
            f.write(f"""
            {company['name']} - Business Plan

            Executive Summary:
            {company['name']} is an innovative company in the {company['name'].split()[0]} sector
            with strong growth potential and a clear market opportunity.

            Business Model:
            We have developed a scalable business model with multiple revenue streams
            and a clear path to profitability.

            Financial Projections:
            Strong financial outlook with projected 40% year-over-year growth.
            Seeking Series A funding to accelerate market expansion.

            Team:
            Experienced founding team with relevant industry expertise and
            successful track record in startup ventures.
            """)

        # Validate document
        validation_result = await workflow.upload_document(
            session_id,
            company['document'],
            company['type']
        )

        print(f"  Validation Score: {validation_result['validation_score']:.2f}")
        print(f"  Industry Fit: {validation_result['industry_fit_score']:.2f}")

        # Cleanup
        if Path(company['document']).exists():
            Path(company['document']).unlink()

    # 4. Get investor recommendations
    print("\n💡 Step 4: Getting investor recommendations...")
    recommendations = await workflow.get_recommendations(session_id)

    print(f"Generated {len(recommendations['recommendations'])} recommendations:")
    for i, rec in enumerate(recommendations['recommendations'], 1):
        print(f"  {i}. {rec['title']}")
        print(f"     {rec['description'][:80]}...")

    # 5. Setup CRM integration for deal tracking
    print("\n🔗 Step 5: Setting up CRM integration...")

    crm_result = await workflow.setup_integration(
        session_id,
        'salesforce',
        {
            'domain': 'venturepartners.my.salesforce.com',
            'api_key': 'demo_api_key',
            'auto_sync_deals': True
        }
    )

    print(f"Salesforce integration: {crm_result['status']}")

    print("\n✅ Investor workflow example completed!")
    return session_id

async def system_administration_example():
    """Example of system administration tasks."""
    print("\n\n⚙️ SYSTEM ADMINISTRATION EXAMPLE")
    print("=" * 50)

    # Initialize system
    workflow = Innov8WorkflowSystem()

    # 1. Get system metrics
    print("\n📈 Step 1: Getting system metrics...")
    metrics = workflow.get_system_metrics()

    print("System Metrics:")
    for key, value in metrics.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # 2. Demonstrate integration management
    print("\n🔗 Step 2: Integration management...")

    # Initialize integration framework database
    from integration_framework import IntegrationFramework
    integration_framework = IntegrationFramework()

    # Get integration health
    health_status = await integration_framework.health_check()
    print(f"Integration Framework Health: {health_status['status']}")
    print(f"Active Integrations: {health_status['active_integrations']}")
    print(f"Total Connections: {health_status['total_integrations']}")

    # 3. Demonstrate validation engine capabilities
    print("\n🔍 Step 3: Validation engine capabilities...")

    from validation_engine import ValidationEngine
    validation_engine = ValidationEngine()

    # Get available document types
    doc_types = validation_engine.get_supported_document_types()
    print(f"Supported document types: {doc_types}")

    # Get validation categories
    categories = validation_engine.get_validation_categories()
    print(f"Validation categories: {list(categories.keys())}")

    # 4. Demonstrate question engine configuration
    print("\n❓ Step 4: Question engine capabilities...")

    from question_engine import QuestionEngine
    question_engine = QuestionEngine()

    # Get available industries
    industries = question_engine.get_supported_industries()
    print(f"Supported industries: {[ind.value for ind in industries]}")

    # Get business stages
    stages = question_engine.get_business_stages()
    print(f"Business stages: {[stage.value for stage in stages]}")

    print("\n✅ System administration example completed!")

async def complete_workflow_demo():
    """Complete demonstration of the entire workflow system."""
    print("🎯 COMPLETE WORKFLOW SYSTEM DEMONSTRATION")
    print("=" * 60)

    # Run all examples
    entrepreneur_session = await entrepreneur_workflow_example()
    investor_session = await investor_workflow_example()
    await system_administration_example()

    # Final system summary
    print("\n\n📋 FINAL SYSTEM SUMMARY")
    print("=" * 30)

    workflow = Innov8WorkflowSystem()
    final_metrics = workflow.get_system_metrics()

    print("\n🚀 System Performance:")
    print(f"  Total sessions created: {final_metrics['total_sessions']}")
    print(f"  Active sessions: {final_metrics['active_sessions']}")
    print(f"  Documents validated: {final_metrics['documents_validated']}")
    print(f"  Questions answered: {final_metrics['questions_answered']}")

    print("\n✨ Key Features Demonstrated:")
    print("  ✅ Adaptive question engine with industry-specific paths")
    print("  ✅ Dual-sided user experience (entrepreneur + investor)")
    print("  ✅ AI-powered document validation")
    print("  ✅ External tool integrations")
    print("  ✅ Real-time dashboard and analytics")
    print("  ✅ Personalized recommendations")
    print("  ✅ System administration tools")

    print("\n🎉 Complete workflow system demo finished successfully!")

if __name__ == "__main__":
    # Run the complete demonstration
    asyncio.run(complete_workflow_demo())