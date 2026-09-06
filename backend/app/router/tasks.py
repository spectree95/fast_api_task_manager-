from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.schemas.tasks import TaskCreate, TaskResponse, TaskListResponce, TaskUpdate, SortField, OrderField
from app.services.tasks import create_task, get_tasks, get_task, update_task,delete_task


router = APIRouter(prefix="/tasks", tags=["Tasks"],)


@router.post("/create", response_model=TaskResponse)
def create(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(
        task=task,
        db=db,
        current_user=current_user
    )

@router.get("", response_model=TaskListResponce)
def tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    completed: bool | None = None,
    sort: SortField = SortField.created_at,
    order: OrderField = OrderField.desc,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tasks(
        skip=skip,
        limit=limit,
        completed=completed,
        sort=sort,
        order=order,
        db=db,
        current_user=current_user,
    )



    
@router.get("/{task_id}", response_model=TaskResponse)
def get_one_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task(
        task_id=task_id,
        db=db,
        current_user=current_user,
    )
    
    
@router.patch("/{task_id}", response_model=TaskResponse)
def update(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_task(
        task_id=task_id,
        task_data=task_data,
        db=db,
        current_user=current_user,
    )
    
    
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_task(
        task_id=task_id,
        db=db,
        current_user=current_user,
    )