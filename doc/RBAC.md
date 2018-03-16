# Role Based Access Control

## Design
* A `Route` is correspond to one or more `Resource` or `Object`
* A `Route` can be protected by a `Permission`
* A `Role` can be assigned zero or more `Permissions`(verbs)
* A `Subject`, user in our context, can be assigned zero or more `Roles`

## Use Case
A company has many departments each has many employees. This company is maintaining a `todo` list.
```
# an example of todo 
{
    title: 'visit usa',
    created_by: 'lisa',
    created_at: 1512345678,
    finished_at: 1521345678,
    finished_by: 'Josh',
    dep: 'R&D'
}
```

* `admin` can do everything to this list  
* `dep manager` can do everything to `todos` that belong to that department  
* `employee` can mark `todos`, belong to his department, as completed.

That says we have:
* 3 roles: `admin`, `manager`, `employee`.
* 5(always) permissions: `LIST`, `GET`, `POST`, `PATCH`, `DELETE`
* 1 set of `n` **subset** of todos

We have 5 basic routes and 1 permission defined as below.
1. `POST /todos/`
2. `GET /todos/`
3. `GET /todos/<int:id>`
4. `PATCH /todos/<int:id>`
5. `DELETE /todos/<int:id>` => delete todo

As employee does not have `delete todo` permission, he is blocked from that API access. 

But How do we avoid manager/employee from touching `todos` of other departments? 

We change our routes like below:
1. `GET     /todos/`                        => list todo
1. `POST    /dep/<depname>/todos/`
2. `GET     /dep/<depname>/todos/`
3. `GET     /dep/<depname>/todos/<int:id>`
4. `PATCH   /dep/<depname>/todos/<int:id>`
5. `DELETE  /dep/<depname>/todos/<int:id>`  => delete todo

* `admin` must only be assigned with `list todo` permission.
* do department relationship check for `route` that start with `/dep/`

We now have `admin` that can do anything and touch any todo and power restricted
manager and employee.

It should be stressed that whether one role can touch an object(resource) or not is application specific logic and not in the scope of this RBAC design. We only check if one role has a specific permission or ability.