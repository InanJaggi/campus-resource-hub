# AI Contribution: Cursor AI suggested the initial DAL structure for resource data access.
# The CRUD methods were reviewed and enhanced with proper type hints and error handling.

from typing import List, Optional
from ..extensions import db
from ..models.models import Resource


def create_resource(**kwargs) -> Resource:
    resource = Resource(**kwargs)
    db.session.add(resource)
    db.session.commit()
    return resource


def get_resource(resource_id: int) -> Optional[Resource]:
    return Resource.query.get(resource_id)


def search_resources(keyword: str | None = None, category: str | None = None) -> List[Resource]:
    query = Resource.query
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((Resource.title.ilike(like)) | (Resource.description.ilike(like)))
    if category:
        query = query.filter_by(category=category)
    return query.order_by(Resource.created_at.desc()).all()


def update_resource(resource: Resource, **kwargs) -> Resource:
    for k, v in kwargs.items():
        setattr(resource, k, v)
    db.session.commit()
    return resource


