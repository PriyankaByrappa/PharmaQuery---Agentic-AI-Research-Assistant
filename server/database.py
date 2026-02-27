"""Firebase database integration."""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any, Optional
import json
from config import FIREBASE_CREDENTIALS

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(str(FIREBASE_CREDENTIALS))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Warning: Firebase initialization failed: {e}")
        print("Running in mock mode - data will not persist")

db = firestore.client() if firebase_admin._apps else None


class Database:
    """Database operations for storing agent outputs and analysis results."""
    
    @staticmethod
    def save_agent_output(analysis_id: str, agent_type: str, output: Dict[str, Any]) -> bool:
        """Save agent output to Firebase."""
        try:
            if db is None:
                print(f"[MOCK] Would save {agent_type} output for analysis {analysis_id}")
                return True
            
            doc_ref = db.collection("analyses").document(analysis_id).collection("agents").document(agent_type)
            doc_ref.set({
                "agent_type": agent_type,
                "output": output,
                "timestamp": firestore.SERVER_TIMESTAMP
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error saving agent output: {e}")
            return False
    
    @staticmethod
    def save_master_workflow(analysis_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Save master agent workflow state."""
        try:
            if db is None:
                print(f"[MOCK] Would save workflow for analysis {analysis_id}")
                return True
            
            doc_ref = db.collection("analyses").document(analysis_id)
            doc_ref.set({
                "workflow": workflow_data,
                "status": workflow_data.get("status", "in_progress"),
                "timestamp": firestore.SERVER_TIMESTAMP
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error saving workflow: {e}")
            return False
    
    @staticmethod
    def save_opportunities(analysis_id: str, opportunities: list) -> bool:
        """Save ranked opportunities."""
        try:
            if db is None:
                print(f"[MOCK] Would save {len(opportunities)} opportunities for analysis {analysis_id}")
                return True
            
            doc_ref = db.collection("analyses").document(analysis_id)
            doc_ref.set({
                "opportunities": opportunities,
                "opportunity_count": len(opportunities),
                "timestamp": firestore.SERVER_TIMESTAMP
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error saving opportunities: {e}")
            return False
    
    @staticmethod
    def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete analysis from Firebase."""
        try:
            if db is None:
                return None
            
            doc_ref = db.collection("analyses").document(analysis_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                # Get all agent outputs
                agents_ref = doc_ref.collection("agents")
                agents = {}
                for agent_doc in agents_ref.stream():
                    agents[agent_doc.id] = agent_doc.to_dict()
                data["agents"] = agents
                return data
            return None
        except Exception as e:
            print(f"Error retrieving analysis: {e}")
            return None





