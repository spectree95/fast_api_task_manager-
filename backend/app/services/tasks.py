from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.users import User
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskUpdate, SortField, OrderField, TaskListResponce
from app.core.exceptions import TaskNotFoundExceptions


def create_task(
    db: Session,
    task:TaskCreate,
    current_user: User,
):
    db_task = Task(
        title = task.title,
        description = task.description,
        owner_id = current_user.id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


def get_tasks(
    skip: int,
    limit: int,
    completed: bool | None,
    sort: SortField,
    order: OrderField,
    db: Session,
    current_user: User,
):
    query = select(Task)
    
    if completed is not None:
        query = query.where(Task.completed == completed)
        
    count_query = select(func.count(Task.id))
    
    if completed is not None:
        count_query = count_query.where(
            Task.completed == completed,
            Task.owner_id == current_user.id    
        )
    
    total = db.execute(count_query).scalar_one()
    
    sorted_columns = {
        SortField.created_at: Task.created_at,
        SortField.updated_at: Task.updated_at,
        SortField.title: Task.title
    }
    
    sorted_column = sorted_columns[sort]
    
    if order == OrderField.desc:
        query = query.order_by(sorted_column.desc())
        
    elif order == OrderField.asc:
        query = query.order_by(sorted_column.asc())
    
    query = query.offset(skip).limit(limit)
    
    tasks = db.execute(query).scalars().all()
    return TaskListResponce(
        items=tasks,
        total=total,
        skip=skip,
        limit=limit,
        
    )





def get_task(
    db: Session,
    task_id: int,
    current_user: User
):
    task = db.execute(select(Task).where(
        Task.id == task_id,
        Task.owner_id == current_user.id,    
    )).scalar_one_or_none()
    
    if task is None:
        raise TaskNotFoundExceptions()
    
    return task
    

def update_task(
    task_id: int,
    db: Session,
    current_user: User,
    task_data: TaskUpdate,
):
    task = db.execute(select(Task).where(
        Task.id == task_id,
        Task.owner_id == current_user.id,
    )).scalar_one_or_none()
    
    if task is None:
        raise TaskNotFoundExceptions()
    
    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task
    

def delete_task(
    task_id: int,
    db:Session,
    current_user: User,
):
    task = db.execute(select(Task).where(
        Task.id == task_id,
        Task.owner_id == current_user.id
    )).scalar_one_or_none()
    
    if task is None:
        raise TaskNotFoundExceptions()
    
    db.delete(task)
    db.commit()
    
    
    