from typing import List, Type

from fastapi import Depends, Path, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.util.errors import InvalidParameter, ResourceDoesNotExist, ResourceAlreadyExists


class PlainOkResponse(BaseModel):
    content: dict = {'result': 'OK'}
    definition: dict = {"content": {'application/json': {'example': content}}}


def instance_existence(model: Base, id_field: str):
    def wrapped(id_value: str = Path(..., alias=id_field), db: Session = Depends(get_db)) -> Base:
        if type(id_value) == str:
            filters = {k: v for k, v in zip(id_field.split('_'), id_value.split('_'))}
        else:
            filters = {id_field: id_value}
        db_instance = db.query(model).filter_by(**filters).first()

        if db_instance is None:
            error = ResourceDoesNotExist(model.__name__)
            raise HTTPException(error.status_code, error.content)
        return db_instance

    return wrapped


def create_instance(db: Session, instance: BaseModel, model: Base):
    db_instance = model(**instance.dict())
    return save_instance(db=db, db_instance=db_instance)


def save_instance(db_instance, db: Session):
    try:
        db.add(db_instance)
        db.commit()
        db.refresh(db_instance)
    except IntegrityError as err:
        raise ResourceAlreadyExists(type(db_instance).__name__)
    return db_instance


def delete_instance(instance: BaseModel, db: Session):
    db.delete(instance)
    db.commit()


def paginator(query, page_number, per_page_limit):
    count = query.count()
    total_pages = max(1, (count % per_page_limit != 0) + count // per_page_limit)
    has_next = page_number < total_pages
    has_prev = page_number > 1
    if not (0 < page_number <= total_pages):
        raise InvalidParameter('page number exceeds limits')
    offset = (page_number - 1) * per_page_limit
    items = query.offset(offset).limit(per_page_limit).all()

    return {
        'page': page_number,
        'total_pages': total_pages,
        'total_items': count,
        'items_per_page': per_page_limit,
        'has_next': has_next,
        'has_prev': has_prev,
        'items': items
    }


class Filter:
    operators = {
        'exact': {
            'description': "Matches the exact value. Equivalent to <field = 'value'>",
            'expression': lambda column: column.__eq__},
        'partial': {
            'description':
                "Matches the value as contained in the field. Equivalent to <field LIKE '%value%'>",
            'expression': lambda column: lambda value: column.like(f'%{value}%')},
        'start': {
            'description':
                "Matches the value as start of field. Equivalent to <field LIKE 'value%'>",
            'expression': lambda column: lambda value: column.like(f'{value}%')},
        'end': {
            'description': "Matches the value as end of field. Equivalent to <field LIKE '%value'>",
            'expression': lambda column: lambda value: column.like(f'%{value}')},
        'word_start': {
            'description':
                "Matches the start of any word in the field. Equivalent to <field LIKE '% value%'>",
            'expression': lambda column: lambda value: column.like(f'% {value}%')},
        'anyOf': {
            'description':
                "Matches any field whose value is any from the given set. Equivalent to "
                "<field IN (value1, value2, ...)>.<br>Value format should be a list of values "
                "separated by pipe symbol (e.g. anyOf(budget, [1|10|100]))",
            'expression': lambda column: lambda values: column.in_(values[1:-1].split('|'))},
    }

    docs = "Filter data. Input format: operation(field, value). Available operations: <br>" \
           + '\n'.join([f'<br>**-{k}**: ' + v.get('description') for k, v in operators.items()])

    def __init__(self, expression: str, model: Base):
        operator, expression = tuple(expression.split('(', 1))
        self.model = model
        self.operator = self.operators.get(operator).get('expression')
        self.column, expression = tuple(expression.split(', ', 1))
        self.value = expression[:-1]

    def evaluate(self):
        criteria = self.operator(getattr(self.model, self.column))(self.value)
        return criteria if type(criteria) == tuple else (criteria,)


def query_objects(query_model,
                  db: Session,
                  filters: List[str] = (),
                  sort: List[str] = (),
                  filter_model: Type[Filter] = Filter):
    query = db.query(query_model)
    query = apply_filters(query, query_model, filters, filter_model)
    query = apply_sorts(query, sort)
    return query


def apply_filters(query, query_model, filters: List[str] = (), filter_model: Type[Filter] = Filter):
    for i in filters:
        criteria = filter_model(i, query_model).evaluate()
        query = query.filter(*criteria)
    return query


def apply_sorts(query, sort: List[str] = ()):
    for i in sort:
        expression = i.replace('.', ' ')
        split = i.split('.')
        if len(split) != 2 or split[1] not in ['asc', 'desc']:
            raise InvalidParameter('Sorting format must be in the form of <field>.<asc|desc>')

        query = query.order_by(text(expression))
    return query


def update_instance_data(data, instance, db: Session):
    for k, v in data.dict().items():
        getattr(instance, k)
        setattr(instance, k, v)
    return save_instance(db_instance=instance, db=db)


def error_docs(resource_name, *args: Type[Exception]):
    default = {404: "Unknown error"}
    return {
        k: {"description": v.replace('resource', resource_name)} for error in args
        for k, v in getattr(error, 'docs', default).items()
    }
