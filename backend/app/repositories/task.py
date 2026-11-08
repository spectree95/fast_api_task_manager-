from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.models.tasks import Task
from app.schemas.tasks import TaskCreate, TaskFilter, TaskListResponce, OrderField, SortField
from app.models.users import User



class TaskRepository:
    
    def __init__(self, db: Session, current_user: User):    
        self.db = db
        self.current_user = current_user
        
    
    def get_by_id(self, task_id) -> Task:
        return (self.db
                .execute(select(Task)
                .where(Task.id==task_id, Task.owner_id==self.current_user.id))
                .scalar_one_or_none()
                )
    
    
    
    def get_tasks(self, task_filter: TaskFilter) -> TaskListResponce:
        filters = [Task.owner_id == self.current_user.id]

        if task_filter.completed is not None:
            filters.append(Task.completed == task_filter.completed)

        if task_filter.q:
            filters.append(or_(
                Task.title.icontains(task_filter.q, autoescape=True),
                Task.description.icontains(task_filter.q, autoescape=True),
            ))

        # Reuse every filter so pagination totals describe the same result set.
        query = select(Task).where(*filters)
        count_query = select(func.count(Task.id)).where(*filters)
        total = self.db.execute(count_query).scalar_one()
                
        sorted_columns = {
            SortField.created_at: Task.created_at,
            SortField.updated_at: Task.updated_at,
            SortField.title: Task.title
        }
                
        sorted_column = sorted_columns[task_filter.sort]
                
        if task_filter.order == OrderField.desc:
            query = query.order_by(sorted_column.desc())
                    
        elif task_filter.order == OrderField.asc:
            query = query.order_by(sorted_column.asc())
                
        query = query.order_by(Task.id).offset(task_filter.skip).limit(task_filter.limit)
                
        tasks = self.db.execute(query).scalars().all()
        return TaskListResponce(
            items=tasks,
            total=total,
            skip=task_filter.skip,
            limit=task_filter.limit,
                    
        )
    
    
    
    def create(self, task: TaskCreate) -> Task:
        new_task = Task(title = task.title, description = task.description, owner = self.current_user)
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task
        
    
    def update(self,task_id, data):
        task = self.get_by_id(task_id)
        
        for field, value in data.items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task        
                
    
    
    def delete(self, task_id: int) -> None:
        task = self.get_by_id(task_id)
        self.db.delete(task)
        self.db.commit()
