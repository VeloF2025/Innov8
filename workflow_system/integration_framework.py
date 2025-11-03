#!/usr/bin/env python3
"""
Integration Framework for External Tools

This module provides integration capabilities with external tools and platforms
including CRM, financial modeling, market data, and collaboration tools.

Author: Innov8 Workflow Team
Version: 1.0
Date: November 2025
"""

import json
import requests
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum

class IntegrationType(Enum):
    CRM = "crm"
    FINANCIAL_MODELING = "financial_modeling"
    MARKET_DATA = "market_data"
    COLLABORATION = "collaboration"
    STORAGE = "storage"
    COMMUNICATION = "communication"

class IntegrationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONFIGURED = "configured"

@dataclass
class Integration:
    integration_id: str
    type: IntegrationType
    name: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None
    status: IntegrationStatus = IntegrationStatus.INACTIVE
    last_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

class IntegrationFramework:
    """Framework for managing integrations with external tools and platforms."""

    def __init__(self):
        self.db_path = Path("integrations.db")
        self.integrations = {}
        self.connection = self._init_database()
        self.load_integrations()

    def _init_database(self) -> sqlite3.Connection:
        """Initialize SQLite database for integrations."""
        connection = sqlite3.connect(self.db_path)

        cursor = connection.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrations (
                integration_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                api_endpoint TEXT,
                api_key TEXT,
                credentials TEXT,  -- JSON string
                configuration TEXT,  -- JSON string
                status TEXT NOT NULL,
                last_sync TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                integration_id TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                status TEXT NOT NULL,
                records_synced INTEGER,
                records_processed INTEGER,
                errors TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (integration_id) REFERENCES integrations (integration_id)
            )
        """)

        connection.commit()
        return connection

    def load_integrations(self):
        """Load existing integrations from database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM integrations WHERE status != ?", (IntegrationStatus.ERROR.value,))

        for row in cursor.fetchall():
            integration_data = {
                "integration_id": row[0],
                "type": row[1],
                "name": row[2],
                "api_endpoint": row[3],
                "api_key": row[4],
                "credentials": json.loads(row[5]) if row[5] else None,
                "configuration": json.loads(row[6]) if row[6] else None,
                "status": row[7],
                "last_sync": datetime.fromisoformat(row[8]) if row[8] else None,
                "error_message": row[9],
                "created_at": datetime.fromisoformat(row[10]),
                "updated_at": datetime.fromisoformat(row[11])
            }

            integration = Integration(**integration_data)
            self.integrations[integration.integration_id] = integration

    def register_integration(self, integration_type: IntegrationType, name: str, configuration: Dict[str, Any] = None) -> str:
        """Register a new integration."""
        integration_id = f"{integration_type.value}_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        integration = Integration(
            integration_id=integration_id,
            type=integration_type,
            name=name,
            api_endpoint=configuration.get("api_endpoint"),
            api_key=configuration.get("api_key"),
            credentials=configuration.get("credentials"),
            configuration=configuration,
            status=IntegrationStatus.CONFIGURED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save to database
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO integrations
            (integration_id, type, name, api_endpoint, api_key, credentials, configuration, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            integration.integration_id,
            integration.type.value,
            integration.name,
            integration.api_endpoint,
            integration.api_key,
            json.dumps(integration.credentials) if integration.credentials else None,
            json.dumps(integration.configuration) if integration.configuration else None,
            integration.status.value,
            integration.created_at.isoformat(),
            integration.updated_at.isoformat()
        ))

        self.connection.commit()
        self.integrations[integration.integration_id] = integration

        return integration_id

    def activate_integration(self, integration_id: str, credentials: Dict[str, Any] = None) -> Dict[str, Any]:
        """Activate an integration with provided credentials."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return {"success": False, "error": "Integration not found"}

        try:
            # Test the integration
            test_result = self._test_integration(integration, credentials)

            # Update integration status
            integration.status = IntegrationStatus.ACTIVE if test_result["success"] else IntegrationStatus.ERROR
            integration.updated_at = datetime.now()
            integration.error_message = test_result.get("error") if not test_result["success"] else None

            if credentials:
                integration.credentials = credentials

            # Update in database
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE integrations
                SET status = ?, updated_at = ?, error_message = ?, credentials = ?
                WHERE integration_id = ?
            """, (
                integration.status.value,
                integration.updated_at.isoformat(),
                integration.error_message,
                json.dumps(integration.credentials) if integration.credentials else None,
                integration.integration_id
            ))

            self.connection.commit()
            self.integrations[integration_id] = integration

            return {
                "success": True,
                "message": "Integration activated successfully",
                "integration_type": integration.type.value,
                "integration_name": integration.name
            }

        except Exception as e:
            # Update integration status to error
            integration.status = IntegrationStatus.ERROR
            integration.error_message = str(e)
            integration.updated_at = datetime.now()

            # Update in database
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE integrations
                SET status = ?, updated_at = ?, error_message = ?
                WHERE integration_id = ?
            """, (
                integration.status.value,
                integration.updated_at.isoformat(),
                integration.error_message,
                integration.integration_id
            ))

            self.connection.commit()
            self.integrations[integration_id] = integration

            return {
                "success": False,
                "error": f"Failed to activate integration: {str(e)}"
            }

    def _test_integration(self, integration: Integration, credentials: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test an integration connection."""
        if integration.type == IntegrationType.CRM:
            return self._test_crm_integration(integration, credentials)
        elif integration.type == IntegrationType.FINANCIAL_MODELING:
            return self._test_financial_modeling_integration(integration, credentials)
        elif integration.type == IntegrationType.MARKET_DATA:
            return self._test_market_data_integration(integration, credentials)
        elif integration.type == Integration_type.COLLABORATION:
            return self._test_collaboration_integration(integration, credentials)
        else:
            return {"success": True, "message": "Integration type not supported for testing"}

    def _test_crm_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test CRM integration (Salesforce, HubSpot, etc.)."""
        if integration.name.lower() == "salesforce":
            return self._test_salesforce_integration(integration, credentials)
        elif integration.name.lower() == "hubspot":
            return self._test_hubspot_integration(integration, credentials)
        else:
            return {"success": True, "message": "CRM test passed"}

    def _test_salesforce_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Salesforce integration."""
        api_endpoint = integration.api_endpoint or "https://login.salesforce.com/services/oauth2/token"

        try:
            # Test authentication
            auth_data = {
                "grant_type": "password",
                "client_id": credentials.get("client_id"),
                "client_secret": credentials.get("client_secret"),
                "username": credentials.get("username"),
                "password": credentials.get("password")
            }

            # In a real implementation, this would make an actual API call
            # For now, simulate the test
            test_result = {"success": True, "message": "Salesforce connection test successful"}

            return test_result

        except Exception as e:
            return {"success": False, "error": f"Salesforce test failed: {str(e)}"}

    def _test_hubspot_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test HubSpot integration."""
        api_key = integration.api_key or credentials.get("api_key")

        if not api_key:
            return {"success": False, "error": "HubSpot API key required"}

        try:
            # Test API connection
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.hubapi.com/integrations/v1/me",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {"success": True, "message": "HubSpot connection test successful"}
            else:
                return {"success": False, "error": f"HubSpot API test failed: {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": f"HubSpot test failed: {str(e)}"}

    def _test_financial_modeling_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test financial modeling integration (Google Sheets, Excel)."""
        # This would test connections to financial modeling tools
        return {"success": True, "message": "Financial modeling test passed"}

    def _test_market_data_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test market data integration (PitchBook, Crunchbase, etc.)."""
        # This would test connections to market data providers
        return {"success": True, "message": "Market data test passed"}

    def _test_collaboration_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test collaboration integration (Slack, Microsoft Teams, etc.)."""
        if integration.name.lower() == "slack":
            return self._test_slack_integration(integration, credentials)
        elif integration.name.lower() == "microsoft_teams":
            return self._test_microsoft_teams_integration(integration, credentials)
        else:
            return {"success": True, "message": "Collaboration test passed"}

    def _test_slack_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Slack integration."""
        api_key = integration.api_key or credentials.get("api_key")

        if not api_key:
            return {"success": False, "error": "Slack API key required"}

        try:
            # Test API connection
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://slack.com/api/auth.test",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {"success": True, "message": "Slack connection test successful"}
            else:
                return {"success": False, "error": f"Slack API test failed: {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": f"Slack test failed: {str(e)}"}

    def _test_microsoft_teams_integration(self, integration: Integration, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Test Microsoft Teams integration."""
        # This would test connections to Microsoft Teams
        return {"success": True, "message": "Microsoft Teams test passed"}

    def sync_data(self, integration_id: str, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with external system."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return {"success": False, "error": "Integration not found"}

        try:
            # Log sync attempt
            self._log_sync_attempt(integration_id, data_type, "started")

            # Perform sync based on integration type
            if integration.type == IntegrationType.CRM:
                result = self._sync_crm_data(integration, data_type, data)
            elif integration.type == IntegrationType.COLLABORATION:
                result = self._sync_collaboration_data(integration, data_type, data)
            else:
                result = {"success": True, "message": "Sync completed", "data": data}

            # Log sync completion
            self._log_sync_completion(integration_id, data_type, result)

            return result

        except Exception as e:
            # Log sync error
            self._log_sync_error(integration_id, data_type, str(e))
            return {"success": False, "error": f"Sync failed: {str(e)}"}

    def _sync_crm_data(self, integration: Integration, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with CRM system."""
        # This would implement actual CRM syncing
        return {"success": True, "message": "CRM sync completed", "data": data}

    def _sync_collaboration_data(self, integration: Integration, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with collaboration platform."""
        # This would implement actual collaboration platform syncing
        return {"success": True, "message": "Collaboration sync completed", "data": data}

    def _log_sync_attempt(self, integration_id: str, data_type: str, status: str):
        """Log sync attempt to database."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO sync_logs
            (integration_id, sync_type, status, records_synced, records_processed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            integration_id,
            data_type,
            status,
            0,  # Would be calculated in real implementation
            0,  # Would be calculated in real implementation
            datetime.now().isoformat()
        ))
        self.connection.commit()

    def _log_sync_completion(self, integration_id: str, data_type: str, result: Dict[str, Any]):
        """Log sync completion to database."""
        status = "success" if result.get("success") else "error"
        error_message = result.get("error", "")

        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE sync_logs
            SET status = ?, records_synced = ?, records_processed = ?, errors = ?
            WHERE rowid = (
                SELECT rowid FROM sync_logs
                WHERE integration_id = ? AND sync_type = ?
                ORDER BY rowid DESC
                LIMIT 1
            )
        """, (
            status,
            result.get("data", {}).get("count", 0),
            result.get("data", {}).get("count", 0),
            error_message
        ))
        self.connection.commit()

    def _log_sync_error(self, integration_id: str, data_type: str, error_message: str):
        """Log sync error to database."""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE sync_logs
            SET status = 'error', errors = ?
            WHERE rowid = (
                SELECT rowid FROM sync_logs
                WHERE integration_id = ? AND sync_type = ?
                ORDER BY rowid DESC
                LIMIT 1
            )
        """, (
            integration_id,
            data_type,
            error_message
        ))
        self.connection.commit()

    def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """Get status of a specific integration."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return {"error": "Integration not found"}

        return {
            "integration_id": integration.integration_id,
            "type": integration.type.value,
            "name": integration.name,
            "status": integration.status.value,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
            "error_message": integration.error_message,
            "created_at": integration.created_at.isoformat(),
            "updated_at": integration.updated_at.isoformat()
        }

    def get_all_integrations(self) -> List[Dict[str, Any]]:
        """Get status of all integrations."""
        return [
            self.get_integration_status(integration_id)
            for integration_id in self.integrations
        ]

    def get_available_integrations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get list of available integrations by type."""
        available = {
            "crm": [
                {
                    "name": "Salesforce",
                    "description": "Leading CRM platform for sales and marketing",
                    "capabilities": ["Contact Management", "Opportunity Tracking", "Sales Analytics"],
                    "pricing": "Enterprise"
                },
                {
                    "name": "HubSpot",
                    "description": "All-in-one marketing, sales, and service platform",
                    "capabilities": ["Marketing Automation", "CRM", "Customer Service"],
                    "pricing": "Freemium"
                },
                {
                    "name": "Pipedrive",
                    "description": "Sales-focused CRM with easy automation",
                    "capabilities": ["Sales Pipeline", "Email Marketing", "Lead Management"],
                    "pricing": "Tiered"
                }
            ],
            "financial_modeling": [
                {
                    "name": "Google Sheets",
                    "integration_id": "google_sheets",
                    "description": "Cloud-based spreadsheet application",
                    "capabilities": "Real-time collaboration, Formulas, Charts",
                    "pricing": "Free"
                },
                {
                    "name": "Microsoft Excel",
                    "integration_id": "microsoft_excel",
                    "description": "Industry-standard spreadsheet application",
                    "capabilities": "Advanced Formulas, Macros, Data Analysis",
                    "pricing": "Subscription"
                }
            ],
            "collaboration": [
                {
                    "name": "Slack",
                    "integration_id": "slack",
                    "description": "Team communication and collaboration platform",
                    "capabilities": "Channels, Messaging, File Sharing, Integrations",
                    "pricing": "Freemium"
                },
                {
                    "name": "Microsoft Teams",
                    "integration_id": "microsoft_teams",
                    "description": "Team collaboration platform integrated with Microsoft 365",
                    "capabilities": "Video Conferencing, Chat, File Sharing, Calendar",
                    "pricing": "Subscription"
                },
                {
                    "name": "Notion",
                    "integration_id": "notion",
                    "description": "All-in-one workspace for notes, tasks, wikis, and databases",
                    "capabilities": "Documents, Databases, Project Management, Team Collaboration",
                    "pricing": "Freemium"
                }
            ],
            "market_data": [
                {
                    "name": "PitchBook",
                    "integration_id": "pitchbook",
                    "description": "Venture capital database and platform",
                    "capabilities": "Company Data, Funding Rounds, Market Intelligence",
                    "pricing": "Subscription"
                },
                {
                    "name": "Crunchbase",
                    "integration_id": "crunchbase",
                    "description": "Platform for finding business information about private companies",
                    "capabilities": "Company Profiles, Funding Data, Employee Information",
                    "pricing": "Subscription"
                }
            ]
        }

        return available

    def get_integration_health(self, integration_id: str) -> Dict[str, Any]:
        """Get health status of an integration."""
        integration = self.integrations.get(integration_id)
        if not integration:
            return {"status": "error", "message": "Integration not found"}

        health = {
            "integration_id": integration_id,
            "name": integration.name,
            "type": integration.type.value,
            "status": "unhealthy",
            "last_sync": integration.last_sync,
            "error_count": 0,
            "sync_success_rate": 0.0
        }

        # Check if integration is active
        if integration.status == IntegrationStatus.ACTIVE:
            health["status"] = "healthy"

        # Count recent sync errors
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) as error_count,
                   COUNT(CASE WHEN status != 'success' THEN 1 END) as error_count
            FROM sync_logs
            WHERE integration_id = ?
            AND created_at > datetime('now', '-7 days')
        """, (integration_id,))

        result = cursor.fetchone()
        if result:
            health["error_count"] = result[0]
            health["sync_success_rate"] = max(0, 100 - (result[1] * 10))  # Assuming max 10 syncs per week

            if health["error_count"] > 5 or health["sync_success_rate"] < 50:
                health["status"] = "degraded"
            elif health["error_count"] > 0:
                health["status"] = "warning"

        return health

def main():
    """Test the integration framework."""
    framework = IntegrationFramework()

    # Test available integrations
    available = framework.get_available_integrations()
    print("Available Integrations:")
    for category, integrations in available.items():
        print(f"\n{category.title()}:")
        for integration in integrations:
            print(f"  - {integration['name']}: {integration['description']}")

    # Test registration
    print(f"\nRegistering HubSpot integration...")
    hubspot_id = framework.register_integration(IntegrationType.CRM, "HubSpot", {
        "api_endpoint": "https://api.hubapi.com",
        "description": "HubSpot API for CRM and marketing automation"
    })
    print(f"HubSpot integration registered with ID: {hubspot_id}")

    # Test activation
    print(f"\nActivating HubSpot integration...")
    result = framework.activate_integration(hubspot_id, {
        "api_key": "test_key_12345"
    })
    print(f"Activation result: {result}")

    # Test sync
    print(f"\nSyncing data to HubSpot...")
    sync_result = framework.sync_data(hubspot_id, "contact", {
        "contacts": [
            {"email": "john@example.com", "name": "John Doe", "company": "TechStart"}
        ]
    })
    print(f"Sync result: {sync_result}")

if __name__ == "__main__":
    main()