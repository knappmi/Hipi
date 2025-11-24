"""Plugin marketplace registry"""

import logging
import uuid
import json
from typing import List, Optional, Dict
from datetime import datetime

from home_assistant_platform.marketplace.database import Database, PluginListing, Purchase, Review
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


class MarketplaceRegistry:
    """Manages plugin marketplace registry"""
    
    def __init__(self):
        self.db = Database()
    
    def register_plugin(self, plugin_data: Dict) -> Optional[str]:
        """Register a new plugin in the marketplace"""
        session = self.db.get_session()
        try:
            plugin_id = plugin_data.get("id") or str(uuid.uuid4())
            
            listing = PluginListing(
                id=plugin_id,
                name=plugin_data["name"],
                version=plugin_data["version"],
                description=plugin_data.get("description", ""),
                author=plugin_data["author"],
                author_id=plugin_data.get("author_id", ""),
                price=plugin_data.get("price", 0.0),
                is_free=plugin_data.get("price", 0.0) == 0.0,
                category=plugin_data.get("category"),
                tags=json.dumps(plugin_data.get("tags", [])),
                image_url=plugin_data.get("image_url"),
                download_url=plugin_data.get("download_url"),
                is_verified=False,
            )
            
            session.add(listing)
            session.commit()
            logger.info(f"Registered plugin: {plugin_id}")
            return plugin_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to register plugin: {e}")
            return None
        finally:
            session.close()
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Get plugin listing"""
        session = self.db.get_session()
        try:
            listing = session.query(PluginListing).filter_by(id=plugin_id).first()
            if listing:
                return self._listing_to_dict(listing)
            return None
        except Exception as e:
            logger.error(f"Failed to get plugin {plugin_id}: {e}")
            return None
        finally:
            session.close()
    
    def list_plugins(self, category: Optional[str] = None, search: Optional[str] = None, 
                     min_rating: Optional[float] = None, free_only: bool = False) -> List[Dict]:
        """List plugins with filters"""
        session = self.db.get_session()
        try:
            query = session.query(PluginListing).filter_by(is_active=True)
            
            if category:
                query = query.filter_by(category=category)
            
            if search:
                query = query.filter(
                    PluginListing.name.ilike(f"%{search}%") |
                    PluginListing.description.ilike(f"%{search}%")
                )
            
            if min_rating:
                query = query.filter(PluginListing.average_rating >= min_rating)
            
            if free_only:
                query = query.filter_by(is_free=True)
            
            listings = query.all()
            return [self._listing_to_dict(listing) for listing in listings]
        except Exception as e:
            logger.error(f"Failed to list plugins: {e}")
            return []
        finally:
            session.close()
    
    def purchase_plugin(self, plugin_id: str, user_id: str) -> Optional[Dict]:
        """Purchase a plugin"""
        session = self.db.get_session()
        try:
            listing = session.query(PluginListing).filter_by(id=plugin_id).first()
            if not listing:
                return None
            
            # Check if already purchased
            existing = session.query(Purchase).filter_by(
                plugin_id=plugin_id,
                user_id=user_id,
                status="completed"
            ).first()
            
            if existing:
                return {"status": "already_purchased", "purchase_id": existing.id}
            
            # Calculate revenue share
            amount = listing.price
            platform_share = amount * (settings.revenue_share_percentage / 100)
            author_share = amount - platform_share
            
            # Create purchase record
            purchase = Purchase(
                id=str(uuid.uuid4()),
                plugin_id=plugin_id,
                user_id=user_id,
                transaction_id=str(uuid.uuid4()),
                amount=amount,
                platform_share=platform_share,
                author_share=author_share,
                status="completed" if listing.is_free else "pending",
            )
            
            session.add(purchase)
            
            # Update plugin statistics
            listing.downloads += 1
            
            session.commit()
            
            logger.info(f"Plugin {plugin_id} purchased by {user_id}")
            return {
                "purchase_id": purchase.id,
                "transaction_id": purchase.transaction_id,
                "status": purchase.status,
                "download_url": listing.download_url,
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to purchase plugin {plugin_id}: {e}")
            return None
        finally:
            session.close()
    
    def add_review(self, plugin_id: str, user_id: str, rating: int, comment: Optional[str] = None) -> bool:
        """Add a review for a plugin"""
        session = self.db.get_session()
        try:
            # Check if user purchased the plugin
            purchase = session.query(Purchase).filter_by(
                plugin_id=plugin_id,
                user_id=user_id,
                status="completed"
            ).first()
            
            if not purchase:
                logger.warning(f"User {user_id} has not purchased plugin {plugin_id}")
                return False
            
            # Check if review already exists
            existing = session.query(Review).filter_by(
                plugin_id=plugin_id,
                user_id=user_id
            ).first()
            
            if existing:
                # Update existing review
                existing.rating = rating
                existing.comment = comment
            else:
                # Create new review
                review = Review(
                    id=str(uuid.uuid4()),
                    plugin_id=plugin_id,
                    user_id=user_id,
                    rating=rating,
                    comment=comment,
                )
                session.add(review)
            
            # Update plugin average rating
            listing = session.query(PluginListing).filter_by(id=plugin_id).first()
            if listing:
                reviews = session.query(Review).filter_by(plugin_id=plugin_id).all()
                if reviews:
                    listing.ratings_count = len(reviews)
                    listing.average_rating = sum(r.rating for r in reviews) / len(reviews)
            
            session.commit()
            logger.info(f"Review added for plugin {plugin_id}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add review: {e}")
            return False
        finally:
            session.close()
    
    def get_user_purchases(self, user_id: str) -> List[Dict]:
        """Get user's purchased plugins"""
        session = self.db.get_session()
        try:
            purchases = session.query(Purchase).filter_by(
                user_id=user_id,
                status="completed"
            ).all()
            
            return [{
                "purchase_id": p.id,
                "plugin_id": p.plugin_id,
                "purchased_at": p.purchased_at.isoformat(),
                "amount": p.amount,
            } for p in purchases]
        except Exception as e:
            logger.error(f"Failed to get user purchases: {e}")
            return []
        finally:
            session.close()
    
    def _listing_to_dict(self, listing: PluginListing) -> Dict:
        """Convert listing to dictionary"""
        return {
            "id": listing.id,
            "name": listing.name,
            "version": listing.version,
            "description": listing.description,
            "author": listing.author,
            "price": listing.price,
            "is_free": listing.is_free,
            "category": listing.category,
            "tags": json.loads(listing.tags) if listing.tags else [],
            "image_url": listing.image_url,
            "download_url": listing.download_url,
            "downloads": listing.downloads,
            "ratings_count": listing.ratings_count,
            "average_rating": listing.average_rating,
            "is_verified": listing.is_verified,
            "created_at": listing.created_at.isoformat() if listing.created_at else None,
        }

