"""
Firestore database module with automatic local/cloud detection.

Detects environment based on FIRESTORE_EMULATOR_HOST:
- If set: Uses local Firestore emulator (Docker)
- If not set: Uses production Cloud Firestore
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import firestore

# Auto-detect environment
USING_EMULATOR = bool(os.getenv('FIRESTORE_EMULATOR_HOST'))
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'eleventyseven-45e7c')

print(f"{'='*80}")
print(f"FIRESTORE CONFIGURATION:")
print(f"  Environment: {'LOCAL EMULATOR' if USING_EMULATOR else 'PRODUCTION CLOUD'}")
print(f"  Project ID: {GCP_PROJECT_ID}")
if USING_EMULATOR:
    print(f"  Emulator Host: {os.getenv('FIRESTORE_EMULATOR_HOST')}")
print(f"{'='*80}")

# Initialize Firestore client
db = firestore.Client(project=GCP_PROJECT_ID)


class ConversationDB:
    """Handles all Firestore conversation operations."""

    COLLECTION = 'conversations'

    @staticmethod
    def generate_id() -> str:
        """Generate a unique conversation ID."""
        return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

    @staticmethod
    def save_conversation(
        conversation_id: str,
        messages: List[Dict[str, Any]],
        title: Optional[str] = None,
        user_saved: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save or update a conversation in Firestore.

        Args:
            conversation_id: Unique conversation identifier
            messages: List of message dicts with {role, content}
            title: Optional user-provided title
            user_saved: Whether user explicitly saved this conversation
            metadata: Optional additional metadata

        Returns:
            Dict with conversation data
        """
        doc_ref = db.collection(ConversationDB.COLLECTION).document(conversation_id)

        # Check if conversation exists
        existing = doc_ref.get()

        conversation_data = {
            'conversation_id': conversation_id,
            'messages': messages,
            'title': title,
            'user_saved': user_saved,
            'message_count': len(messages),
            'updated_at': firestore.SERVER_TIMESTAMP,
            'metadata': metadata or {}
        }

        # Add created_at only for new conversations
        if not existing.exists:
            conversation_data['created_at'] = firestore.SERVER_TIMESTAMP

        doc_ref.set(conversation_data, merge=True)

        # Get the saved document to return with timestamps
        saved_doc = doc_ref.get()
        return saved_doc.to_dict()

    @staticmethod
    def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation by ID."""
        doc_ref = db.collection(ConversationDB.COLLECTION).document(conversation_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None

    @staticmethod
    def list_conversations(
        user_saved_only: bool = False,
        limit: int = 100,
        order_by: str = 'updated_at',
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        List conversations with optional filtering.

        Args:
            user_saved_only: If True, only return user-saved conversations
            limit: Maximum number of conversations to return
            order_by: Field to order by (created_at, updated_at, message_count)
            descending: Sort in descending order

        Returns:
            List of conversation dicts
        """
        query = db.collection(ConversationDB.COLLECTION)

        if user_saved_only:
            query = query.where('user_saved', '==', True)

        direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
        query = query.order_by(order_by, direction=direction).limit(limit)

        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    @staticmethod
    def update_conversation_title(conversation_id: str, title: str) -> bool:
        """Update the title of a conversation."""
        doc_ref = db.collection(ConversationDB.COLLECTION).document(conversation_id)

        if not doc_ref.get().exists:
            return False

        doc_ref.update({
            'title': title,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True

    @staticmethod
    def toggle_user_saved(conversation_id: str, user_saved: bool = True, title: Optional[str] = None) -> bool:
        """
        Toggle user_saved flag and optionally set title.

        This is called when user clicks "Save" button.
        """
        doc_ref = db.collection(ConversationDB.COLLECTION).document(conversation_id)

        if not doc_ref.get().exists:
            return False

        update_data = {
            'user_saved': user_saved,
            'updated_at': firestore.SERVER_TIMESTAMP
        }

        if title:
            update_data['title'] = title

        doc_ref.update(update_data)
        return True

    @staticmethod
    def delete_conversation(conversation_id: str) -> bool:
        """Delete a conversation."""
        doc_ref = db.collection(ConversationDB.COLLECTION).document(conversation_id)

        if not doc_ref.get().exists:
            return False

        doc_ref.delete()
        return True

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get conversation statistics."""
        all_convs = list(db.collection(ConversationDB.COLLECTION).stream())
        user_saved_convs = [c for c in all_convs if c.to_dict().get('user_saved', False)]

        total_messages = sum(c.to_dict().get('message_count', 0) for c in all_convs)

        return {
            'total_conversations': len(all_convs),
            'user_saved_conversations': len(user_saved_convs),
            'auto_saved_conversations': len(all_convs) - len(user_saved_convs),
            'total_messages': total_messages,
            'environment': 'emulator' if USING_EMULATOR else 'production'
        }


# Export for easy access
def get_db() -> ConversationDB:
    """Get ConversationDB instance."""
    return ConversationDB


# Test connection on import
try:
    # Try a simple operation to verify connection
    db.collection(ConversationDB.COLLECTION).limit(1).get()
    print(f"✓ Firestore connection successful")
except Exception as e:
    print(f"✗ Firestore connection failed: {e}")
