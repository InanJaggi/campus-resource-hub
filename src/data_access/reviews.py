# AI Contribution: Cursor AI suggested the review aggregation and rating calculation logic.
# The _recalculate_resource_rating function was reviewed and enhanced for accuracy.

from statistics import mean
from ..extensions import db
from ..models.models import Review, Resource


def add_review(resource_id: int, user_id: int, rating: int, comment: str = "") -> Review:
    rv = Review(resource_id=resource_id, user_id=user_id, rating=rating, comment=comment)
    db.session.add(rv)
    db.session.commit()
    _recalculate_resource_rating(resource_id)
    return rv


def _recalculate_resource_rating(resource_id: int) -> None:
    ratings = [r.rating for r in Review.query.filter_by(resource_id=resource_id).all()]
    avg = mean(ratings) if ratings else 0
    res = Resource.query.get(resource_id)
    if res:
        res.avg_rating = avg
        db.session.commit()


