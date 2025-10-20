"""
MongoDB Database Backup & Export System
Provides full database backup and individual collection exports
"""
import os
import json
from datetime import datetime, timezone
from typing import Dict, List
import zipfile
from io import BytesIO

class DatabaseBackupManager:
    """
    Handles all database backup operations:
    - Full database export
    - Individual collection exports  
    - Backup to JSON files
    - Backup history tracking
    """
    
    def __init__(self, db):
        self.db = db
        self.backup_dir = "/app/backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def get_full_database_export(self) -> Dict:
        """
        Export complete database with all collections
        Returns structured JSON-compatible data
        """
        try:
            backup_data = {
                "backup_info": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "database_name": self.db.name,
                    "backup_type": "full_export",
                    "version": "1.0"
                },
                "collections": {}
            }
            
            # Get all collection names
            collection_names = await self.db.list_collection_names()
            
            # Export each collection
            for collection_name in collection_names:
                try:
                    collection = self.db[collection_name]
                    documents = await collection.find().to_list(length=None)
                    
                    # Convert MongoDB documents to JSON-serializable format
                    serialized_docs = [
                        self._serialize_document(doc) for doc in documents
                    ]
                    
                    backup_data["collections"][collection_name] = {
                        "document_count": len(serialized_docs),
                        "documents": serialized_docs
                    }
                    
                    print(f"✅ Exported {len(serialized_docs)} documents from {collection_name}")
                    
                except Exception as e:
                    print(f"⚠️ Error exporting {collection_name}: {e}")
                    backup_data["collections"][collection_name] = {
                        "error": str(e),
                        "document_count": 0,
                        "documents": []
                    }
            
            # Add summary
            backup_data["summary"] = {
                "total_collections": len(collection_names),
                "total_documents": sum(
                    c.get("document_count", 0) 
                    for c in backup_data["collections"].values()
                ),
                "successful_collections": len([
                    c for c in backup_data["collections"].values()
                    if "error" not in c
                ])
            }
            
            return backup_data
            
        except Exception as e:
            print(f"❌ Error in full database export: {e}")
            raise Exception(f"خطا در تهیه نسخه پشتیبان: {str(e)}")
    
    async def create_backup_file(self, backup_type: str = "full") -> str:
        """
        Create backup file and save to disk
        Returns: backup file path
        """
        try:
            # Get backup data
            backup_data = await self.get_full_database_export()
            
            # Generate filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{backup_type}_{timestamp}.json"
            filepath = os.path.join(self.backup_dir, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(filepath)
            
            print(f"✅ Backup created: {filepath} ({file_size / 1024 / 1024:.2f} MB)")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error creating backup file: {e}")
            raise Exception(f"خطا در ایجاد فایل پشتیبان: {str(e)}")
    
    async def get_collection_export(self, collection_name: str) -> Dict:
        """Export single collection"""
        try:
            collection = self.db[collection_name]
            documents = await collection.find().to_list(length=None)
            
            serialized_docs = [
                self._serialize_document(doc) for doc in documents
            ]
            
            return {
                "collection_name": collection_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "document_count": len(serialized_docs),
                "documents": serialized_docs
            }
            
        except Exception as e:
            print(f"❌ Error exporting collection {collection_name}: {e}")
            raise Exception(f"خطا در صادرات {collection_name}: {str(e)}")
    
    async def get_backup_list(self) -> List[Dict]:
        """Get list of all backup files"""
        try:
            backups = []
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, filename)
                    file_stat = os.stat(filepath)
                    
                    backups.append({
                        "filename": filename,
                        "filepath": filepath,
                        "size_mb": round(file_stat.st_size / 1024 / 1024, 2),
                        "created_at": datetime.fromtimestamp(file_stat.st_ctime, tz=timezone.utc).isoformat(),
                        "modified_at": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat()
                    })
            
            # Sort by creation date, newest first
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"❌ Error listing backups: {e}")
            return []
    
    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {
                "database_name": self.db.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "collections": []
            }
            
            collection_names = await self.db.list_collection_names()
            
            for collection_name in collection_names:
                collection = self.db[collection_name]
                count = await collection.count_documents({})
                
                # Get estimated collection size (sampling)
                sample_doc = await collection.find_one()
                estimated_size = len(json.dumps(
                    self._serialize_document(sample_doc) if sample_doc else {}
                )) * count
                
                stats["collections"].append({
                    "name": collection_name,
                    "document_count": count,
                    "estimated_size_kb": round(estimated_size / 1024, 2)
                })
            
            stats["total_collections"] = len(collection_names)
            stats["total_documents"] = sum(c["document_count"] for c in stats["collections"])
            stats["total_size_mb"] = round(
                sum(c["estimated_size_kb"] for c in stats["collections"]) / 1024,
                2
            )
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {"error": str(e)}
    
    def _serialize_document(self, doc: Dict) -> Dict:
        """
        Convert MongoDB document to JSON-serializable format
        Handles ObjectId, datetime, and other special types
        """
        if not doc:
            return {}
        
        serialized = {}
        
        for key, value in doc.items():
            if key == '_id':
                # Skip MongoDB's internal _id
                continue
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = self._serialize_document(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_document(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        
        return serialized
    
    async def delete_backup(self, filename: str) -> bool:
        """Delete backup file"""
        try:
            filepath = os.path.join(self.backup_dir, filename)
            
            if os.path.exists(filepath) and filename.endswith('.json'):
                os.remove(filepath)
                print(f"✅ Deleted backup: {filename}")
                return True
            else:
                raise Exception(f"فایل یافت نشد: {filename}")
                
        except Exception as e:
            print(f"❌ Error deleting backup: {e}")
            raise Exception(f"خطا در حذف پشتیبان: {str(e)}")
    
    async def restore_from_backup(self, backup_data: Dict) -> Dict:
        """
        Restore database from backup data
        CAUTION: This will DELETE existing data and replace with backup
        """
        try:
            result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "started",
                "collections_restored": [],
                "collections_failed": [],
                "total_documents_restored": 0
            }
            
            # Validate backup structure
            if "collections" not in backup_data:
                raise Exception("Invalid backup format: 'collections' key not found")
            
            collections_data = backup_data.get("collections", {})
            
            for collection_name, collection_info in collections_data.items():
                try:
                    print(f"🔄 Restoring {collection_name}...")
                    
                    # Get documents from backup
                    documents = collection_info.get("documents", [])
                    
                    if not documents:
                        print(f"⚠️ No documents to restore in {collection_name}")
                        continue
                    
                    # Get MongoDB collection
                    collection = self.db[collection_name]
                    
                    # Delete existing data
                    delete_result = await collection.delete_many({})
                    print(f"   🗑️ Deleted {delete_result.deleted_count} existing documents")
                    
                    # Prepare documents for insertion
                    docs_to_insert = []
                    for doc in documents:
                        # Remove _id if present (let MongoDB create new ones)
                        cleaned_doc = {k: v for k, v in doc.items() if k != '_id'}
                        
                        # Convert ISO datetime strings back to datetime objects
                        for key, value in cleaned_doc.items():
                            if isinstance(value, str) and 'T' in value and ('+' in value or 'Z' in value):
                                try:
                                    # Try parsing as datetime
                                    from dateutil import parser
                                    cleaned_doc[key] = parser.parse(value)
                                except:
                                    # Keep as string if not valid datetime
                                    pass
                        
                        docs_to_insert.append(cleaned_doc)
                    
                    # Insert documents
                    if docs_to_insert:
                        insert_result = await collection.insert_many(docs_to_insert)
                        inserted_count = len(insert_result.inserted_ids)
                        
                        result["collections_restored"].append({
                            "name": collection_name,
                            "documents_restored": inserted_count
                        })
                        result["total_documents_restored"] += inserted_count
                        
                        print(f"   ✅ Restored {inserted_count} documents to {collection_name}")
                    
                except Exception as e:
                    error_msg = f"Error restoring {collection_name}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    result["collections_failed"].append({
                        "name": collection_name,
                        "error": error_msg
                    })
            
            result["status"] = "completed"
            result["success"] = len(result["collections_failed"]) == 0
            
            print(f"\n✅ Restore completed:")
            print(f"   - Collections restored: {len(result['collections_restored'])}")
            print(f"   - Collections failed: {len(result['collections_failed'])}")
            print(f"   - Total documents: {result['total_documents_restored']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Critical error in restore: {e}")
            raise Exception(f"خطا در بازگردانی: {str(e)}")


# Singleton instance
_backup_manager = None

async def get_backup_manager(db):
    """Get singleton instance of Backup Manager"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = DatabaseBackupManager(db)
    return _backup_manager
