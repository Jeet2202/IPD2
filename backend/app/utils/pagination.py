"""
Pagination utilities — complements PaginationParams from dependencies.py.

PaginationParams (in dependencies.py) = query parameter extraction.
This module = building paginated responses from query results.

The main utility is paginate_query(), which runs a Beanie query with
skip/limit and total count, returning data ready for PaginatedResponse.

Usage in repository layer:
    from app.utils.pagination import paginate_query

    async def list_workers(pagination: PaginationParams, filters: dict):
        query = Worker.find(filters)
        return await paginate_query(query, pagination)

Usage in router layer:
    data, total = await worker_repo.list_workers(pagination, filters)
    return PaginatedResponse.build(
        data=data,
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total,
    )
"""

from typing import Any, TypeVar

from beanie import Document
from beanie.odm.queries.find import FindMany

from app.core.dependencies import PaginationParams


T = TypeVar("T", bound=Document)


async def paginate_query(
    query: FindMany[T],
    pagination: PaginationParams,
) -> tuple[list[T], int]:
    """
    Execute a Beanie find query with pagination and return results + total.

    Runs two queries in sequence:
        1. Count total matching documents (for pagination metadata).
        2. Fetch the page of documents with skip/limit.

    Args:
        query: A Beanie FindMany query (e.g., Worker.find(filters)).
        pagination: PaginationParams with page, page_size, skip.

    Returns:
        Tuple of (list of documents, total count).

    Example:
        query = Worker.find({"is_active": True})
        workers, total = await paginate_query(query, pagination)
    """
    total = await query.count()

    documents = (
        await query
        .skip(pagination.skip)
        .limit(pagination.page_size)
        .to_list()
    )

    return documents, total


async def paginate_aggregation(
    document_class: type[T],
    pipeline: list[dict[str, Any]],
    pagination: PaginationParams,
) -> tuple[list[dict[str, Any]], int]:
    """
    Execute a MongoDB aggregation pipeline with pagination.

    For complex queries that can't use Beanie's find() — aggregations
    with $lookup, $group, $project, etc.

    Adds $skip and $limit stages to the pipeline and runs a separate
    count pipeline for the total.

    Args:
        document_class: The Beanie Document class to aggregate on.
        pipeline: MongoDB aggregation pipeline stages.
        pagination: PaginationParams with page, page_size, skip.

    Returns:
        Tuple of (list of result dicts, total count).

    Example:
        pipeline = [
            {"$match": {"status": "available"}},
            {"$lookup": {...}},
            {"$project": {"name": 1, "rating": 1}},
        ]
        results, total = await paginate_aggregation(
            Worker, pipeline, pagination
        )
    """
    # Count pipeline — same match stages, then count
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result = await document_class.aggregate(count_pipeline).to_list()
    total = count_result[0]["total"] if count_result else 0

    # Data pipeline — add skip and limit
    data_pipeline = pipeline + [
        {"$skip": pagination.skip},
        {"$limit": pagination.page_size},
    ]
    documents = await document_class.aggregate(data_pipeline).to_list()

    return documents, total
