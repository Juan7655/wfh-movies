from typing import Type, List

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.models.schemas import Page
from app.service.commons import error_docs, Filter, query_objects, paginator, create_instance, instance_existence, \
    update_instance_data, PlainOkResponse, delete_instance
from app.util.decorators import error_handling
from app.util.errors import InvalidParameter, ResourceAlreadyExists, ResourceDoesNotExist


def crud(router, read_model: Type[BaseModel], write_model: Type[BaseModel], query_model: Base, id_field: str,
         filter_model: Type[Filter] = Filter, **kwargs):
    entity_name = query_model.__name__

    @router.get('', response_model=Page[read_model], responses=error_docs(entity_name, InvalidParameter))
    @error_handling
    def read_all(
            db: Session = Depends(get_db),
            limit: int = Query(10, description='Max number of items per page'),
            page: int = 1,
            sort: List[str] = Query([], description="Sorting parameter given in the format field."
                                                    "{asc|desc} (e.g. title.asc)"),
            filters: List[str] = Query([], description=filter_model.docs, alias='filter')
    ):
        query = query_objects(db=db, query_model=query_model, filters=filters, sort=sort, filter_model=filter_model)
        return paginator(query, page_number=page, per_page_limit=limit)

    @router.post('', response_model=read_model, responses=error_docs(entity_name, ResourceAlreadyExists))
    @error_handling
    def create(data: write_model, db: Session = Depends(get_db)):
        fun = kwargs.get('post', create_instance)
        return fun(db=db, instance=data, model=query_model)

    @router.get("/{%s}" % id_field, response_model=read_model, responses=error_docs(entity_name, ResourceDoesNotExist))
    @error_handling
    def read_one(instance: Base = Depends(instance_existence(query_model, id_field=id_field))):
        return instance

    @router.put("/{%s}" % id_field, response_model=read_model, responses=error_docs(entity_name, ResourceDoesNotExist))
    @error_handling
    def update_data(
            data: write_model,
            db: Session = Depends(get_db),
            instance: Base = Depends(instance_existence(query_model, id_field=id_field))
    ):
        return update_instance_data(db=db, data=data, instance=instance)

    @router.delete(
        "/{%s}" % id_field,
        responses={200: PlainOkResponse().definition, **error_docs(entity_name, ResourceDoesNotExist)}
    )
    @error_handling
    def delete(
            db: Session = Depends(get_db),
            instance: Base = Depends(instance_existence(query_model, id_field=id_field))
    ):
        delete_instance(db=db, instance=instance)
        return PlainOkResponse().content
